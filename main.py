import feedparser
from google import genai
import os

# API設定
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def get_available_model():
    """利用可能なモデル一覧から最適なものを自動選択する"""
    print("Fetching available models...")
    try:
        # 使用可能なモデルをリストアップ
        models = client.models.list()
        model_names = [m.name for m in models]
        print(f"Available models: {model_names}")
        
        # 優先順位をつけて探す
        priority_models = [
            "gemini-2.0-flash", 
            "gemini-1.5-flash",
            "gemini-3-flash",
            "gemini-2.0-flash-exp"
        ]
        
        for pm in priority_models:
            # SDKが内部で models/ を補完する場合があるため、両方の形式でチェック
            if pm in model_names: return pm
            if f"models/{pm}" in model_names: return f"models/{pm}"
            
        # 何も見つからない場合はリストの最初（大抵 Flash 系）を返す
        return model_names[0]
    except Exception as e:
        print(f"Failed to list models: {e}")
        return "gemini-2.0-flash" # フォールバック

def main():
    # 実行時にモデルを決定
    MODEL_ID = get_available_model()
    print(f"Selected Model: {MODEL_ID}")

    report_content = f"# Daily Tech Report ({os.popen('date +%Y-%m-%d').read().strip()})\n\n"
    report_content += f"使用モデル: `{MODEL_ID}`\n\n---\n"
    
    RSS_FEEDS = ["https://hnrss.org/frontpage", "https://zenn.dev/feed"]
    
    for url in RSS_FEEDS:
        print(f"Fetching feed: {url}")
        feed = feedparser.parse(url)
        for entry in feed.entries[:2]: 
            prompt = f"以下の記事を日本語で3行要約してください。\nTitle: {entry.title}\nLink: {entry.link}"
            
            try:
                print(f"Generating content for: {entry.title}")
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=prompt
                )
                if response.text:
                    report_content += f"## {entry.title}\n{response.text}\n\n---\n"
            except Exception as e:
                report_content += f"## {entry.title}\n❌ エラー: {str(e)}\n\n---\n"
    
    with open("report.md", "w", encoding="utf-8") as f:
        f.write(report_content)
    print("Done!")

if __name__ == "__main__":
    main()
