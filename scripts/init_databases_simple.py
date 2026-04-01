"""Initialize databases from CSV files in the database folder."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from e2sc.data import initialize_databases
from e2sc.utils import get_logger

logger = get_logger(__name__)


def main():
    """Initialize all databases from CSV files."""
    # Get the database directory
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "database"
    
    if not data_dir.exists():
        print(f"❌ Error: Database directory not found: {data_dir}")
        sys.exit(1)
    
    print(f"📁 Database directory: {data_dir}")
    print(f"🔍 Looking for CSV files...")
    
    # Check for CSV files
    csv_files = list(data_dir.glob("*.csv"))
    if not csv_files:
        print(f"❌ No CSV files found in {data_dir}")
        sys.exit(1)
    
    print(f"✓ Found {len(csv_files)} CSV files:")
    for csv_file in csv_files:
        print(f"  - {csv_file.name}")
    
    print(f"\n🚀 Initializing databases...")
    
    try:
        initialize_databases(data_dir)
        print("\n✅ All databases initialized successfully!")
        print(f"\n📊 Database files created in: ~/.e2sc/databases/")
        print("   - string.db")
        print("   - hmdb.db")
        print("   - trrust.db")
        print("   - gutmgene.db")
        
    except Exception as e:
        print(f"\n❌ Error initializing databases: {e}")
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
