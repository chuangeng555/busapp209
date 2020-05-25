import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    BOT_TOKEN = os.environ.get('BOT_TOKEN') or 'you-will-never-guess'
    APP_URL = os.environ.get('APP_URL')
    API_KEY = os.environ.get('API_KEY')

# print (Config.BOT_TOKEN)
# print (Config.APP_URL)
# print (Config.API_KEY)