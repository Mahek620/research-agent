from fastapi import FastAPI

from app.agent import run_research

app = FastAPI(title="Research-to-Action Agent")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/research")
async def research(question: str):
    result = await run_research(question)
    return {"question": question, **result}