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
# COSTANTI
# inizio programmi ore 6:00
START_TIME_PROGRAMS = "06:00:00"
MAX_MESSAGE_LENGTH = 4096;


# recupero data e orario corrente: restituisce una lista con data come primo elemento e ora come secondo elemento
def get_date_time(datetime_input):
    time_date_list = datetime_input.split(" ")
    return time_date_list


# funzione per dividere i messaggi in parti di 4096 (limite di telegram)
def send_message(bot, chat_id, text: str, **kwargs):
    if len(text) <= MAX_MESSAGE_LENGTH:
        return bot.send_message(chat_id, text, **kwargs)

    parts = []
    while len(text) > 0:
        if len(text) > MAX_MESSAGE_LENGTH:
            part = text[:MAX_MESSAGE_LENGTH]
            first_lnbr = part.rfind('\n')
            if first_lnbr != -1:
                parts.append(part[:first_lnbr])
                text = text[first_lnbr + 1:]
            else:
                parts.append(part)
                text = text[MAX_MESSAGE_LENGTH:]
        else:
            parts.append(text)
            break

    msg = None
    for part in parts:
        msg = bot.send_message(chat_id, part, **kwargs)
        time.sleep(1)
    return msg  # return only the last message



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
    text_response = ""
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
            if str(int(datetime.timestamp(datetime.now() + timedelta(hours=2)))) >= str(program['startTime']) and str(int(datetime.timestamp(datetime.now() + timedelta(hours=2)))) <= str(program['endTime']):
                program_response['channel'] = channel['channelName']
                program_response['details'] = program
                #print("dentro")
                if channel['channelName'] == "Canale 5":
                    print("localTime: " + str(calendar.timegm(time.localtime())))
                    print("startTime: " + str(program['startTime']))
                    print("endTime: " + str(program['endTime']))
                    print(program_response)
                text_response += str(
                    get_date_time(datetime.strftime(datetime.fromtimestamp(program_response['details']['startTime']), "%Y-%m-%d %H:%M"))[1]
                    ) + "-" + get_date_time(
                    datetime.strftime(datetime.fromtimestamp(program_response['details']['endTime']), "%Y-%m-%d %H:%M"))[1] + " " + "*" + str(
                    program_response['channel']) + "*" + "\t" + str(program_response['details']['title']) + "\n\n"

                # context.bot.send_message(chat_id=update.message.chat_id, text=str(
                #     get_date_time(datetime.strftime(datetime.fromtimestamp(program_response['details']['startTime']), "%Y-%m-%d %H:%M"))[1]
                #     ) + "-" + get_date_time(
                #     datetime.strftime(datetime.fromtimestamp(program_response['details']['endTime']), "%Y-%m-%d %H:%M"))[1] + " " + "*" + str(
                #     program_response['channel']) + "*" + " " + str(program_response['details']['title']), parse_mode=telegram.ParseMode.MARKDOWN)

            else:
                continue
    send_message(context.bot, update.message.chat_id, text_response, parse_mode=telegram.ParseMode.MARKDOWN)

    #print(program_response)
    #context.bot.send_message(chat_id=update.message.chat_id, text=str(get_date_time(datetime.strftime(program_response['details']['startTime'], "%Y-%m-%d %H:%M:%S"))[1]
#) + "-" + str(get_date_time(datetime.strftime((program_response['details']['endTime'], "%Y-%m-%d %H:%M:%S")))[1]) + " " + str(program_response['channel']) + " " + str(program_response['details']['title']))


updater.dispatcher.add_handler(CommandHandler('ora', ora))

def dopo(update, context):
    request_time = get_date_time(datetime.strftime(datetime.fromtimestamp(time.time()), "%Y-%m-%d %H:%M:%S"))[1]

    # calcolo il giorno per l'API in base all'orario: dalle 0:00 alle 5:59 la programmazione appartiene ancora al giorno precedente
    update_message_date = update.message.date if request_time >= START_TIME_PROGRAMS else update.message.date - timedelta(
        days=1)

    # recupero la data della richiesta nel formato YYYY-MM-DD
    request_date = get_date_time(datetime.strftime(update_message_date, "%Y-%m-%d %H:%M:%S"))[0]

    # richiesta API
    req = requests.get(
        "https://tvzap.kataweb.it/ws/epg_channels_days.php?date=" + request_date + "&offset=0&limit=1000&filter=")
    response = json.loads(req.content)

    program_response = {}
    text_response = ""
    channels = response['payload']['channels']

    for channel in channels:
        stop_flag = False
        for program in channel['programs']:
            if str(int(datetime.timestamp(datetime.now() + timedelta(hours=2)))) >= str(program['endTime']) and str(
                    int(datetime.timestamp(datetime.now() + timedelta(hours=2)))) <= str(program['endTime']):
                stop_flag = True
                continue
            if stop_flag is True:
                print("dentro flag = true")
                program_response['channel'] = channel['channelName']
                program_response['details'] = program
                text_response += str(
                    get_date_time(datetime.strftime(datetime.fromtimestamp(program_response['details']['startTime']),
                                                    "%Y-%m-%d %H:%M"))[1]
                ) + "-" + get_date_time(
                    datetime.strftime(datetime.fromtimestamp(program_response['details']['endTime']),
                                      "%Y-%m-%d %H:%M"))[1] + " " + "*" + str(
                    program_response['channel']) + "*" + "\t" + str(program_response['details']['title']) + "\n\n"
            else:
                continue
    send_message(context.bot, update.message.chat_id, text_response, parse_mode=telegram.ParseMode.MARKDOWN)
    print(text_response)
updater.dispatcher.add_handler(CommandHandler('dopo', dopo))

updater.start_polling()
updater.idle()
