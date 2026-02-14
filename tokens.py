# compare.py

import os
import time
import json
import requests
from pathlib import Path

# -----------------------
# CONFIG
# -----------------------

BASE_URL = "https://api.concentrate.ai"
API_KEY = os.environ.get("CONCENTRATE_API_KEY")

if not API_KEY:
    raise RuntimeError("Set CONCENTRATE_API_KEY environment variable first.")

OUTDIR = Path("results")
OUTDIR.mkdir(exist_ok=True)

# -----------------------
# API CALL
# -----------------------

def call_concentrate(model: str, prompt: str, temperature: float, max_output_tokens: int):
    url = f"{BASE_URL}/v1/responses"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "accept": "application/json",
    }

    payload = {
        "model": model,
        "input": prompt,
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,  # now correctly passed
    }

    start = time.time()
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    latency_ms = int((time.time() - start) * 1000)

    try:
        data = response.json()
    except Exception:
        data = {"raw_text": response.text}

    return response.status_code, latency_ms, data


# -----------------------
# RETRY WRAPPER (FIXED)
# -----------------------

def call_with_retries(model, prompt, temperature, max_output_tokens, attempts=2):
    for attempt in range(1, attempts + 1):
        status, latency_ms, data = call_concentrate(
            model, prompt, temperature, max_output_tokens
        )
        if status == 200:
            return status, latency_ms, data
        print(f"Attempt {attempt} failed (status={status}). Retrying...")
        time.sleep(2)
    return status, latency_ms, data


# -----------------------
# RESPONSE PARSING
# -----------------------

def extract_text(resp_json: dict) -> str:
    try:
        return resp_json["output"][0]["content"][0]["text"]
    except Exception:
        return json.dumps(resp_json, indent=2)


# -----------------------
# JSON VALIDATION
# -----------------------

def json_validity_check(text: str):
    try:
        parsed = json.loads(text)
        required_keys = {"insights", "risk", "next_action"}

        if not required_keys.issubset(parsed.keys()):
            return False

        if not isinstance(parsed["insights"], list):
            return False

        if len(parsed["insights"]) != 3:
            return False

        return True
    except Exception:
        return False


# -----------------------
# MAIN EXPERIMENT
# -----------------------

def run_experiment():

    prompt = (
        "Respond ONLY in valid JSON with this exact schema. "
        "Do not include explanation, markdown, or code fences.\n\n"
        "{\n"
        '  "insights": ["", "", ""],\n'
        '  "risk": "",\n'
        '  "next_action": ""\n'
        "}\n\n"
        "Text:\n"
        "Revenue grew 18% YoY, but churn increased from 3.1% to 4.0%. "
        "Support tickets rose 25% after a pricing change. "
        "New enterprise deals improved ARPA."
    )

    runs = [
        ("openai/gpt-5.2", 0.2, 120),
        ("openai/gpt-5.2", 0.2, 800),
        ("anthropic/claude-opus-4-5", 0.2, 120),
        ("anthropic/claude-opus-4-5", 0.2, 800),
    ]

    summary_results = []

    for i, (model, temp, max_tokens) in enumerate(runs, start=1):

        print(f"\nRunning: {model} | temp={temp} | max_tokens={max_tokens}")

        status, latency_ms, data = call_with_retries(
            model, prompt, temp, max_tokens
        )

        if status != 200:
            print("ERROR:", data)
            continue

        text = extract_text(data)
        usage = data.get("usage", {})
        json_valid = json_validity_check(text)

        result = {
            "run": i,
            "model": model,
            "temperature": temp,
            "max_output_tokens": max_tokens,
            "status": status,
            "latency_ms": latency_ms,
            "json_valid": json_valid,
            "usage": usage,
            "text": text,
            "timestamp": int(time.time())
        }

        filename = OUTDIR / f"run_{i}_{model.replace('/', '_')}_t{int(temp*10)}_m{max_tokens}.json"
        with open(filename, "w") as f:
            json.dump(result, f, indent=2)

        summary_results.append(result)

        print(f"Saved → {filename}")
        print(f"Latency: {latency_ms} ms")
        print(f"Output tokens: {usage.get('output_tokens')}")
        print(f"JSON Valid: {json_valid}")

    with open(OUTDIR / "summary_3.json", "w") as f:
        json.dump(summary_results, f, indent=2)

    print("\nAll runs complete. Results saved in /results folder.")


if __name__ == "__main__":
    run_experiment()
