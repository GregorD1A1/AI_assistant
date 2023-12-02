import requests
from eleven import say
import os
import io
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

# Replace YOUR_CHAT_ID with your actual chat ID
chat_id = 1258213321

# Send the message
url_txt = f'https://api.telegram.org/bot{bot_token}/sendMessage'
url_voice = f'https://api.telegram.org/bot{bot_token}/sendVoice'


def send_text(msg):
    payload = {'chat_id': chat_id, 'text': msg}
    requests.post(url_txt, json=payload)


def send_voice(msg):
    voice_file = say(msg)
    voice_file = io.BytesIO(voice_file)
    requests.post(url_voice, params={'chat_id': chat_id}, files={'voice': voice_file})

