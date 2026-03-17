from playwright.sync_api import sync_playwright
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json, os, re

targets = [
("篠塚大輝","https://x.com/ABCMART_INFO/status/2033696817473519907"),
("猪俣周杜","https://x.com/ABCMART_INFO/status/2033696566016381225"),
("橋本将生","https://x.com/ABCMART_INFO/status/2033696314236801343"),
("原嘉孝","https://x.com/ABCMART_INFO/status/2033696062938943853"),
("寺西拓人","https://x.com/ABCMART_INFO/status/2033695811071004930"),
("松島聡","https://x.com/ABCMART_INFO/status/2033695560880824458"),
("菊池風磨","https://x.com/ABCMART_INFO/status/2033695307821944843"),
("佐藤勝利","https://x.com/ABCMART_INFO/status/2033695056226402795")
]

scopes = ["https://www.googleapis.com/auth/spreadsheets"]

creds_dict = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT"])
creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)

gc = gspread.authorize(creds)

sheet = gc.open_by_key(
"167kAxRTdIQjkyjW2uJx8KDiRUQ_aV4OLXFF6SqtbBPo"
).worksheet("data")


def parse_number(text):
    text = text.replace(",", "")
    if "万" in text:
        return int(float(text.replace("万",""))*10000)
    return int(re.findall(r"\d+", text)[0])


with sync_playwright() as p:

    browser = p.chromium.launch()
    page = browser.new_page()

    for talent, url in targets:

        page.goto(url)
        page.wait_for_timeout(5000)

        article = page.locator("article").inner_text()

        reply = parse_number(article.split("\n")[1])
        repost = parse_number(article.split("\n")[2])
        like = parse_number(article.split("\n")[3])
        bookmark = parse_number(article.split("\n")[4])

        views_text = page.locator("text=件の表示").inner_text()
        views = parse_number(views_text)

        now = datetime.utcnow().isoformat()

        sheet.append_row([
            now,
            talent,
            url,
            reply,
            repost,
            like,
            bookmark,
            views
        ])

    browser.close()
