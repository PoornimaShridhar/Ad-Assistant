from typing import Dict, Iterator
import re
from app.models.llm import load_model

TARGET_CPL = 20.0

def build_prompt(rec: Dict) -> str:
    return f"""
    You are a Google Ads performance analyst.

    You are a deterministic business text generator. You do NOT explain instructions. You do NOT describe what you are doing. 
    You ONLY output the final advertisement recommendation in 2–3 sentences.

    Do NOT include:
    - reasoning steps
    - thinking process
    - tags like <think>
    - meta commentary

    Campaign ID: {rec.get("campaign_id")}
    Type: {rec.get("type")}
    Action: {rec.get("action")}
    Reason: {rec.get("reason")}
    CPL: {rec.get("cpl", "N/A")}
    Target CPL: {rec.get("target_cpl", TARGET_CPL)}
    CTR: {rec.get("ctr", "N/A")}

    Output only the final explanation.
    """

def fallback_explanation(rec: Dict) -> str:
    """
    Used when the local model fails.
    """
    action = rec.get("action", "")
    if action == "reduce_budget":
        return (
            "This campaign is generating leads at a higher cost than the target. "
            "Reducing budget allocation may help improve overall efficiency."
        )
    if action == "increase_budget":
        return (
            "This campaign is performing efficiently and generating leads below the target cost. "
            "Increasing budget may help scale results."
        )
    if action == "review_ad_copy":
        return (
            "The click-through rate is below expectations. "
            "Reviewing ad copy and keyword targeting may improve engagement."
        )
    return (
        "This recommendation was generated from campaign performance metrics."
    )

def sanitize_explanation(text: str, rec: Dict) -> str:
    """
    Strip prompt echoes and boilerplate so the UI only shows the actual explanation.
    """
    cleaned = re.sub(r"\s+", " ", text).strip()
    boilerplate_patterns = [
        r"^first,? i need to.*$",
        r"^i must not.*$",
        r"^i should not.*$",
        r"^i will.*$",
        r"^final answer:?\s*",
        r"^i can\'t.*$",
    ]

    for pattern in boilerplate_patterns:
        if re.match(pattern, cleaned, flags=re.IGNORECASE):
            print("Using fallback explanation")
            return fallback_explanation(rec)

    prompt_echo_markers = [
        "campaign id:",
        "recommendation type:",
        "action:",
        "reason:",
        "cpl:",
        "target cpl:",
        "ctr:",
    ]

    marker_hits = sum(marker in cleaned.lower() for marker in prompt_echo_markers)
    if marker_hits >= 2:
        return fallback_explanation(rec)

    cleaned = cleaned.replace("<think>", "").replace("</think>", "").strip()

    if cleaned.lower().startswith("final answer:"):
        cleaned = cleaned.split(":", 1)[-1].strip()
    if not cleaned:
        return fallback_explanation(rec)
    if len(cleaned) < 20:
        return fallback_explanation(rec)
    return cleaned

def _build_messages(rec: Dict) -> list[dict[str, str]]:
    prompt = build_prompt(rec)
    return [
        {
            "role": "system",
            "content": (
                "You are a Google Ads expert. Write concise, natural explanations in plain prose."
            ),
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

def _stream_explanation(rec: Dict) -> Iterator[str]:
    print("🔥 STREAM MODE ENTERED")
    llm = load_model()
    messages = _build_messages(rec)
    try:
        response = llm.create_chat_completion(
            messages=messages,
            max_tokens=512,
            temperature=0.1,
            stop=["</think>"],
            stream=True,
        )
        full_text = ""
        for chunk in response:
            delta = chunk["choices"][0]["delta"].get("content", "")
            if not delta:
                continue
            full_text += delta
            if "</think>" in full_text:
                final = full_text.split("</think>")[-1]
                yield sanitize_explanation(final, rec)

    except Exception as e:
        print(f"LLM generation failed: {e}")
        yield fallback_explanation(rec)

def generate_explanation(rec: Dict, stream: bool = False):
    """
    Generate a natural-language explanation for a recommendation.
    """
    print("🔥 LLM CALLED")
    
    if stream:
        return _stream_explanation(rec)
    llm = load_model()
    print("MODEL:", llm)
    messages = _build_messages(rec)
    try:
        response = llm.create_chat_completion(
            messages=messages,
            max_tokens=512,
            temperature=0.1,
            stop=["</think>"],
            stream=False,
        )
        explanation = response["choices"][0]["message"]["content"].strip()
        return sanitize_explanation(explanation, rec)
        # print("🔥 RAW LLM OUTPUT:", explanation)
        # return explanation

    except Exception as e:
        print("❌ LLM ERROR:", e)
        print(f"LLM generation failed: {e}")
        return fallback_explanation(rec)