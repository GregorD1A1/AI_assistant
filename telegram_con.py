import requests
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

# Replace YOUR_CHAT_ID with your actual chat ID
chat_id = 1258213321

# Send the message
url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

def send_msg(msg):
    payload = {'chat_id': chat_id, 'text': msg}
    requests.post(url, json=payload)
