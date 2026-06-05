import pytest
from unittest.mock import patch

from app.recs.rules import generate_recommendations
from app.recs.generate import generate_explanation
from app.db.repo import init_db, SessionLocal
from app.db.models import Campaign, Recommendation


# -------------------------
# DB fixture
# -------------------------
@pytest.fixture
def session():
    init_db()
    db = SessionLocal()
    yield db
    db.close()


# -------------------------
# Step 1: seed campaigns (DB → metrics extraction simulation)
# -------------------------
def seed_campaign_metrics(session):
    campaigns = [
        Campaign(
            google_campaign_id="c1",
            name="High CPL Campaign",
            budget=100,
            spend=500,
            clicks=100,
            impressions=2000,
            ctr=5.0,
            leads=5,
            cpl=100.0,
        ),
        Campaign(
            google_campaign_id="c2",
            name="Low CPL Campaign",
            budget=100,
            spend=200,
            clicks=150,
            impressions=3000,
            ctr=5.0,
            leads=20,
            cpl=10.0,
        ),
        Campaign(
            google_campaign_id="c3",
            name="Low CTR Campaign",
            budget=100,
            spend=300,
            clicks=20,
            impressions=3000,
            ctr=1.0,
            leads=5,
            cpl=60.0,
        ),
    ]

    session.add_all(campaigns)
    session.commit()

    return campaigns


# -------------------------
# Convert DB → rule engine input format
# -------------------------
def extract_metrics(session):
    campaigns = session.query(Campaign).all()

    return [
        {
            "campaign_id": c.google_campaign_id,
            "cpl": c.cpl,
            "ctr": c.ctr,
        }
        for c in campaigns
    ]


# -------------------------
# E2E TEST
# -------------------------
def test_e2e_pipeline(session):

    # STEP 1: seed DB
    seed_campaign_metrics(session)

    metrics = extract_metrics(session)

    # STEP 2: rule engine
    recs = generate_recommendations(metrics)

    assert len(recs) > 0, "Rule engine returned no recommendations"

    # (Optional sanity check)
    assert any(r["type"] == "high_cpl" for r in recs)
    assert any(r["type"] == "low_ctr" for r in recs)

    # STEP 3: mock LLM (MiniCPM)
    def fake_llm_response(rec):
        return f"Mock explanation for {rec['campaign_id']}"

    with patch("app.recs.generate.load_model", return_value=None), \
         patch("app.recs.generate.generate_explanation") as mocked:

        mocked.side_effect = fake_llm_response

        enriched = [
            {
                **r,
                "explanation": generate_explanation(r)
            }
            for r in recs
        ]

    # STEP 4: verify enrichment
    assert len(enriched) == len(recs)

    for e in enriched:
        assert "explanation" in e
        assert e["explanation"] is not None
        assert isinstance(e["explanation"], str)