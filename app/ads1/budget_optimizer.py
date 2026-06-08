from app.recs.generate import generate_explanation

def build_campaign_summary(dfs: dict) -> dict:
    df = dfs["keywords"]

    total_cost = df["cost"].sum()
    total_conv = df["conversions"].sum()

    avg_cpl = (
        total_cost / total_conv
        if total_conv > 0
        else 0
    )

    return {
        "total_spend": round(total_cost, 2),
        "total_conversions": int(total_conv),
        "avg_cpl": round(avg_cpl, 2),
    }

def build_scale_candidates(dfs: dict):
    kw = dfs["keywords"].copy()

    kw["cpl"] = (
        kw["cost"] /
        kw["conversions"].replace(0, 1)
    )

    account_avg = (
        kw["cost"].sum() /
        max(kw["conversions"].sum(), 1)
    )

    winners = kw[
        (kw["conversions"] > 0)
        & (kw["cpl"] < account_avg * 0.7)
    ]

    winners = winners.sort_values(
        "conversions",
        ascending=False
    )

    return winners.head(3)[[
        "keyword",
        "ad_group_name",
        "cpl",
        "conversions"
    ]].to_dict("records")

def build_cut_candidates(dfs: dict):
    kw = dfs["keywords"].copy()

    kw["cpl"] = (
        kw["cost"] /
        kw["conversions"].replace(0, 1)
    )

    account_avg = (
        kw["cost"].sum() /
        max(kw["conversions"].sum(), 1)
    )

    losers = kw[
        (kw["cost"] > 0)
        & (
            (kw["conversions"] == 0)
            |
            (kw["cpl"] > account_avg * 1.5)
        )
    ]

    losers = losers.sort_values(
        "cost",
        ascending=False
    )

    return losers.head(3)[[
        "keyword",
        "ad_group_name",
        "cost",
        "conversions",
        "cpl"
    ]].to_dict("records")

def build_budget_optimizer_context(dfs: dict):

    summary = build_campaign_summary(dfs)

    return {
        "summary": summary,
        "scale_candidates": build_scale_candidates(dfs),
        "cut_candidates": build_cut_candidates(dfs),
    }

def build_budget_optimizer_prompt(context):

    return f"""
You are a Google Ads budget optimization expert.

Your goal is to identify where budget should be increased and where it should be reduced.

Campaign Summary:
{context["summary"]}

Best Opportunities To Scale:
{context["scale_candidates"]}

Worst Budget Drains:
{context["cut_candidates"]}

Rules:
- Return exactly 3 to 5 bullet points.
- Use simple business language.
- Mention where budget should increase.
- Mention where budget should decrease.
- Focus on efficiency and lead generation.
- No reasoning process.
"""

def run_budget_optimizer_card(dfs):

    context = build_budget_optimizer_context(dfs)

    prompt = build_budget_optimizer_prompt(context)

    rec = {
        "campaign_id": "BUDGET_OPTIMIZER",
        "type": "budget_optimization",
        "action": "reallocate_budget",
        "reason": prompt,
    }

    return generate_explanation(rec)