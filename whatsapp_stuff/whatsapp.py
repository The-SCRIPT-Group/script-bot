import base64
import json
import os
import re
from time import sleep

import requests
from emoji import emojize
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

whatsapp_api = 'https://api.whatsapp.com/send?phone=91'  # Format of url to open chat with someone

home = '' if re.match('.+whatsapp_stuff', os.getcwd()) else 'whatsapp_stuff/'

driver = {
    'firefox': webdriver.Firefox,
    'chrome': webdriver.Chrome
}


def waitTillElementLoaded(browser, element):
    try:
        element_present = ec.presence_of_element_located((By.XPATH, element))
        WebDriverWait(browser, 10000).until(element_present)
    except TimeoutException:
        print('Timed out waiting for page to load')


def waitTillLinkLoaded(browser, element):
    try:
        element_present = ec.presence_of_element_located((By.LINK_TEXT, element))
        WebDriverWait(browser, 10000).until(element_present)
    except TimeoutException:
        print('Timed out waiting for page to load')


# Method to send a message to someone
def sendMessage(num, name, msg, browser):
    api = whatsapp_api + str(num)  # Specific url
    print(api, name)
    browser.get(api)  # Open url in browser

    waitTillElementLoaded(browser, '//*[@id="action-button"]')  # Wait till send message button is loaded
    browser.find_element_by_xpath('//*[@id="action-button"]').click()  # Click on "send message" button

    waitTillLinkLoaded(browser, "use WhatsApp Web")  # wait till the link is loaded
    browser.find_element_by_link_text("use WhatsApp Web").click()  # click on link to open chat

    # Wait till the text box is loaded onto the screen, then type out and send the full message
    waitTillElementLoaded(browser, '/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div[2]/div/div[2]')

    browser.find_element_by_xpath(
        '/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div[2]/div/div[2]'
    ).send_keys(emojize(msg.format(name), use_aliases=True))

    sleep(3)  # Just so that we can supervise, otherwise it's too fast

    return name


def startSession(browser_type, driver_path, bot, message):
    browser = driver[browser_type](executable_path=driver_path)
    browser.get('https://web.whatsapp.com/')
    print('whatsapp opened')

    # Get the qr image
    waitTillElementLoaded(browser, '/html/body/div[1]/div/div/div[2]/div[1]/div/div[2]/div/img')
    print('qr loaded')
    meow = open(home + 'qr.png', 'wb')
    meow.write(base64.b64decode(browser.find_element_by_xpath(
        '/html/body/div[1]/div/div/div[2]/div[1]/div/div[2]/div/img').get_attribute('src')[22:]))
    print('downlaoded qr')
    meow.close()
    print('qr saved')

    return browser


def getData(url, token, ids):
    names_list = []  # List of all names
    numbers_list = []  # List of all numbers

    # Get data from our API
    api_data = json.loads(requests.get(url, headers={'Authorization': token}, ).text)

    if ids == 'all':
        ids = map(int, api_data.keys())

    # Add names and numbers to respective lists
    for user_id in api_data:
        if int(user_id) in ids:
            names_list.append(api_data[user_id]['name'])
            numbers_list.append(api_data[user_id]['phone'].split('|')[-1])

    return names_list, numbers_list
