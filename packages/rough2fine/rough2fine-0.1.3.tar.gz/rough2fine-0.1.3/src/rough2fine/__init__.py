
from . import server
from . import core

__version__ = "0.1.0"


def main():
    """Main entry point for the package."""
    server.main()


__all__ = ["main", "server", "core", "__version__"]