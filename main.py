import gradio as gr
import pandas as pd
from app.db.repo import init_db
from app.recs.generate import generate_explanation
from app.ui.dashboard import load_dashboard, build_dashboard

from dotenv import load_dotenv
load_dotenv()

init_db()

# STREAM WRAPPER (UNCHANGED LOGIC, JUST CLEAN)
# def stream_to_gradio(rec):
#     print("🔥 STREAM FUNCTION CALLED")
#     full_text = ""
#     for chunk in generate_explanation(rec, stream=True):
#         full_text = chunk
#         print("CHUNK:", chunk)

#     final_text = full_text.replace("<think>", "").strip()
#     if not final_text:
#         final_text = "No explanation was generated."
#     yield final_text

def get_latest_rec():
    from app.db.repo import SessionLocal
    from app.db.models import Recommendation

    session = SessionLocal()
    rec = session.query(Recommendation).order_by(Recommendation.id.desc()).first()

    if not rec:
        return {}

    return {
        "campaign_id": rec.campaign_id,
        "type": rec.recommendation_type,
        "action": rec.action,
        "reason": rec.reason,
        "status": rec.status,
    }

# LOAD RECOMMENDATIONS
def load_recs():
    from app.db.repo import SessionLocal
    from app.db.models import Recommendation

    session = SessionLocal()
    recs = session.query(Recommendation).all()

    # return [[r.campaign_id, r.action, r.status] for r in recs]
    df = pd.DataFrame([
        {
            "Campaign ID": r.campaign_id,
            "Recommendation": r.recommendation_type,
            "Action": r.action,
            "Reason": r.reason,
            "Status": r.status,
        }
        for r in recs
    ])

    return df

# GRADIO APP
with gr.Blocks(title="Ads Assistant") as demo:

    gr.Markdown("# Preschool Ads Dashboard")

    # DASHBOARD TAB
    with gr.Tab("Campaign Dashboard"):
        build_dashboard()

    # RECOMMENDATIONS TAB
    with gr.Tab("Recommendations"):

        rec_table = gr.Dataframe(label="Recommendations", interactive=False)

        btn2 = gr.Button("Load Recommendations")

        btn2.click(
            fn=load_recs,
            outputs=rec_table
        )

    # MINI CPM STREAMING TAB
    with gr.Tab("AI Explanation (MiniCPM)"):

        out = gr.Textbox(lines=10)

        rec_state = gr.State({
            "campaign_id": "Test Campaign",
            "type": "high_cpl",
            "action": "reduce_budget",
            "reason": "CPL too high",
            "cpl": 42,
            "target_cpl": 20,
            "ctr": 1.2,
        })

        btn3 = gr.Button("Run Explanation")

        btn3.click(
            fn=lambda rec: generate_explanation(get_latest_rec(), stream=False),
            inputs=None,   # ✅ FIXED (THIS WAS WRONG)
            outputs=out,
            show_progress=True
        )

demo.launch()