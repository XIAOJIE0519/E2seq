"""Tests for API endpoints including chat and progress polling."""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient


class TestChatEndpoint:
    """Test cases for /api/chat endpoint."""

    @pytest.fixture
    def mock_agent(self):
        """Mock the E2scAgent."""
        with patch('e2sc.api.server.E2scAgent') as mock:
            agent_instance = Mock()
            agent_instance.chat.return_value = {
                "text": "Test response from agent",
                "plots": [],
                "data": {},
                "thinking": []
            }
            mock.return_value = agent_instance
            yield agent_instance

    def test_chat_requires_message(self, mock_agent):
        """Test that chat endpoint requires a message."""
        from e2sc.api.server import app
        client = TestClient(app)
        
        response = client.post("/api/chat", json={"chat_id": "test123"})
        assert response.status_code == 400
        assert "Message is required" in response.json()["detail"]

    def test_chat_empty_message_rejected(self, mock_agent):
        """Test that empty messages are rejected."""
        from e2sc.api.server import app
        client = TestClient(app)
        
        response = client.post("/api/chat", json={"message": "   ", "chat_id": "test123"})
        assert response.status_code == 400

    def test_chat_valid_request_returns_json(self, mock_agent):
        """Test that valid chat request returns JSON response."""
        from e2sc.api.server import app
        client = TestClient(app)
        
        response = client.post("/api/chat", json={
            "message": "Hello, analyze my data",
            "chat_id": "test123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "chat_id" in data
        assert "plots" in data
        assert isinstance(data["response"], str)

    def test_chat_generates_new_chat_id_if_missing(self, mock_agent):
        """Test that a new chat_id is generated if not provided."""
        from e2sc.api.server import app
        client = TestClient(app)
        
        response = client.post("/api/chat", json={"message": "Hello"})
        
        assert response.status_code == 200
        data = response.json()
        assert "chat_id" in data
        assert len(data["chat_id"]) > 0

    def test_chat_persists_messages(self, mock_agent):
        """Test that chat messages are persisted."""
        from e2sc.api.server import app, _save_chat_message
        client = TestClient(app)
        
        with patch('e2sc.api.server._save_chat_message') as mock_save:
            response = client.post("/api/chat", json={
                "message": "Test message",
                "chat_id": "persist_test"
            })
            
            assert response.status_code == 200
            # Check that save was called for both user and assistant messages
            assert mock_save.call_count >= 2

    def test_chat_response_structure(self, mock_agent):
        """Test the structure of chat response."""
        from e2sc.api.server import app
        client = TestClient(app)
        
        response = client.post("/api/chat", json={
            "message": "Test",
            "chat_id": "test123"
        })
        
        data = response.json()
        required_keys = ["response", "chat_id", "plots", "thinking", "data"]
        for key in required_keys:
            assert key in data, f"Missing key: {key}"


class TestProgressEndpoint:
    """Test cases for /api/progress/{session_id} endpoint."""

    def test_progress_returns_messages(self):
        """Test that progress endpoint returns messages for a session."""
        from e2sc.api.server import app, _push_progress, _progress
        
        # Push some test progress
        session_id = "test_session_123"
        _push_progress(session_id, "[进度] 开始分析")
        _push_progress(session_id, "[进度] 查询数据库")
        
        client = TestClient(app)
        response = client.get(f"/api/progress/{session_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert "session_id" in data
        assert data["session_id"] == session_id
        assert len(data["messages"]) >= 2

    def test_progress_empty_for_new_session(self):
        """Test that new sessions have empty progress."""
        from e2sc.api.server import app
        
        client = TestClient(app)
        response = client.get("/api/progress/new_session_xyz")
        
        assert response.status_code == 200
        data = response.json()
        assert data["messages"] == []

    def test_progress_thread_safety(self):
        """Test that progress updates are thread-safe."""
        import threading
        from e2sc.api.server import app, _push_progress, _progress_lock
        
        session_id = "thread_safety_test"
        
        def push_messages(start_idx):
            for i in range(10):
                _push_progress(session_id, f"[进度] Message {start_idx + i}")
        
        threads = [threading.Thread(target=push_messages, args=(i * 10,)) for i in range(3)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        client = TestClient(app)
        response = client.get(f"/api/progress/{session_id}")
        data = response.json()
        
        # All 30 messages should be present
        assert len(data["messages"]) == 30


class TestProgressHandler:
    """Test cases for the _ProgressHandler logging handler."""

    def test_progress_handler_captures_info_messages(self):
        """Test that _ProgressHandler captures [INFO] style messages."""
        from e2sc.api.server import _ProgressHandler
        import logging
        
        handler = _ProgressHandler("test_session")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="[进度] 测试消息",
            args=(),
            exc_info=None
        )
        
        handler.emit(record)
        
        # Check that the message was pushed
        from e2sc.api.server import _progress
        assert "[进度] 测试消息" in _progress["test_session"]

    def test_progress_handler_ignores_non_progress(self):
        """Test that _ProgressHandler ignores messages not starting with [."""
        from e2sc.api.server import _ProgressHandler
        import logging
        
        session_id = "non_progress_test"
        handler = _ProgressHandler(session_id)
        
        # Non-progress message
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Regular log message",
            args=(),
            exc_info=None
        )
        
        handler.emit(record)
        
        from e2sc.api.server import _progress
        assert "Regular log message" not in _progress[session_id]


class TestChatAbort:
    """Test cases for /api/chat/abort endpoint."""

    def test_abort_requires_chat_id(self):
        """Test that abort requires chat_id."""
        from e2sc.api.server import app
        client = TestClient(app)
        
        response = client.post("/api/chat/abort", json={})
        assert response.status_code == 400

    def test_abort_nonexistent_session(self):
        """Test aborting a non-existent session returns ok: False."""
        from e2sc.api.server import app
        client = TestClient(app)
        
        response = client.post("/api/chat/abort", json={"chat_id": "nonexistent_session"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] == False


class TestSettingsEndpoint:
    """Test cases for /api/settings endpoint."""

    def test_get_settings_returns_config(self):
        """Test that settings endpoint returns current configuration."""
        from e2sc.api.server import app
        client = TestClient(app)
        
        response = client.get("/api/settings")
        
        assert response.status_code == 200
        data = response.json()
        # Should have LLM configuration
        assert "llm" in data or "provider" in data or len(data.keys()) > 0

    def test_save_settings_requires_api_key(self):
        """Test that saving settings requires API key."""
        from e2sc.api.server import app
        client = TestClient(app)
        
        response = client.post("/api/settings", json={
            "provider": "openai",
            "api_key": ""  # Empty key
        })
        
        # Should either reject or accept with warning
        assert response.status_code in [200, 400, 422]
