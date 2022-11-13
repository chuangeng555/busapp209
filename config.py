from dotenv import load_dotenv
load_dotenv()
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    BOT_TOKEN = os.environ.get('BOT_TOKEN') or 'you-will-never-guess'
    APP_URL = os.environ.get('APP_URL')
    API_KEY = os.environ.get('API_KEY')
    MODE = os.environ.get('MODE')