"""
Python Executor Skill - Sandbox code execution
"""

import subprocess
import tempfile
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class ExecutionResult:
    """Result of code execution."""
    success: bool
    stdout: str
    stderr: str
    return_code: int


def execute_python(
    code: str,
    timeout: int = 30,
    working_dir: Optional[str] = None
) -> ExecutionResult:
    """
    Execute Python code in a sandboxed subprocess.
    
    Args:
        code: Python code to execute
        timeout: Maximum execution time in seconds
        working_dir: Working directory for execution
    
    Returns:
        ExecutionResult with stdout, stderr, and status
    """
    # Create temporary file for the code
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.py',
        delete=False
    ) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        # Execute in subprocess with timeout
        result = subprocess.run(
            ["python", temp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=working_dir
        )
        
        return ExecutionResult(
            success=result.returncode == 0,
            stdout=result.stdout,
            stderr=result.stderr,
            return_code=result.returncode
        )
    
    except subprocess.TimeoutExpired:
        return ExecutionResult(
            success=False,
            stdout="",
            stderr=f"Execution timed out after {timeout} seconds",
            return_code=-1
        )
    
    except Exception as e:
        return ExecutionResult(
            success=False,
            stdout="",
            stderr=str(e),
            return_code=-1
        )
    
    finally:
        # Cleanup temp file
        Path(temp_path).unlink(missing_ok=True)


# Tool definition for agent
TOOL_DEFINITION = {
    "name": "python_executor",
    "description": "Execute Python code and return the result",
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code to execute"
            },
            "timeout": {
                "type": "integer",
                "description": "Maximum execution time in seconds",
                "default": 30
            }
        },
        "required": ["code"]
    }
}
