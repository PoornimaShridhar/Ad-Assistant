from typing import Dict, Iterator
import re
from app.models.llm import load_model

TARGET_CPL = 20.0


def fallback_explanation(rec: Dict = None) -> str:
    return "This recommendation was generated from campaign performance metrics."


def sanitize_explanation(text: str, rec: Dict = None) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()

    if not cleaned or len(cleaned) < 10:
        return fallback_explanation(rec)

    return cleaned

def generate_explanation(prompt: str, rec: Dict = None, stream: bool = False):
    print("🔥 LLM CALLED")

    llm = load_model()

    try:

        response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": "You are an expert marketing analyst for Google Ads.You MUST NOT output reasoning, thinking, or tags like <think>.You MUST ONLY output final answer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,)
        raw = response["choices"][0]["message"]["content"]

        clean = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)
        clean = re.sub(r"(?s).*?Reasoning:.*?\n", "", clean)
        clean = re.sub(r"(?s).*?Step \d+.*?\n", "", clean)

        print(clean)
        return clean

    except Exception as e:
        print("❌ LLM ERROR:", e)
        return fallback_explanation(rec)