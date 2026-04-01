"""Test script to verify E2sc setup and functionality."""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from e2sc.utils import get_config, get_logger
from e2sc.data import STRINGDatabase, HMDBDatabase, TRRUSTDatabase, GUTMGENEDatabase
from e2sc.data.vector_store import get_vector_store

logger = get_logger(__name__)


def test_config():
    """Test configuration management."""
    print("\n" + "="*60)
    print("🔧 Testing Configuration")
    print("="*60)
    
    try:
        config = get_config()
        print(f"✓ Config loaded successfully")
        print(f"  - LLM Provider: {config.llm.provider}")
        print(f"  - Model: {config.llm.model}")
        print(f"  - Database Path: {config.database.db_path}")
        return True
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        return False


def test_databases():
    """Test local database connections."""
    print("\n" + "="*60)
    print("💾 Testing Local Databases")
    print("="*60)
    
    results = {}
    
    # Test STRING database
    try:
        string_db = STRINGDatabase()
        string_db.connect()
        print(f"✓ STRING database connected")
        
        # Try a simple query
        interactions = string_db.get_interactions("TP53", min_score=0.7)
        print(f"  - Found {len(interactions)} interactions for TP53")
        string_db.close()
        results['string'] = True
    except Exception as e:
        print(f"✗ STRING database failed: {e}")
        results['string'] = False
    
    # Test HMDB database
    try:
        hmdb_db = HMDBDatabase()
        hmdb_db.connect()
        print(f"✓ HMDB database connected")
        
        metabolites = hmdb_db.get_metabolites("NT5E")
        print(f"  - Found {len(metabolites)} metabolites for NT5E")
        hmdb_db.close()
        results['hmdb'] = True
    except Exception as e:
        print(f"✗ HMDB database failed: {e}")
        results['hmdb'] = False
    
    # Test TRRUST database
    try:
        trrust_db = TRRUSTDatabase()
        trrust_db.connect()
        print(f"✓ TRRUST database connected")
        
        targets = trrust_db.get_targets("TP53")
        print(f"  - Found {len(targets)} targets for TP53")
        trrust_db.close()
        results['trrust'] = True
    except Exception as e:
        print(f"✗ TRRUST database failed: {e}")
        results['trrust'] = False
    
    # Test GUTMGENE database
    try:
        gutmgene_db = GUTMGENEDatabase()
        gutmgene_db.connect()
        print(f"✓ GUTMGENE database connected")
        
        microbes = gutmgene_db.get_microbes("IL6")
        print(f"  - Found {len(microbes)} microbe associations for IL6")
        gutmgene_db.close()
        results['gutmgene'] = True
    except Exception as e:
        print(f"✗ GUTMGENE database failed: {e}")
        results['gutmgene'] = False
    
    return all(results.values())


def test_vector_store():
    """Test vector store functionality."""
    print("\n" + "="*60)
    print("🔍 Testing Vector Store (RAG)")
    print("="*60)
    
    try:
        vs = get_vector_store()
        print(f"✓ Vector store initialized")
        
        # Get stats
        stats = vs.get_collection_stats()
        print(f"  - Collection: {stats.get('name')}")
        print(f"  - Documents: {stats.get('count', 0)}")
        
        # Test adding a case
        vs.add_case(
            case_id="test_case_001",
            question="Test differential expression analysis",
            analysis_type="deg",
            results={"deg": {"results": []}},
            metadata={"test": True}
        )
        print(f"✓ Added test case")
        
        # Test searching
        similar = vs.search_similar_cases("differential expression", n_results=1)
        print(f"✓ Search returned {len(similar)} results")
        
        return True
    except Exception as e:
        print(f"✗ Vector store test failed: {e}")
        return False


def test_api_clients():
    """Test API client creation."""
    print("\n" + "="*60)
    print("🌐 Testing API Clients")
    print("="*60)
    
    try:
        from e2sc.data.api_client import create_api_clients
        
        clients = create_api_clients()
        print(f"✓ Created {len(clients)} API clients:")
        for name in clients.keys():
            print(f"  - {name}")
        
        return True
    except Exception as e:
        print(f"✗ API client test failed: {e}")
        return False


def test_agent_import():
    """Test agent module imports."""
    print("\n" + "="*60)
    print("🤖 Testing Agent Modules")
    print("="*60)
    
    try:
        from e2sc import E2scAgent
        print(f"✓ E2scAgent imported successfully")
        
        from e2sc.agent import PlannerAgent, RetrieverAgent, SynthesizerAgent
        print(f"✓ All agent modules imported")
        
        return True
    except Exception as e:
        print(f"✗ Agent import test failed: {e}")
        return False


def test_tools():
    """Test analysis tools."""
    print("\n" + "="*60)
    print("🛠️  Testing Analysis Tools")
    print("="*60)
    
    try:
        from e2sc.tools import ScancpyTools, EnrichmentAnalyzer, NetworkAnalyzer, Visualizer
        print(f"✓ ScancpyTools imported")
        print(f"✓ EnrichmentAnalyzer imported")
        print(f"✓ NetworkAnalyzer imported")
        print(f"✓ Visualizer imported")
        
        return True
    except Exception as e:
        print(f"✗ Tools test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 E2sc System Test Suite")
    print("="*60)
    
    results = {
        "Configuration": test_config(),
        "Local Databases": test_databases(),
        "Vector Store": test_vector_store(),
        "API Clients": test_api_clients(),
        "Agent Modules": test_agent_import(),
        "Analysis Tools": test_tools(),
    }
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! E2sc is ready to use.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\n💡 Common issues:")
        print("   - Databases not initialized: Run 'python scripts/init_databases_simple.py'")
        print("   - Missing dependencies: Run 'pip install -e .'")
        print("   - Configuration needed: Run 'e2sc config'")
        return 1


if __name__ == "__main__":
    sys.exit(main())
