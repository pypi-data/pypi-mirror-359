import argparse
import asyncio
import os

from . import server


def main():
    """Main entry point for the package."""
    parser = argparse.ArgumentParser(description="Neo4j Cypher MCP Server")
    parser.add_argument("--db-url", default=None, help="Neo4j connection URL")
    parser.add_argument("--username", default=None, help="Neo4j username")
    parser.add_argument("--password", default=None, help="Neo4j password")
    parser.add_argument("--database", default=None, help="Neo4j database name")
    parser.add_argument("--transport", default=None, help="Transport type")
    parser.add_argument("--namespace", default=None, help="Tool namespace")
    parser.add_argument("--server-host", default=None, help="Server host")
    parser.add_argument("--server-port", default=None, help="Server port")

    args = parser.parse_args()
    asyncio.run(
        server.main(
            args.db_url or os.getenv("NEO4J_URL") or os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            args.username or os.getenv("NEO4J_USERNAME", "neo4j"),
            args.password or os.getenv("NEO4J_PASSWORD", "password"),
            args.database or os.getenv("NEO4J_DATABASE", "neo4j"),
            args.transport or os.getenv("NEO4J_TRANSPORT", "stdio"),
            args.namespace or os.getenv("NEO4J_NAMESPACE", ""),
            args.server_host or os.getenv("NEO4J_MCP_SERVER_HOST", "127.0.0.1"),
            args.server_port or os.getenv("NEO4J_MCP_SERVER_PORT", 8000),
        )
    )


__all__ = ["main", "server"]
