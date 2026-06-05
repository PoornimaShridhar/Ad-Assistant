from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Base, Campaign, Recommendation

engine = create_engine("sqlite:///ads.db")

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_campaigns():
    session = SessionLocal()
    try:
        return session.query(Campaign).all()
    finally:
        session.close()

def get_recommendations():
    session = SessionLocal()
    try:
        return session.query(Recommendation).all()
    finally:
        session.close()

def approve_recommendation(recommendation_id: int):
    session = SessionLocal()
    try:
        recommendation = (
            session.query(Recommendation)
            .filter(Recommendation.id == recommendation_id)
            .first()
        )

        if recommendation:
            recommendation.status = "Approved"
            session.commit()

        return "Recommendation approved"
    finally:
        session.close()

def reject_recommendation(recommendation_id: int):
    session = SessionLocal()
    try:
        recommendation = (
            session.query(Recommendation)
            .filter(Recommendation.id == recommendation_id)
            .first()
        )
        if recommendation:
            recommendation.status = "Rejected"
            session.commit()
        return "Recommendation rejected"
    finally:
        session.close()