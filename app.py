import os
import time
from flask import Flask, request
from werkzeug.utils import secure_filename
import google.generativeai as genai

# --- 設定 (Configuration) ---
UPLOAD_FOLDER = os.path.join(os.path.expanduser('~'), 'Desktop', 'uploads')
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

try:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("エラー: 環境変数 GOOGLE_API_KEY が設定されていません。")
    genai.configure(api_key=api_key)
    print("Gemini APIキーの認証に成功しました。")
except Exception as e:
    print(e)

# --- HTMLテンプレート ---
HTML_FORM = """
<!doctype html>
<title>音声ファイルをアップロード</title>
<style>
  body {{ font-family: sans-serif; margin: 2em; }}
  .result {{ margin-top: 2em; padding: 1em; border: 1px solid #ccc; background-color: #f9f9f9; white-space: pre-wrap; }}
</style>
<h1>音声ファイルをアップロードして文字起こし</h1>
<form method=post action="/upload" enctype=multipart/form-data>
  <p>対応ファイル形式: mp3, wav, aiff, m4a など</p>
  <input type=file name=audio_file>
  <input type=submit value=文字起こし実行>
</form>
"""

RESULT_HTML = """
<!doctype html>
<title>文字起こし結果</title>
<style>
  body {{ font-family: sans-serif; margin: 2em; }}
  .result {{ margin-top: 1em; padding: 1em; border: 1px solid #ccc; background-color: #f9f9f9; white-space: pre-wrap; }}
</style>
<h1>文字起こし結果</h1>
<div class="result">{transcribed_text}</div>
<br>
<a href="/">別のファイルを試す</a>
"""

# --- Flaskのルート定義 ---
@app.route('/')
def show_upload_form():
    return HTML_FORM

@app.route('/upload', methods=['POST'])
def handle_upload_and_transcribe():
    if 'audio_file' not in request.files:
        return "エラー: リクエストにファイルパートがありません"

    file = request.files['audio_file']
    if file.filename == '':
        return "エラー: ファイルが選択されていません"

    if file:
        filename = secure_filename(file.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        print(f"ファイル '{filename}' を '{save_path}' に保存しました。")

        try:
            print("Geminiにファイルをアップロードしています...")
            gemini_file = genai.upload_file(path=save_path)

            print("Gemini側でのファイル処理を待っています...")
            while gemini_file.state.name == "PROCESSING":
                time.sleep(2)
                gemini_file = genai.get_file(name=gemini_file.name)

            if gemini_file.state.name == "FAILED":
                return f"エラー: Geminiへのファイルアップロードに失敗しました。"

            print("ファイル準備完了。文字起こしを開始します...")
            model = genai.GenerativeModel(model_name='models/gemini-1.5-flash-latest')

            response = model.generate_content(
                ["この音声ファイルを日本語で文字起こししてください。", gemini_file],
                request_options={"timeout": 600}
            )

            genai.delete_file(name=gemini_file.name)
            return RESULT_HTML.format(transcribed_text=response.text)

        except Exception as e:
            print(f"エラーが発生しました: {e}")
            return f"文字起こし中にエラーが発生しました: {e}"

    return "予期せぬエラーが発生しました。"
