# Research Agent (FastAPI + FastMCP + LLM)

An LLM agent that answers research questions by calling tools in a multi-step loop.

## How it works
- `app/mcp_server.py`: FastMCP server exposing `web_search` and `fetch_page` tools
- `app/agent.py`: tool-calling loop using an OpenAI-compatible API (Groq)
- `app/main.py`: FastAPI endpoint `POST /research` returning answer, sources and tool-call trace

## Run locally
    pip install -r requirements.txt
    set LLM_API_KEY=your-key   (PowerShell: $env:LLM_API_KEY="your-key")
    set LLM_MODEL=openai/gpt-oss-20b
    python -m uvicorn app.main:app --reload

Open http://127.0.0.1:8000/docs and try `POST /research`.
