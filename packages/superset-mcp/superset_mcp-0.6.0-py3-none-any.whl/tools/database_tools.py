"""
Database Tools for Superset MCP

This module contains all database-related tools for the Superset MCP server.
"""

from main import mcp
from typing import Dict, Any, List, Optional
from mcp.server.fastmcp import Context
from utils import requires_auth, handle_api_errors, make_api_request, parse_response_or_return_raw
from pydantic import BaseModel, Field


class SqlValidationRequest(BaseModel):
    """Request model for SQL validation."""
    database_id: int = Field(description="ID of the database to validate against")
    sql: str = Field(description="SQL statement to validate")
    catalog: Optional[str] = Field(None, description="Optional database catalog name")
    db_schema: Optional[str] = Field(None, alias="schema", description="Optional database schema name")
    template_params: Optional[Dict[str, Any]] = Field(None, description="Optional template parameters for the SQL")


class SqlValidationError(BaseModel):
    """Model for individual SQL validation error."""
    line_number: int = Field(description="Line number where the error occurred")
    start_column: int = Field(description="Starting column position of the error")
    end_column: int = Field(description="Ending column position of the error")
    message: str = Field(description="Error message describing the validation issue")


class SqlValidationResult(BaseModel):
    """Response model for SQL validation."""
    result: Optional[List[SqlValidationError]] = Field(None, description="List of SQL validation errors found")
    error: Optional[str] = Field(None, description="Error message if validation failed")


class DatabaseResult(BaseModel):
    """Represents a single database record."""
    id: int
    database_name: str
    extra: Optional[str] = None
    # Add other relevant fields as needed


class DatabaseListResult(BaseModel):
    """Represents the result of a database list operation."""
    count: Optional[int] = None
    result: List[DatabaseResult]


@mcp.tool()
@requires_auth
@handle_api_errors
async def superset_database_list(ctx: Context) -> Dict[str, Any]:
    """
    Get a list of databases from Superset
    """
    response_data = await make_api_request(ctx, "get", "/api/v1/database/")
    return parse_response_or_return_raw(DatabaseListResult, response_data)


@mcp.tool()
@requires_auth
@handle_api_errors
async def superset_database_get_by_id(ctx: Context, database_id: int) -> Dict[str, Any]:
    """
    Get details for a specific database
    """
    response_data = await make_api_request(ctx, "get", f"/api/v1/database/{database_id}")
    database_data = response_data.get("result", response_data)
    return parse_response_or_return_raw(DatabaseResult, database_data)


@mcp.tool()
@requires_auth
@handle_api_errors
async def superset_database_validate_sql(
    ctx: Context, payload: SqlValidationRequest
) -> Dict[str, Any]:
    """
    Validate arbitrary SQL against a database
    """
    # Extract database_id from payload
    database_id = payload.database_id
    
    # Convert to API payload, excluding database_id since it goes in the URL
    api_payload = payload.model_dump(by_alias=True, exclude_none=True, exclude={"database_id"})
    
    response_data = await make_api_request(
        ctx, "post", f"/api/v1/database/{database_id}/validate_sql/", data=api_payload
    )
    
    return parse_response_or_return_raw(SqlValidationResult, response_data)
