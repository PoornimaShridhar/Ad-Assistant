from dotenv import load_dotenv
load_dotenv()
from app.ads1.connector import list_campaigns, get_campaign_metrics
import pandas as pd
import os

CUSTOMER_ID = os.getenv("GOOGLE_ADS_CUSTOMER_ID")

def inspect_google_ads():
    campaigns = list_campaigns(CUSTOMER_ID)

    print("4️⃣ Campaigns received:", len(campaigns))

    print(pd.DataFrame(campaigns))

    metrics = get_campaign_metrics(CUSTOMER_ID)

    print("6️⃣ Metrics received:", len(metrics))

    print(pd.DataFrame(metrics))


if __name__ == "__main__":
    inspect_google_ads()

