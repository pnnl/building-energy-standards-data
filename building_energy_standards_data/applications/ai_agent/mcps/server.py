import argparse
import logging

from fastmcp import FastMCP

from building_energy_standards_data.applications.ai_agent.core.services import (
    SchemaMetadataService,
)
from building_energy_standards_data.applications.ai_agent.mcps.database import (
    DB_PATH_ENV,
    ensure_database,
)
from building_energy_standards_data.applications.ai_agent.mcps.tools import (
    register_tools,
)

SERVER_NAME = "building_energy_standards_database"


def create_mcp_server(
    schema_service: "SchemaMetadataService",
    name="building-energy-standards",
) -> FastMCP:

    mcp = FastMCP(
        name=name,
    )
    register_tools(mcp, schema_service)

    return mcp


def serve(host, port, transport, db_path=None, rebuild=False):
    """Build the database if needed and run the MCP server.

    ``host`` and ``port`` only apply to network transports; with ``stdio`` they are
    ignored. Nothing but MCP protocol messages may be written to stdout in that case.
    """
    db_file = ensure_database(db_path, rebuild=rebuild)
    schema_service = SchemaMetadataService(db_path=str(db_file))
    server = create_mcp_server(schema_service, name=SERVER_NAME)

    if transport == "stdio":
        server.run(transport="stdio", show_banner=False)
    else:
        server.run(transport=transport, host=host, port=port)


def main(argv=None):
    """Console entry point (``besd-mcp``). Defaults to the stdio transport."""
    parser = argparse.ArgumentParser(
        prog="besd-mcp",
        description="MCP server for the Building Energy Standards Data database.",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "http", "streamable-http"],
        default="stdio",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Network transports only")
    parser.add_argument(
        "--port", type=int, default=11000, help="Network transports only"
    )
    parser.add_argument(
        "--db-path",
        help=f"SQLite file to use (default: ${DB_PATH_ENV} or the user cache dir). "
        "Built from the packaged JSON if it does not exist.",
    )
    parser.add_argument(
        "--rebuild", action="store_true", help="Rebuild the database before serving"
    )
    args = parser.parse_args(argv)

    # stdout carries the protocol in stdio mode; keep all logging on stderr.
    logging.basicConfig(level=logging.INFO)
    serve(args.host, args.port, args.transport, args.db_path, args.rebuild)


if __name__ == "__main__":
    main()
