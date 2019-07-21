import telegram
from telegram.ext import Updater, CommandHandler
import requests
import re
import calendar
import time
from datetime import datetime, timedelta
import json
import logging
import ssl


#logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


class style:
   BOLD = '\033[1m'
   END = '\033[0m'

# recupero data e orario corrente: restituisce una lista con data come primo elemento e ora come secondo elemento


def get_date_time(datetime_input):
    time_date_list = datetime_input.split(" ")
    return time_date_list


# print (today)
# esempio di saluto
def hello(update, context):
    print()
    update.message.reply_text(
        'Hello {}'.format(update.message.chat.first_name))


updater = Updater('829880140:AAErm0t9GKRpDNzVUKcAkSt4lZDdtYPhqlM', use_context=True)

updater.dispatcher.add_handler(CommandHandler('hello', hello))


# esempio /start
def start(update, context):
    print(update.message)
    context.bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")
start_handler = CommandHandler('start', start)
updater.dispatcher.add_handler(start_handler)

# comando /ora
def get_actual_program(response, request_time):
    program_response = {}
    channels = response['payload']['channels']
    #print("channels: " + str(channels))
    for channel in channels:
        for program in channel['programs']:
            #print("programs:" + str(channel['programs']))
            #print("request_time: ")
            #print(request_time)
            #print("startTime: " + str(program['startTime']))
            #print("endTime: " + str(program['endTime']))
            if str(request_time) >= str(program['startTime']) and str(request_time) <= str(program['endTime']):
                program_response['channel'] = channel['channelName']
                program_response['details'] = program
                #print(program_response)
                return program_response
            else:
                continue

def ora(update, context):
    # inizio programmi ore 6:00
    START_TIME_PROGRAMS = "06:00:00"

    #print("Update: ")
    #print(update)
    # recupero l'ora della richiesta nel formato hh:mm:ss
    request_time = get_date_time(datetime.strftime(datetime.fromtimestamp(time.time()), "%Y-%m-%d %H:%M:%S"))[1]
    print("update.message.date" + str(update.message.date))
    print("requestTime: " + request_time)
    # calcolo il giorno per l'API in base all'orario: dalle 0:00 alle 5:59 la programmazione appartiene ancora al giorno precedente
    update_message_date = update.message.date if request_time >= START_TIME_PROGRAMS else update.message.date - timedelta(days=1)

    # recupero la data della richiesta nel formato YYYY-MM-DD
    request_date = get_date_time(datetime.strftime(update_message_date, "%Y-%m-%d %H:%M:%S"))[0]

    print(request_date)
    # richiesta API
    req =  requests.get("https://tvzap.kataweb.it/ws/epg_channels_days.php?date=" + request_date + "&offset=0&limit=1000&filter=")
    response = json.loads(req.content)

    #program_response = get_actual_program(response, int(datetime.timestamp(update.message.date)))
    program_response = {}
    channels = response['payload']['channels']
    # print("channels: " + str(channels))
    for channel in channels:
        for program in channel['programs']:
            #print("ChannelName!!!:" + str(channel['channelName']))
            #if channel['channelName'] == "Canale 5":
                # print("primo: " + str(int(datetime.timestamp(update.message.date))))
                # print("secondo(time)" + str(calendar.timegm(time.localtime())))
                # print("request_time: ")
                # print(str(int(datetime.timestamp(update.message.date))))
                # print("startTime: " + str(program['startTime']))
                # print("endTime: " + str(program['endTime']))
                #print(str(int(datetime.timestamp(update.message.date))))
            # print("timestamp attuale: " + str(calendar.timegm(time.localtime())))
            # print("start: " + str(program['startTime']))
            # print("end: " + str(program['endTime']))
            if str(calendar.timegm(time.localtime())) >= str(program['startTime']) and str(calendar.timegm(time.localtime())) <= str(program['endTime']):
                program_response['channel'] = channel['channelName']
                program_response['details'] = program
                #print("dentro")
                if channel['channelName'] == "Canale 5":
                    print("localTime: " + str(calendar.timegm(time.localtime())))
                    print("startTime: " + str(program['startTime']))
                    print("endTime: " + str(program['endTime']))
                    print(program_response)
                context.bot.send_message(chat_id=update.message.chat_id, text=str(
                    get_date_time(datetime.strftime(datetime.fromtimestamp(program_response['details']['startTime']), "%Y-%m-%d %H:%M"))[1]
                    ) + "-" + get_date_time(
                    datetime.strftime(datetime.fromtimestamp(program_response['details']['endTime']), "%Y-%m-%d %H:%M"))[1] + " " + str(
                    program_response['channel']) + " " + str(program_response['details']['title']))

            else:
                continue

    #print(program_response)
    #context.bot.send_message(chat_id=update.message.chat_id, text=str(get_date_time(datetime.strftime(program_response['details']['startTime'], "%Y-%m-%d %H:%M:%S"))[1]
#) + "-" + str(get_date_time(datetime.strftime((program_response['details']['endTime'], "%Y-%m-%d %H:%M:%S")))[1]) + " " + str(program_response['channel']) + " " + str(program_response['details']['title']))


updater.dispatcher.add_handler(CommandHandler('ora', ora))


updater.start_polling()
updater.idle()
