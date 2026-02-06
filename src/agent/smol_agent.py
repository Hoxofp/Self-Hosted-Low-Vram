"""
SmolAgents Integration - Ollama Backend
HuggingFace SmolAgents compatible agent with local Ollama models
"""

from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
import json
import re

from .core import OllamaClient, AgentConfig


@dataclass
class Tool:
    """Tool definition for agent."""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Callable
    

@dataclass
class AgentState:
    """Agent execution state."""
    messages: List[Dict[str, str]] = field(default_factory=list)
    tools_used: List[str] = field(default_factory=list)
    current_step: int = 0
    max_steps: int = 10
    

class SmolAgent:
    """
    SmolAgents-compatible agent with Ollama backend.
    
    Features:
    - Tool calling with JSON parsing
    - Multi-step reasoning (ReAct pattern)
    - Conversation memory
    - Skill loading
    """
    
    SYSTEM_PROMPT = """You are an AI coding assistant.

IMPORTANT: For simple questions or conversations, respond DIRECTLY without using any special format.

Only use the JSON tool format when you ACTUALLY NEED to:
- Execute code (python_exec)
- Read/write files (read_file, write_file)
- List directory contents (list_files)

If you need to use a tool, respond with ONLY this JSON (no other text):
```json
{{"thought": "why I need this tool", "action": "tool_name", "action_input": {{"param": "value"}}}}
```

Available tools:
{tools_description}

Remember: Most questions can be answered directly without tools. Only use tools when actually needed."""

    def __init__(
        self,
        model: str = "qwen2.5-coder:3b-instruct-q4_K_M",
        base_url: str = "http://localhost:11434",
        max_steps: int = 10
    ):
        self.client = OllamaClient(base_url)
        self.model = model
        self.max_steps = max_steps
        self.tools: Dict[str, Tool] = {}
        self.state = AgentState(max_steps=max_steps)
        
    def register_tool(self, tool: Tool):
        """Register a tool for the agent to use."""
        self.tools[tool.name] = tool
        
    def get_tools_description(self) -> str:
        """Generate tools description for system prompt."""
        if not self.tools:
            return "No tools available."
        
        descriptions = []
        for name, tool in self.tools.items():
            params = json.dumps(tool.parameters, indent=2)
            descriptions.append(f"- **{name}**: {tool.description}\n  Parameters: {params}")
        
        return "\n".join(descriptions)
    
    def get_system_prompt(self) -> str:
        """Build system prompt with tools."""
        return self.SYSTEM_PROMPT.format(
            tools_description=self.get_tools_description()
        )
    
    def parse_action(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse action from LLM response."""
        # Try to find JSON block
        json_pattern = r'```json\s*(.*?)\s*```'
        matches = re.findall(json_pattern, response, re.DOTALL)
        
        if matches:
            try:
                return json.loads(matches[-1])
            except json.JSONDecodeError:
                pass
        
        # Try direct JSON
        try:
            # Find JSON-like content
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
        except json.JSONDecodeError:
            pass
        
        return None
    
    def execute_tool(self, action: str, action_input: Dict[str, Any]) -> str:
        """Execute a tool and return result."""
        if action == "final_answer":
            return action_input.get("answer", str(action_input))
        
        if action not in self.tools:
            return f"Error: Tool '{action}' not found. Available: {list(self.tools.keys())}"
        
        tool = self.tools[action]
        try:
            result = tool.function(**action_input)
            self.state.tools_used.append(action)
            return str(result)
        except Exception as e:
            return f"Error executing {action}: {str(e)}"
    
    def run(self, user_input: str) -> str:
        """
        Run agent with user input.
        
        Implements ReAct loop:
        1. Think about what to do
        2. Take action (use tool or answer)
        3. Observe result
        4. Repeat until done
        """
        self.state = AgentState(max_steps=self.max_steps)
        
        # Build messages
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": user_input}
        ]
        
        for step in range(self.max_steps):
            self.state.current_step = step + 1
            
            # Get LLM response
            response = self.client.chat(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            
            # Parse action
            action_data = self.parse_action(response)
            
            # No valid JSON found = direct answer
            if not action_data:
                return response
            
            action = action_data.get("action", "")
            action_input = action_data.get("action_input", {})
            
            # No action specified = direct answer
            if not action:
                return response
            
            # Unknown tool = direct answer (model didn't follow format)
            if action not in self.tools and action != "final_answer":
                return response
            
            # Check for final answer
            if action == "final_answer":
                return action_input.get("answer", str(action_input))
            
            # Execute tool
            observation = self.execute_tool(action, action_input)
            
            # Add to conversation
            messages.append({"role": "assistant", "content": response})
            messages.append({
                "role": "user", 
                "content": f"Tool result: {observation}\n\nNow provide your response to the user."
            })
        
        return "Max steps reached. Please try a simpler request."
    
    def chat(self, user_input: str) -> str:
        """Simple chat without tools."""
        messages = [
            {"role": "system", "content": "You are a helpful AI coding assistant."},
            {"role": "user", "content": user_input}
        ]
        
        return self.client.chat(
            model=self.model,
            messages=messages,
            temperature=0.7
        )


# Convenience function
def create_smol_agent(
    model: str = "qwen2.5-coder:3b-instruct-q4_K_M",
    tools: Optional[List[Tool]] = None
) -> SmolAgent:
    """Create a SmolAgent with optional tools."""
    agent = SmolAgent(model=model)
    
    if tools:
        for tool in tools:
            agent.register_tool(tool)
    
    return agent
