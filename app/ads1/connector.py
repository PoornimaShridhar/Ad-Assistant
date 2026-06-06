from logging import config
from xmlrpc import client
import os
from google.ads.googleads.client import GoogleAdsClient

def get_client():
    required = [
        "GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET",
        "GOOGLE_ADS_REFRESH_TOKEN"
    ]

    for r in required:
        if not os.getenv(r):
            raise ValueError(f"Missing env var: {r}")

    config = {
        "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
        "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
        "use_proto_plus": True
    }

    client = GoogleAdsClient.load_from_dict(config)
    return client


def list_campaigns(customer_id):
    client = get_client()
    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
          campaign.id,
          campaign.name,
          campaign.status
        FROM campaign
        LIMIT 20
    """

    response = ga_service.search(customer_id=customer_id, query=query)

    results = []

    for row in response:
        results.append({
            "id": row.campaign.id,
            "name": row.campaign.name,
            "status": row.campaign.status.name
        })

    return results

def get_campaign_metrics(customer_id):
    client = get_client()
    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
          campaign.id,
          metrics.impressions,
          metrics.clicks,
          metrics.cost_micros,
          metrics.conversions,
          metrics.ctr
        FROM campaign
        WHERE segments.date DURING LAST_30_DAYS
    """

    response = ga_service.search(customer_id=customer_id, query=query)

    data = []

    for row in response:
        data.append({
            "campaign_id": row.campaign.id,
            "impressions": row.metrics.impressions,
            "clicks": row.metrics.clicks,
            "cost": row.metrics.cost_micros / 1e6,
            "conversions": row.metrics.conversions,
            "ctr": row.metrics.ctr,
        })

    return data