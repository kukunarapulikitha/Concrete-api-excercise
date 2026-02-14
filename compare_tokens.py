# compare.py
import os, time, json, requests
from pathlib import Path

BASE_URL = "https://api.concentrate.ai"
API_KEY = os.environ.get("CONCENTRATE_API_KEY")
OUTDIR = Path("results")
OUTDIR.mkdir(exist_ok=True)

if not API_KEY:
    raise RuntimeError("Set CONCENTRATE_API_KEY env var first")

def call_concentrate(model: str, prompt: str, temperature: float, max_output_tokens=300, try_id=0):
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
        "max_output_tokens": max_output_tokens,
    }
    t0 = time.time()
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    latency_ms = int((time.time() - t0) * 1000)
    try:
        data = r.json()
    except Exception:
        data = {"raw_text": r.text}
    return r.status_code, latency_ms, data

def extract_text(resp_json: dict) -> str:
    try:
        return resp_json["output"][0]["content"][0]["text"]
    except Exception:
        return json.dumps(resp_json, indent=2)

def format_adherence_score(text: str) -> int:
    # simple heuristic: presence of required sections
    score = 0
    for token in ["1)", "2)", "3)", "insight", "risk", "action", "next action"]:
        if token in text.lower():
            score += 1
    # normalize 0-100
    return min(100, int((score / 7) * 100))

def run_experiments():
    prompt = (
    "Respond ONLY in valid JSON with this exact schema. "
    "Do not include any explanation or markdown.\n\n"
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
        ("openai/gpt-5.2", 0.2),
        ("openai/gpt-5.2", 0.8),
        ("anthropic/claude-opus-4-5", 0.2),
        ("anthropic/claude-opus-4-5", 0.8),
    ]

    all_results = []
    for i, (model, temp) in enumerate(runs, start=1):
        status, latency_ms, data = call_concentrate(model, prompt, temp)
        text = extract_text(data) if status == 200 else json.dumps(data)
        usage = data.get("usage", {})
        adherence = format_adherence_score(text)
        result = {
            "run": i,
            "model": model,
            "temperature": temp,
            "status": status,
            "latency_ms": latency_ms,
            "adherence": adherence,
            "text": text,
            "usage": usage,
            "raw": data,
            "timestamp": int(time.time())
        }
        all_results.append(result)
        # save per-run file
        fname = OUTDIR / f"run_{i}_{model.replace('/', '_')}_t{int(temp*10)}.json"
        with open(fname, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Saved {fname} | status={status} | latency={latency_ms}ms | adherence={adherence}")

    # summary file
    with open(OUTDIR / "summary.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print("All runs complete. Results in results/")

if __name__ == "__main__":
    run_experiments()
