"""
SQL Lab Tools for Superset MCP

This module contains all SQL Lab-related tools for the Superset MCP server.
"""

from main import mcp
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import Context
from utils import requires_auth, handle_api_errors, make_api_request, get_csrf_token, parse_response_or_return_raw


class SqlExecutePayload(BaseModel):
    """
    Defines the payload for executing a SQL query in SQL Lab.
    """
    database_id: int = Field(description="ID of the database to query.")
    sql: str = Field(description="The SQL query to execute.")
    db_schema: Optional[str] = Field(None, alias="schema", description="The schema to run the query against. If not provided, the database's default schema is used.")
    catalog: Optional[str] = Field(None, description="The catalog to run the query against.")
    query_limit: Optional[int] = Field(100, alias="queryLimit", description="The maximum number of rows to return.")


class SupersetError(BaseModel):
    """
    Represents a single error from Superset API.
    """
    error_type: Optional[str] = Field(None, description="The type of error (e.g., 'GENERIC_DB_ENGINE_ERROR').")
    message: str = Field(description="The error message.")
    level: Optional[str] = Field(None, description="The error level (e.g., 'error', 'warning', 'info').")
    extra: Optional[Dict[str, Any]] = Field(None, description="Additional error information.")


class SupersetErrorResponse(BaseModel):
    """
    Represents an error response from Superset API.
    """
    errors: Optional[List[SupersetError]] = Field(None, description="List of errors.")
    message: Optional[str] = Field(None, description="General error message.")
    stacktrace: Optional[str] = Field(None, description="Stack trace if available.")


class SqlLabExecutionResult(BaseModel):
    """
    Represents the result of a SQL Lab query execution.
    """
    status: str = Field(description="The status of the query (e.g., 'success', 'running', 'failed').")
    query_id: int = Field(description="The ID of the executed query.")
    columns: Optional[List[Dict[str, Any]]] = Field(None, description="List of column metadata dictionaries.")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="A list of dictionaries, each representing a row of data.")
    expanded_columns: Optional[List[Dict[str, Any]]] = Field(None, description="List of expanded column metadata for struct/map types.")
    query: Optional[Dict[str, Any]] = Field(None, description="Detailed information about the query that was run.")
    selected_columns: Optional[List[Dict[str, Any]]] = Field(None, description="List of selected column metadata.")


@mcp.tool()
@requires_auth
@handle_api_errors
async def superset_sqllab_execute_query(
    ctx: Context, payload: SqlExecutePayload
) -> Dict[str, Any]:
    """
    Execute a SQL query in SQL Lab
    """
    # Ensure we have a CSRF token before executing the query
    from main import SupersetContext
    superset_ctx: SupersetContext = ctx.request_context.lifespan_context
    if not superset_ctx.csrf_token:
        await get_csrf_token(ctx)

    api_payload = payload.model_dump(by_alias=True, exclude_none=True)
    api_payload["tab"] = "MCP Query"
    api_payload["runAsync"] = False
    api_payload["select_as_cta"] = False

    response_data = await make_api_request(ctx, "post", "/api/v1/sqllab/execute/", data=api_payload)

    # Check if make_api_request returned an error
    if isinstance(response_data, dict) and "error" in response_data and len(response_data) == 1:
        error_msg = response_data["error"]
        # Try to extract JSON from the error message if it contains API response
        if "API request failed:" in error_msg and " - " in error_msg:
            try:
                # Extract the JSON part from error message like "API request failed: 500 - {...}"
                json_part = error_msg.split(" - ", 1)[1]
                import json
                actual_response = json.loads(json_part)
                # Now process this as if it was the original response
                response_data = actual_response
            except (json.JSONDecodeError, IndexError):
                # If we can't parse it, just raise the original error
                raise ValueError(error_msg)

    # Check for various error response formats
    if isinstance(response_data, dict):
        # Check for stacktrace (common in SQL execution errors)
        if response_data.get("stacktrace"):
            try:
                error_response = SupersetErrorResponse(**response_data)
                if error_response.errors and len(error_response.errors) > 0:
                    error_msg = error_response.errors[0].message
                else:
                    error_msg = error_response.message or "An unknown error occurred"
                # Convert escaped newlines to actual newlines
                error_msg = error_msg.replace('\\n', '\n')
                # Also handle other common escape sequences
                error_msg = error_msg.replace('\\t', '\t').replace('\\r', '\r')
                raise ValueError(f"SQL execution error: {error_msg}")
            except Exception:
                raise ValueError(f"SQL execution error with stacktrace: {response_data.get('message', 'Unknown error')}")
        
        # Check for errors array (standard Superset error format)
        if response_data.get("errors"):
            try:
                error_response = SupersetErrorResponse(**response_data)
                if error_response.errors and len(error_response.errors) > 0:
                    error_details = []
                    for error in error_response.errors:
                        error_detail = f"{error.message}"
                        if error.error_type:
                            error_detail += f" (Type: {error.error_type})"
                        error_details.append(error_detail)
                    raise ValueError(f"API errors: {'; '.join(error_details)}")
                else:
                    raise ValueError(f"API error: {response_data}")
            except ValueError:
                raise
            except Exception:
                raise ValueError(f"API error response: {response_data}")
        
        # Check for general error field
        if "error" in response_data:
            raise ValueError(f"API error: {response_data.get('error')}")
        
        # Check if query result contains error message
        if response_data.get("query", {}).get("errorMessage"):
            error_msg = response_data["query"]["errorMessage"]
            raise ValueError(f"Query execution error: {error_msg}")

    # Try to parse as successful response, otherwise return raw data
    return parse_response_or_return_raw(SqlLabExecutionResult, response_data)
