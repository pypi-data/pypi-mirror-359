import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict
import uvicorn
from tc_localagent.agent_runner import AgentRunner
from dotenv import load_dotenv

app = FastAPI()

agent_runner = None  # Will initialize later

# Request model that supports browser_context override
class AgentRequest(BaseModel):
    prompt: str
    browser_context: Optional[Dict] = None

@app.post("/run_agent")
async def run_agent_endpoint(request: AgentRequest):
    try:
        result = await agent_runner.run_agent(request.prompt, request.browser_context)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def start_server(args):  # <== make this synchronous
    global agent_runner
    print("Starting server...")

    # Load environment variables
    load_dotenv(args.env)

    browser_context_config = {
        "mode": args.browser_mode,
        "cdp_url": args.cdp_url
    }

    agent_runner = AgentRunner(browser_context_config)

    # Pass the app directly
    uvicorn.run(app, host="0.0.0.0", port=args.port, reload=False)