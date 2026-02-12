import feedparser
from google import genai
import os

# API設定 (2026年最新版の書き方)
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL_ID = "gemini-1.5-flash" # モデルを指定

RSS_FEEDS = [
    "https://hnrss.org/frontpage",
    "https://zenn.dev/feed"
]

def main():
    report_content = "# Daily Tech Report\n\n"
    
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:
            prompt = f"""
            以下の記事の要約と英語学習レポートを作成してください。
            Title: {entry.title}
            Link: {entry.link}
            
            1. 日本語で3行要約
            2. 注目すべき技術用語(英語)と意味
            3. (英文の場合) 構文のポイント解説（1箇所ピックアップ）
            """
            # モデル呼び出し
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt
            )
            report_content += f"## {entry.title}\n{response.text}\n\n---\n"
    
    with open("report.md", "w", encoding="utf-8") as f:
        f.write(report_content)

if __name__ == "__main__":
    main()
