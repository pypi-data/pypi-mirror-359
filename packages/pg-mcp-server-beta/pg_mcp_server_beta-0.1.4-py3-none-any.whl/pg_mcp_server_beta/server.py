from fastmcp import FastMCP
from .tools import list_docs, get_docs, search_docs
from .core.document_repository import initialize_repository
from .core import documents

def main():
    instructions = documents.get("instructions.md", "")
    readme = documents.get("README.md", "")

    initialize_repository(documents)

    mcp = FastMCP(
        "hecto-financial-mcp",
        instructions=instructions + "\n" + readme,
    )

    mcp.tool(list_docs)
    mcp.tool(get_docs)
    mcp.tool(search_docs)

    mcp.run("stdio")

