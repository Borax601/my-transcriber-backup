import os
import google.generativeai as genai

print("APIキーの読み込みテストを開始します...")

try:
    api_key = os.environ.get("GOOGLE_API_KEY")

    if not api_key:
        print("エラー: 環境変数 GOOGLE_API_KEY が設定されていません。")
        print("ターミナルで export GOOGLE_API_KEY=... のコマンドを再実行してください。")
    else:
        print("OK: 環境変数からAPIキーを読み込みました。")
        # 実際にAPIキーを使って認証を試みる
        genai.configure(api_key=api_key)
        print("成功！ Geminiライブラリの認証設定が完了しました。準備OKです！")

except Exception as e:
    print(f"予期せぬエラーが発生しました: {e}")