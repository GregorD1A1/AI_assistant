from elevenlabs import set_api_key, generate
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

set_api_key(os.getenv('ELEVENLABS_API_KEY'))

def say(text):
    return generate(text, voice="Clyde", model="eleven_multilingual_v1")


if __name__ == "__main__":
    say("dzik")