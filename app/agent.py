import json
import os

from fastmcp import Client
from openai import AsyncOpenAI

from app.mcp_server import mcp

SYSTEM = (
    "You are a research agent. Use web_search to find sources, then fetch_page "
    "to read the most relevant 1-2 pages. Answer concisely using only what you "
    "read, and mention which sources support the answer."
)


async def run_research(question: str, max_steps: int = 6) -> dict:
    llm = AsyncOpenAI(
        api_key=os.environ.get("LLM_API_KEY", "ollama"),
        base_url=os.environ.get("LLM_BASE_URL", "https://api.groq.com/openai/v1"),
    )
    model = os.environ.get("LLM_MODEL", "llama-3.3-70b-versatile")

    trace: list[dict] = []
    sources: set[str] = set()

    async with Client(mcp) as mcp_client:
        tools = await mcp_client.list_tools()
        openai_tools = [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description or "",
                    "parameters": t.inputSchema,
                },
            }
            for t in tools
        ]

        messages = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": question},
        ]

        for _ in range(max_steps):
            resp = await llm.chat.completions.create(
                model=model, messages=messages, tools=openai_tools
            )
            msg = resp.choices[0].message

            if not msg.tool_calls:
                return {"answer": msg.content, "sources": sorted(sources), "trace": trace}

            messages.append(msg)
            for call in msg.tool_calls:
                args = json.loads(call.function.arguments or "{}")
                result = await mcp_client.call_tool(
                    call.function.name, args, raise_on_error=False
                )
                text = "\n".join(c.text for c in result.content if hasattr(c, "text"))
                trace.append({"tool": call.function.name, "args": args})
                if call.function.name == "fetch_page" and "url" in args:
                    sources.add(args["url"])
                messages.append(
                    {"role": "tool", "tool_call_id": call.id, "content": text}
                )

    return {
        "answer": "Stopped after reaching the step limit.",
        "sources": sorted(sources),
        "trace": trace,
    }