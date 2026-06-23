"""Memory system for E2sc Agent — Short-term and Long-term memory.

P0  — Fix session-switch断层: load SQLite history into WorkingMemory on restore
P1  — Auto-summarization: compress old messages when history grows too long
P1  — LongTermMemory context integration: get_relevant_context() now used
P2  — Dynamic token budget: estimate context size before building messages
P3  — Cross-session memory: similar past cases injected into synthesizer
"""

import json
import re
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from e2sc.data.vector_store import get_vector_store
from e2sc.utils import get_config, get_logger

logger = get_logger(__name__)

# ── Configurable thresholds ────────────────────────────────────────────────────

# Auto-summarize once history exceeds this many messages
_HISTORY_SUMMARIZE_THRESHOLD = 20  # ~10 user+assistant pairs

# How many messages to keep *after* summarization (recent = preserved)
_HISTORY_KEEP_RECENT_AFTER_SUMMARIZE = 10

# Token budget (chars ≈ tokens × 0.75) for the compressed history section
_SUMMARY_BUDGET_CHARS = 3000

# Token budget for RAG context (model-agnostic, tuned for 32K context)
_RAG_BUDGET_CHARS = 6000

# Token budget for results / knowledge sections
_RESULTS_BUDGET_CHARS = 15000
_KNOWLEDGE_BUDGET_CHARS = 40000
_SIMILAR_CASES_BUDGET_CHARS = 3000


class WorkingMemory:
    """Short-term working memory for current conversation.
    
    P1 Enhancement: tracks summarization state to avoid redundant compression.
    """
    
    def __init__(self):
        self.conversation_history: List[Dict[str, Any]] = []
        self.current_context: Dict[str, Any] = {}
        self.intermediate_results: Dict[str, Any] = {}
        self.analysis_state: Dict[str, Any] = {}
        # P1: flag to prevent double-summarization within same session
        self._is_summarized: bool = False

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        msg = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.conversation_history.append(msg)
        logger.debug(f"Added message to working memory: {role}")

    def update_context(self, key: str, value: Any):
        self.current_context[key] = value
        logger.debug(f"Updated context: {key}")

    def store_intermediate_result(self, step: str, result: Any):
        self.intermediate_results[step] = {
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        logger.debug(f"Stored intermediate result: {step}")

    def get_recent_messages(self, n: int = 5) -> List[Dict[str, Any]]:
        return self.conversation_history[-n:]

    def get_context_summary(self) -> str:
        parts = []
        ds = self.current_context.get("dataset")
        if ds:
            parts.append(f"Dataset: {ds.get('n_cells', 0)} cells, {ds.get('n_genes', 0)} genes")
        cts = self.current_context.get("cell_types", [])
        if cts:
            parts.append(f"Cell types: {', '.join(cts[:5])}")
        if self.intermediate_results:
            parts.append(f"Completed steps: {', '.join(self.intermediate_results.keys())}")
        return " | ".join(parts) if parts else "No context"

    def get_history_for_llm(self, max_messages: int = 20) -> List[Dict[str, Any]]:
        """Return conversation history suitable for LLM injection.

        P2 Enhancement: respects max_messages cap and skips system-role messages
        (system is injected separately by the synthesizer).
        """
        history = self.conversation_history
        # Always keep at least the last N messages
        if len(history) <= max_messages:
            return [m for m in history if m.get("role") in ("user", "assistant")]
        # If over budget, keep recent + any "summary" compressed block
        recent = history[-max_messages:]
        return [m for m in recent if m.get("role") in ("user", "assistant")]

    def estimate_history_tokens(self) -> int:
        """P2: Estimate total token count of conversation history."""
        total = 0
        for m in self.conversation_history:
            # rough estimate: each role tag ~4 tokens + content
            total += 4 + len(m.get("content", "")) // 4
        return total

    def clear(self):
        self.conversation_history = []
        self.current_context = {}
        self.intermediate_results = {}
        self.analysis_state = {}
        self._is_summarized = False
        logger.info("Working memory cleared")


class LongTermMemory:
    """Long-term memory for persistent knowledge storage.
    
    P3 Enhancement: enriches session records with full conversation text
    for better vector similarity matching.
    """
    
    def __init__(self):
        config = get_config()
        self.memory_dir = Path(config.database.db_path).expanduser() / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_file = self.memory_dir / "sessions.jsonl"
        self.knowledge_file = self.memory_dir / "knowledge.json"
        
        try:
            self.vector_store = get_vector_store()
        except Exception as e:
            logger.warning(f"Vector store not available: {e}")
            self.vector_store = None
        
        self.knowledge_base = self._load_knowledge()
        # P3: lock for thread-safe session saves
        self._lock = threading.Lock()

    def _load_knowledge(self) -> Dict[str, Any]:
        if self.knowledge_file.exists():
            try:
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading knowledge base: {e}")
        
        return {
            "learned_patterns": {},
            "successful_analyses": [],
            "failed_analyses": [],
            "user_preferences": {}
        }
    
    def _save_knowledge(self):
        try:
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
            logger.debug("Knowledge base saved")
        except Exception as e:
            logger.error(f"Error saving knowledge base: {e}")
    
    def save_session(self, session_data: Dict[str, Any]):
        """P3 Enhancement: stores full conversation text for better similarity search."""
        try:
            # Build a richer text for vector indexing (not just question + summary)
            conv_text_parts = []
            for msg in session_data.get("conversation", []):
                role = msg.get("role", "?")
                content = msg.get("content", "")
                if content and role in ("user", "assistant"):
                    conv_text_parts.append(f"{role}: {content[:500]}")
            conv_text = "\n".join(conv_text_parts)

            session_record = {
                "timestamp": datetime.now().isoformat(),
                "session_id": session_data.get("session_id"),
                "question": session_data.get("question", ""),
                "analysis_type": session_data.get("analysis_type", "unknown"),
                "success": session_data.get("success", True),
                "results_summary": session_data.get("results_summary", ""),
                "error": session_data.get("error"),
                # P3: richer text for semantic similarity
                "conv_text": conv_text[:5000],  # cap at 5k chars
            }
            
            with self._lock:
                with open(self.session_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(session_record, ensure_ascii=False) + '\n')
            
            # Add to vector store
            if self.vector_store and session_data.get("success") and hasattr(self.vector_store, "add_case"):
                # P3: index the richer conversation text for better recall
                case_text = (
                    f"Question: {session_data.get('question', '')}\n"
                    f"Analysis type: {session_data.get('analysis_type', 'unknown')}\n"
                    f"Conversation: {conv_text}"
                )
                self.vector_store.add_case(
                    case_id=session_data.get("session_id", str(datetime.now().timestamp())),
                    case_text=case_text,
                    metadata={
                        "timestamp": session_record["timestamp"],
                        "analysis_type": session_data.get("analysis_type", "unknown"),
                        "success": session_data.get("success", True),
                    }
                )
            
            if session_data.get("success"):
                self.knowledge_base["successful_analyses"].append(session_record)
            else:
                self.knowledge_base["failed_analyses"].append(session_record)
            
            self._save_knowledge()
            logger.info(f"Session saved to long-term memory: {session_data.get('session_id')}")
            
        except Exception as e:
            logger.error(f"Error saving session: {e}")
    
    def learn_pattern(self, pattern_name: str, pattern_data: Dict[str, Any]):
        self.knowledge_base["learned_patterns"][pattern_name] = {
            "data": pattern_data,
            "timestamp": datetime.now().isoformat(),
            "usage_count": self.knowledge_base["learned_patterns"].get(pattern_name, {}).get("usage_count", 0) + 1
        }
        self._save_knowledge()
        logger.info(f"Learned pattern: {pattern_name}")
    
    def get_similar_sessions(self, query: str, n: int = 3) -> List[Dict[str, Any]]:
        """P3 Enhancement: falls back to keyword search in JSONL if vector store unavailable."""
        if not self.vector_store:
            return self._keyword_similar_sessions(query, n)
        
        try:
            return self.vector_store.search_similar_cases(query, n_results=n)
        except Exception as e:
            logger.warning(f"Vector search failed, falling back to keyword: {e}")
            return self._keyword_similar_sessions(query, n)

    def _keyword_similar_sessions(self, query: str, n: int = 3) -> List[Dict[str, Any]]:
        """P3 Fallback: keyword-based similarity when vector store unavailable."""
        if not self.session_file.exists():
            return []
        
        # Extract key terms from query (genes, diseases, analysis types)
        terms = re.findall(r'\b[A-Z]{2,}[0-9]*\b|\b(综合|分析|基因|细胞|通路|网络|富集|PPI|GO|KEGG)\b', query)
        terms = [t.lower() for t in terms]
        
        results = []
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except Exception:
                        continue
                    
                    score = 0
                    question = rec.get("question", "").lower()
                    conv = rec.get("conv_text", "").lower()
                    combined = question + " " + conv
                    
                    for term in terms:
                        score += combined.count(term) * 2
                    
                    # Boost for analysis_type match
                    at = rec.get("analysis_type", "").lower()
                    if any(t in at for t in terms):
                        score += 5
                    
                    if score > 0:
                        rec["_keyword_score"] = score
                        rec["distance"] = 1.0 / (score + 1)
                        results.append(rec)
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
        
        results.sort(key=lambda x: x.get("_keyword_score", 0), reverse=True)
        return results[:n]

    def get_learned_patterns(self) -> Dict[str, Any]:
        return self.knowledge_base.get("learned_patterns", {})
    
    def get_statistics(self) -> Dict[str, Any]:
        sa = self.knowledge_base.get("successful_analyses", [])
        fa = self.knowledge_base.get("failed_analyses", [])
        total = len(sa) + len(fa)
        return {
            "total_sessions": total,
            "successful_sessions": len(sa),
            "failed_sessions": len(fa),
            "learned_patterns": len(self.knowledge_base.get("learned_patterns", {})),
            "success_rate": len(sa) / max(1, total)
        }


class MemoryManager:
    """Unified memory manager combining working and long-term memory.
    
    P0 Enhancement: restore_session() loads SQLite history into WorkingMemory
                    when user switches back to an existing chat.
    P1 Enhancement: auto_summarize() uses LLM to compress long history.
    P2 Enhancement: dynamic_token_budget() estimates context before LLM call.
    P3 Enhancement: cross_session memory now enriched and used.
    """
    
    def __init__(self):
        self.working_memory = WorkingMemory()
        self.long_term_memory = LongTermMemory()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._llm: Optional[Any] = None  # lazily injected by orchestrator
        logger.info(f"Memory manager initialized. Session ID: {self.session_id}")
    
    def set_llm(self, llm: Any):
        """Inject the LLM client for summarization (called by orchestrator)."""
        self._llm = llm
        logger.debug("MemoryManager LLM set for summarization")

    def add_interaction(self, user_message: str, assistant_response: str,
                       metadata: Optional[Dict] = None):
        self.working_memory.add_message("user", user_message, metadata)
        self.working_memory.add_message("assistant", assistant_response, metadata)
        # P1: trigger auto-summarization check after each exchange
        self.maybe_summarize()

    def maybe_summarize(self):
        """P1: Automatically summarize conversation history when it grows too long.
        
        Uses the LLM to compress old messages (before the last _HISTORY_KEEP_RECENT_AFTER_SUMMARIZE)
        into a concise summary, replacing the old block with a single summary message.
        This runs after every add_interaction() call.
        """
        wm = self.working_memory
        if wm._is_summarized:
            return  # already summarized in this session
        
        if len(wm.conversation_history) < _HISTORY_SUMMARIZE_THRESHOLD:
            return  # not yet at threshold
        
        if self._llm is None:
            logger.debug("LLM not set, skipping auto-summarize")
            return
        
        # Identify the "old" block to compress (everything except the last KEEP messages)
        keep = _HISTORY_KEEP_RECENT_AFTER_SUMMARIZE
        old_block = wm.conversation_history[:-keep]
        recent_block = wm.conversation_history[-keep:]
        
        if any(m.get("role") == "summary" for m in old_block):
            logger.debug("Old block already contains a summary, skipping")
            wm._is_summarized = True
            return
        
        # Build a compact digest for the LLM
        digest_lines = []
        for m in old_block:
            role = m.get("role", "?")
            content = m.get("content", "")
            # Truncate each message to first 300 chars for the digest
            snippet = content[:300] + ("..." if len(content) > 300 else "")
            digest_lines.append(f"[{role}] {snippet}")
        digest = "\n".join(digest_lines)
        
        logger.info(f"[Memory] Auto-summarizing {len(old_block)} messages (total history: {len(wm.conversation_history)})")
        
        try:
            summary_text = self._summarize_with_llm(digest)
            summary_msg = {
                "role": "summary",
                "content": f"[EARLIER CONVERSATION SUMMARY — DO NOT repeat verbatim, but use as context]\n{summary_text}",
                "timestamp": datetime.now().isoformat(),
                "metadata": {"type": "auto_summary", "n_messages_compressed": len(old_block)}
            }
            # Replace old block with single summary + recent messages
            wm.conversation_history = [summary_msg] + recent_block
            wm._is_summarized = True
            logger.info(f"[Memory] Summarization complete. History now: {len(wm.conversation_history)} messages")
        except Exception as e:
            logger.warning(f"[Memory] Summarization failed, keeping raw history: {e}")

    def _summarize_with_llm(self, digest: str) -> str:
        """Call LLM to generate a concise summary of old conversation messages."""
        if self._llm is None:
            return "[summary unavailable — LLM not set]"
        
        prompt = (
            "You are a conversation summarizer. Given the following earlier conversation messages, "
            "produce a concise SUMMARY (max 400 words) that captures:\n"
            "1. The user's main goals / questions\n"
            "2. Key findings, decisions, or data explored\n"
            "3. Any important context (dataset type, analysis type, genes studied)\n\n"
            "IMPORTANT: Write the summary as continuous prose. Do NOT list each message. "
            "This summary will be prepended to the recent conversation.\n\n"
            f"=== Earlier messages ===\n{digest}\n\n"
            "=== Summary ==="
        )
        
        try:
            resp = self._llm.chat([
                {"role": "system", "content": "You are a helpful assistant that summarizes conversation history."},
                {"role": "user", "content": prompt}
            ])
            return resp.strip()[:_SUMMARY_BUDGET_CHARS]
        except Exception as e:
            logger.warning(f"LLM summarization call failed: {e}")
            return "[Could not generate summary — see earlier messages]"

    def update_analysis_state(self, state_updates: Dict[str, Any]):
        self.working_memory.analysis_state.update(state_updates)
        logger.debug(f"Analysis state updated: {list(state_updates.keys())}")
    
    def save_current_session(self, success: bool = True, error: Optional[str] = None):
        """Enhanced P3: includes full conversation in session record for better similarity."""
        session_data = {
            "session_id": self.session_id,
            "question": (self.working_memory.conversation_history[0]["content"]
                        if self.working_memory.conversation_history else ""),
            "analysis_type": self.working_memory.analysis_state.get("analysis_type", "unknown"),
            "success": success,
            "results_summary": self.working_memory.get_context_summary(),
            "results": self.working_memory.intermediate_results,
            "error": error,
            "conversation": self.working_memory.conversation_history,  # P3: full history
        }
        self.long_term_memory.save_session(session_data)
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """P2 Enhancement: returns history with smart truncation based on token budget."""
        return self.working_memory.conversation_history

    def get_conversation_history_for_llm(
        self,
        max_messages: int = 20,
        max_total_chars: int = 8000,
    ) -> List[Dict[str, Any]]:
        """P2: Return conversation history that fits within character budget.
        
        Prioritizes recent messages and summary messages. Skips system-role.
        """
        wm = self.working_memory
        all_msgs = wm.conversation_history
        
        if not all_msgs:
            return []
        
        # Build list of (index, msg) for non-system messages
        candidates = [(i, m) for i, m in enumerate(all_msgs)
                      if m.get("role") in ("user", "assistant", "summary")]
        
        total_chars = sum(len(m["content"]) for _, m in candidates)
        if total_chars <= max_total_chars and len(candidates) <= max_messages:
            return [m for _, m in candidates]
        
        result = []
        chars_used = 0
        
        # Prefer: summary messages first, then most recent
        summary_msgs = [(i, m) for i, m in candidates if m.get("role") == "summary"]
        recent_msgs = [(i, m) for i, m in candidates if m.get("role") != "summary"]
        # Sort recent by index descending (most recent last = will be kept in reverse)
        recent_msgs.sort(key=lambda x: x[0], reverse=True)
        
        for i, m in summary_msgs:
            if chars_used + len(m["content"]) <= max_total_chars and len(result) < max_messages:
                result.append(m)
                chars_used += len(m["content"])
        
        for i, m in recent_msgs:
            if chars_used + len(m["content"]) <= max_total_chars and len(result) < max_messages:
                result.append(m)
                chars_used += len(m["content"])
        
        # Restore chronological order
        result.sort(key=lambda m: (
            0 if m.get("role") == "summary" else 1,
            all_msgs.index(m) if m in all_msgs else 0
        ))
        return result

    def get_relevant_context(self, query: str) -> Dict[str, Any]:
        """P1/P3: Gather relevant context from both working and long-term memory.
        
        This is called before each synthesis to build rich contextual awareness.
        """
        wm = self.working_memory
        ltm = self.long_term_memory
        
        # Long-term: semantic similarity search across past sessions
        similar_sessions = ltm.get_similar_sessions(query, n=3)
        
        # Learned patterns filtered by relevance
        all_patterns = ltm.get_learned_patterns()
        relevant_patterns = {}
        for name, pat in all_patterns.items():
            pat_str = json.dumps(pat.get("data", {}), ensure_ascii=False)
            if any(term.lower() in (name + " " + pat_str).lower() for term in query.split()[:5]):
                relevant_patterns[name] = pat
        
        return {
            "current_context": wm.get_context_summary(),
            "recent_messages": wm.get_recent_messages(n=5),
            "conversation_history": wm.conversation_history,
            "similar_sessions": similar_sessions,
            "relevant_patterns": relevant_patterns,
            "intermediate_results": wm.intermediate_results,
        }
    
    def dynamic_token_budget(
        self,
        system_chars: int,
        prompt_chars: int,
        available_tokens: int = 28000,
    ) -> Dict[str, int]:
        """P2: Compute per-section character budgets based on estimated context usage.
        
        Returns a dict with max_chars for each section: results, knowledge, similar_cases, history.
        """
        # Rough conversion: 1 token ≈ 4 chars
        available_chars = available_tokens * 4
        
        # Fixed costs
        overhead = system_chars + prompt_chars + 200  # safety margin
        
        remaining = max(0, available_chars - overhead)
        if remaining <= 0:
            return {"results": 0, "knowledge": 0, "similar_cases": 0, "history": 0}
        
        # Proportional allocation: knowledge > results > history > similar_cases
        weights = {"knowledge": 0.50, "results": 0.25, "history": 0.15, "similar_cases": 0.10}
        
        budgets = {}
        for section, weight in weights.items():
            budget = int(remaining * weight)
            # Apply hard caps
            if section == "results":
                budget = min(budget, _RESULTS_BUDGET_CHARS)
            elif section == "knowledge":
                budget = min(budget, _KNOWLEDGE_BUDGET_CHARS)
            elif section == "similar_cases":
                budget = min(budget, _SIMILAR_CASES_BUDGET_CHARS)
            elif section == "history":
                budget = min(budget, _SUMMARY_BUDGET_CHARS)
            budgets[section] = budget
        
        return budgets

    def restore_session(self, session_id: str, messages: List[Dict[str, Any]]):
        """P0: Restore conversation history from SQLite when user loads an existing chat.
        
        Loads the full message history from the chat sidebar into WorkingMemory,
        fixing the critical断层 where switching sessions lost LLM context.
        """
        wm = self.working_memory
        wm.conversation_history = []
        wm._is_summarized = False
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ("user", "assistant", "summary") and content:
                wm.conversation_history.append({
                    "role": role,
                    "content": content,
                    "timestamp": msg.get("created_at", datetime.now().isoformat()),
                    "metadata": {}
                })
        
        self.session_id = session_id
        logger.info(
            f"[Memory] Restored session {session_id}: "
            f"{len(wm.conversation_history)} messages loaded"
        )
        # If restored history is long, mark as already summarized to avoid re-compression
        if len(wm.conversation_history) >= _HISTORY_SUMMARIZE_THRESHOLD:
            wm._is_summarized = True

    def clear_working_memory(self):
        if self.working_memory.conversation_history:
            self.save_current_session()
        self.working_memory.clear()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info(f"Working memory cleared. New session ID: {self.session_id}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        wm = self.working_memory
        ltm = self.long_term_memory
        return {
            "current_session": {
                "session_id": self.session_id,
                "messages": len(wm.conversation_history),
                "is_summarized": wm._is_summarized,
                "context_items": len(wm.current_context),
                "intermediate_results": len(wm.intermediate_results),
                "estimated_tokens": wm.estimate_history_tokens(),
            },
            "long_term": ltm.get_statistics()
        }


# ── Module-level singleton ────────────────────────────────────────────────────

_memory_manager: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """Get the global MemoryManager instance (singleton per process)."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager
