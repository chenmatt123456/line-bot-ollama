from flask import Flask, request, abort
import requests
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)
configuration = Configuration(access_token='Ztz/W+Bz54YIL2jWPIwnjZ1gDm64eezkJD8cHjDhGNJzpkhtbm7nf9hIVousFFYNyKCbbY4ctb1wEwFha5WGmCt6f0sZQENbO8PgByvhtnMixSC7XadofI1MnaYq+gmtRmiiOokS+NVqwkdLLgKYRwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('fd28e86bbe3b02b212cd7b8975bc9281')
OLLAMA_API_URL = 'OLLAMA_URL/api/chat'  # 稍後更新為 Ollama 的 Render URL

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature.")
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        try:
            response = requests.post(OLLAMA_API_URL, json={
                'model': 'gemma3:4b',
                'messages': [{'role': 'user', 'content': event.message.text}]
            }).json()
            reply_text = response['message']['content'].strip()
        except Exception as e:
            reply_text = f"錯誤：{str(e)}"
            app.logger.error(f"Ollama error: {e}")

        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=8080)