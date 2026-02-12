import feedparser
from google import genai
import os

# API設定
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# --- ここを修正 ---
# 'models/' を外して、リストにあった名称に変更します
MODEL_ID = "gemini-3-flash" 
# もし 3-flash でまた limit 0 が出る場合は "gemini-2.0-flash" を試してください
# ----------------

RSS_FEEDS = [
    "https://hnrss.org/frontpage",
    "https://zenn.dev/feed"
]

def main():
    print("Starting report generation...")
    report_content = f"# Daily Tech Report ({os.popen('date +%Y-%m-%d').read().strip()})\n\n"
    
    for url in RSS_FEEDS:
        print(f"Fetching feed: {url}")
        feed = feedparser.parse(url)
        if not feed.entries:
            continue

        for entry in feed.entries[:2]: 
            prompt = f"""
            以下の記事の要約と英語学習レポートを作成してください。
            Title: {entry.title}
            Link: {entry.link}
            
            1. 日本語で3行要約
            2. 注目すべき技術用語(英語)と意味
            3. (英文の場合) 構文のポイント解説（1箇所ピックアップ）
            """
            
            try:
                print(f"Calling Gemini API ({MODEL_ID}) for: {entry.title}")
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=prompt
                )
                if response.text:
                    report_content += f"## {entry.title}\n{response.text}\n\n---\n"
            except Exception as e:
                print(f"Error: {e}")
                report_content += f"## {entry.title}\n❌ エラー発生: {str(e)}\n\n---\n"
                continue
    
    with open("report.md", "w", encoding="utf-8") as f:
        f.write(report_content)
    print("Success: report.md has been written.")

if __name__ == "__main__":
    main()
