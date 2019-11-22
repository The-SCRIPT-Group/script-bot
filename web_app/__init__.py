import json
import os
from random import choice
from string import ascii_letters

from flask import Flask, render_template, session, request, redirect, url_for

from whatsapp_stuff import whatsapp as meow

app = Flask('whatsapp bot')
app.secret_key = 'telegram_api_is_weird'
browser = {}

meow.set_home(os.path.join(app.static_folder, 'images', ''))

# Get config data from json / env
if os.path.exists(os.getcwd().replace('web_app', '').replace('\\', '/') + r'whatsapp_stuff/data.json'):
    with open(os.getcwd().replace('web_app', '').replace('\\', '/') + r'whatsapp_stuff/data.json', 'r') as f:
        data = json.load(f)
else:
    try:
        data = {
            'api-token': os.environ['API_TOKEN'],
            'bot-token': os.environ['BOT_TOKEN'],
            'browser': os.environ['BROWSER'],
            'driver-path': os.environ['DRIVER_PATH'],
            'notify-id': os.environ['NOTIFY_ID'],
            'url': os.environ['API_URL'],
            'whitelist': os.environ['WHITELIST'].split(',')
        }
    except KeyError:
        print("You don't have configuration JSON or os.environment variables set, go away")
        exit(1)


# wrapper; only execute function if user is logged in or request from qrstuff
def authorized(func):
    def inner(*args, **kwargs):
        if 'username' in session:
            return func(*args, **kwargs)
        else:
            return render_template('begone.html')

    return inner


# homepage - basically come here after he's logged in qrstuff
@app.route('/')
def home():
    print(session)
    return render_template('index.html')


# login user and retrieve qr
@app.route('/get-qr', methods=['POST'])
def login():
    if request.form['username'] == 'tsg_user' and request.form['password'] == 'haveli':
        session['username'] = request.form['username']
        session['id'] = ''.join([choice(ascii_letters) for _ in range(21)])
        return redirect(url_for('qr'))
    else:
        return render_template('begone.html')


# display qr code to scan
@authorized
@app.route('/qr')
def qr():
    browser[session['id']], qr_img = meow.startWebSession(data['browser'], data['driver-path'])
    return render_template('qr.html', qr=qr_img)


# display message details form
@authorized
@app.route('/form')
def form():
    return render_template('form.html')


# send messages on whatsapp
@authorized
@app.route('/send')
def send():
    names, numbers = meow.getData(data['url'], data['api-token'], [])
    for name, number in zip(names, numbers):
        meow.sendMessage(number, name, "test\n", browser[session['id']])
    browser[session['id']].close()
    return render_template('begone.html')
