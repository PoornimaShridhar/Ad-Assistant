import pandas as pd
from typing import Dict

from app.recs.generate import generate_explanation

TARGET_CPL = 20.0

# -------------------------
# 1. DATA BUILDERS
# -------------------------

def build_campaign_snapshot(dfs: dict) -> dict:
    df = dfs["campaigns"]

    total_spend = df["cost"].sum()
    total_clicks = df["clicks"].sum()
    total_impr = df["impressions"].sum()
    total_leads = df["conversions"].sum()

    ctr = (total_clicks / total_impr * 100) if total_impr else 0
    cpl = (total_spend / total_leads) if total_leads else 0

    return {
        "spend": round(total_spend, 2),
        "clicks": int(total_clicks),
        "impressions": int(total_impr),
        "leads": int(total_leads),
        "ctr": round(ctr, 2),
        "cpl": round(cpl, 2),
    }


def build_simple_trend(df_hourly: pd.DataFrame) -> dict:
    df = df_hourly.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    mid = len(df) // 2
    first, second = df.iloc[:mid], df.iloc[mid:]

    def agg(x):
        return {
            "cost": x["cost"].sum(),
            "clicks": x["clicks"].sum(),
            "impressions": x["impressions"].sum(),
        }

    a, b = agg(first), agg(second)

    def pct(old, new):
        return ((new - old) / old * 100) if old else 0

    return {
        "spend_change_pct": round(pct(a["cost"], b["cost"]), 1),
        "clicks_change_pct": round(pct(a["clicks"], b["clicks"]), 1),
        "impressions_change_pct": round(pct(a["impressions"], b["impressions"]), 1),
    }


def build_top_drivers(dfs: dict) -> dict:
    kw = dfs["keywords"].copy()

    kw["cpl"] = kw["cost"] / kw["conversions"].replace(0, 1)

    worst = kw.sort_values("cpl", ascending=False).head(3)
    best = kw.sort_values("cpl", ascending=True).head(3)

    return {
        "best_keywords": best[["keyword", "cpl", "conversions"]].to_dict("records"),
        "worst_keywords": worst[["keyword", "cpl", "conversions"]].to_dict("records"),
    }


def build_signals(dfs: dict) -> dict:
    kw = dfs["keywords"].copy()

    kw["ctr"] = kw["clicks"] / kw["impressions"].replace(0, 1)

    return {
        "low_ctr_ratio": round((kw["ctr"] < 0.02).mean(), 2),
        "wasted_spend_ratio": round((kw["conversions"] == 0).mean(), 2),
    }


# -------------------------
# 2. CONTEXT BUILDER
# -------------------------

def build_ads_analyst_context(dfs: dict) -> dict:
    return {
        "campaign": build_campaign_snapshot(dfs),
        "trend": build_simple_trend(dfs["hourly"]),
        "top_drivers": build_top_drivers(dfs),
        "signals": build_signals(dfs),
    }


# -------------------------
# 3. PROMPT BUILDER
# -------------------------

def build_ads_analyst_prompt(context: dict) -> str:
    return f"""
You are an Ads performance analyst.

Return ONLY 3–5 insights.
No reasoning. No explanation of steps.

Campaign:
{context["campaign"]}

Trend:
{context["trend"]}

Top drivers:
{context["top_drivers"]}

Signals:
{context["signals"]}

Format:
- short bullet points only
- Simple language, no jargon
- Focus on actionable insights
"""


# -------------------------
# 4. MAIN ORCHESTRATOR (THIS IS WHAT MAIN.PY CALLS)
# -------------------------

def run_ads_analyst_card(dfs: dict) -> str:
    context = build_ads_analyst_context(dfs)
    prompt = build_ads_analyst_prompt(context)

    print("\n========== PROMPT ==========")
    print(prompt)

    result = generate_explanation(prompt)

    print("\n========== LLM OUTPUT ==========")
    print(result)

    return result