import feedparser
from google import genai
import os

# API設定
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL_ID = "models/gemini-1.5-flash" 

RSS_FEEDS = [
    "https://hnrss.org/frontpage",
    "https://zenn.dev/feed",
    "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhWbUVnSnRhSFFvQUFQAQ?hl=ja&gl=JP&ceid=JP:ja"
]

def main():
    print("Starting report generation...")
    report_content = f"# Daily Tech Report ({os.popen('date +%Y-%m-%d').read().strip()})\n\n"
    
    for url in RSS_FEEDS:
        print(f"Fetching feed: {url}")
        feed = feedparser.parse(url)
        if not feed.entries:
            report_content += f"⚠️ フィードの取得に失敗しました: {url}\n\n"
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
                print(f"Calling Gemini API for: {entry.title}")
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=prompt
                )
                # AIが空の返答をした場合のチェック
                if response.text:
                    report_content += f"## {entry.title}\n{response.text}\n\n---\n"
                else:
                    report_content += f"## {entry.title}\n⚠️ AIからの応答が空でした。\n\n---\n"
            except Exception as e:
                # エラーが起きたらその内容をレポートに書き込む
                print(f"Error: {e}")
                report_content += f"## {entry.title}\n❌ エラー発生: {str(e)}\n\n---\n"
                continue
    
    # ファイル書き出し
    with open("report.md", "w", encoding="utf-8") as f:
        f.write(report_content)
    print("Success: report.md has been written.")

if __name__ == "__main__":
    main()
