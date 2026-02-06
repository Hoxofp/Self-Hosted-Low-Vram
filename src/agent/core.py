"""
Agent Core - Qwen + Ollama Integration
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import httpx
import json


@dataclass
class Message:
    """Chat message."""
    role: str  # "user", "assistant", "system"
    content: str


@dataclass 
class AgentConfig:
    """Agent configuration."""
    model: str = "qwen2.5-coder:3b-instruct-q4_K_M"
    base_url: str = "http://localhost:11434"
    temperature: float = 0.7
    max_tokens: int = 2048
    system_prompt: str = """You are an AI coding assistant. You help users with programming tasks.
You can use tools and skills when available. Always explain your reasoning step by step."""


class OllamaClient:
    """Client for Ollama API."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.client = httpx.Client(timeout=120.0)
    
    def generate(
        self, 
        model: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        stream: bool = False
    ) -> str:
        """Generate completion from Ollama."""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature
            }
        }
        
        if system:
            payload["system"] = system
        
        response = self.client.post(
            f"{self.base_url}/api/generate",
            json=payload
        )
        response.raise_for_status()
        
        return response.json().get("response", "")
    
    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        stream: bool = False
    ) -> str:
        """Chat completion from Ollama."""
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature
            }
        }
        
        response = self.client.post(
            f"{self.base_url}/api/chat",
            json=payload
        )
        response.raise_for_status()
        
        return response.json().get("message", {}).get("content", "")
    
    def list_models(self) -> List[str]:
        """List available models."""
        response = self.client.get(f"{self.base_url}/api/tags")
        response.raise_for_status()
        
        models = response.json().get("models", [])
        return [m["name"] for m in models]


class Agent:
    """Main AI Agent with Ollama backend."""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()
        self.client = OllamaClient(self.config.base_url)
        self.history: List[Message] = []
        self.skills: Dict[str, Any] = {}
    
    def add_message(self, role: str, content: str):
        """Add message to history."""
        self.history.append(Message(role=role, content=content))
    
    def get_messages_for_api(self) -> List[Dict[str, str]]:
        """Convert history to API format."""
        messages = [{"role": "system", "content": self.config.system_prompt}]
        for msg in self.history:
            messages.append({"role": msg.role, "content": msg.content})
        return messages
    
    def chat(self, user_input: str) -> str:
        """Process user input and return response."""
        self.add_message("user", user_input)
        
        messages = self.get_messages_for_api()
        
        response = self.client.chat(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature
        )
        
        self.add_message("assistant", response)
        return response
    
    def clear_history(self):
        """Clear conversation history."""
        self.history = []
    
    def load_skill(self, skill_path: str):
        """Load a skill from path."""
        # TODO: Implement skill loading
        pass


# Convenience function
def create_agent(model: Optional[str] = None) -> Agent:
    """Create an agent with optional custom model."""
    config = AgentConfig()
    if model:
        config.model = model
    return Agent(config)
