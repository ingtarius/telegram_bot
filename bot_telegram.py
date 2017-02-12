from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import MessageHandler, Filters
import logging

# For yandex
import requests
import os
import sys
import socket
import re
from datetime import datetime, timedelta
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


updater = Updater(token='TELEGRAM_BOT_TOKEN')
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


# Define start message for /start command. Welcome text
def start(bot, update): 
   bot.sendMessage(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

# CAPS function, just for tests
def caps(bot, update, args):
   text_caps = ' '.join(args).upper()
   bot.sendMessage(chat_id=update.message.chat_id, text=text_caps)

# Unknown command
def unknown(bot, update):
   bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")

# Help handler
def help(bot, update):
   bot.sendMessage(chat_id=update.message.chat_id, text="My command is: \n /help \n /start \n /caps")

def yandexrasp(bot, update, args):
   # Variables
   API_KEY='YANDEX_API_KEY'
   BASE_URL='https://api.rasp.yandex.net/v1.0/search/?'

   if args[0] == "work":
      FROM ='c10743' # Одинцово
      TO ='c213' # Белорусская
   elif args[0] == "home":
      TO ='c10743' # Одинцово
      FROM ='c213' # Белорусская
   else:
      bot.sendMessage(chat_id=update.message.chat_id, text="Unknown destination. Use home or work")
      sys.exit(1)

   DATE=datetime.strftime(datetime.now(), "%Y-%m-%d")
   payload="apikey=" + API_KEY + "&format=json&from=" + FROM + "&to=" + TO + "&lang=ru&page=1&date=" + DATE + "&transport_types=suburban"

   try:
      url = requests.get(BASE_URL + payload, verify=False, timeout=30)
   except requests.exceptions.RequestException as e:
      bot.sendMessage(chat_id=update.message.chat_id, text="Cant make request. Terminated")
      sys.exit(1)

   data = url.json()
   count = 0
   answer = 'Поезда в ближайший час: \n'
   for line in data['threads']:
      time_departure = datetime.strptime(line['departure'], '%Y-%m-%d %H:%M:%S')
      if time_departure > datetime.now() and time_departure < datetime.now() + timedelta(hours=1):
         answer = answer + 'Поезд: ' + line['thread']['title']
         answer = answer + '\n       Отправление: ' + line['from']['title'] + ' в ' + line['departure'] + '\n'
         answer = answer + '       Прибытие: ' + line['to']['title'] + ' в ' + line['arrival'] + '\n'
   bot.sendMessage(chat_id=update.message.chat_id, text=str(answer))


# Add functins to bot
help_handler = CommandHandler('help', help)
start_handler = CommandHandler('start', start)
caps_handler = CommandHandler('caps', caps, pass_args=True)
yandexrasp_handler = CommandHandler('rasp', yandexrasp, pass_args=True)
unknown_handler = MessageHandler(Filters.command, unknown)

dispatcher.add_handler(help_handler)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(caps_handler)
dispatcher.add_handler(yandexrasp_handler)
dispatcher.add_handler(unknown_handler)

#updater.idle()
updater.start_polling()
