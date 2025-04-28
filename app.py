import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

events = [
    {"date": "5/6", "subject": "パターン認識特論", "person": "山田太郎", "detail": "確率論"},
    {"date": "5/6", "subject": "パターン認識特論", "person": "山田花子", "detail": "確率密度"},
    {"date": "5/14", "subject": "アルゴリズム特論", "person": "everyone", "detail": "第１回課題期限"},
    {"date": "5/20", "subject": "パターン認識特論", "person": "山田太郎", "detail": "次元の呪い"},
    {"date": "5/20", "subject": "パターン認識特論", "person": "山田花子", "detail": "決定理論"},
    {"date": "5/25", "subject": "研究室", "person": "everyone", "detail": "MICCAI課題"},
    {"date": "6/10", "subject": "パターン認識特論", "person": "山田花子", "detail": "確率分布/二値変数"},
    {"date": "7/1", "subject": "パターン認識特論", "person": "山田太郎", "detail": "分類における最小二乗"},
    {"date": "7/8", "subject": "パターン認識特論", "person": "山田太郎", "detail": "最尤解"},
]

def get_user_events(events, username):
    result = []
    for event in events:
        if event['person'] == username or event['person'] == 'everyone':
            text = f"📅 {event['date']} {event['subject']}: {event['detail']}"
            result.append(text)
    if result:
        return "\n".join(result)
    else:
        return "該当するイベントはありませんでした。"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print(e)
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()

    if user_message.startswith('/check'):
        try:
            _, username = user_message.split(maxsplit=1)
            reply_text = get_user_events(events, username)
        except ValueError:
            reply_text = "名前が入力されていません。\n例: /check 山田花子"
    else:
        reply_text = "コマンドが認識できませんでした。\n例: /check 山田花子"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run(port=8000)
