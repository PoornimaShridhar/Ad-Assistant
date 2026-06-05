from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True)
    google_campaign_id = Column(String, unique=True)
    name = Column(String)

    budget = Column(Float)
    spend = Column(Float)
    clicks = Column(Integer)
    impressions = Column(Integer)

    ctr = Column(Float)
    leads = Column(Integer)
    cpl = Column(Float)

    last_synced = Column(DateTime, default=datetime.utcnow)

    recommendations = relationship("Recommendation", back_populates="campaign")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True)

    campaign_id = Column(Integer, ForeignKey("campaigns.id"))

    recommendation_type = Column(String)
    action = Column(String)
    reason = Column(String)

    status = Column(String, default="Pending")  # Pending / Approved / Rejected
    created_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="recommendations")