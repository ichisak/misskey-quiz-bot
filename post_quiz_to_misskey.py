import requests
import random
from dotenv import load_dotenv
import os
import logging
import google.cloud.logging
from datetime import datetime
import gspread

#環境変数読み込み
load_dotenv()


#自分のMisskeyインスタンスのURL
MISSKEY_INSTANCE = os.getenv("MISSKEY_URL")
#発行したAPIトークン
API_TOKEN = os.getenv("API_TOKEN") 

#Google Sheets設定
SERVICE_ACCOUNT = os.getenv("SERVICE_ACCOUNT")  
FILE_NAME = os.getenv("FILE_NAME")     

#Cloud Loggingの初期化
client = google.cloud.logging.Client()
client.setup_logging()
logging.basicConfig(level=logging.INFO)

#日付設定
exectuion_date = datetime.today().strftime("%Y-%m-%d")

#Loggingへログの書き込み
def log_message(message):
    logging.info(f"{datetime.now()} - {message}")

#ランダムにクイズを取得する
def get_random_quiz():
    gc = gspread.service_account(filename=SERVICE_ACCOUNT)
    sh = gc.open(FILE_NAME)
    worksheet = sh.worksheet("クイズ")
    rows = worksheet.get_all_values()
    header, data = rows[0], rows[1:]
    quiz = random.choice(data)
    question, answer = quiz
    print(f"DEBUG: question={question}, answer={answer}")
    return question, answer

    

def post_to_misskey(question,answer):
    url = f"{MISSKEY_INSTANCE}/api/notes/create"
    payload = {
        "i": API_TOKEN,
        "visibility": "home",
        "cw": f"【問題】{question}",
        "text":f"【正解】{answer}" #折りたたみテキスト
    }

    try:
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload,headers=headers)

        response.raise_for_status()
        
        if response.status_code == 200:
            data = response.json()
            if "createdNote" in data:
                return True
            else:
                log_message(f"投稿失敗（レスポンス異常）：{data}")
                return False
        else:
            log_message(f"投稿失敗（ステータスコード: {response.status_code}）：{response.text}")
            return False
    except requests.exceptions.RequestException as e:
        log_message(f"Misskey投稿エラー：{e}")
        return False


if __name__ == "__main__":
    question, answer = get_random_quiz()
    post_to_misskey(question, answer)
