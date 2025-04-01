import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
IP_RASPBERRY = os.getenv('IP_RASPBERRY')