from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/adwords"]

flow = InstalledAppFlow.from_client_secrets_file(
    "client_secret.json",  # 👈 your downloaded file name
    SCOPES
)

creds = flow.run_local_server(port=0)

print("\n===== REFRESH TOKEN =====\n")
print(creds.refresh_token)
print("\n=========================\n")