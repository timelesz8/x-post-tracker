import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json
import os

scopes = ["https://www.googleapis.com/auth/spreadsheets"]

creds_dict = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT"])

creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)

gc = gspread.authorize(creds)

sheet = gc.open_by_key(
"167kAxRTdIQjkyjW2uJx8KDiRUQ_aV4OLXFF6SqtbBPo"
).worksheet("data")

sheet.append_row([
    datetime.utcnow().isoformat(),
    "test",
    "https://example.com",
    "1","2","3","4","5"
])
