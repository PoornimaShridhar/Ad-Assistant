import gradio as gr
import pandas as pd
# from dotenv import load_dotenv
# load_dotenv()

# becoz of deployment on hf space - above 2 lines replaced as below:
import os

from app.db.repo import init_db
from app.ui.dashboard import load_dashboard, build_dashboard
from app.controller.session_loader import load_google_ads_data

from app.ads1.ads_analyst import run_ads_analyst_card
from app.ads1.budget_optimizer import run_budget_optimizer_card


init_db()

# HELPERS
def on_campaign_select(campaign_name):
    dfs = load_google_ads_data()

    filtered = dfs.copy()
    filtered["campaigns"] = dfs["campaigns"][
        dfs["campaigns"]["name"] == campaign_name
    ]
    return filtered

def run_ads_card(state):
    if not state:
        return "⚠️ Please select a campaign from the Dashboard first."
    return run_ads_analyst_card(state["dfs"])

def run_budget_card(state):
    if not state:
        return "⚠️ Please select a campaign from the Dashboard first."
    return run_budget_optimizer_card(state["dfs"])

def campaign_row_selected(evt: gr.SelectData):
    """
    Triggered when user clicks a row in the dashboard table
    """

    df = load_dashboard()[4]  # campaign table returned by load_dashboard()
    campaign_name = df.iloc[evt.index[0]]["Campaign"]
    dfs = on_campaign_select(campaign_name)

    return (
        {
            "campaign_name": campaign_name,
            "dfs": dfs
        },
        f"## 📊 Selected Campaign: {campaign_name}"
    )

# GRADIO APP
with gr.Blocks(title="Ads Assistant") as demo:

    campaign_state = gr.State()
    gr.Markdown("# 🎯 Preschool Ads Dashboard")

    # TAB 1: DASHBOARD
    # -------------------------
    with gr.Tab("Dashboard"):

        campaign_table = build_dashboard()

    # TAB 2: CAMPAIGN ANALYSIS
    # -------------------------
    with gr.Tab("Campaign Analysis"):

        selected_campaign = gr.Markdown(
            "👈 Select a campaign from the Dashboard tab"
        )

        analyst_btn = gr.Button("Run Ads Analysis")
        budget_btn = gr.Button("Run Budget Optimization")

        output = gr.Markdown()

        analyst_btn.click(
            fn=run_ads_card,
            inputs=campaign_state,
            outputs=output
        )

        budget_btn.click(
            fn=run_budget_card,
            inputs=campaign_state,
            outputs=output
        )

    # CONNECT TABLE CLICK → STATE
    # -------------------------
    campaign_table.select(
        fn=campaign_row_selected,
        outputs=[
            campaign_state,
            selected_campaign
        ]
    )

demo.launch()