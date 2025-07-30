#!/usr/bin/env python3
"""MCP server providing database exploration and query tools."""

import json
import logging
import sys
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP

from .config import Settings
from .exceptions import (
    DatabaseToolsError,
    QueryExecutionError,
    QueryTimeoutError,
    QueryValidationError,
    TableNotFoundError,
    TableAccessDeniedError,
)
from .query_builder import QueryValidator
from .repository import DatabaseRepository

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize settings
settings = Settings()

# Set log level from settings
logging.getLogger().setLevel(settings.log_level)

# Initialize MCP application
app = FastMCP("database-tools")

# Global repository and configs - will be initialized lazily
repository = None
query_config = None


def get_repository() -> DatabaseRepository:
    """Get or initialize the database repository."""
    global repository, query_config
    if repository is None:
        db_config = settings.get_database_config()
        query_config = settings.get_query_config()
        table_filter_config = settings.get_table_filter_config()
        repository = DatabaseRepository(db_config, table_filter_config)
    return repository


def format_simple_error(error: Exception) -> Dict[str, Any]:
    """
    Format error as simple error response.
    
    list_tables and explore_table return simple {"error": str}
    query_database returns full error object
    """
    if isinstance(error, DatabaseToolsError):
        return {"error": error.message}
    return {"error": str(error)}


def format_query_error(error: Exception) -> Dict[str, Any]:
    """Format error for query_database with full details."""
    error_message = str(error)
    
    # Clean up SQL details from error message
    if '\n[SQL' in error_message:
        error_message = error_message.split('\n[SQL')[0].strip()
    
    # Truncate long error messages
    if len(error_message) > 300:
        error_message = error_message[:300] + "..."
    
    # Handle known exception types
    if isinstance(error, QueryValidationError):
        return {
            "error": error_message,
            "error_type": "ValidationError",
            "recommendation": "Only SELECT and WITH queries are allowed for security"
        }
    elif isinstance(error, QueryTimeoutError):
        return {
            "error": error_message,
            "error_type": "TimeoutError",
            "recommendation": "Try a simpler query or increase the timeout"
        }
    elif isinstance(error, QueryExecutionError):
        return {
            "error": error_message,
            "error_type": "QueryExecutionError",
            "recommendation": "Review query syntax and table structure"
        }
    
    # Analyze error message for specific patterns
    recommendation = _get_error_recommendation(error_message)
    
    return {
        "error": error_message,
        "error_type": type(error).__name__,
        "recommendation": recommendation
    }


def _get_error_recommendation(error_message: str) -> str:
    """
    Get recommendation based on error message patterns.
    
    Returns most specific recommendation that matches the error.
    """
    # Define error patterns and their recommendations
    error_patterns = [
        # BigQuery STRUCT errors
        {
            "patterns": ["No matching signature for operator", "STRUCT<"],
            "recommendation": "BigQuery STRUCT columns cannot be compared directly. Use dot notation to access individual fields (e.g., struct_column.field_name <= value)"
        },
        {
            "patterns": ["STRUCT<", "cannot be accessed"],
            "recommendation": "Access STRUCT fields using dot notation (e.g., SELECT struct_col.field FROM table)"
        },
        {
            "patterns": ["STRUCT<"],
            "recommendation": "BigQuery STRUCT columns require special handling. Use explore_table to see field structure and access fields with dot notation"
        },
        # BigQuery ARRAY errors
        {
            "patterns": ["ARRAY<"],
            "exclude": ["UNNEST"],
            "recommendation": "Array columns need UNNEST() to access elements. Example: SELECT * FROM table, UNNEST(array_column) AS element"
        },
        # Field access errors
        {
            "patterns": ["Cannot access field"],
            "recommendation": "Field not found in STRUCT. Use explore_table to see available fields"
        },
        # Table/column errors
        {
            "patterns": ["does not exist"],
            "recommendation": "Check table and column names with list_tables and explore_table"
        },
        {
            "patterns": ["doesn't exist"],
            "recommendation": "Check table and column names with list_tables and explore_table"
        },
        {
            "patterns": ["not found"],
            "recommendation": "Check table and column names with list_tables and explore_table"
        },
        # Permission errors
        {
            "patterns": ["permission denied"],
            "recommendation": "Check database permissions and credentials"
        },
        {
            "patterns": ["access denied"],
            "recommendation": "Check database permissions and credentials"
        },
        {
            "patterns": ["forbidden"],
            "recommendation": "Check database permissions and credentials"
        },
        # Syntax errors
        {
            "patterns": ["syntax error"],
            "recommendation": "Review SQL syntax - check for typos, missing quotes, or incorrect keywords"
        },
        {
            "patterns": ["unexpected token"],
            "recommendation": "Review SQL syntax - check for typos, missing quotes, or incorrect keywords"
        },
        {
            "patterns": ["invalid syntax"],
            "recommendation": "Review SQL syntax - check for typos, missing quotes, or incorrect keywords"
        }
    ]
    
    # Check each pattern (case-insensitive)
    error_message_lower = error_message.lower()
    
    for pattern_config in error_patterns:
        patterns = [p.lower() for p in pattern_config["patterns"]]
        exclude = [e.lower() for e in pattern_config.get("exclude", [])]
        
        # Check if all required patterns match
        if all(pattern in error_message_lower for pattern in patterns):
            # Check if any exclude patterns are present
            if not any(exc in error_message_lower for exc in exclude):
                return pattern_config["recommendation"]
    
    # Default recommendation
    return "Use list_tables and explore_table to understand the database structure"


@app.tool()
def list_tables(include_views: bool = True) -> str:
    """
    Get list of tables and optionally views in the database.
    """
    start_time = time.time()
    
    try:
        repo = get_repository()
        tables = repo.get_tables()
        views = repo.get_views() if include_views else []
        
        response = {
            "tables": tables,
            "views": views,
            "total_tables": len(tables),
            "total_views": len(views),
            "database_type": repo.get_database_type()
        }
        
        execution_time = time.time() - start_time
        logger.info(f"Found {len(tables)} tables and {len(views)} views in {execution_time:.3f}s")
        return json.dumps(response, indent=2)
        
    except Exception as e:
        logger.exception(f"Error retrieving table list after {time.time() - start_time:.3f}s")
        return json.dumps(format_simple_error(e), indent=2)


@app.tool()
def explore_table(table_name: str, sample_size: int = 3) -> str:
    """
    Get table structure and sample data.
    """
    if not table_name or not table_name.strip():
        return json.dumps({"error": "Table name is required"}, indent=2)
    
    start_time = time.time()
    
    try:
        # Initialize repository and config
        repo = get_repository()
        sample_size = min(query_config.max_sample_size, max(0, sample_size))
        columns = repo.get_table_columns(table_name)
        primary_key = repo.get_primary_keys(table_name)
        foreign_keys = repo.get_foreign_keys(table_name)
        row_count = repo.get_row_count(table_name)
        sample_data = repo.get_sample_data(table_name, sample_size)
        
        response = {
            "table_name": table_name,
            "row_count": row_count,
            "columns": columns,
            "primary_key": primary_key,
            "foreign_keys": foreign_keys,
            "sample_data": sample_data
        }
        
        execution_time = time.time() - start_time
        logger.info(f"Table '{table_name}' analyzed successfully in {execution_time:.3f}s")
        return json.dumps(response, indent=2)
        
    except TableAccessDeniedError:
        return json.dumps({"error": f"Access to table '{table_name}' is denied by filter configuration"}, indent=2)
    except TableNotFoundError:
        return json.dumps({"error": f"Table '{table_name}' not found"}, indent=2)
    except Exception as e:
        execution_time = time.time() - start_time
        logger.exception(f"Error analyzing table after {execution_time:.3f}s")
        return json.dumps(format_simple_error(e), indent=2)


@app.tool()
def query_database_readonly(
    query: str,
    timeout_seconds: Optional[int] = None,
    max_rows: Optional[int] = None
) -> str:
    """
    Execute read-only SELECT query with safety features.
    
    Only supports SELECT queries and WITH clauses. Other operations
    (INSERT, UPDATE, DELETE, etc.) are blocked for safety.
    """
    # Initialize repository to ensure config is loaded
    get_repository()
    
    # Use defaults from config if not provided
    if timeout_seconds is None:
        timeout_seconds = query_config.default_timeout
    if max_rows is None:
        max_rows = query_config.default_max_rows
    
    if not query or not query.strip():
        return json.dumps({
            "error": "Query parameter is required and cannot be empty",
            "error_type": "ValidationError",
            "recommendation": "Provide a valid SQL SELECT query"
        }, indent=2)
    
    # Validate query
    try:
        QueryValidator.validate(query)
    except QueryValidationError as e:
        return json.dumps(format_query_error(e), indent=2)
    
    start_time = time.time()
    
    try:
        # Execute with timeout using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                get_repository().execute_query,
                query,
                timeout_seconds
            )
            
            try:
                results, columns = future.result(timeout=timeout_seconds)
                execution_time = time.time() - start_time
            except FutureTimeoutError:
                raise QueryTimeoutError(timeout_seconds)
        
        # Apply row limit
        if max_rows > 0 and len(results) > max_rows:
            results = results[:max_rows]
        
        response = {
            "result": results,
            "row_count": len(results),
            "columns": columns,
            "execution_time": round(execution_time, 3)
        }
        
        logger.info(f"Query executed in {execution_time:.3f}s, returned {len(results)} rows")
        return json.dumps(response, indent=2)
        
    except Exception as e:
        logger.exception("Query execution error")
        return json.dumps(format_query_error(e), indent=2)


def main():
    """Main entry point."""
    try:
        app.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.exception("Unexpected error")
        sys.exit(1)
    finally:
        if repository is not None:
            repository.close()


if __name__ == "__main__":
    main()