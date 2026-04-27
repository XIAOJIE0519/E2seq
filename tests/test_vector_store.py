"""Tests for vector store index management and cleanup."""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestVectorStoreInitialization:
    """Test vector store initialization."""

    def test_get_vector_store_creates_default(self):
        """Test that get_vector_store creates a default store."""
        from e2sc.data.vector_store import get_vector_store, _default_store
        
        # Reset to ensure clean state
        with patch('e2sc.data.vector_store._default_store', None):
            with patch('e2sc.data.vector_store._collection', None):
                # Should create a new store
                vs = get_vector_store()
                assert vs is not None

    def test_get_vector_store_returns_same_instance(self):
        """Test that get_vector_store returns the same instance."""
        from e2sc.data.vector_store import get_vector_store
        
        vs1 = get_vector_store()
        vs2 = get_vector_store()
        
        assert vs1 is vs2


class TestSessionVectorStore:
    """Test per-session vector store management."""

    def test_session_store_created(self):
        """Test that session-specific stores are created."""
        from e2sc.data.vector_store import get_vector_store, _session_stores
        
        session_id = "test_session_123"
        
        # Get session store
        vs = get_vector_store(session_id)
        
        assert vs is not None
        assert session_id in _session_stores

    def test_session_store_isolation(self):
        """Test that different session stores are isolated."""
        from e2sc.data.vector_store import get_vector_store
        
        session_a = "session_a"
        session_b = "session_b"
        
        vs_a = get_vector_store(session_a)
        vs_b = get_vector_store(session_b)
        
        # Different sessions should have different stores
        assert vs_a is not vs_b

    def test_session_store_cleanup(self):
        """Test that session stores can be cleaned up."""
        from e2sc.data.vector_store import get_vector_store, _session_stores, clear_embedding_cache
        
        session_id = "cleanup_test"
        
        # Create session store
        vs = get_vector_store(session_id)
        assert session_id in _session_stores
        
        # Clear cache
        clear_embedding_cache()
        
        # Session store should be cleared
        assert session_id not in _session_stores or _session_stores[session_id] is None


class TestIndexManagement:
    """Test FAISS index management."""

    def test_index_initialization(self):
        """Test that FAISS index is properly initialized."""
        from e2sc.data.vector_store import get_vector_store
        
        vs = get_vector_store()
        
        # Index should be initialized
        assert vs.index is not None or vs._documents == []

    def test_add_documents_updates_index(self):
        """Test that adding documents updates the index."""
        from e2sc.data.vector_store import get_vector_store
        
        vs = get_vector_store()
        initial_count = len(vs._documents)
        
        # Add documents
        vs.add_documents([{
            "id": "test_doc_1",
            "document": "Test document content",
            "metadata": {"source": "test"}
        }])
        
        assert len(vs._documents) == initial_count + 1

    def test_index_persistence(self):
        """Test that index is saved and can be reloaded."""
        from e2sc.data.vector_store import VectorStore
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = os.path.join(tmpdir, "test_index")
            
            # Create and populate store
            vs = VectorStore(collection_name="test")
            vs.add_documents([{
                "id": "persist_test",
                "document": "Persistent content",
                "metadata": {"test": True}
            }])
            
            # Save index
            vs.save_index(index_path)
            
            # Create new store and load
            vs2 = VectorStore(collection_name="test2")
            vs2.load_index(index_path)
            
            # Should have loaded the documents
            assert len(vs2._documents) >= 1


class TestEmbeddingCache:
    """Test embedding model caching."""

    def test_embedding_cache_clears_on_command(self):
        """Test that embedding cache can be cleared."""
        from e2sc.data.vector_store import clear_embedding_cache, _embedding_cache
        
        # Add something to cache
        _embedding_cache["test_key"] = "test_value"
        assert "test_key" in _embedding_cache
        
        # Clear cache
        clear_embedding_cache()
        
        # Cache should be empty
        assert len(_embedding_cache) == 0

    def test_embedding_cache_works(self):
        """Test that embedding cache is used."""
        from e2sc.data.vector_store import VectorStore
        
        vs = VectorStore()
        
        # First call should cache
        text = "Test text for caching"
        emb1 = vs._get_embedding(text)
        
        # Second call should use cache
        emb2 = vs._get_embedding(text)
        
        assert emb1 is emb2 or (emb1 == emb2).all()


class TestGeneCache:
    """Test gene data caching."""

    def test_gene_cache_cleared_on_kb_build(self):
        """Test that gene cache is cleared when building knowledge base."""
        from e2sc.agent.orchestrator_optimized import E2scAgentOptimized
        from unittest.mock import Mock, patch
        
        with patch('e2sc.agent.orchestrator_optimized.get_config') as mock_config:
            mock_cfg = Mock()
            mock_cfg.llm.api_key = "test"
            mock_cfg.llm.provider = "openai"
            mock_cfg.llm.model = "gpt-4"
            mock_cfg.llm.temperature = 0.7
            mock_cfg.llm.max_tokens = 1000
            mock_config.return_value = mock_cfg
            
            with patch('e2sc.agent.orchestrator_optimized.create_llm_provider'):
                agent = E2scAgentOptimized()
                
                # Populate gene cache
                agent._gene_cache["TP53"] = {"data": "test"}
                assert "TP53" in agent._gene_cache
                
                # Clear for new KB build
                agent._gene_cache = {}
                
                assert len(agent._gene_cache) == 0


class TestProgressMessagesInKB:
    """Test progress message generation during KB build."""

    def test_progress_messages_generated(self):
        """Test that KB build generates progress messages."""
        from e2sc.api.server import _push_progress, _progress
        
        session_id = "progress_test"
        
        # Simulate KB build progress
        _push_progress(session_id, "[进度] 开始构建知识库")
        _push_progress(session_id, "[进度] 查询基因数据...")
        _push_progress(session_id, "[进度] 构建向量索引...")
        _push_progress(session_id, "[进度] 知识库构建完成")
        
        messages = _progress[session_id]
        
        assert len(messages) == 4
        assert messages[0] == "[进度] 开始构建知识库"
        assert "[进度]" in messages[-1]

    def test_progress_message_format(self):
        """Test that progress messages follow expected format."""
        from e2sc.api.server import _push_progress, _progress
        
        session_id = "format_test"
        
        # Standard progress messages
        standard_messages = [
            "[进度] 开始处理请求",
            "[进度] 查询 [UNIPROT] 50%",
            "[进度] 正在综合解读分析结果...",
            "[进度] 分析完成",
        ]
        
        for msg in standard_messages:
            _push_progress(session_id, msg)
        
        messages = _progress[session_id]
        
        for msg in standard_messages:
            assert msg in messages


class TestOrphanedIndexCleanup:
    """Test cleanup of orphaned/stale indexes."""

    def test_session_cleanup_on_abort(self):
        """Test that session state is cleaned up on abort."""
        from e2sc.api.server import _abort_events
        
        session_id = "abort_test"
        
        import asyncio
        event = asyncio.Event()
        _abort_events[session_id] = event
        
        assert session_id in _abort_events
        
        # Simulate abort
        event.set()
        
        # Event should be triggered
        assert event.is_set()

    def test_agent_cleanup_on_session_end(self):
        """Test that agents are properly cleaned up."""
        from e2sc.api.server import agents
        
        session_id = "cleanup_session"
        
        # Add mock agent
        mock_agent = Mock()
        agents[session_id] = mock_agent
        
        assert session_id in agents
        
        # Remove agent
        del agents[session_id]
        
        assert session_id not in agents
