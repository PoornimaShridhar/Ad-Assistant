# app/ads1/reports.py

CAMPAIGNS_QUERY = """
SELECT
  campaign.id,
  campaign.name,
  campaign.status,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions,
  metrics.ctr
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
"""

DEVICES_QUERY = """
SELECT
  segments.device,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
"""

HOURLY_QUERY = """
SELECT
  segments.date,
  segments.hour,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
"""

GEO_QUERY = """
SELECT
  geographic_view.country_criterion_id,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros
FROM geographic_view
WHERE segments.date DURING LAST_30_DAYS
"""

SEARCH_TERMS_QUERY = """
SELECT
  search_term_view.search_term,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros
FROM search_term_view
WHERE segments.date DURING LAST_30_DAYS
"""

KEYWORDS_QUERY = """
SELECT
  campaign.id,
  campaign.name,
  ad_group.id,
  ad_group.name,
  ad_group_criterion.keyword.text,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions
FROM keyword_view
WHERE segments.date DURING LAST_30_DAYS
"""

RECOMMENDATIONS_QUERY = """
SELECT
  recommendation.type,
  recommendation.resource_name,
  recommendation.campaign
FROM recommendation
"""