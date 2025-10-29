#!/usr/bin/env python3
"""
diagnostic-agent.py
------------------------------------------------------------
Runs as a FastAPI microservice on its own port (default: 8010).
Listens for POSTs from the Monitoring Agent and performs
root-cause reasoning using NVIDIA Nemotron.
------------------------------------------------------------
"""

import os
import json
from openai import OpenAI
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import uvicorn

# ───────────────────────────────────────────────
# 1️⃣  Setup
# ───────────────────────────────────────────────
load_dotenv()

API_KEY = os.getenv("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")  # Hackathon fallback
NIM_API_BASE = os.getenv("NIM_API_BASE", "https://integrate.api.nvidia.com/v1")

client = OpenAI(base_url=NIM_API_BASE, api_key=API_KEY)

# ───────────────────────────────────────────────
# 2️⃣  Diagnostic Reasoning Function
# ───────────────────────────────────────────────
def diagnostic_agent(monitoring_output):
    """Use Nemotron to infer root cause from MonitoringAgent's observations."""
    system_message = {
        "role": "system",
        "content": (
            "You are a network diagnostic AI. Analyze the anomalies described by the monitoring agent "
            "and infer the most probable root cause. Respond ONLY in JSON format:\n"
            "{\n"
            "  'root_cause': str,\n"
            "  'confidence': float,\n"
            "  'supporting_evidence': list[str],\n"
            "  'recommended_next_agent': 'GuidanceAgent'\n"
            "}\n"
            "Do not restate metrics or hypothesize without evidence."
        ),
    }

    user_message = {
        "role": "user",
        "content": (
            "Here is the monitoring agent's observation report. Identify the most probable root cause:\n\n"
            + json.dumps(monitoring_output, indent=2)
        ),
    }

    try:
        completion = client.chat.completions.create(
            model="nvidia/nvidia-nemotron-nano-9b-v2",
            messages=[system_message, user_message],
            temperature=0.3,
            top_p=0.9,
            max_tokens=1024,
        )

        response_text = completion.choices[0].message.content
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            result = {"raw_output": response_text, "parse_error": True}

        return result

    except Exception as e:
        print(f"❌ Error in diagnostic_agent: {e}")
        return {"error": "nemotron_call_failed", "details": str(e)}

# ───────────────────────────────────────────────
# 3️⃣  FastAPI Setup
# ───────────────────────────────────────────────
app = FastAPI(
    title="Diagnostic Agent API",
    description="Receives MonitoringAgent output and performs root-cause reasoning via Nemotron.",
    version="1.0.0",
)

@app.post("/diagnose")
async def diagnose(request: Request):
    """Endpoint for POSTing MonitoringAgent data."""
    try:
        data = await request.json()
        print("\n📥 Received data from MonitoringAgent:")
        print(json.dumps(data, indent=2))

        result = diagnostic_agent(data)

        print("\n📤 Returning Diagnostic Output:")
        print(json.dumps(result, indent=2))

        return JSONResponse(content=result)

    except Exception as e:
        print(f"❌ Exception in /diagnose: {e}")
        return JSONResponse(
            content={"error": "diagnostic_agent_failed", "details": str(e)},
            status_code=500,
        )

# ───────────────────────────────────────────────
# 4️⃣  Launch Server
# ───────────────────────────────────────────────
if __name__ == "__main__":
    # Choose a different port from Monitoring Agent (ex: 8010)
    port = int(os.getenv("DIAGNOSTIC_PORT", 8010))
    print(f"🚀 Diagnostic Agent running at http://localhost:{port}/diagnose")
    uvicorn.run(app, host="0.0.0.0", port=port)