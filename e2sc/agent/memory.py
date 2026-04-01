"""Memory system for E2sc Agent - Short-term and Long-term memory."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from e2sc.data.vector_store import get_vector_store
from e2sc.utils import get_config, get_logger

logger = get_logger(__name__)


class WorkingMemory:
    """Short-term working memory for current conversation."""
    
    def __init__(self):
        """Initialize working memory."""
        self.conversation_history: List[Dict[str, Any]] = []
        self.current_context: Dict[str, Any] = {}
        self.intermediate_results: Dict[str, Any] = {}
        self.analysis_state: Dict[str, Any] = {}
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add message to conversation history.
        
        Args:
            role: Message role (user/assistant/system)
            content: Message content
            metadata: Additional metadata
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.conversation_history.append(message)
        logger.debug(f"Added message to working memory: {role}")
    
    def update_context(self, key: str, value: Any):
        """Update current context.
        
        Args:
            key: Context key
            value: Context value
        """
        self.current_context[key] = value
        logger.debug(f"Updated context: {key}")
    
    def store_intermediate_result(self, step: str, result: Any):
        """Store intermediate analysis result.
        
        Args:
            step: Analysis step name
            result: Result data
        """
        self.intermediate_results[step] = {
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        logger.debug(f"Stored intermediate result: {step}")
    
    def get_recent_messages(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get recent messages.
        
        Args:
            n: Number of recent messages
            
        Returns:
            List of recent messages
        """
        return self.conversation_history[-n:]
    
    def get_context_summary(self) -> str:
        """Get summary of current context.
        
        Returns:
            Context summary string
        """
        summary_parts = []
        
        if self.current_context.get("dataset"):
            ds = self.current_context["dataset"]
            summary_parts.append(f"Dataset: {ds.get('n_cells', 0)} cells, {ds.get('n_genes', 0)} genes")
        
        if self.current_context.get("cell_types"):
            summary_parts.append(f"Cell types: {', '.join(self.current_context['cell_types'][:5])}")
        
        if self.intermediate_results:
            summary_parts.append(f"Completed steps: {', '.join(self.intermediate_results.keys())}")
        
        return " | ".join(summary_parts) if summary_parts else "No context"
    
    def clear(self):
        """Clear working memory."""
        self.conversation_history = []
        self.current_context = {}
        self.intermediate_results = {}
        self.analysis_state = {}
        logger.info("Working memory cleared")


class LongTermMemory:
    """Long-term memory for persistent knowledge storage."""
    
    def __init__(self):
        """Initialize long-term memory."""
        config = get_config()
        self.memory_dir = Path(config.database.db_path).expanduser() / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_file = self.memory_dir / "sessions.jsonl"
        self.knowledge_file = self.memory_dir / "knowledge.json"
        
        # Initialize vector store for semantic search
        try:
            self.vector_store = get_vector_store()
        except Exception as e:
            logger.warning(f"Vector store not available: {e}")
            self.vector_store = None
        
        # Load existing knowledge
        self.knowledge_base = self._load_knowledge()
    
    def _load_knowledge(self) -> Dict[str, Any]:
        """Load knowledge base from file.
        
        Returns:
            Knowledge base dictionary
        """
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
        """Save knowledge base to file."""
        try:
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
            logger.debug("Knowledge base saved")
        except Exception as e:
            logger.error(f"Error saving knowledge base: {e}")
    
    def save_session(self, session_data: Dict[str, Any]):
        """Save session to long-term memory.
        
        Args:
            session_data: Session data including conversation and results
        """
        try:
            session_record = {
                "timestamp": datetime.now().isoformat(),
                "session_id": session_data.get("session_id"),
                "question": session_data.get("question"),
                "analysis_type": session_data.get("analysis_type"),
                "success": session_data.get("success", True),
                "results_summary": session_data.get("results_summary"),
                "error": session_data.get("error")
            }
            
            # Append to sessions file
            with open(self.session_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(session_record, ensure_ascii=False) + '\n')
            
            # Add to vector store for semantic search (only if add_case is available)
            if self.vector_store and session_data.get("success") and hasattr(self.vector_store, "add_case"):
                case_text = json.dumps({
                    "question": session_data.get("question", ""),
                    "analysis_type": session_data.get("analysis_type", "unknown"),
                    "results": session_data.get("results", {}),
                }, ensure_ascii=False)
                self.vector_store.add_case(
                    case_id=session_data.get("session_id", str(datetime.now().timestamp())),
                    case_text=case_text,
                    metadata={"timestamp": session_record["timestamp"]}
                )
            
            # Update knowledge base
            if session_data.get("success"):
                self.knowledge_base["successful_analyses"].append(session_record)
            else:
                self.knowledge_base["failed_analyses"].append(session_record)
            
            self._save_knowledge()
            logger.info(f"Session saved to long-term memory: {session_data.get('session_id')}")
            
        except Exception as e:
            logger.error(f"Error saving session: {e}")
    
    def learn_pattern(self, pattern_name: str, pattern_data: Dict[str, Any]):
        """Learn a new pattern from successful analysis.
        
        Args:
            pattern_name: Pattern identifier
            pattern_data: Pattern data
        """
        self.knowledge_base["learned_patterns"][pattern_name] = {
            "data": pattern_data,
            "timestamp": datetime.now().isoformat(),
            "usage_count": self.knowledge_base["learned_patterns"].get(pattern_name, {}).get("usage_count", 0) + 1
        }
        self._save_knowledge()
        logger.info(f"Learned pattern: {pattern_name}")
    
    def get_similar_sessions(self, query: str, n: int = 3) -> List[Dict[str, Any]]:
        """Get similar past sessions using semantic search.
        
        Args:
            query: Query string
            n: Number of results
            
        Returns:
            List of similar sessions
        """
        if not self.vector_store:
            return []
        
        try:
            similar_cases = self.vector_store.search_similar_cases(query, n_results=n)
            return similar_cases
        except Exception as e:
            logger.error(f"Error searching similar sessions: {e}")
            return []
    
    def get_learned_patterns(self) -> Dict[str, Any]:
        """Get all learned patterns.
        
        Returns:
            Dictionary of learned patterns
        """
        return self.knowledge_base.get("learned_patterns", {})
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            "total_sessions": len(self.knowledge_base.get("successful_analyses", [])) + 
                            len(self.knowledge_base.get("failed_analyses", [])),
            "successful_sessions": len(self.knowledge_base.get("successful_analyses", [])),
            "failed_sessions": len(self.knowledge_base.get("failed_analyses", [])),
            "learned_patterns": len(self.knowledge_base.get("learned_patterns", {})),
            "success_rate": len(self.knowledge_base.get("successful_analyses", [])) / 
                          max(1, len(self.knowledge_base.get("successful_analyses", [])) + 
                              len(self.knowledge_base.get("failed_analyses", [])))
        }


class MemoryManager:
    """Unified memory manager combining working and long-term memory."""
    
    def __init__(self):
        """Initialize memory manager."""
        self.working_memory = WorkingMemory()
        self.long_term_memory = LongTermMemory()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info(f"Memory manager initialized. Session ID: {self.session_id}")
    
    def add_interaction(self, user_message: str, assistant_response: str, 
                       metadata: Optional[Dict] = None):
        """Add user-assistant interaction to memory.
        
        Args:
            user_message: User's message
            assistant_response: Assistant's response
            metadata: Additional metadata
        """
        self.working_memory.add_message("user", user_message, metadata)
        self.working_memory.add_message("assistant", assistant_response, metadata)
    
    def update_analysis_state(self, state_updates: Dict[str, Any]):
        """Update current analysis state.
        
        Args:
            state_updates: State updates dictionary
        """
        self.working_memory.analysis_state.update(state_updates)
        logger.debug(f"Analysis state updated: {list(state_updates.keys())}")
    
    def save_current_session(self, success: bool = True, error: Optional[str] = None):
        """Save current session to long-term memory.
        
        Args:
            success: Whether session was successful
            error: Error message if failed
        """
        session_data = {
            "session_id": self.session_id,
            "question": self.working_memory.conversation_history[0]["content"] if self.working_memory.conversation_history else "",
            "analysis_type": self.working_memory.analysis_state.get("analysis_type", "unknown"),
            "success": success,
            "results_summary": self.working_memory.get_context_summary(),
            "results": self.working_memory.intermediate_results,
            "error": error
        }
        
        self.long_term_memory.save_session(session_data)
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get full conversation history from working memory.
        
        Returns:
            List of message dicts with role and content.
        """
        return self.working_memory.conversation_history

    def get_relevant_context(self, query: str) -> Dict[str, Any]:
        """Get relevant context from both working and long-term memory.
        
        Args:
            query: Query string
            
        Returns:
            Relevant context dictionary
        """
        context = {
            "current_context": self.working_memory.get_context_summary(),
            "recent_messages": self.working_memory.get_recent_messages(n=5),
            "similar_sessions": self.long_term_memory.get_similar_sessions(query, n=3),
            "learned_patterns": self.long_term_memory.get_learned_patterns(),
            "intermediate_results": self.working_memory.intermediate_results
        }
        
        return context
    
    def clear_working_memory(self):
        """Clear working memory and start new session."""
        # Save current session before clearing
        if self.working_memory.conversation_history:
            self.save_current_session()
        
        self.working_memory.clear()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info(f"Working memory cleared. New session ID: {self.session_id}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics.
        
        Returns:
            Memory statistics
        """
        return {
            "current_session": {
                "session_id": self.session_id,
                "messages": len(self.working_memory.conversation_history),
                "context_items": len(self.working_memory.current_context),
                "intermediate_results": len(self.working_memory.intermediate_results)
            },
            "long_term": self.long_term_memory.get_statistics()
        }


def get_memory_manager() -> MemoryManager:
    """Get global memory manager instance.
    
    Returns:
        MemoryManager instance
    """
    global _memory_manager
    if "_memory_manager" not in globals():
        _memory_manager = MemoryManager()
    return _memory_manager
