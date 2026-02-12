import feedparser
import google.generativeai as genai
import os

# API設定
genai.configure(api_key=os.environ["gemini_api_key"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 収集したいRSSフィード（英・日）
RSS_FEEDS = [
    "https://hnrss.org/frontpage",  # Hacker News (英)
    "https://zenn.dev/feed"         # Zenn (日)
]

def main():
    report_content = "# Daily Tech Report\n\n"
    
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        # 最新3件を取得
        for entry in feed.entries[:3]:
            prompt = f"""
            以下の記事の要約と英語学習レポートを作成してください。
            Title: {entry.title}
            Link: {entry.link}
            
            1. 日本語で3行要約
            2. 注目すべき技術用語(英語)と意味
            3. (英文の場合) 構文のポイント解説（1箇所ピックアップ）
            """
            response = model.generate_content(prompt)
            report_content += f"## {entry.title}\n{response.text}\n\n---\n"
    
    # レポートをファイルに書き出し
    with open("report.md", "w", encoding="utf-8") as f:
        f.write(report_content)

if __name__ == "__main__":
    main()
