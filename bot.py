import json
import os
import re
from collections import defaultdict as dd
from os import environ

import requests
import telebot

# Get config data from json / env
if os.path.exists(r'data.json'):
    with open(r'data.json', 'r') as f:
        data = json.load(f)
else:
    try:
        data = {
            'api-token': environ['API_TOKEN'],
            'bot-token': environ['BOT_TOKEN'],
            'notify-id': environ['NOTIFY_ID'],
            'url': environ['API_URL'],
            'whitelist': environ['WHITELIST'].split(',')
        }
    except KeyError:
        print("You don't have configuration JSON or environment variables set, go away")
        exit(1)

bot = telebot.AsyncTeleBot(data['bot-token'])  # Create bot object


# Decorator for authorizing ids that send certain commands
def needs_authorization(func):
    def inner(message):
        if str(message.from_user.id) in data['whitelist']:
            func(message)
        else:
            bot.reply_to(message, 'Not allowed. Go cry to your mama, or suck rittmang to get whitelisted')

    return inner


def normalise(txt):
    return re.sub('^/\w+[ ,\n]', '', txt)  # To remove the /command@botname from message.text
    
    


# No meow ksdfg
@bot.message_handler(commands=['start'])
def startBot(message):
    bot.reply_to(message, 'Hello ladiej')


# Just to get ids of ppl to add to whitelist
@bot.message_handler(commands=['id'])
def id(message):
    bot.reply_to(message, 'Your ID is {}'.format(message.from_user.id))
    bot.reply_to(message, 'The chat ID is {}'.format(message.chat.id))


# Echo the same message back to the caller - just for fun
@bot.message_handler(commands=['echo'])
@needs_authorization
def echo(message):
    if "give" in normalise(message.text).lower():
        bot.reply_to(message, "Get this man a \""
                     + re.sub('.*give ', '', normalise(message.text).lower()) + "\"")  # Avengers reference XD
    else:
        bot.send_message(message.chat.id, normalise(message.text))


# Brooklyn Nine-Nine needs more seasons
@bot.message_handler(commands=['coolcoolcoolcoolcool'])
def peralta(message):
    bot.reply_to(message, 'nodoubtnodoubtnodoubtnodoubtnodoubt')


# Start ze bot
print('start')
bot.send_message(data['notify-id'], 'Bot started')
bot.polling()
