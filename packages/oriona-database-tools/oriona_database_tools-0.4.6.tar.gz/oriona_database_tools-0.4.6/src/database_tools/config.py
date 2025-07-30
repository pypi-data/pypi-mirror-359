"""Configuration management using pydantic."""

import base64
import binascii
import json
import os
import tempfile
from pathlib import Path

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BigQueryConfig(BaseModel):
    """BigQuery-specific configuration."""
    
    project_id: str = Field(..., description="BigQuery project ID")
    credentials_base64: Optional[str] = Field(default=None, description="Base64 encoded service account JSON")
    dataset: Optional[str] = Field(default=None, description="Default dataset name")
    location: str = Field(default="US", description="BigQuery location/region")
    
    def get_credentials_path(self) -> Optional[str]:
        """Create temporary credentials file from base64 data."""
        if not self.credentials_base64:
            return None
        
        try:
            # Clean and fix base64 string
            cleaned_base64 = self.credentials_base64.strip()
            
            # Add padding if necessary
            missing_padding = len(cleaned_base64) % 4
            if missing_padding:
                cleaned_base64 += '=' * (4 - missing_padding)
            
            # Decode base64 credentials
            credentials_json = base64.b64decode(cleaned_base64).decode('utf-8')
            
            # Validate JSON
            json.loads(credentials_json)
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
            temp_file.write(credentials_json)
            temp_file.close()
            
            return temp_file.name
        except (binascii.Error, json.JSONDecodeError, Exception) as e:
            raise ValueError(f"Invalid BigQuery credentials: {e}")
    
    def cleanup_credentials_file(self, file_path: str) -> None:
        """Clean up temporary credentials file."""
        if file_path and Path(file_path).exists():
            try:
                Path(file_path).unlink()
            except Exception:
                pass  # Best effort cleanup


class DatabaseConfig(BaseModel):
    """Database connection configuration."""
    
    url: str = Field(..., description="Database connection URL")
    pool_size: int = Field(2, ge=1, le=20, description="Connection pool size")
    max_overflow: int = Field(3, ge=0, le=30, description="Maximum overflow connections")
    pool_timeout: int = Field(30, ge=5, le=300, description="Pool timeout in seconds")
    pool_recycle: int = Field(1800, ge=300, le=7200, description="Connection recycle time in seconds")
    connect_timeout: int = Field(10, ge=1, le=60, description="Connection timeout in seconds")
    statement_timeout: int = Field(30000, ge=1000, le=300000, description="Statement timeout in milliseconds")
    bigquery_config: Optional[BigQueryConfig] = Field(default=None, description="BigQuery-specific configuration")
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Convert postgres:// to postgresql:// for compatibility."""
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v
    
    @property
    def is_postgresql(self) -> bool:
        """Check if database is PostgreSQL."""
        return self.url.startswith("postgresql://")
    
    @property
    def is_bigquery(self) -> bool:
        """Check if database is BigQuery."""
        return self.url.startswith("bigquery://")
    
    @property
    def is_mssql(self) -> bool:
        """Check if database is Microsoft SQL Server."""
        return (self.url.startswith("mssql://") or 
                self.url.startswith("mssql+pymssql://"))


class QueryConfig(BaseModel):
    """Query execution configuration."""
    
    default_timeout: int = Field(30, ge=1, le=300, description="Default query timeout in seconds")
    default_max_rows: int = Field(100, ge=0, le=10000, description="Default max rows to return")
    max_sample_size: int = Field(100, ge=1, le=1000, description="Maximum sample size for table exploration")


class TableFilterConfig(BaseModel):
    """Table filtering configuration."""
    
    whitelist: Optional[List[str]] = Field(default=None, description="List of allowed tables (if set, only these tables are accessible)")
    blacklist: Optional[List[str]] = Field(default=None, description="List of forbidden tables (these tables are always inaccessible)")
    
    @field_validator('whitelist', 'blacklist')
    @classmethod
    def normalize_table_names(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Normalize table names to lowercase for case-insensitive matching."""
        if v is None:
            return None
        return [table.lower().strip() for table in v if table.strip()]
    
    def is_table_allowed(self, table_name: str) -> bool:
        """Check if a table is allowed based on whitelist/blacklist rules."""
        table_lower = table_name.lower()
        
        # Blacklist takes precedence
        if self.blacklist and table_lower in self.blacklist:
            return False
        
        # If whitelist exists, table must be in it
        if self.whitelist:
            return table_lower in self.whitelist
        
        # No whitelist means all tables are allowed (unless blacklisted)
        return True


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    # Database settings
    database_url: str = Field(default="")
    
    # Query settings
    default_timeout: int = Field(default=30)
    default_max_rows: int = Field(default=100)
    max_sample_size: int = Field(default=100)
    
    # Pool settings
    pool_size: int = Field(default=2)
    max_overflow: int = Field(default=3)
    pool_recycle: int = Field(default=1800)
    
    # Logging
    log_level: str = Field(default="INFO")
    
    # Table filtering
    table_whitelist: Optional[List[str]] = Field(default=None, description="Comma-separated list of allowed tables")
    table_blacklist: Optional[List[str]] = Field(default=None, description="Comma-separated list of forbidden tables")
    
    # BigQuery settings
    bigquery_project_id: Optional[str] = Field(default=None, description="BigQuery project ID")
    bigquery_credentials_base64: Optional[str] = Field(default=None, description="Base64 encoded BigQuery service account JSON")
    bigquery_dataset: Optional[str] = Field(default=None, description="Default BigQuery dataset")
    bigquery_location: str = Field(default="US", description="BigQuery location/region")
    

    @field_validator('table_whitelist', 'table_blacklist', mode='before')
    @classmethod
    def parse_table_list(cls, v: Optional[str]) -> Optional[List[str]]:
        """Parse comma-separated table names from environment variable."""
        if v is None or not isinstance(v, str):
            return v
        return [table.strip() for table in v.split(',') if table.strip()]
    
    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration."""
        # Handle BigQuery configuration first (doesn't need DATABASE_URL)
        if self.bigquery_project_id:
            # BigQuery mode - DATABASE_URL is not required
            bigquery_config = BigQueryConfig(
                project_id=self.bigquery_project_id,
                credentials_base64=self.bigquery_credentials_base64,
                dataset=self.bigquery_dataset,
                location=self.bigquery_location,
            )
            
            # Construct BigQuery URL from project info
            dataset_part = f"/{self.bigquery_dataset}" if self.bigquery_dataset else ""
            database_url = f"bigquery://{self.bigquery_project_id}{dataset_part}"
            
            return DatabaseConfig(
                url=database_url,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_recycle=self.pool_recycle,
                bigquery_config=bigquery_config,
            )
        
        # Check if DATABASE_URL indicates BigQuery but no BIGQUERY_PROJECT_ID is set
        if self.database_url and self.database_url.startswith("bigquery://"):
            raise ValueError("BIGQUERY_PROJECT_ID is required when using bigquery:// DATABASE_URL")
        
        # SQL database mode - DATABASE_URL is required
        if not self.database_url:
            # Allow missing DATABASE_URL during testing
            if "pytest" in os.sys.modules:
                self.database_url = "sqlite:///test.db"
            else:
                raise ValueError("DATABASE_URL environment variable is required for SQL databases")
        
        return DatabaseConfig(
            url=self.database_url,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_recycle=self.pool_recycle,
            bigquery_config=None,
        )
    
    def get_query_config(self) -> QueryConfig:
        """Get query configuration."""
        return QueryConfig(
            default_timeout=self.default_timeout,
            default_max_rows=self.default_max_rows,
            max_sample_size=self.max_sample_size,
        )
    
    def get_table_filter_config(self) -> TableFilterConfig:
        """Get table filter configuration."""
        return TableFilterConfig(
            whitelist=self.table_whitelist,
            blacklist=self.table_blacklist,
        )