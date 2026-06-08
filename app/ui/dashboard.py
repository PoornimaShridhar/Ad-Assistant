import gradio as gr
import pandas as pd
from app.controller.session_loader import load_google_ads_data

# DATA LOADER
# -------------------------
def load_dashboard():
    dfs = load_google_ads_data()
    df = dfs["campaigns"].copy()

    if df.empty:
        return (
            0, 0, 0, 0,
            pd.DataFrame(columns=[
                "Campaign", "Spend", "Leads", "CPL", "CTR"
            ])
        )

    # derive missing fields safely
    df["leads"] = df["conversions"] if "conversions" in df.columns else 0
    df["cpl"] = df["cost"] / df["leads"].replace(0, 1)
    df["ctr"] = df["ctr"]

    formatted = pd.DataFrame({
        "Campaign": df["name"],
        "Spend": df["cost"],
        "Leads": df["leads"],
        "CPL": df["cpl"],
        "CTR": df["ctr"],
    })

    return (
        round(formatted["Spend"].sum(), 2),
        int(formatted["Leads"].sum()),
        round(formatted["CPL"].mean(), 2),
        len(formatted),
        formatted
    )

# UI BUILDER
# -------------------------
def build_dashboard():
    gr.Markdown("## Campaign Dashboard")

    with gr.Row():
        total_spend = gr.Number(label="Total Spend")
        total_leads = gr.Number(label="Total Leads")
        average_cpl = gr.Number(label="Average CPL")
        active_campaigns = gr.Number(label="Active Campaigns")

    campaign_table = gr.Dataframe(
        label="Campaign Performance",
        interactive=True   # IMPORTANT: needed for row click
    )

    refresh_btn = gr.Button("Refresh Dashboard")
    refresh_btn.click(
        fn=load_dashboard,
        outputs=[
            total_spend,
            total_leads,
            average_cpl,
            active_campaigns,
            campaign_table,
        ],
    )

    # ✅ IMPORTANT FIX: return table so main.py can attach .select()
    return campaign_table