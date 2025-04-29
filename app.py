import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

events = [
    {"date": "5/6", "subject": "パターン認識特論", "person": "浦田海翔", "detail": "確率論"},
    {"date": "5/6", "subject": "パターン認識特論", "person": "江口純矢", "detail": "確率密度"},
    {"date": "5/14", "subject": "アルゴリズム特論", "person": "everyone", "detail": "第１回課題期限"},
    {"date": "5/20", "subject": "パターン認識特論", "person": "清水透真", "detail": "次元の呪い"},
    {"date": "5/20", "subject": "パターン認識特論", "person": "鈴木榛名", "detail": "決定理論"},
    {"date": "5/25", "subject": "研究室", "person": "everyone", "detail": "MICCAI課題"},
    {"date": "6/2", "subject": "ヒューマンマシンシステム特論", "person": "everyone", "detail": "ユニバーサルデザイン7原則発表"},
    {"date": "6/10", "subject": "パターン認識特論", "person": "長尾茉衣子", "detail": "確率分布/二値変数"},
    {"date": "6/16", "subject": "視覚色彩情報処理特論", "person": "厚地風太", "detail": "発表"},
    {"date": "6/16", "subject": "視覚色彩情報処理特論", "person": "江口純矢", "detail": "発表"},
    {"date": "7/1", "subject": "パターン認識特論", "person": "松本侑真", "detail": "分類における最小二乗"},
    {"date": "7/8", "subject": "パターン認識特論", "person": "横地累", "detail": "最尤解"},
]

def get_user_events(events, username):
    result = []
    for event in events:
        if event['person'] == username or event['person'] == 'everyone':
            text = f"📅 {event['date']} {event['subject']}: {event['detail']}"
            result.append(text)
    if result:
        return "\n\n".join(result)
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

@handler.add(FollowEvent)
def follow_message(line_follow_event):
    profile = line_bot_api.get_profile(line_follow_event.source.user_id)
    logger.info(profile)
    line_bot_api.reply_message(line_follow_event.reply_token, TextSendMessage(text=f'{profile.display_name}さん、フォローありがとう！ \n\n /check [自分の名前] : 自分の課題の確認 \n\n /add_event [日付(ex. 6/20)] [講義名] [対象者] [詳細]: 自分の課題を追加 \n\n /delete_event [日付(ex. 6/20)] [講義名]: 自分の課題を削除 \n '))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()

    if user_message.startswith('/check'):
        try:
            _, username = user_message.split(maxsplit=1)
            reply_text = get_user_events(events, username)
        except ValueError:
            reply_text = "名前が入力されていません。\n例: /check 山田花子"
            
    elif user_message.startswith('/add_event'):
        try:
            _, date, subject, person, detail = user_message.split(maxsplit=4)
            new_event = {"date": date, "subject": subject, "person": person, "detail": detail}
            events.append(new_event)
            reply_text = "新しいイベントが追加されました！"
        except ValueError:
            reply_text = "イベント情報が不完全です。\n例: /add_event 6/20 アルゴリズム特論 everyone 第2回課題"

    elif user_message.startswith('/delete_event'):
        try:
            _, date, subject, person = user_message.split(maxsplit=3)
            # 削除するイベントを見つけて削除
            event_to_delete = None
            for event in events:
                if event['date'] == date and event['subject'] == subject and event['person'] == person:
                    event_to_delete = event
                    break
            if event_to_delete:
                events.remove(event_to_delete)
                reply_text = "イベントが削除されました:" + str(date) + str(subject) + str(person)
            else:
                reply_text = "削除できるイベントが見つかりませんでした。"
        except ValueError:
            reply_text = "削除するイベントの情報が不完全です。\n\n 例: /delete_event 5/6 パターン認識特論 山田花子"

    else:
        reply_text = "コマンドが認識できませんでした。\n\n 例: /check 山田花子 または /add_event 6/20 アルゴリズム特論 everyone 第2回課題"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run(port=8000)
