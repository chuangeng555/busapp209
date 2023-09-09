from logging.handlers import RotatingFileHandler
import os
import logging
from flask import Response, Flask, request
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

from config import Config

from mod import (calculation, testStatus)

log_file_name="info.log"
handler = RotatingFileHandler(log_file_name, maxBytes=2000, backupCount=3)
logging.basicConfig(handlers=[handler],  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

app = Flask(__name__)
app.config.from_object(Config)

logger = logging.getLogger(__name__)

LOCATION, REFRESH = range(2)

busStopID = ''

#temporary dictionary
BusCode = {} #mapping of ID number to postal code
prevLocation = {'location' : 'placeholder'}
#####################

@app.route('/keepalive/')			# binds URL to view function
def hello():
    logger.info("stay alive")
    return 'alive'

def start(update, context):
    logger.info("service start")
    if testStatus() == 200:
        update.message.reply_text(
'''`Welcome to Bus Bot 🚌,` \n
    To display the main menu: \n
    *Press --> /start* \n
    To check bus timing in bus stop: \n
    *Press --> /busstop* \n
    To cancel process anytime: \n
    *Press --> /cancel* \n
You can type / anytime to kickstart the above mention process
    ''', parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    else:
        error(update, context)
        update.message.reply_text(
        ''' There is no information available today, \n
            ''', parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


#user to input their location
def busstop(update, context):
    if testStatus() == 200:
        location_keyboard = KeyboardButton(text="Send location ?", request_location=True)
        # contact_keyboard = KeyboardButton(text="No", request_location=False)
        custom_keyboard = [[location_keyboard]]

        logger.info("request input")

        update.message.reply_text("Would you mind sharing your location? \nIf not, you can press --> /cancel",
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True, one_time_keyboard = True))

        return LOCATION
    else:
        error(update, context)
        update.message.reply_text(
        ''' There is no information available today
            ''', parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())

        return ConversationHandler.END

#accept location and print bus stop [ bus + bus timing ]
def location(update, context):
    logger.info("get location and print bus stop")

    global busStopID
    busStopDes = []
    num = []
    user = update.message.from_user
    print (user)
    text = update.message.location
    print(type(text['latitude']))
    prevLocation['location'] = "{},{}".format(text['latitude'], text['longitude'])
    # print (prevLocation['location'])
    # print (type(prevLocation['location']))

    update.message.reply_text('Please hold on for bus bot to search the nearest bus stop to your location :) ') #, reply_markup=ReplyKeyboardRemove())
    update.message.reply_text('{}'.format(calculation(text['latitude'], text['longitude'])), parse_mode="Markdown")#, reply_markup=ReplyKeyboardRemove())
    update.message.reply_text('Key in /refreshTiming to refresh Time', parse_mode="Markdown") # reply_markup=ReplyKeyboardRemove())

    return REFRESH


# Refresh timng of the same location
def refreshTiming(update, context):
    logger.info("refresh timing ")
    try:
        location = prevLocation['location'].split(",")
        update.message.reply_text('{}'.format(calculation(float(location[0]),float(location[1]))), parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    except:
        logger.info("refresh timing error")
        error(update, context)
        update.message.reply_text(
        ''' You have not send your location, \n
            ''', parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    update.message.reply_text('Key in /refreshTiming to refresh Time', parse_mode="Markdown")
    update.message.reply_text('Key in /busstop to update location', parse_mode="Markdown")

    return REFRESH

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main():
    TOKEN = app.config['BOT_TOKEN']
    updater = Updater(TOKEN, use_context=True)
    

    #####################################################################################
    if (app.config['MODE'] != "polling"): 
        TOKEN = app.config['BOT_TOKEN']
        PORT = int(os.environ.get('PORT', '8443'))
            
        updater.start_webhook(listen="0.0.0.0",
                            port=PORT,
                            url_path=TOKEN)

        updater.bot.set_webhook(app.config['APP_URL'] + TOKEN)

        print('start bot in webhook mode')
    #########################################################################################
    else: 
        print('start bot in polling mode')

        updater.start_polling()

    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('busstop', busstop)],

        states={
            # LOCATION: [MessageHandler(Filters.regex('^(Yes|No)$'), location)]
            LOCATION: [MessageHandler(Filters.location, location)],
            REFRESH: [CommandHandler('refreshTiming', refreshTiming)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('start', start))
    dp.add_error_handler(error)
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    # updater.idle()

if __name__ == '__main__':
    main()
    app.run(debug=False)