import gradio as gr
import pandas as pd

from app.db.repo import (
    get_recommendations,
    approve_recommendation,
    reject_recommendation,
)

def load_recommendations():
    recommendations = get_recommendations()
    data = []
    for recommendation in recommendations:
        campaign_name = ""
        if recommendation.campaign:
            campaign_name = recommendation.campaign.name
        data.append(
            {
                "ID": recommendation.id,
                "Campaign": campaign_name,
                "Recommendation": recommendation.action,
                "Status": recommendation.status,
            }
        )
    return pd.DataFrame(data)


def approve_action(rec_id):
    approve_recommendation(int(rec_id))
    return (
        "Recommendation approved",
        load_recommendations(),
    )

def reject_action(rec_id):
    reject_recommendation(int(rec_id))
    return (
        "Recommendation rejected",
        load_recommendations(),
    )

def build_recommendations_page():
    gr.Markdown("## Recommendations")
    recommendation_table = gr.Dataframe(
        label="Recommendations",
        interactive=False,
    )
    recommendation_id = gr.Number(
        label="Recommendation ID"
    )
    status_message = gr.Textbox(
        label="Status"
    )
    with gr.Row():
        approve_btn = gr.Button("Approve")
        reject_btn = gr.Button("Reject")
    refresh_btn = gr.Button("Refresh")
    refresh_btn.click(
        fn=load_recommendations,
        outputs=recommendation_table,
    )
    approve_btn.click(
        fn=approve_action,
        inputs=recommendation_id,
        outputs=[
            status_message,
            recommendation_table,
        ],
    )
    reject_btn.click(
        fn=reject_action,
        inputs=recommendation_id,
        outputs=[
            status_message,
            recommendation_table,
        ],
    )