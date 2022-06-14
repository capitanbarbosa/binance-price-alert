import os
from unittest import result
import requests
import time
import re
from binance import Client
from telegram import ParseMode
from telegram.ext import CommandHandler, Defaults, Updater

token = "5502330273:AAF43xM3FcSFwNDNwWbxgqsnagTNMw8rjAA"  # Telegram bot token
chat_id = "1554810140"  # Your telegram userid for bot update

# -100xxxxxxx add bot to your channel as admin to update on channel
channel_id = '-1001775085172'

fiatCurrency = 'USDT'

client = Client()

##

def bruhCommand(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text='bruh')


def helpCommand(update, context):
    return

### wiz ^^

#/start
def startCommand(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text='Hello there!, I can send you alert when your favorite crypto reaches at certain price.\nJust use command \n<i>/alert {crypto code} {> / &lt;} {price}</i>')

#regex to format the: /alert {BTC} > {target price}
def truncate(num):
    return re.sub(r'^(\d+\.\d{,5})\d*$', r'\1', str(num))

#/alert
def priceAlert(update, context):
    # a context starts null or 0 when introduced as a param,
    #   - When its 0, it asks for a /alert call along with a crypto symbol and its price.
    #   - if the length of its arguments are more than 0, then updates its args each 15 sec and then
    #       with the priceAlertCallback() and then returns a response.
    if len(context.args) > 2:
        crypto = context.args[0].upper()
        sign = context.args[1]
        price = context.args[2]
        result = client.get_ticker(symbol=crypto+fiatCurrency)
        d = dict()
        spotPrice = truncate(result['lastPrice'])

        context.job_queue.run_repeating(priceAlertCallback, interval=15, first=15, context=[
                                        crypto, sign, price, update.message.chat_id])
        
        response = f"⏳ I will update you when {crypto} reaches {price} {fiatCurrency}, \n"
        response += f"the current price of {crypto} is {spotPrice} {fiatCurrency}"
    else:
        response = '⚠️ Please provide a crypto code and a price value: \n<i>/alert {crypto code} {> / &lt;} {price}</i>'

    context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    # Use this to get update on channel
    context.bot.send_message(channel_id, text=response)


def priceAlertCallback(context):
    crypto = context.job.context[0]
    sign = context.job.context[1]
    price = context.job.context[2]
    chat_id = context.job.context[3]

    send = False
    ## Imported binance client and called get_ticker.
    result = client.get_ticker(symbol=crypto+fiatCurrency)
    d = dict()
    # We now regex (truncate) what the result pulls from the 'lastPrice' key pair.
    spotPrice = truncate(result['lastPrice'])

    if sign == '<':
        if float(price) >= float(spotPrice):
            send = True
    else:
        if float(price) <= float(spotPrice):
            send = True

    if send:
        response = f'👋 {crypto} has surpassed {price} and has just reached <b>{spotPrice} {fiatCurrency}</b>!'

        context.job.schedule_removal()

        context.bot.send_message(chat_id=chat_id, text=response)
        # Use this to get update on channel
        #context.bot.send_message(channel_id, text=response)


# the update / updater is created here
## as well as the dispatcher from it.
###
# We can add, edit commands from here.

if __name__ == '__main__':
    updater = Updater(token=token,
                      defaults=Defaults(parse_mode=ParseMode.HTML))
    dispatcher = updater.dispatcher

#/start
    dispatcher.add_handler(CommandHandler(
        'start', startCommand))
#/alert
    dispatcher.add_handler(CommandHandler('alert', priceAlert))
#/bruh
    dispatcher.add_handler(CommandHandler(
        'bruh', bruhCommand))

    

    ########### HOST ON HEROKU ###############
    # - Remove polling when using webhook
    #updater.start_webhook(listen="0.0.0.0", port=os.environ.get("PORT", 443), url_path=token, webhook_url="https://appname.herokuapp.com/"+token)
    updater.start_polling()

    updater.idle()
