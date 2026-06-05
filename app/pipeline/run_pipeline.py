from app.db.repo import SessionLocal
from app.db.models import Campaign, Recommendation
from app.recs.rules import generate_recommendations
from app.recs.generate import generate_explanation

def run_recommendation_pipeline():
    session = SessionLocal()
    try:
        campaigns = session.query(Campaign).all()
        metrics = [
            {
                "campaign_id": c.google_campaign_id,
                "cpl": c.cpl,
                "ctr": c.ctr,
            }
            for c in campaigns
        ]

        # 1. Rule engine
        recs = generate_recommendations(metrics)

        stored_recs = []

        for r in recs:
            print(">>> generating explanation")
            # 2. LLM explanation (MiniCPM)
            explanation = generate_explanation(r)
            print(f">>> Generated explanation for campaign {r['campaign_id']}: {explanation}")
            rec = Recommendation(
                campaign_id=r["campaign_id"],
                recommendation_type=r["type"],
                action=r["action"],
                reason=explanation,
                status="Pending",
            )

            session.add(rec)
            stored_recs.append(rec)
        session.commit()
        return len(stored_recs)

    finally:
        session.close()