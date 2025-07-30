import mcp.types as types

google_sheets_tools = [
    types.Tool(
        name="read_google_sheet",
        description="""Read data from a Google Sheet using the Google Sheets API.
        
        This tool:
        - Authenticates with Google Sheets API using service account credentials
        - Reads data from a specified Google Sheet by spreadsheet ID and sheet name/range
        - Returns the sheet data in a structured format
        - Supports reading entire sheets by sheet name (e.g., 'Sheet1') or specific ranges (e.g., 'Sheet1!A1:D10')
        - Handles authentication errors and missing sheets gracefully
        
        Use this for extracting data from Google Sheets for analysis, reporting, or data processing tasks.
        The spreadsheet ID can be found in the URL of the Google Sheet.""",
        inputSchema={
            "type": "object",
            "properties": {
                "spreadsheet_id": {
                    "type": "string", 
                    "description": "The ID of the Google Sheet (found in the URL)"
                },
                "sheet_name": {
                    "type": "string", 
                    "description": "The name of the sheet to read (e.g., 'Sheet1', 'Data', 'Main'). This will read the entire sheet. Alternatively, you can specify a range like 'Sheet1!A1:D10' for specific cells."
                }
            },
            "required": ["spreadsheet_id", "sheet_name"]
        },
    )
]

tool_definitions = google_sheets_tools