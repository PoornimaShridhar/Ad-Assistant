from llama_cpp import Llama
import re

print("Script started")

# llm = Llama.from_pretrained(
#     repo_id="mradermacher/MiniCPM4.1-8B-GGUF",
#     filename="MiniCPM4.1-8B.IQ4_XS.gguf",
#     n_ctx=4096,
#     verbose=False
# )

llm = Llama.from_pretrained(
    repo_id="Abiray/MiniCPM5-1B-GGUF",
    filename="minicpm5-1b-Q4_K_M.gguf",
    n_ctx=3048,
    verbose=True
)

prompt = """
You are a senior Google Ads performance analyst.

You must output ONLY 3–5 bullet insights.

STRICT RULES:
- Do NOT include reasoning
- Do NOT include calculations
- Do NOT include step-by-step analysis
- Do NOT use <think> tags
- Do NOT show working or explanations
- Only final insights allowed

Use only the provided data. Do not derive new metrics.

DATA:

Campaign:
- Name: Preschool Search
- Spend: 1200
- Clicks: 300
- Impressions: 15000
- Conversions: 30

Trends:
- Spend increasing steadily over last 10 days
- Clicks increasing steadily
- Impressions increasing slightly faster than clicks

Keywords:
- preschool near me → strong performance (15 conversions, low cost)
- nursery admission → moderate (5 conversions)
- best preschool london → poor (0 conversions, high cost)
- early learning center → good (8 conversions)

Signals:
- CTR: 0.35 (low)
- Wasted spend: 0.25 (high)

Business targets:
- Target CPL: 20
- Current CPL: 40

OUTPUT RULES:
- Exactly 3–5 bullets
- No numbering
- No explanations
- No thinking traces
- Each bullet must be independently useful for decision-making
"""

response = llm.create_chat_completion(
    messages=[
        {"role": "system", "content": "You are an expert marketing analyst for Google Ads."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
)

raw = response["choices"][0]["message"]["content"]

clean = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

print(clean)