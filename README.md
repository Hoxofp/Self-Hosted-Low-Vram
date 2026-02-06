# AI Agent - Self-Hosted Coding Assistant

Self-hosted, skill-based AI coding agent with Qwen 2.5 + HuggingFace Skills + RAG support.

## 🚀 Quick Start

```bash
# Windows
.\scripts\install.bat

# Linux/Mac
chmod +x scripts/install.sh && ./scripts/install.sh
```

## 📋 Requirements

- Python 3.10+
- 4GB+ VRAM (or 16GB RAM for CPU mode)
- [Ollama](https://ollama.ai) installed

## 🛠️ Manual Setup

```bash
# 1. Install Ollama
winget install Ollama.Ollama

# 2. Download model
ollama pull qwen2.5-coder:7b-instruct-q4_K_M

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run agent
python scripts/run_agent.py
```

## 📁 Project Structure

```
ai-agent/
├── config/           # Configuration files
├── scripts/          # Setup and run scripts
├── skills/           # Agent skills (SKILL.md format)
├── src/              # Source code
│   ├── agent/        # Agent core
│   ├── memory/       # Memory systems
│   └── tools/        # MCP tools
└── tests/            # Tests
```

## 🎯 Features

- **Qwen 2.5 Coder 3B** - Optimized for 4GB VRAM
- **HuggingFace Skills** - Upskill compatible
- **RAG** - Codebase context with ChromaDB
- **MCP Tools** - File, shell, git integration
- **Self-Reflection** - Auto error correction

## 📄 License

MIT
