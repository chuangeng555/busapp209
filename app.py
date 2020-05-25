import os 
import logging
from flask import Response, Flask, request
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

from config import Config 

from mod import (current_timing, distance, calculation, bus_stops, BusStopMsg, numlist, get_BusStopNumber, testStatus)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


app = Flask(__name__)
app.config.from_object(Config)

logger = logging.getLogger(__name__)

LOCATION, BUSTIMING, REFRESH = range(3)

busStopID = ''

#temporary dictionary 
BusCode = {} #mapping of ID number to postal code 
prevSelection = {'select' : 'placeholder'}

#####################


@app.route('/test/')			# binds URL to view function
def hello():				
	return 'Hello, World!'

def start(update, context):
    if testStatus() == 200: 
        update.message.reply_text(
'''`Welcome to Bus Bot 🚌,` \n
    To display the main menu: \n
    *Press --> /start* \n 
    To check bus timing in bus stop: \n 
    *Press --> /busstop* \n
    To cancel process anytime: \n
    *Press --> /cancel* \n
    To refresh Timing: \n
    *Press -->* /refreshTiming \n
You can type / anytime to kickstart the above mention process
    ''', parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text(
        ''' There is no information available today, \n
            ''', parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def busstop(update, context):
    if testStatus() == 200: 
        location_keyboard = KeyboardButton(text="Yes", request_location=True)
        # contact_keyboard = KeyboardButton(text="No", request_location=False)
        custom_keyboard = [[ location_keyboard]]

        update.message.reply_text("Would you mind sharing your location? \nIf not, you can press --> /cancel",
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard = True))

        return LOCATION  
    else:
        update.message.reply_text(
        ''' There is no information available today
            ''', parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
        
        return ConversationHandler.END


def location(update, context):

    global busStopID 

    busStopDes = []
    num = []
    
    user = update.message.from_user
    print (user)
    text = update.message.location 
    print (text['longitude'], text['latitude'])
    
    # print (text['longtitude'],text['latitude'])
    # reply_markup=ReplyKeyboardRemove()
    update.message.reply_text('Please hold on for bus bot to search the nearest bus stop to your location :) ', reply_markup=ReplyKeyboardRemove())
    
    busStopDict = calculation(text['latitude'], text['longitude'])
    # print (busStopList)
    # print (len(busStopList))

    for k in busStopDict :

        busStopDes.append(busStopDict[k]['Description']) 
        BusCode[str(busStopDict[k]['Count'])] = k

    # print(BusCode)

    for i in range(0, len(busStopDict)):
        num.append(str(i))

    busStopID = numlist(num)
    print (busStopID)
    reply_keyboard = [num]

    update.message.reply_text(
        'Please choose the No. of the bus stop that you want to look at?{}'.format(BusStopMsg(busStopDes)),
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard =True, one_time_keyboard=True))
    
    return BUSTIMING



def bustiming(update, context):
    user = update.message.from_user
    print (user)
    text = update.message.text
    print (text)
    prevSelection['select'] = text 
    print (prevSelection)
    output = BusCode[text]
    print (output)
    
    update.message.reply_text('{}'.format(current_timing(output)), parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    update.message.reply_text('Key in /refreshTiming to refresh Time', parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())

    return REFRESH 

def refreshTiming(update, context):
    try:
        output = BusCode[prevSelection['select']]
        update.message.reply_text('{}'.format(current_timing(output)), parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    except:
        update.message.reply_text(
        ''' You have not selected your Bus stop, \n
            ''', parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    return REFRESH 

def checkBusNumber(update, context):
    return 


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

    #####################################################################################
    
    TOKEN = app.config['BOT_TOKEN']
    PORT = int(os.environ.get('PORT', '8443'))
    updater = Updater(TOKEN, use_context=True)

    updater.start_webhook(listen="0.0.0.0",
                        port=PORT,
                        url_path=TOKEN)

    updater.bot.set_webhook(app.config['APP_URL'] + TOKEN)
    
    ######################################################################
    dp = updater.dispatcher

    #call function here 

    # busStopID = numlist(num)

    #########

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('busstop', busstop)],

        states={
            # LOCATION: [MessageHandler(Filters.regex('^(Yes|No)$'), location)]
            LOCATION: [MessageHandler(Filters.location, location)],
            BUSTIMING: [MessageHandler(Filters.regex(busStopID), bustiming)],
            REFRESH: [CommandHandler('refreshTiming', refreshTiming)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    dp.add_handler(CommandHandler('start', start))

    dp.add_error_handler(error)
    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()


