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

ids = dd(lambda: [])  # List of ids to send message to


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


def dogbin(content):
    # Save names of who all are gonna get messages in dogbin
    return 'https://del.dog/{}'.format(json.loads(requests.post("https://del.dog/documents",
                                                                content).content.decode())['key'])


def getData(url, token, ids):
    names_list = []  # List of all names
    numbers_list = []  # List of all numbers

    # Get data from our API
    api_data = json.loads(requests.get(url, headers={'Authorization': token}).text)

    if ids == 'all':
        ids = list(map(lambda x: x['id'], api_data))

    # Add names and numbers to respective lists
    for user in api_data:
        if int(user['id']) in ids:
            names_list.append(user['name'])
            numbers_list.append(user['phone'].split('|')[-1])

    return names_list, numbers_list


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


# Responds to caller with the current api url from which data is requested
@bot.message_handler(commands=['showurl'])
def showURL(message):
    bot.reply_to(message, data['url'])


# Responds to caller with the current list of names to whom message is to be sent
@bot.message_handler(commands=['showlist'])
def showlist(message):
    names, _ = getData(data['url'], data['api-token'], ids['nyan'])
    bot.reply_to(message, 'The list of names to whom the message will be sent can be found at\n' +
                 dogbin('\n'.join(names)))
    
    
# Just to piss of Pranav
@bot.message_handler(func=lambda message: True)
def piss_of_bakre(message):
    if str(message.from_user.id) == "893696358":
        bot.reply_to(message, "no u bish")


# Start ze bot
print('start')
bot.send_message(data['notify-id'], 'Bot started')
bot.polling()
