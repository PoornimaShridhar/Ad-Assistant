from app.ads1.fetch_ads_data import fetch_all_data, to_dataframes
import os

_cached_dfs = None

def load_google_ads_data(force_refresh=False):
    global _cached_dfs

    customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")

    if not customer_id:
        raise ValueError("GOOGLE_ADS_CUSTOMER_ID missing")

    if _cached_dfs is not None and not force_refresh:
        return _cached_dfs

    raw = fetch_all_data(customer_id)
    dfs = to_dataframes(raw)

    _cached_dfs = dfs
    return dfs