"""
Main entry point for running the Slidesmith MCP server.
"""

from .server import create_server, run_server

if __name__ == "__main__":
    server = create_server()
    run_server(server)