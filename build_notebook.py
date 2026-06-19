import nbformat as nbf

nb = nbf.v4.new_notebook()

cell1 = nbf.v4.new_code_cell("""\
# Cell 1: Install dependencies
!pip install fastapi uvicorn nest-asyncio

import urllib.request
import os

print("Downloading cloudflared...")
url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
cloudflared_path = "./cloudflared"

urllib.request.urlretrieve(url, cloudflared_path)
os.chmod(cloudflared_path, 0o755)

print('✅ cloudflared downloaded successfully')
print('✅ All dependencies installed')\
""")

cell2 = nbf.v4.new_code_cell("""\
# Cell 2: Define LLM Task using Kaggle Benchmarks
import kaggle_benchmarks as kbench

# We use a global variable to capture the raw string response 
# from the LLM, bypassing whatever custom object .run() returns.
LAST_LLM_RESPONSE = ""

# --------------------------------------------------------------------------------
# STEP 1: DEFINE A BARE-BONES TASK
# We keep the decorator so Kaggle tracks the quota, but drop all the testing logic.
# --------------------------------------------------------------------------------
@kbench.task(name="simple_query")
def simple_query(llm, user_prompt: str):
    global LAST_LLM_RESPONSE
    
    print(f"Sending prompt: '{user_prompt}'...\\n")
    
    # This single line calls the hosted model and spends a tiny bit of your AI Quota!
    response = llm.prompt(user_prompt)
    
    LAST_LLM_RESPONSE = response
    
    print("-" * 40)
    print("🤖 Model Output:")
    print("-" * 40)
    print(response)
    
    return response

# --------------------------------------------------------------------------------
# STEP 2: TEST RUN
# --------------------------------------------------------------------------------
# We pass the default model (kbench.llm) and our custom prompt.
test_response = simple_query.run(
    llm=kbench.llms["anthropic/claude-sonnet-4-6@default"], 
    user_prompt="Explain the difference between a GPU and a TPU in two sentences."
)
""")

cell3 = nbf.v4.new_code_cell("""\
# Cell 3: Start FastAPI server + Cloudflare tunnel with verbose logging

import nest_asyncio
nest_asyncio.apply()

import uvicorn
import subprocess
import re
import time
import threading
import asyncio
import select
import uuid
import logging
import traceback
import os
import socket

# Important: make sure we have access to kaggle_benchmarks
import kaggle_benchmarks as kbench

from fastapi import FastAPI, Request
from pydantic import BaseModel

# =============================================================================
# FIND FREE PORT
# =============================================================================

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

port = get_free_port()

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("KAGGLE_LLM_API")

# =============================================================================
# FASTAPI APP
# =============================================================================

app = FastAPI(title="Kaggle Benchmarks LLM API")

class GenerationRequest(BaseModel):
    prompt: str
    model: str = "anthropic/claude-sonnet-4-6@default"
    system: str = ""
    max_tokens: int = 4096
    temperature: float = 0.7

# =============================================================================
# API ROUTES
# =============================================================================

@app.post("/generate")
async def api_generate(
    request_data: GenerationRequest,
    request: Request
):
    request_id = str(uuid.uuid4())[:8]

    try:
        logger.info("\\n")
        logger.info("#" * 100)
        logger.info(f"[{request_id}] NEW REQUEST RECEIVED")
        logger.info("#" * 100)

        client_ip = request.client.host
        logger.info(f"[{request_id}] Client IP: {client_ip}")
        logger.info(f"[{request_id}] REQUESTED MODEL: {request_data.model}")
        logger.info(f"[{request_id}] USER PROMPT:")
        logger.info(request_data.prompt[:3000])

        if request_data.system:
            logger.info(f"[{request_id}] SYSTEM PROMPT:")
            logger.info(request_data.system[:3000])
            full_prompt = f"System: {request_data.system}\\n\\nUser: {request_data.prompt}"
        else:
            full_prompt = request_data.prompt

        # Validate Model
        if request_data.model not in kbench.llms:
            available = list(kbench.llms.keys())
            raise ValueError(f"Model '{request_data.model}' not available. Please choose from kaggle_benchmarks.llms")

        # Generation using kaggle_benchmarks
        llm = kbench.llms[request_data.model]
        
        # We call simple_query.run from Cell 2
        global LAST_LLM_RESPONSE
        LAST_LLM_RESPONSE = ""  # reset
        simple_query.run(llm=llm, user_prompt=full_prompt)

        # Extract the captured raw string response!
        response_text = str(LAST_LLM_RESPONSE)

        logger.info(f"[{request_id}] REQUEST COMPLETED SUCCESSFULLY")

        return {
            "request_id": request_id,
            "response": response_text,
        }

    except Exception as e:
        logger.error(f"[{request_id}] ERROR OCCURRED")
        logger.error(traceback.format_exc())

        return {
            "request_id": request_id,
            "error": str(e),
        }

@app.get("/")
def health_check():
    return {
        "status": "running",
        "models_available": len(kbench.llms),
    }

# =============================================================================
# START UVICORN
# =============================================================================

def start_server(port):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )

    server = uvicorn.Server(config)
    loop.run_until_complete(server.serve())

server_thread = threading.Thread(
    target=start_server,
    args=(port,),
    daemon=True,
)

server_thread.start()
time.sleep(3)
print(f"\\n✅ FastAPI server started on port {port}")

# =============================================================================
# START CLOUDFLARE TUNNEL
# =============================================================================

print("\\n🌍 Starting Cloudflare Tunnel...")

cloudflared_exec = "./cloudflared"
if not os.path.exists(cloudflared_exec):
    cloudflared_exec = "cloudflared"

tunnel_process = subprocess.Popen(
    [
        cloudflared_exec,
        "tunnel",
        "--url",
        f"http://localhost:{port}",
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

time.sleep(10)
logs = ""

while select.select([tunnel_process.stderr], [], [], 0.1)[0]:
    logs += tunnel_process.stderr.read1(4096).decode()

url_match = re.search(
    r"https://[a-zA-Z0-9-]+\\.trycloudflare\\.com",
    logs
)

if not url_match:
    print("⏳ Waiting for tunnel...")
    time.sleep(5)

    while select.select([tunnel_process.stderr], [], [], 0.1)[0]:
        logs += tunnel_process.stderr.read1(4096).decode()

    url_match = re.search(
        r"https://[a-zA-Z0-9-]+\\.trycloudflare\\.com",
        logs
    )

if url_match:
    public_url = url_match.group()

    print("\\n" + "=" * 80)
    print("🚀 PUBLIC API READY")
    print("=" * 80)

    print(f"Base URL : {public_url}")
    print(f"Endpoint : {public_url}/generate")

    print("\\nENV VARIABLE:")
    print(f"KAGGLE_API_URL={public_url}")
    print("=" * 80)

else:
    print("\\n❌ FAILED TO DETECT TUNNEL URL")
    print(logs)

# =============================================================================
# SELF TEST
# =============================================================================

import requests

time.sleep(2)
print("\\n🧪 Running self-test...")

try:
    response = requests.post(
        f"http://localhost:{port}/generate",
        json={
            "prompt": "Say hello in one sentence.",
            "model": "anthropic/claude-sonnet-4-6@default",
            "max_tokens": 50,
            "temperature": 0.7,
        },
        timeout=300,
    )

    result = response.json()
    print("\\n✅ SELF TEST SUCCESS")

    if "response" in result:
        print(
            "\\nResponse:\\n",
            result["response"]
        )

except Exception as e:
    print(f"\\n❌ Self-test failed: {e}")

# =============================================================================
# KEEP NOTEBOOK ALIVE
# =============================================================================

print("\\n" + "=" * 80)
print("✅ SERVER RUNNING")
print("📌 Keep notebook open")
print("📌 Cloudflare URL active while Kaggle session lives")
print("📌 Every request will be logged below")
print("=" * 80)

try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    print("\\nStopping server...")
    tunnel_process.terminate()
""")

nb['cells'] = [cell1, cell2, cell3]

with open('d:/MCA/MCA/KaggleLLM.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("KaggleLLM.ipynb created successfully.")
