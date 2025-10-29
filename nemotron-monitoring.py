#!/usr/bin/env python3
"""
nemotron_stream_reasoner.py
Quick Nemotron streaming example that fetches local FastAPI metrics and:
  1) Streams observation-only reasoning (optional demo),
  2) Produces structured JSON observations (no root cause),
  3) Sends that JSON to the Diagnostic Agent API.

For hackathon demo only — do not commit your API key.
"""

import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv

# ──────────────────────────────────────────────────────────────
# 1️⃣  Environment setup
# ──────────────────────────────────────────────────────────────
load_dotenv()

API_KEY = "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" # ⚠️ Hard-code for hackathon speed only
NIM_API_BASE = "https://integrate.api.nvidia.com/v1"
METRICS_URL = "http://localhost:8000/metrics"
DIAGNOSTIC_URL = "http://localhost:8010/diagnose"

if not API_KEY:
    raise RuntimeError("API_KEY is missing — insert your key above or set NVIDIA_API_KEY env var.")

client = OpenAI(base_url=NIM_API_BASE, api_key=API_KEY)

# ──────────────────────────────────────────────────────────────
# 2️⃣  Helpers
# ──────────────────────────────────────────────────────────────
def get_network_metrics():
    """Fetch metrics from your FastAPI /metrics endpoint."""
    try:
        r = requests.get(METRICS_URL, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": "failed_to_fetch_metrics", "exception": str(e)}

def build_messages(metrics):
    """Messages for streaming demo — observation-only."""
    system = {
        "role": "system",
        "content": (
            "You are a network monitoring assistant. Describe current network conditions "
            "based only on numeric metrics. Identify anomalies but DO NOT infer causes. "
            "Keep it concise and factual for a technical log."
        )
    }
    user = {
        "role": "user",
        "content": "Here are the current network metrics:\n\n" + json.dumps(metrics, indent=2)
    }
    return [system, user]

# ──────────────────────────────────────────────────────────────
# 3️⃣  Streaming demo (optional)
# ──────────────────────────────────────────────────────────────
def stream_reasoning(metrics):
    """Stream an observation-only narration (no root cause)."""
    messages = build_messages(metrics)

    completion = client.chat.completions.create(
        model="nvidia/nvidia-nemotron-nano-9b-v2",
        messages=messages,
        temperature=0.6,
        top_p=0.95,
        max_tokens=1024,
        stream=True,
        extra_body={
            "min_thinking_tokens": 256,  # keep small for demo speed
            "max_thinking_tokens": 768
        }
    )

    try:
        for chunk in completion:
            delta = chunk.choices[0].delta
            reasoning = getattr(delta, "reasoning_content", None)
            if reasoning:
                print(reasoning, end="", flush=True)
            content = getattr(delta, "content", None)
            if content is not None:
                print(content, end="", flush=True)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as e:
        print(f"\nError during streaming: {e}")

# ──────────────────────────────────────────────────────────────
# 4️⃣  JSON observation (for agent handoff)
# ──────────────────────────────────────────────────────────────
def get_reasoning_json(metrics):
    """
    Create structured descriptive reasoning (no root cause) for handoff to Diagnostic Agent.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are a network monitoring assistant. "
                "Describe current network conditions based only on provided metrics. "
                "Identify anomalies or irregularities but DO NOT explain why they happen. "
                "Respond ONLY with a valid JSON object using this structure:\n"
                "{\n"
                "  'observation_summary': str,\n"
                "  'metrics': { key: value },\n"
                "  'anomaly_flags': list[str],\n"
                "  'confidence_score': float,\n"
                "  'recommended_next_agent': 'DiagnosticAgent'\n"
                "}\n"
                "Be factual and concise."
            )
        },
        {
            "role": "user",
            "content": "Analyze and summarize these metrics:\n\n" + json.dumps(metrics, indent=2)
        }
    ]

    completion = client.chat.completions.create(
        model="nvidia/nvidia-nemotron-nano-9b-v2",
        messages=messages,
        temperature=0.3,
        top_p=0.9,
        max_tokens=1024,
    )

    response_text = completion.choices[0].message.content

    try:
        reasoning_json = json.loads(response_text)
    except json.JSONDecodeError:
        reasoning_json = {"raw_output": response_text, "parse_error": True}

    return reasoning_json

def send_to_diagnostic_agent(monitoring_output):
    """POST MonitoringAgent JSON to the Diagnostic Agent service."""
    try:
        headers = {"Content-Type": "application/json"}
        resp = requests.post(DIAGNOSTIC_URL, headers=headers, data=json.dumps(monitoring_output), timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"⚠️ Failed to send data to Diagnostic Agent: {e}")
        return {"error": "diagnostic_agent_unreachable", "exception": str(e)}

# ──────────────────────────────────────────────────────────────
# 5️⃣  Entrypoint
# ──────────────────────────────────────────────────────────────
def main():
    metrics = get_network_metrics()
    print("=== Metrics ===")
    print(json.dumps(metrics, indent=2))

    # (Optional) Stream a human-readable observation
    # print("\n=== Streaming Observation (optional) ===\n")
    # stream_reasoning(metrics)
    # print("\n")

    print("=== MonitoringAgent JSON (observation-only) ===")
    observation = get_reasoning_json(metrics)
    print(json.dumps(observation, indent=2))

    # 🚀 Handoff to Diagnostic Agent (THIS WAS WRONG BEFORE)
    diagnostic_output = send_to_diagnostic_agent(observation)
    print("\n=== DiagnosticAgent Response ===")
    print(json.dumps(diagnostic_output, indent=2))

    print("\n=== Done ===")

if __name__ == "__main__":
    main()