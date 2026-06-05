import gradio as gr
import pandas as pd
from app.db.repo import get_campaigns

def load_dashboard():
    campaigns = get_campaigns()
    data = []
    for campaign in campaigns:
        data.append(
            {
                "Campaign": campaign.name,
                "Spend": campaign.spend,
                "Leads": campaign.leads,
                "CPL": campaign.cpl,
                "CTR": campaign.ctr,
            }
        )

    df = pd.DataFrame(data)

    if len(df) == 0:

        return (
            0,
            0,
            0,
            0,
            pd.DataFrame(
                columns=[
                    "Campaign",
                    "Spend",
                    "Leads",
                    "CPL",
                    "CTR",
                ]
            ),
        )

    total_spend = df["Spend"].sum()
    total_leads = df["Leads"].sum()
    average_cpl = df["CPL"].mean()
    active_campaigns = len(df)

    return (
        round(total_spend, 2),
        int(total_leads),
        round(average_cpl, 2),
        active_campaigns,
        df,
    )

def build_dashboard():
    gr.Markdown("## Campaign Dashboard")
    with gr.Row():
        total_spend = gr.Number(label="Total Spend")
        total_leads = gr.Number(label="Total Leads")
        average_cpl = gr.Number(label="Average CPL")
        active_campaigns = gr.Number(label="Active Campaigns")

    campaign_table = gr.Dataframe(
        label="Campaign Performance",
        interactive=False,
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