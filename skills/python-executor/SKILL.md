---
name: python-executor
description: Execute Python code in a sandboxed environment and return the result.
---

# Python Executor Skill

This skill allows the agent to execute Python code safely.

## Usage

When you need to run Python code, use this skill to execute it in a sandboxed environment.

## Capabilities

- Execute Python code
- Capture stdout and stderr
- Return execution results
- Timeout protection (30 seconds max)

## Safety

- Code runs in isolated subprocess
- Limited file system access
- Network access restricted
- Memory limits enforced

## Example

```python
# Agent can execute code like:
result = execute_python("print('Hello, World!')")
# Returns: "Hello, World!"
```
