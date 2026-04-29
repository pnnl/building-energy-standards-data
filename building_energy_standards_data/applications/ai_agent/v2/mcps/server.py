from fastmcp import FastMCP

from building_energy_standards_data.applications.ai_agent.v2.core.services import SchemaMetadataService
from building_energy_standards_data.applications.ai_agent.v2.mcps.tools import register_tools



def create_mcp_server(
    schema_service: "SchemaMetadataService",
    name="building-energy-standards",
) -> FastMCP:

    mcp = FastMCP(
        name=name,
    )
    register_tools(mcp, schema_service)
    
    return mcp

def serve(host, port, transport):

    schema_service = SchemaMetadataService()

    server = create_mcp_server(schema_service, name="building_energy_standards_database")

    server.run(transport=transport, host=host, port=port)

if __name__ == "__main__":
    serve("127.0.0.1", 11000, "sse")