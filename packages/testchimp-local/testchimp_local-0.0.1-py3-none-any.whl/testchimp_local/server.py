import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uvicorn
from .explore_runner import ExploreRunner, run_exploration_from_file
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

app = FastAPI()

explore_runner: Optional[ExploreRunner] = None  # Will initialize later

# Request model for exploration
class ExplorationRequest(BaseModel):
    configFile: str

@app.post("/run_exploration")
async def run_exploration_endpoint(request: ExplorationRequest):
    if explore_runner is None:
        return {"status": "error", "message": "Explore runner not initialized"}
    
    try:
        result = await run_exploration_from_file(request.configFile, explore_runner.openai_api_key)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def start_server(args, api_key):
    global explore_runner
    logger.info("Starting Local Agent server... (supports prompt-based and script-based exploration configs)")
    logger.info("""To trigger an exploration, run:
        curl -X POST http://localhost:43449/run_exploration \
        -H \"Content-Type: application/json\" \
        -d '{\n    \"configFile\": \"<YOUR CONFIG FILE PATH>\"\n}'
        """)
    logger.info("Refer to documentation at https://github.com/awarelabshq/testchimp-sdk/blob/main/localagent/README.md for configuration")

    from dotenv import load_dotenv
    load_dotenv(args.env)

    explore_runner = ExploreRunner(openai_api_key=api_key)

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=args.port, reload=False)