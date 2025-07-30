# tools.py

import os
import logging
import json
from typing import List
from dotenv import load_dotenv
from .mcp_instance import mcp
from .tool_schema import tool_definitions
import mcp.types as types
import gspread
from google.oauth2.service_account import Credentials
from google.auth.exceptions import GoogleAuthError
from gspread.exceptions import SpreadsheetNotFound, APIError

# Simple logging setup
logger = logging.getLogger("google_sheet_mcp")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(name)s] %(message)s"))
    logger.addHandler(handler)

# Load environment variables
load_dotenv()

# Google Sheets API setup
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_google_sheets_client():
    """
    Initialize and return a Google Sheets client using service account credentials.
    
    Supports two methods:
    1. GOOGLE_SERVICE_ACCOUNT_INFO as file path (local development)
    2. GOOGLE_SERVICE_ACCOUNT_INFO as JSON string (server deployment)
    
    Returns:
        gspread.Client: Authenticated Google Sheets client
        
    Raises:
        GoogleAuthError: If authentication fails
    """
    try:
        # Get service account credentials from environment variable
        service_account_info = os.getenv("GOOGLE_SERVICE_ACCOUNT_INFO")
        
        if not service_account_info:
            raise GoogleAuthError("GOOGLE_SERVICE_ACCOUNT_INFO environment variable not set")
        
        # Determine if it's a file path or JSON content
        service_account_dict = None
        
        # Try to parse as JSON first (server deployment)
        try:
            service_account_dict = json.loads(service_account_info)
            logger.info("Using service account JSON from environment variable")
        except json.JSONDecodeError:
            # If JSON parsing fails, treat as file path (local development)
            if not os.path.exists(service_account_info):
                raise GoogleAuthError(f"Service account file not found: {service_account_info}")
            
            try:
                with open(service_account_info, 'r') as file:
                    service_account_dict = json.load(file)
                logger.info(f"Using service account file: {service_account_info}")
            except json.JSONDecodeError as e:
                raise GoogleAuthError(f"Invalid JSON in service account file: {e}")
            except IOError as e:
                raise GoogleAuthError(f"Failed to read service account file: {e}")
        
        if not service_account_dict:
            raise GoogleAuthError("Failed to load service account credentials")
        
        # Validate required fields
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in service_account_dict]
        if missing_fields:
            raise GoogleAuthError(f"Missing required fields in service account: {missing_fields}")
        
        # Create credentials
        credentials = Credentials.from_service_account_info(
            service_account_dict, 
            scopes=SCOPES
        )
        
        # Create and return the client
        client = gspread.authorize(credentials)
        return client
        
    except GoogleAuthError:
        # Re-raise GoogleAuthError as-is
        raise
    except Exception as e:
        logger.error(f"Failed to initialize Google Sheets client: {e}")
        raise GoogleAuthError(f"Authentication failed: {e}")

def register_tools():
    """Register Google Sheets tools with the MCP server."""
    
    @mcp.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        return tool_definitions

    @mcp.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        if name == "read_google_sheet":
            return await read_google_sheet(**arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

async def read_google_sheet(spreadsheet_id: str, sheet_name: str) -> list[types.TextContent]:
    """
    Read data from a Google Sheet using the Google Sheets API.
    
    Args:
        spreadsheet_id (str): The ID of the Google Sheet (found in the URL)
        sheet_name (str): The name of the sheet to read (e.g., 'Sheet1', 'Data') or a range (e.g., 'Sheet1!A1:D10')
        
    Returns:
        list[types.TextContent]: List containing the sheet data as structured content
    """
    try:
        logger.info(f"Reading Google Sheet: {spreadsheet_id}, Sheet/Range: {sheet_name}")
        
        # Get authenticated client
        client = get_google_sheets_client()
        
        # Open the spreadsheet
        try:
            spreadsheet = client.open_by_key(spreadsheet_id)
            logger.info(f"Successfully opened spreadsheet: {spreadsheet.title}")
        except SpreadsheetNotFound:
            return [types.TextContent(
                type="text",
                text=f"Error: Spreadsheet with ID '{spreadsheet_id}' not found. Please check the spreadsheet ID and ensure the service account has access."
            )]
        except APIError as e:
            return [types.TextContent(
                type="text",
                text=f"Error accessing spreadsheet: {str(e)}"
            )]
        
        # Parse sheet_name to determine if it's a specific range or just a sheet name
        if '!' in sheet_name:
            # Specific range like 'Sheet1!A1:D10'
            actual_sheet_name, cell_range = sheet_name.split('!', 1)
            try:
                worksheet = spreadsheet.worksheet(actual_sheet_name)
                values = worksheet.get(cell_range)
                range_used = sheet_name
            except gspread.WorksheetNotFound:
                return [types.TextContent(
                    type="text",
                    text=f"Error: Worksheet '{actual_sheet_name}' not found in spreadsheet '{spreadsheet.title}'"
                )]
        else:
            # Sheet name only, read entire sheet
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
                values = worksheet.get_all_values()
                range_used = f"{sheet_name} (entire sheet)"
            except gspread.WorksheetNotFound:
                return [types.TextContent(
                    type="text",
                    text=f"Error: Worksheet '{sheet_name}' not found in spreadsheet '{spreadsheet.title}'. Available sheets: {[ws.title for ws in spreadsheet.worksheets()]}"
                )]
        
        if not values:
            return [types.TextContent(
                type="text",
                text=f"No data found in sheet '{sheet_name}' of spreadsheet '{spreadsheet.title}'"
            )]
        
        # Convert to markdown table format
        markdown_table = _convert_to_markdown_table(values)
        
        # Create response with metadata
        response_data = {
            "spreadsheet_title": spreadsheet.title,
            "worksheet_name": worksheet.title,
            "range_read": range_used,
            "rows": len(values),
            "columns": len(values[0]) if values else 0,
            "data": markdown_table
        }
        
        # Return formatted response
        content = types.TextContent(
            type="text",
            text=json.dumps(response_data, indent=2),
            title=f"Google Sheet Data: {spreadsheet.title} - {worksheet.title}",
            format="json"
        )
        
        return [content]
        
    except GoogleAuthError as e:
        logger.error(f"Google authentication error: {e}")
        return [types.TextContent(
            type="text",
            text=f"Authentication error: {str(e)}"
        )]
    except Exception as e:
        logger.error(f"Error reading Google Sheet: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error reading Google Sheet: {str(e)}"
        )]

def _convert_to_markdown_table(values: List[List[str]]) -> str:
    """
    Convert a 2D list of values to a markdown table format.
    
    Args:
        values (List[List[str]]): 2D list of cell values
        
    Returns:
        str: Markdown formatted table
    """
    if not values:
        return "No data available"
    
    # Find the maximum width for each column
    max_widths = []
    for col in range(len(values[0])):
        max_width = max(len(str(row[col] if col < len(row) else "")) for row in values)
        max_widths.append(max_width)
    
    # Build the markdown table
    markdown_lines = []
    
    # Header row
    header_cells = []
    for i, cell in enumerate(values[0]):
        header_cells.append(f"| {str(cell):<{max_widths[i]}} ")
    markdown_lines.append("".join(header_cells) + "|")
    
    # Separator row
    separator_cells = []
    for width in max_widths:
        separator_cells.append(f"| {'-' * width} ")
    markdown_lines.append("".join(separator_cells) + "|")
    
    # Data rows
    for row in values[1:]:
        data_cells = []
        for i in range(len(max_widths)):
            cell = str(row[i]) if i < len(row) else ""
            data_cells.append(f"| {cell:<{max_widths[i]}} ")
        markdown_lines.append("".join(data_cells) + "|")
    
    return "\n".join(markdown_lines)
