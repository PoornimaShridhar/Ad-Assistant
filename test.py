from app.recs.generate import generate_explanation

rec = {
    "campaign_id": "Test",
    "type": "high_cpl",
    "action": "reduce_budget",
    "reason": "CPL too high",
    "cpl": 42,
    "target_cpl": 20,
    "ctr": 1.2,
}

# for x in generate_explanation(rec, stream=True):
#     print(x)

gen = generate_explanation(rec, stream=True)

for i, chunk in enumerate(gen):
    print(f"[{i}]", chunk)