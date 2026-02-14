# Concentrate API Exercise — Likitha Kukunarapu

## Goal
Compare outputs from two LLM providers (OpenAI & Anthropic) via Concentrate and observe differences in adherence, latency, token usage, temperature.

## What I built
- `compare.py` runs 4 configs, saves JSON results and a summary.
- Basic fallback retry and a simple adherence scoring heuristic.

## Experiments performed
- 1) temperature: 0.2 vs 0.8
- 2) structured JSON output vs free text
- 3) small vs long context
- 4) max_output_tokens: 120 vs 800

## Key findings
- Strict schema enforcement dramatically improves structural reliability
- Output token limits directly affect structural integrity because it truncates the output
- Longer input increases latency and token usage
- Both models handled long context well without hallucination
- Temperature changes wording, not structure (when JSON is enforced) 
   Higher temperature made responses slightly more verbose.
- OpenAI followed exact formatting more strictly in free-text prompts.
  Claude sometimes reformatted headings but kept meaning correct.
  Claude tended to be slightly more concise in longer-context outputs
    
## Conclusion

This exercise helped me understand how model behavior changes across structure, temperature, token limits, and context size.

The biggest takeaway is that strict JSON schema enforcement dramatically improves reliability across providers. When structure is explicitly defined, both OpenAI and Claude consistently return valid, parseable outputs.

However, token limits directly impact system stability. Setting a low max_output_tokens caused both models to truncate responses and produce invalid JSON. This shows that proper token budgeting is critical in production systems that depend on structured outputs.

Longer input contexts increased token usage and latency for both models. OpenAI’s latency increased more noticeably in the long-context test, while Claude remained slightly more concise in output length.

Temperature primarily affected wording and verbosity, not structure, when schema constraints were applied.

## How to run locally
1. export CONCENTRATE_API_KEY=...
2. python compare.py
3. Inspect results/*


## Evaluation Summary:

## Experiment 1:

I compared OpenAI GPT-5.2 and Anthropic Claude Opus 4.5 across temperature 0.2 and 0.8.

# Format adherence

OpenAI followed the exact requested numbered structure consistently (adherence score: 100).

Claude preserved semantic structure but reformatted headings, reducing strict adherence (score: 57).

OpenAI demonstrated stronger compliance with explicit formatting constraints.

# Latency

OpenAI responses ranged from 3.9–5.1 seconds.

Claude responses ranged from 5.5–6.7 seconds.

OpenAI was consistently faster by ~1–2 seconds.

# Token usage

OpenAI outputs averaged ~176 tokens.

Claude outputs averaged ~193 tokens.

Claude was more verbose, resulting in slightly higher token usage.

# Temperature impact

Increasing temperature slightly increased verbosity.

Structural adherence remained stable across temperatures for both models.


## Experiment 2: Strict JSON Schema Enforcement

I compared OpenAI GPT-5.2 and Anthropic Claude Opus 4.5 across temperature 0.2 and 0.8 using a strict JSON-only response constraint.

JSON validity

OpenAI returned valid JSON matching the exact schema across both temperatures (100% success rate).

Claude also returned valid JSON matching the schema across both temperatures (100% success rate).

Unlike the earlier formatting experiment, strict schema instructions significantly improved structural reliability across both providers.

Latency

OpenAI responses ranged from 3.3–4.4 seconds.

Claude responses ranged from 4.4–4.7 seconds.

Performance differences were relatively minor under structured JSON constraints, though OpenAI remained slightly faster on average (~0.7 seconds).

Token usage

OpenAI outputs averaged ~240 total tokens per request.

Claude outputs averaged ~261 total tokens per request.

Claude consistently used ~20 more tokens per request, indicating slightly higher verbosity even under strict structural constraints.

Temperature impact

Increasing temperature did not degrade JSON structure adherence for either provider.

Output wording varied slightly at higher temperature, but schema compliance remained stable.

Strict JSON enforcement reduced formatting variability across providers.

## Experiment 3: max_output_tokens Scaling & Truncation Test

I compared OpenAI GPT-5.2 and Anthropic Claude Opus 4.5 using strict JSON schema enforcement under two output ceilings: max_output_tokens = 120 and max_output_tokens = 800.

Truncation behavior

When max_output_tokens = 120, both OpenAI and Claude hit the exact 120-token limit and truncated mid-response.

As a result, JSON structure was incomplete and schema validation failed (0% validity at 120 tokens).

When max_output_tokens = 800, both providers returned fully completed JSON responses with valid schema (100% validity).

This confirms that the API strictly enforces output token ceilings and that aggressive limits can compromise structured output integrity.

Latency

OpenAI responses decreased from ~3.2 seconds (800 tokens) to ~2.9 seconds (120 tokens).

Claude responses decreased from ~4.4 seconds (800 tokens) to ~3.5 seconds (120 tokens).

Lower token ceilings resulted in faster response times, indicating that latency scales with generation length.

Token usage

At max_output_tokens = 120, both providers generated exactly 120 output tokens and stopped mid-response.

At max_output_tokens = 800, OpenAI generated ~147 output tokens and Claude generated ~149 output tokens, both well below the ceiling.

This shows that the models naturally constrained output length based on schema requirements when sufficient headroom was provided.

Structural reliability impact

Aggressive output ceilings can break structured JSON responses, even when the model understands the required schema.

Structured systems relying on strict JSON parsing must therefore maintain safe output headroom to prevent truncation-related failures.

Conclusion

The truncation experiment demonstrates that while both providers reliably follow strict schema instructions, output token limits directly affect structural completeness and system reliability. Proper token budgeting is essential in production environments where structured outputs must remain parseable and valid.


## **Experiment 4: Long Context Stability Test**

I compared OpenAI GPT-5.2 and Anthropic Claude Opus 4.5 across temperature 0.2 and 0.8 using a longer multi-paragraph input under strict JSON schema enforcement.

---

### **JSON validity**

OpenAI returned valid JSON matching the exact schema across both temperatures (100% success rate).

Claude also returned valid JSON matching the schema across both temperatures (100% success rate).

Increasing input size did not degrade structural reliability for either provider.

---

### **Latency**

OpenAI responses ranged from 5.7–6.0 seconds.

Claude responses ranged from 4.3–4.7 seconds.

Latency increased compared to the short-context experiment, particularly for OpenAI, indicating that response time scales with input token size.

OpenAI latency increased noticeably

Claude increased slightly but less dramatically

This suggests:

OpenAI latency scaled more with input size than Claude in this test.
---

### **Token usage**

OpenAI input tokens increased to ~178 (from ~93 in the short-context test).

Claude input tokens increased to ~207 (from ~107 previously).

OpenAI output tokens ranged from ~202–230.

Claude output tokens ranged from ~159–160.

Total token usage increased substantially for both providers due to the larger input context.

OpenAI is more sensitive to context richness and temperature in output expansion.

Claude appears more concise.

That’s a behavioral difference.

---

### **Temperature impact**

Increasing temperature slightly increased verbosity for OpenAI (202 → 230 output tokens).

Claude output length remained relatively stable across temperatures.

JSON validity and schema adherence were unaffected by temperature changes.

---

### **Hallucination**

Longer context did NOT increase hallucination risk in this structured task.

