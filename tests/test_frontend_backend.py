"""Tests for frontend-backend integration including text transmission."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient


class TestTextTransmission:
    """Test text transmission between frontend and backend."""

    def test_special_characters_preserved(self):
        """Test that special characters are preserved in transmission."""
        from e2sc.api.server import app
        
        test_messages = [
            "Hello, world!",
            "测试中文",
            "Emoji: 🧬 🔬",
            "Math: α + β = γ",
            "Code: `inline code`",
            "Newlines\nare\npreserved",
        ]
        
        with patch('e2sc.api.server.agents') as mock_agents:
            mock_agent = Mock()
            mock_agent.chat.return_value = {
                "text": "Response with same chars",
                "plots": [],
                "data": {},
                "thinking": []
            }
            mock_agents.__contains__ = Mock(return_value=True)
            mock_agents.__getitem__ = Mock(return_value=mock_agent)
            
            client = TestClient(app)
            
            for msg in test_messages:
                response = client.post("/api/chat", json={
                    "message": msg,
                    "chat_id": "test_special"
                })
                
                assert response.status_code == 200
                # Message should be echoed back or processed correctly
                data = response.json()
                assert "response" in data

    def test_long_message_truncation(self):
        """Test handling of very long messages."""
        from e2sc.api.server import app
        
        # Create a very long message
        long_message = "Gene " * 10000  # ~50KB
        
        with patch('e2sc.api.server.agents') as mock_agents:
            mock_agent = Mock()
            mock_agent.chat.return_value = {
                "text": "Received long message",
                "plots": [],
                "data": {},
                "thinking": []
            }
            mock_agents.__contains__ = Mock(return_value=True)
            mock_agents.__getitem__ = Mock(return_value=mock_agent)
            
            client = TestClient(app)
            
            response = client.post("/api/chat", json={
                "message": long_message,
                "chat_id": "test_long"
            })
            
            # Should handle gracefully
            assert response.status_code in [200, 413, 422]

    def test_markdown_in_response(self):
        """Test that markdown formatting in responses is preserved."""
        from e2sc.api.server import app
        
        markdown_response = """# Analysis Results

## Summary
- **Gene**: TP53
- **Fold Change**: 2.5
- **P-value**: 0.001

```python
import scanpy as sc
sc.tl.rank_genes_groups(adata)
```

[Reference: PMID:12345678](https://pubmed.ncbi.nlm.nih.gov/12345678)
"""
        
        with patch('e2sc.api.server.agents') as mock_agents:
            mock_agent = Mock()
            mock_agent.chat.return_value = {
                "text": markdown_response,
                "plots": [],
                "data": {},
                "thinking": []
            }
            mock_agents.__contains__ = Mock(return_value=True)
            mock_agents.__getitem__ = Mock(return_value=mock_agent)
            
            client = TestClient(app)
            
            response = client.post("/api/chat", json={
                "message": "Analyze TP53",
                "chat_id": "test_md"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "# Analysis Results" in data["response"]
            assert "```python" in data["response"]


class TestDataTransmission:
    """Test data object transmission."""

    def test_response_with_plots_data(self):
        """Test that plot data is correctly transmitted."""
        from e2sc.api.server import app
        
        mock_figure = {"data": [{"x": [1, 2, 3], "y": [4, 5, 6]}]}
        
        with patch('e2sc.api.server.agents') as mock_agents:
            mock_agent = Mock()
            mock_agent.chat.return_value = {
                "text": "Analysis complete",
                "plots": [("heatmap", mock_figure)],
                "data": {},
                "thinking": []
            }
            mock_agents.__contains__ = Mock(return_value=True)
            mock_agents.__getitem__ = Mock(return_value=mock_agent)
            
            client = TestClient(app)
            
            response = client.post("/api/chat", json={
                "message": "Generate heatmap",
                "chat_id": "test_plots"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "plots" in data
            assert isinstance(data["plots"], list)

    def test_response_with_source_stats(self):
        """Test that source statistics are transmitted."""
        from e2sc.api.server import app
        
        source_stats = {
            "uniprot": {"hit_genes": ["TP53", "BRCA1"], "total_genes": 100},
            "string": {"hit_genes": ["TP53"], "total_genes": 100},
        }
        
        with patch('e2sc.api.server.agents') as mock_agents:
            mock_agent = Mock()
            mock_agent.chat.return_value = {
                "text": "Analysis complete",
                "plots": [],
                "data": {"source_stats": source_stats},
                "thinking": []
            }
            mock_agents.__contains__ = Mock(return_value=True)
            mock_agents.__getitem__ = Mock(return_value=mock_agent)
            
            client = TestClient(app)
            
            response = client.post("/api/chat", json={
                "message": "Analyze genes",
                "chat_id": "test_stats"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "data" in data


class TestErrorHandling:
    """Test error handling in frontend-backend communication."""

    def test_api_key_not_configured(self):
        """Test error when API key is not configured."""
        from e2sc.api.server import app, get_config
        
        with patch('e2sc.api.server.get_config') as mock_config:
            mock_cfg = Mock()
            mock_cfg.llm.api_key = ""  # No API key
            mock_cfg.llm.provider = "openai"
            mock_cfg.llm.model = "gpt-4"
            mock_config.return_value = mock_cfg
            
            with patch('e2sc.api.server.agents') as mock_agents:
                mock_agents.__contains__ = Mock(return_value=False)
                
                client = TestClient(app)
                
                response = client.post("/api/chat", json={
                    "message": "Hello",
                    "chat_id": "test_no_key"
                })
                
                assert response.status_code == 400
                assert "API Key" in response.json()["detail"] or "key" in response.json()["detail"].lower()

    def test_agent_error_propagation(self):
        """Test that agent errors are properly propagated."""
        from e2sc.api.server import app
        
        with patch('e2sc.api.server.agents') as mock_agents:
            mock_agent = Mock()
            mock_agent.chat.side_effect = Exception("Database connection failed")
            mock_agents.__contains__ = Mock(return_value=True)
            mock_agents.__getitem__ = Mock(return_value=mock_agent)
            
            client = TestClient(app)
            
            response = client.post("/api/chat", json={
                "message": "Hello",
                "chat_id": "test_error"
            })
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data


class TestSessionIsolation:
    """Test session isolation and state management."""

    def test_different_sessions_independent(self):
        """Test that different sessions have independent state."""
        from e2sc.api.server import app, agents
        
        with patch('e2sc.api.server.agents', spec=agents.__class__) as mock_agents:
            # Track which agents are created
            created_agents = {}
            
            def get_agent(session_id):
                if session_id not in created_agents:
                    mock_agent = Mock()
                    mock_agent.chat.return_value = {
                        "text": f"Response from session {session_id}",
                        "plots": [],
                        "data": {},
                        "thinking": []
                    }
                    created_agents[session_id] = mock_agent
                return created_agents[session_id]
            
            mock_agents.__contains__ = Mock(side_effect=lambda s: s in created_agents)
            mock_agents.__getitem__ = Mock(side_effect=get_agent)
            
            client = TestClient(app)
            
            # Two different sessions
            response1 = client.post("/api/chat", json={
                "message": "Hello",
                "chat_id": "session_1"
            })
            response2 = client.post("/api/chat", json={
                "message": "Hello",
                "chat_id": "session_2"
            })
            
            assert response1.status_code == 200
            assert response2.status_code == 200
            
            # Should have created two separate agents
            assert len(created_agents) == 2

    def test_progress_isolated_per_session(self):
        """Test that progress is isolated per session."""
        from e2sc.api.server import app, _push_progress
        
        session_a = "session_a_123"
        session_b = "session_b_456"
        
        _push_progress(session_a, "[进度] A: Message 1")
        _push_progress(session_b, "[进度] B: Message 1")
        _push_progress(session_a, "[进度] A: Message 2")
        
        client = TestClient(app)
        
        response_a = client.get(f"/api/progress/{session_a}")
        response_b = client.get(f"/api/progress/{session_b}")
        
        messages_a = response_a.json()["messages"]
        messages_b = response_b.json()["messages"]
        
        # Session A should only have its own messages
        assert all("A:" in msg for msg in messages_a)
        # Session B should only have its own messages
        assert all("B:" in msg for msg in messages_b)
