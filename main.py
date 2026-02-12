import feedparser
from google import genai
import os

# API設定
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL_ID = "models/gemini-1.5-flash" 

RSS_FEEDS = [
    "https://hnrss.org/frontpage",
    "https://zenn.dev/feed"
]

def main():
    report_content = "# Daily Tech Report\n\n"
    
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        # 1.5 Flashの無料枠（RPM 15）を超えないよう、取得件数を少し抑えます
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
                # モデル呼び出し（MODEL_ID変数を使い、promptを正しく渡します）
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=prompt
                )
                report_content += f"## {entry.title}\n{response.text}\n\n---\n"
            except Exception as e:
                print(f"Error processing {entry.title}: {e}")
                continue
    
    with open("report.md", "w", encoding="utf-8") as f:
        f.write(report_content)

if __name__ == "__main__":
    main()
