from dotenv import load_dotenv
load_dotenv()

from app.ads1.fetch_ads_data import fetch_all_data, to_dataframes
import os

CUSTOMER_ID = os.getenv("GOOGLE_ADS_CUSTOMER_ID")

def main():
    raw = fetch_all_data(CUSTOMER_ID)
    dfs = to_dataframes(raw)

    for name, df in dfs.items():
        print("\n====================")
        print(name.upper())
        print("====================")
        print(df.head())

    return dfs


if __name__ == "__main__":
    dfs = main()