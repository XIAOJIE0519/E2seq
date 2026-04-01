"""Script to initialize databases from CSV files."""

import sys
from pathlib import Path

from e2sc.data import initialize_databases
from e2sc.utils import get_logger

logger = get_logger(__name__)


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python init_databases.py <data_directory>")
        print("Example: python init_databases.py ./database")
        sys.exit(1)
    
    data_dir = Path(sys.argv[1])
    
    if not data_dir.exists():
        print(f"Error: Directory {data_dir} does not exist")
        sys.exit(1)
    
    print(f"Initializing databases from {data_dir}")
    
    try:
        initialize_databases(data_dir)
        print("✓ Databases initialized successfully")
    except Exception as e:
        print(f"✗ Error: {e}")
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
