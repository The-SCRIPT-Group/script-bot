import json
import os
import re
import traceback
from collections import defaultdict as dd
from os import environ
from time import sleep

import requests
import telebot
from emoji import demojize

import whatsapp_stuff.whatsapp as meow

# Get config data from json / env
if os.path.exists(r'whatsapp_stuff/data.json'):
    with open(r'whatsapp_stuff/data.json', 'r') as f:
        data = json.load(f)
else:
    try:
        data = {
            'api-token': environ['API_TOKEN'],
            'bot-token': environ['BOT_TOKEN'],
            'browser': environ['BROWSER'],
            'driver-path': environ['DRIVER_PATH'],
            'notify-id': environ['NOTIFY_ID'],
            'url': environ['API_URL'],
            'whitelist': environ['WHITELIST'].split(',')
        }
    except KeyError:
        print("You don't have configuration JSON or environment variables set, go away")
        exit(1)

bot = telebot.TeleBot(data['bot-token'])  # Create bot object

ids = dd(lambda: [])  # List of ids to send message to


# Decorator for authorizing ids that send certain commands
def needs_authorization(func):
    def inner(message):
        if str(message.from_user.id) in data['whitelist']:
            func(message)
        else:
            bot.reply_to(message, 'Kicking this idiot out in')
            for i in range(5):
                bot.send_message(message.chat.id, str(5-i))
                sleep(0.5)
            bot.kick_chat_member(message.chat.id, message.from_user.id)  # Lol

    return inner


def normalise(txt):
    return re.sub('^/\w+[ ,\n]', '', txt)  # To remove the /command@botname from message.text


def dogbin(content):
    # Save names of who all are gonna get messages in dogbin
    return 'https://del.dog/{}'.format(json.loads(requests.post("https://del.dog/documents",
                                                                content).content.decode())['key'])


# meow. lots of meow.
@bot.message_handler(commands=['start'])
def startBot(message):
    bot.reply_to(message, 'meow 😸')


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


# Just give na baba
@bot.message_handler(regexp='^give', content_types=['text'])
def gimmegimme(message):
    bot.reply_to(message, "Get this man a \"" + re.sub('.*give ', '', normalise(message.text).lower())
                 + "\"")
    for _ in range(5):
        sleep(5)
        bot.send_message(message.chat.id, 'Give {} \"'.format(message.from_user.first_name)
                         + re.sub('.*give ', '', normalise(message.text).lower()) + "\"")


# Brooklyn Nine-Nine needs more seasons
@bot.message_handler(commands=['coolcoolcoolcoolcool'])
def peralta(message):
    bot.reply_to(message, 'nodoubtnodoubtnodoubtnodoubtnodoubt')


# Responds to caller with the current api url from which data is requested
@bot.message_handler(commands=['showurl'])
def showURL(message):
    bot.reply_to(message, data['url'])


# Set which user ids will get the message once WhatsApp is run
@bot.message_handler(commands=['setids'])
@needs_authorization
def setIDs(message):
    try:
        # Set to all - it will send to all user_ids fetched from API call to URL
        ids['nyan'] = 'all' if normalise(message.text) == 'all' else list(map(int, normalise(message.text).split()))
        bot.reply_to(message, str(ids['nyan']))
    except:
        bot.reply_to(message, 'invalid ids, resetting list')
        ids['nyan'] = []


# Responds to caller with the current list of names to whom message is to be sent
@bot.message_handler(commands=['showlist'])
def showlist(message):
    names, _ = meow.getData(data['url'], data['api-token'], ids['nyan'])
    bot.reply_to(message, 'The list of names to whom the message will be sent can be found at\n' +
                 dogbin('\n'.join(names)))


# Start sending whatsapp message
@bot.message_handler(commands=['whatsapp'])
@needs_authorization
def startWhatsapp(message):
    """
    set the message in the format -
    Hey name :wave:
    <msg taken from command call>
    - SCRIPT bot :robot_face:
    """
    msg = (
            'Hey, {} :wave:\n' +
            demojize(normalise(message.text)) + '\n' +
            '- SCRIPT bot :robot_face:\n'
    )

    bot.reply_to(message, 'Please wait while we fetch the QR code...')

    messages_sent_to = []

    try:
        browser = meow.startSession(data['browser'], data['driver-path'])  # Start whatsapp in selenium

        # Send qr to caller's chat
        with open(r'whatsapp_stuff/qr.png', 'rb') as qr:
            bot.send_photo(message.from_user.id, qr)
        bot.send_message(message.chat.id, 'The QR code has been sent to ' + message.from_user.first_name)

        # Wait till the search chat text box is loaded onto the screen
        meow.waitTillElementLoaded(browser, '/html/body/div[1]/div/div/div[3]/div/div[1]/div/label/input')

        # Get data from our API
        names, numbers = meow.getData(data['url'], data['api-token'], ids['nyan'])

        # Send messages to all entries in file
        for num, name in zip(numbers, names):
            messages_sent_to.append(meow.sendMessage(num, name, msg, browser))

        browser.close()  # Work done, close selenium

        # Send confirmation messages
        bot.send_message(message.chat.id, 'Messages sent!')
        print('done')

    except Exception as e:
        bot.send_message(message.chat.id, 'Houston, there is a problem')
        print(traceback.format_exc())

    finally:
        # Send the url to dogbin on the chat
        bot.send_message(message.chat.id, 'The list of names to whom the message was sent can be found at\n' +
                         dogbin('\n'.join(messages_sent_to)))


# Start ze bot

print('start')
bot.send_message(data['notify-id'], 'Bot started from ksdfg laptop')
bot.polling()
