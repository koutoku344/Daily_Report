import feedparser
from google import genai
import os

# API設定
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# モデルID（プレフィックス付き）
MODEL_ID = "models/gemini-1.5-flash" 

RSS_FEEDS = [
    "https://hnrss.org/frontpage",
    "https://zenn.dev/feed"
]

def main():
    report_content = "# Daily Tech Report\n\n"
    
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        # 枠を考慮して、各フィードから上位2記事を取得
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
                # 【重要】ここを修正： contents に prompt 変数を渡すようにしました
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=prompt
                )
                
                # 生成されたテキストをレポートに追加
                report_content += f"## {entry.title}\n{response.text}\n\n---\n"
                print(f"Successfully generated report for: {entry.title}")
                
            except Exception as e:
                print(f"Error processing {entry.title}: {e}")
                continue
    
    # 最終的な結果を書き込み
    with open("report.md", "w", encoding="utf-8") as f:
        f.write(report_content)

if __name__ == "__main__":
    main()
