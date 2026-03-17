from playwright.sync_api import sync_playwright
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json, os, re

# ターゲットリスト
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

# Google Sheets 設定
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds_dict = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT"])
creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
gc = gspread.authorize(creds)
sheet = gc.open_by_key("167kAxRTdIQjkyjW2uJx8KDiRUQ_aV4OLXFF6SqtbBPo").worksheet("data")

def parse_number(text):
    """
    「1.2万」「1,234」「567件のいいね」などのテキストから数値を抽出する
    """
    if not text:
        return 0
    
    # 不要な文字を削除
    text = text.replace(",", "").replace(" ", "")
    
    # 正規表現で「数字（小数含む）」と「単位」を分離
    match = re.search(r"(\d+\.?\d*)([万億]?)", text)
    if not match:
        return 0
    
    val = float(match.group(1))
    unit = match.group(2)
    
    if unit == "万":
        return int(val * 10000)
    elif unit == "億":
        return int(val * 100000000)
    
    return int(val)

def get_safe_value(page, test_id):
    """
    指定したtest-idの要素からaria-labelを取得し、数値化する
    """
    try:
        element = page.get_by_test_id(test_id).first
        label = element.get_attribute("aria-label")
        return parse_number(label)
    except:
        return 0

with sync_playwright() as p:
    browser = p.chromium.launch()
    # 言語設定を日本語にして、表示を安定させる
    context = browser.new_context(locale="ja-JP")
    page = context.new_page()

    for talent, url in targets:
        try:
            print(f"Processing: {talent}...")
            # wait_until を "domcontentloaded"（最低限の読み込み）に変更
            page.goto(url, wait_until="domcontentloaded")
            
            # 「投稿内容（article）」が表示されるまで最大15秒待つ
            # これにより、networkidle よりも早く、かつ確実に次に進めます
            page.wait_for_selector("article", timeout=15000)
            
            # 念のため少しだけ追加待機
            page.wait_for_timeout(3000)

            # 念のため、全タレントのスクリーンショットを保存（デバッグ用）
            page.screenshot(path=f"debug_{talent}.png")

            # aria-label（アクセシビリティ用ラベル）から各数値を取得
            # Xの仕様が変わっても比較的壊れにくい
            reply = get_safe_value(page, "reply")
            repost = get_safe_value(page, "retweet")
            like = get_safe_value(page, "like")
            
            # ブックマークは test-id がない場合があるため、リンクから取得
            bookmark = 0
            try:
                bm_element = page.locator('a[href$="/bookmarks"]').first
                bookmark = parse_number(bm_element.inner_text())
            except:
                pass

            # 表示回数（「1.5万件の表示」など）
            views = 0
            try:
                views_text = page.locator("text=件の表示").first.inner_text()
                views = parse_number(views_text)
            except:
                pass

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
            print(f"Success: {talent} (Likes: {like})")

        except Exception as e:
            print(f"Error at {talent}: {e}")
            page.screenshot(path=f"error_{talent}.png")
            continue

    browser.close()
