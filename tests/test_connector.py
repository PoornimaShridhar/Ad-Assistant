from app.ads.connector import list_campaigns, get_campaign_metrics

def test_list_campaigns():
    campaigns = list_campaigns()

    assert isinstance(campaigns, list)
    assert len(campaigns) > 0

    for c in campaigns:
        assert "id" in c
        assert "name" in c
        assert "budget" in c


def test_get_campaign_metrics():
    metrics = get_campaign_metrics()

    assert isinstance(metrics, list)
    assert len(metrics) > 0

    for m in metrics:
        assert "campaign_id" in m
        assert "spend" in m
        assert "clicks" in m
        assert "impressions" in m
        assert "ctr" in m
        assert "leads" in m
        assert "cpl" in m