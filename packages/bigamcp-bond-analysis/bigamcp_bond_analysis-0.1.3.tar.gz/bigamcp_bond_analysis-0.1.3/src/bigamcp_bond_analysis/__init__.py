"""
BigAMCP Bond Analysis - A Model Context Protocol server for convertible bond analysis.
"""

__version__ = "0.1.0"

def main():
    """Lazy import and run the main function to avoid import errors during testing."""
    from .server import main as server_main
    return server_main()

__all__ = ["main"]
