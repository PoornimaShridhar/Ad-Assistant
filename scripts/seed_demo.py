import sys
from pathlib import Path

# ✅ FIX: ensure project root is first in path BEFORE imports
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import random
from datetime import datetime

from app.db.repo import init_db, SessionLocal
from app.db.models import Campaign, Recommendation
from app.recs.rules import generate_recommendations


CAMPAIGN_NAMES = [
    "Preschool Search",
    "Brand Awareness",
    "Local Leads",
    "Early Education Ads",
    "Enrollment Push"
]


# -------------------------
# Campaign generation
# -------------------------
def generate_campaigns(session):
    campaigns = []

    for i, name in enumerate(CAMPAIGN_NAMES):
        campaign = Campaign(
            google_campaign_id=f"gc_{1000+i}",
            name=name,
            budget=random.randint(50, 200),
            spend=0,
            clicks=0,
            impressions=0,
            ctr=0.0,
            leads=0,
            cpl=0.0,
            last_synced=datetime.utcnow()
        )
        session.add(campaign)
        campaigns.append(campaign)

    session.commit()
    return campaigns


# -------------------------
# Metrics simulation
# -------------------------
def simulate_metrics(session, campaigns):
    for campaign in campaigns:
        spend = 0
        clicks = 0
        impressions = 0
        leads = 0

        for _ in range(30):
            daily_impressions = random.randint(50, 500)
            daily_clicks = int(daily_impressions * random.uniform(0.01, 0.1))
            daily_spend = daily_clicks * random.uniform(0.5, 3.0)
            daily_leads = int(daily_clicks * random.uniform(0.05, 0.3))

            impressions += daily_impressions
            clicks += daily_clicks
            spend += daily_spend
            leads += daily_leads

        ctr = clicks / impressions if impressions else 0
        cpl = spend / leads if leads else 0

        campaign.spend = round(spend, 2)
        campaign.clicks = clicks
        campaign.impressions = impressions
        campaign.leads = leads
        campaign.ctr = round(ctr, 4)
        campaign.cpl = round(cpl, 2)
        campaign.last_synced = datetime.utcnow()

    session.commit()


# -------------------------
# Recommendations via rule engine
# -------------------------
def seed_recommendations(session, campaigns):
    # ✅ prevent duplicate entries on re-run
    session.query(Recommendation).delete()
    session.commit()

    metrics = [
        {
            "campaign_id": c.id,
            "cpl": c.cpl,
            "ctr": c.ctr,
        }
        for c in campaigns
    ]

    recs = generate_recommendations(metrics)

    for r in recs:
        session.add(Recommendation(
            campaign_id=r["campaign_id"],
            recommendation_type=r["type"],
            action=r["action"],
            reason=r["reason"],
            status="Pending",
            created_at=datetime.utcnow()
        ))

    session.commit()


# -------------------------
# Main pipeline
# -------------------------
def main():
    print("Initializing DB...")
    init_db()

    session = SessionLocal()

    try:
        print("Seeding campaigns...")
        campaigns = generate_campaigns(session)

        print("Simulating metrics...")
        simulate_metrics(session, campaigns)

        print("Generating recommendations...")
        seed_recommendations(session, campaigns)

        print("✅ Demo database seeded successfully!")

    finally:
        session.close()


if __name__ == "__main__":
    main()