# Google Sheets MCP Server

A clean and focused Model Context Protocol (MCP) server that provides tools to read data from Google Sheets using the Google Sheets API.

## Features

- **Read Google Sheets**: Extract data from Google Sheets using spreadsheet ID and sheet name/range
- **Markdown Table Conversion**: Automatically convert sheet data to markdown table format
- **Flexible Range Support**: Read specific ranges (e.g., 'Sheet1!A1:D10') or entire sheets
- **Error Handling**: Comprehensive error handling for authentication and access issues
- **Clean Architecture**: Minimal dependencies, focused only on Google Sheets functionality

## Setup

### Prerequisites

1. Python 3.10 or higher
2. A Google Cloud Project with Google Sheets API enabled
3. A service account with access to Google Sheets

### Installation

#### From PyPI (Recommended)

```bash
pip install google-sheet-mcp
```

#### From Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mcp-google-sheet.git
cd mcp-google-sheet
```

2. Install dependencies using uv (recommended):
```bash
uv sync
```

   Or using pip:
```bash
pip install -e .
```

2. Set up Google Service Account:
   - Create a service account in Google Cloud Console
   - Download the JSON key file
   - Enable Google Sheets API for the project
   - Share the Google Sheets you want to access with the service account email

3. Configure environment variables:
```bash
# Set the path to your service account JSON file
export GOOGLE_SERVICE_ACCOUNT_INFO="/path/to/your/service-account-key.json"
```

   Or create a `.env` file in the project root:
```env
GOOGLE_SERVICE_ACCOUNT_INFO=/path/to/your/service-account-key.json
```

## Usage

### Tool: read_google_sheet

Reads data from a Google Sheet and returns it in a structured format.

**Parameters:**
- `spreadsheet_id` (string): The ID of the Google Sheet (found in the URL)
- `sheet_name` (string): The sheet name (e.g., 'Sheet1') or range (e.g., 'Sheet1!A1:D10')

**Example:**
```json
{
  "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
  "sheet_name": "Sheet1!A1:D10"
}
```

**Response:**
Returns a JSON object containing:
- `spreadsheet_title`: Title of the spreadsheet
- `worksheet_name`: Name of the worksheet
- `range_read`: The range that was read
- `rows`: Number of rows in the data
- `columns`: Number of columns in the data
- `data`: Markdown formatted table of the data

## Running the Server

With uv (recommended):
```bash
uv run python -m google_sheet_mcp
```

Or with standard Python:
```bash
python -m google_sheet_mcp
```

Make sure your `GOOGLE_SERVICE_ACCOUNT_INFO` environment variable is set or you have a `.env` file configured before running the server.

## Configuration

The server uses the following environment variables:

- `GOOGLE_SERVICE_ACCOUNT_INFO`: File path to the Google service account JSON credentials file

### Security Best Practices

1. **Keep credentials secure**: Store your service account JSON file in a secure location with appropriate file permissions (e.g., `chmod 600`)
2. **Use .gitignore**: Add your service account file to `.gitignore` to prevent accidental commits
3. **Environment-specific files**: Use different service account files for development, staging, and production environments

## Project Structure

```
mcp-google-sheet/
├── google_sheet_mcp/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # Module entry point
│   ├── server.py            # MCP server configuration
│   ├── mcp_instance.py      # MCP instance setup
│   ├── tools.py             # Google Sheets tools implementation
│   └── tool_schema.py       # Tool definitions and schemas
├── pyproject.toml           # Project configuration
├── uv.lock                  # UV lock file for dependencies
├── .gitignore               # Git ignore patterns
└── README.md               # Documentation
```

## Error Handling

The server handles various error scenarios:
- Authentication failures
- Spreadsheet not found
- Worksheet not found
- Invalid ranges
- API rate limiting

All errors are returned as structured error messages with appropriate context. 