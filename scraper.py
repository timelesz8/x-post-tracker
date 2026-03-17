import re

def parse_number(text):
    if not text:
        return 0
    # 不要な文字（カンマ、件数、表示など）を削除
    text = text.replace(",", "").replace("件", "").replace("の", "").replace("表示", "")
    
    # 数字と小数点の部分だけ抽出 (例: "1.2万" -> "1.2", "万")
    match = re.search(r"(\d+\.?\d*)([万億]?)", text)
    if not match:
        return 0
    
    num_part = float(match.group(1))
    unit_part = match.group(2)
    
    if unit_part == "万":
        return int(num_part * 10000)
    elif unit_part == "億":
        return int(num_part * 100000000)
    
    return int(num_part)

# --- ループ内の処理 ---
for talent, url in targets:
    try:
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(5000) # 念のための待機

        # 【デバッグ用】画面の状態を保存（GitHub ActionsのArtifactsで確認可能）
        page.screenshot(path=f"debug_{talent}.png")

        # 各数値を aria-label から取得する
        # Xの構造上、これらが最も安定して取得できるプロパティです
        reply = parse_number(page.get_by_test_id("reply").first.get_attribute("aria-label"))
        repost = parse_number(page.get_by_test_id("retweet").first.get_attribute("aria-label"))
        like = parse_number(page.get_by_test_id("like").first.get_attribute("aria-label"))
        
        # ブックマークと表示回数は別途テキストから取得
        # ※ブックマークボタンがない投稿もあるため try-except 推奨
        try:
            bookmark = parse_number(page.locator('a[href$="/bookmarks"]').first.inner_text())
        except:
            bookmark = 0

        # 表示回数（「1.5万 件の表示」などから抽出）
        views_text = page.locator("text=件の表示").first.inner_text()
        views = parse_number(views_text)

        # スプレッドシートへの書き込み処理（以下略）

    except Exception as e:
        print(f"Error processing {talent}: {e}")
        page.screenshot(path=f"error_{talent}.png") # エラー時のみスクショ
        continue # 次のタレントへ
