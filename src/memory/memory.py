"""
Memory System - Conversation and fact storage
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path


@dataclass
class MemoryEntry:
    """Single memory entry."""
    content: str
    role: str  # "user", "assistant", "fact"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConversationMemory:
    """
    Simple conversation memory with persistence.
    
    Features:
    - Message history
    - Fact storage
    - JSON persistence
    - Context window management
    """
    
    def __init__(
        self,
        persist_path: Optional[str] = None,
        max_messages: int = 100
    ):
        self.persist_path = Path(persist_path) if persist_path else None
        self.max_messages = max_messages
        self.messages: List[MemoryEntry] = []
        self.facts: Dict[str, str] = {}  # key -> fact
        
        if self.persist_path and self.persist_path.exists():
            self._load()
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to memory."""
        entry = MemoryEntry(
            content=content,
            role=role,
            metadata=metadata or {}
        )
        self.messages.append(entry)
        
        # Trim if too many messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
        
        self._save()
    
    def add_fact(self, key: str, fact: str):
        """Store a fact for long-term memory."""
        self.facts[key] = fact
        self._save()
    
    def get_fact(self, key: str) -> Optional[str]:
        """Retrieve a fact."""
        return self.facts.get(key)
    
    def get_recent_messages(self, n: int = 10) -> List[Dict[str, str]]:
        """Get recent messages in API format."""
        recent = self.messages[-n:] if len(self.messages) > n else self.messages
        return [{"role": m.role, "content": m.content} for m in recent]
    
    def get_context_string(self, max_chars: int = 4000) -> str:
        """Get conversation context as string."""
        context = []
        total_chars = 0
        
        for msg in reversed(self.messages):
            line = f"{msg.role}: {msg.content}"
            if total_chars + len(line) > max_chars:
                break
            context.insert(0, line)
            total_chars += len(line)
        
        return "\n".join(context)
    
    def clear(self):
        """Clear all messages (keep facts)."""
        self.messages = []
        self._save()
    
    def clear_all(self):
        """Clear everything including facts."""
        self.messages = []
        self.facts = {}
        self._save()
    
    def _save(self):
        """Persist to disk."""
        if not self.persist_path:
            return
        
        self.persist_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "messages": [
                {
                    "content": m.content,
                    "role": m.role,
                    "timestamp": m.timestamp,
                    "metadata": m.metadata
                }
                for m in self.messages
            ],
            "facts": self.facts
        }
        
        with open(self.persist_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _load(self):
        """Load from disk."""
        if not self.persist_path or not self.persist_path.exists():
            return
        
        try:
            with open(self.persist_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.messages = [
                MemoryEntry(
                    content=m["content"],
                    role=m["role"],
                    timestamp=m.get("timestamp", ""),
                    metadata=m.get("metadata", {})
                )
                for m in data.get("messages", [])
            ]
            self.facts = data.get("facts", {})
        except Exception:
            pass  # Start fresh on error


class SummaryMemory:
    """
    Memory that summarizes old conversations.
    
    Keeps recent messages + summary of older ones.
    """
    
    def __init__(
        self,
        summarizer_fn: Optional[callable] = None,
        recent_count: int = 10,
        summary_threshold: int = 30
    ):
        self.summarizer_fn = summarizer_fn
        self.recent_count = recent_count
        self.summary_threshold = summary_threshold
        self.messages: List[MemoryEntry] = []
        self.summary: str = ""
    
    def add_message(self, role: str, content: str):
        """Add message, summarize if needed."""
        self.messages.append(MemoryEntry(content=content, role=role))
        
        if len(self.messages) > self.summary_threshold and self.summarizer_fn:
            self._summarize()
    
    def _summarize(self):
        """Summarize older messages."""
        if len(self.messages) <= self.recent_count:
            return
        
        # Messages to summarize
        to_summarize = self.messages[:-self.recent_count]
        context = "\n".join([f"{m.role}: {m.content}" for m in to_summarize])
        
        # Get summary from LLM
        if self.summarizer_fn:
            new_summary = self.summarizer_fn(context)
            if self.summary:
                self.summary = f"{self.summary}\n\n{new_summary}"
            else:
                self.summary = new_summary
        
        # Keep only recent messages
        self.messages = self.messages[-self.recent_count:]
    
    def get_full_context(self) -> str:
        """Get summary + recent messages."""
        recent = "\n".join([f"{m.role}: {m.content}" for m in self.messages])
        
        if self.summary:
            return f"Previous conversation summary:\n{self.summary}\n\nRecent messages:\n{recent}"
        return recent
