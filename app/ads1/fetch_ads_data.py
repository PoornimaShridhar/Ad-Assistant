# app/ads1/runner.py

import pandas as pd
from app.ads1.connector import get_client
from app.ads1.ads_queries import (
    CAMPAIGNS_QUERY,
    DEVICES_QUERY,
    HOURLY_QUERY,
    GEO_QUERY,
    SEARCH_TERMS_QUERY,
    KEYWORDS_QUERY,
    RECOMMENDATIONS_QUERY,
)

def run_query(client, customer_id, query):
    service = client.get_service("GoogleAdsService")
    response = service.search(customer_id=customer_id, query=query)

    rows = []
    for r in response:
        rows.append(r)

    return rows


def fetch_all_data(customer_id):
    client = get_client()

    service = client.get_service("GoogleAdsService")

    def execute(query):
        response = service.search(customer_id=customer_id, query=query)
        return list(response)

    print("🔄 Fetching campaigns...")
    campaigns = execute(CAMPAIGNS_QUERY)

    print("🔄 Fetching devices...")
    devices = execute(DEVICES_QUERY)

    print("🔄 Fetching hourly data...")
    hourly = execute(HOURLY_QUERY)

    print("🔄 Fetching geo data...")
    geo = execute(GEO_QUERY)

    print("🔄 Fetching search terms...")
    search_terms = execute(SEARCH_TERMS_QUERY)

    print("🔄 Fetching keywords...")
    keywords = execute(KEYWORDS_QUERY)

    print("🔄 Fetching recommendations...")
    recommendations = execute(RECOMMENDATIONS_QUERY)

    return {
        "campaigns": campaigns,
        "devices": devices,
        "hourly": hourly,
        "geo": geo,
        "search_terms": search_terms,
        "keywords": keywords,
        "recommendations": recommendations
    }


def to_dataframes(raw_data):
    dfs = {}

    # Campaigns
    dfs["campaigns"] = pd.DataFrame([
        {
            "id": r.campaign.id,
            "name": r.campaign.name,
            "status": r.campaign.status.name,
            "impressions": r.metrics.impressions,
            "clicks": r.metrics.clicks,
            "cost": r.metrics.cost_micros / 1e6,
            "ctr": r.metrics.ctr,
            "conversions": r.metrics.conversions or 0 
        }
        for r in raw_data["campaigns"]
    ])

    # Devices
    dfs["devices"] = pd.DataFrame([
        {
            "device": r.segments.device.name,
            "clicks": r.metrics.clicks,
            "impressions": r.metrics.impressions,
            "cost": r.metrics.cost_micros / 1e6
        }
        for r in raw_data["devices"]
    ])

    # Hourly
    dfs["hourly"] = pd.DataFrame([
        {
            "date": r.segments.date,
            "hour": r.segments.hour,
            "clicks": r.metrics.clicks,
            "impressions": r.metrics.impressions,
            "cost": r.metrics.cost_micros / 1e6
        }
        for r in raw_data["hourly"]
    ])

    # Geo
    dfs["geo"] = pd.DataFrame([
    {
        "country_id": r.geographic_view.country_criterion_id,
        "clicks": r.metrics.clicks,
        "impressions": r.metrics.impressions,
        "cost": r.metrics.cost_micros / 1e6
    }
    for r in raw_data["geo"]
])

    # Search terms
    dfs["search_terms"] = pd.DataFrame([
        {
            "search_term": r.search_term_view.search_term,
            "clicks": r.metrics.clicks,
            "impressions": r.metrics.impressions,
            "cost": r.metrics.cost_micros / 1e6
        }
        for r in raw_data["search_terms"]
    ])

    # Keywords
    dfs["keywords"] = pd.DataFrame([
    {
        "campaign_id": r.campaign.id,
        "campaign_name": r.campaign.name,
        "ad_group_id": r.ad_group.id if r.ad_group else None,
        "ad_group_name": r.ad_group.name if r.ad_group else None,
        "keyword": r.ad_group_criterion.keyword.text if r.ad_group_criterion.keyword else None,
        "clicks": r.metrics.clicks,
        "impressions": r.metrics.impressions,
        "cost": r.metrics.cost_micros / 1e6,
        "conversions": r.metrics.conversions,
        "ctr": r.metrics.ctr,
    }
    for r in raw_data["keywords"]
])
    
    dfs["recommendations"] = pd.DataFrame([
    {
        "type": r.recommendation.type.name,
        "resource_name": r.recommendation.resource_name,
        "campaign": r.recommendation.campaign
    }
    for r in raw_data["recommendations"]
])

    return dfs