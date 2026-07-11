"""Regression tests for per-chat runtime isolation and legacy cleanup."""

from pathlib import Path
from types import SimpleNamespace
import asyncio
import inspect
import json
import logging
import threading

from e2sc.agent.error_recovery import ErrorRecovery
from e2sc.agent.memory import MemoryManager
from e2sc.agent.orchestrator_optimized import E2scAgentOptimized
from e2sc.agent.state_manager import AgentState, StateManager
from e2sc.agent.synthesizer import SynthesizerAgent


class _StubLongTermMemory:
    def __init__(self, scope_id=None):
        self.scope_id = scope_id


def test_memory_manager_is_scoped_per_chat(monkeypatch):
    import e2sc.agent.memory as memory_module

    monkeypatch.setattr(memory_module, "LongTermMemory", _StubLongTermMemory)

    first = MemoryManager(session_id="chat-a")
    second = MemoryManager(session_id="chat-b")
    first.working_memory.add_message("user", "private to A")

    assert first.session_id == "chat-a"
    assert second.session_id == "chat-b"
    assert first.long_term_memory.scope_id == "chat-a"
    assert second.long_term_memory.scope_id == "chat-b"
    assert second.working_memory.conversation_history == []


def test_state_manager_uses_separate_persistence_directories(monkeypatch, tmp_path):
    import e2sc.agent.state_manager as state_module

    config = SimpleNamespace(database=SimpleNamespace(db_path=str(tmp_path)))
    monkeypatch.setattr(state_module, "get_config", lambda: config)

    first = StateManager(session_id="chat-a")
    second = StateManager(session_id="chat-b")
    first.set_state(AgentState.PLANNING)

    assert first.state_file == tmp_path / "state" / "chat-a" / "current_state.json"
    assert second.state_file == tmp_path / "state" / "chat-b" / "current_state.json"
    assert first.state_file.exists()
    assert not second.state_file.exists()
    assert second.current_state is AgentState.IDLE


def test_error_recovery_statistics_are_not_shared():
    first = ErrorRecovery(max_retries=1)
    second = ErrorRecovery(max_retries=1)

    first.error_history.append({"error": "only A"})
    first.recovery_stats["total_errors"] = 1

    assert second.error_history == []
    assert second.recovery_stats["total_errors"] == 0


def test_progress_handler_filters_other_session_threads(monkeypatch):
    import e2sc.api.server as server

    captured = []
    monkeypatch.setattr(server, "_push_progress", lambda session_id, msg: captured.append((session_id, msg)))

    local = server._ProgressHandler("chat-a")
    other = server._ProgressHandler("chat-b", bind_current_thread=False)
    other.thread_id = threading.get_ident() + 1
    record = logging.LogRecord("e2sc.agent", logging.INFO, __file__, 1, "[progress] A", (), None)

    local.emit(record)
    other.emit(record)

    assert captured == [("chat-a", "[progress] A")]


def test_optimized_agent_no_longer_exposes_dead_chat_paths():
    removed = {
        "_agentic_synthesize_from_cache",
        "_chat_dataset_info",
        "_chat_targeted",
        "_chat_complete",
        "_chat_stream",
        "_execute_plan",
        "_run_deg_analysis",
        "_run_enrichment_analysis",
        "_run_network_analysis",
        "_create_visualizations",
        "_chat_with_agent_executor",
    }

    assert not removed.intersection(vars(E2scAgentOptimized))


def test_default_rag_paths_do_not_run_extra_sequence_analysis():
    main_source = inspect.getsource(E2scAgentOptimized._chat_agentic_rag)
    csv_source = inspect.getsource(E2scAgentOptimized._chat_csv_rag)
    forbidden = {
        "_build_cross_gene_analysis",
        "grp_diff_summary",
        "ct_grp_joint",
        "rank_genes_groups",
        "pd.DataFrame",
        "is_comprehensive=True",
    }

    assert not forbidden.intersection(vars(E2scAgentOptimized))
    for token in forbidden:
        assert token not in main_source
        assert token not in csv_source
    assert '"interpretation_only": True' in main_source
    assert '"interpretation_only": True' in csv_source
    assert 'knowledge["cross_session_context"]' not in main_source
    assert 'knowledge["cross_session_context"]' not in csv_source


def test_synthesizer_formats_only_uploaded_gene_values():
    synthesizer = SynthesizerAgent(llm=None)
    formatted = synthesizer._format_results({
        "interpretation_only": True,
        "matrix_context": {
            "genes_queried": ["TP53", "EGFR"],
            "overall_gene_values": {"TP53": 2.5, "EGFR": 1.25},
            "top_genes_per_group": {"case": {"TP53": 3.0}},
            "top_genes_per_celltype": {"T cell": {"EGFR": 0.75}},
        },
    })
    rules = synthesizer._build_system_message("请全面解读", True, "detailed")

    assert "TP53:2.5" in formatted
    assert "EGFR:1.25" in formatted
    assert "case" in formatted
    assert "T cell" in formatted
    assert "Do NOT perform" in rules
    assert "never authorizes additional analysis" in rules


def test_sse_done_event_delivers_agent_text(monkeypatch):
    import e2sc.api.server as server
    import e2sc.utils as utils

    class _TextAgent:
        def chat(self, message, **kwargs):
            return {
                "text": "TP53 输入值为 2.5；RAG 证据已返回。",
                "plots": [],
                "data": {"interpretation_only": True},
                "thinking": [],
            }

    config = SimpleNamespace(
        llm=SimpleNamespace(api_key="encrypted", provider="stub", model="stub")
    )
    security = SimpleNamespace(decrypt=lambda value: "decrypted")
    monkeypatch.setattr(utils, "get_config", lambda: config)
    monkeypatch.setattr(utils, "get_security_manager", lambda: security)
    monkeypatch.setattr(server, "_save_chat_message", lambda *args, **kwargs: None)
    monkeypatch.setattr(server, "_push_progress", lambda *args, **kwargs: None)
    server.agents["sse-text"] = _TextAgent()

    async def _collect():
        return [chunk async for chunk in server._stream_agent_chat("sse-text", "解读 TP53")]

    try:
        events = asyncio.run(_collect())
    finally:
        server.agents.pop("sse-text", None)

    done = next(event for event in events if event.startswith("event: done"))
    payload = json.loads(done.split("data: ", 1)[1])
    assert payload["response"] == "TP53 输入值为 2.5；RAG 证据已返回。"
    assert payload["data"]["interpretation_only"] is True


def test_cli_web_delegates_to_supported_start_script(monkeypatch):
    import subprocess
    from e2sc.cli.app import web

    calls = []
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: calls.append((args, kwargs)))

    web(port=8501, host="localhost")

    command = calls[0][0][0]
    assert Path(command[1]).name == "start.py"
    assert calls[0][1]["cwd"] == str(Path(command[1]).parent)
