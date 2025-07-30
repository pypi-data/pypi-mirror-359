from .server import main as server_main
import asyncio


def main():
    """Entry point for the Google Sheets MCP server."""
    asyncio.run(server_main())


if __name__ == "__main__":
    main() 