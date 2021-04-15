from flask import Flask, request, Response
from flask_sslify import SSLify
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
import logging
import config
import json
import requests
import time
from viberbot.api.viber_requests import ViberConversationStartedRequest, ViberFailedRequest

from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.messages import (
    TextMessage,
    ContactMessage,
    PictureMessage,
    VideoMessage,
    FileMessage,
)


application = Flask(__name__)
sslify = SSLify(application)
para = 0
rows = []
messege_tokens = []
viber = Api(BotConfiguration(
    name='createPDF',
    avatar='',
    auth_token=config.token
))


def parse(data_j):
    list_info = []
    for product in data_j['products']:
        try:
            link = json.loads(product['gallery'])[0]['img']
        except:
            # print('Error parse "gallery"')
            continue
        try:
            title = product['title'].strip()  #Артикул
        except:
            title = ''
        try:
            sku = product['sku']
        except:
            sku = ''

        try:
            quantity = int(product['quantity'])  # Наличие
        except:
            quantity = ''
        try:
            descr = product['descr']  # Размер
        except:
            descr = ''
        if product['price']:
            price = float(round((float(product['price'])), 2))
            price = f'{price}'
        else:
            price = ''
        try:
            character = product['characteristics'][0]['value']
        except:
            character = ''


        info_f = {'link': link,
                  'sku': sku,
                  'title': title,
                  'quantity': quantity,
                  'descr': descr,
                  'price': price,
                  'character': character,
                  }
        list_info.append(info_f)
    return list_info


def search_info(art, func):
    skus = []
    for i in func:
        if art.strip() == i['sku'].strip():
            skus.append(i)
    return skus


def get_buttons(textd):
    return {
        "Columns": 6,
        "Rows": 1,
        "BgColor": "#e6f5ff",
        "BgLoop": True,
        "ActionType": "reply",
        "ActionBody": textd,
        "ReplyType": "message",
        "Text": textd
    }


@application.route(f'/{config.token}/', methods=['POST'])
def incoming():
    global para
    global rows
    global messege_tokens
    if len(messege_tokens) > 5000:
        messege_tokens = []
    url_j = config.url

    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data().decode('utf8'))
    if isinstance(viber_request, ViberFailedRequest):
        logging.getLogger().warning("client failed receiving message. failure: {0}".format(viber_request))
    elif isinstance(viber_request, ViberMessageRequest):
        if viber_request.message.text == 'Настройки параметров':
            vrt = viber_request.message_token
            if not vrt in messege_tokens:
                viber.send_messages(viber_request.sender.id, [
                    TextMessage(text='Выберите параметры отображения.', keyboard={
                        "DefaultHeight": True,
                        "BgColor": "#FFFFFF",
                        "Type": "keyboard",
                        "Buttons": [get_buttons('Артикул и Размеры'),
                                    get_buttons('Артикул и Размеры + Цена'),
                                    get_buttons('Артикул, Размеры, Состав + Цена'),
                                    get_buttons('Все в наличии')]
                    })])
                messege_tokens.append(vrt)
        elif viber_request.message.text == 'Артикул и Размеры':
            vrt = viber_request.message_token
            if not vrt in messege_tokens:
                para = 0
                viber.send_messages(viber_request.sender.id, [
                    TextMessage(text='Установлены параметры "Артикул и Размеры". Введите Артикул.', keyboard={
                        "DefaultHeight": True,
                        "BgColor": "#FFFFFF",
                        "Type": "keyboard",
                        "Buttons": [get_buttons('Артикул и Размеры'),
                                    get_buttons('Артикул и Размеры + Цена'),
                                    get_buttons('Артикул, Размеры, Состав + Цена'),
                                    get_buttons('Все в наличии')]
                    })])
                messege_tokens.append(vrt)
        elif viber_request.message.text == 'Артикул и Размеры + Цена':
            vrt = viber_request.message_token
            if not vrt in messege_tokens:
                para = 1
                viber.send_messages(viber_request.sender.id, [
                    TextMessage(text='Установлены параметры "Артикул и Размеры + Цена". Введите Артикул.', keyboard={
                        "DefaultHeight": True,
                        "BgColor": "#FFFFFF",
                        "Type": "keyboard",
                        "Buttons": [get_buttons('Артикул и Размеры'),
                                    get_buttons('Артикул и Размеры + Цена'),
                                    get_buttons('Артикул, Размеры, Состав + Цена'),
                                    get_buttons('Все в наличии')]
                    })])
                messege_tokens.append(vrt)
        elif viber_request.message.text == 'Артикул, Размеры, Состав + Цена':
            vrt = viber_request.message_token
            if not vrt in messege_tokens:
                para = 2
                viber.send_messages(viber_request.sender.id, [
                    TextMessage(text='Установлены параметры "Артикул, Размеры, Состав + Цена". Введите Артикул.', keyboard={
                        "DefaultHeight": True,
                        "BgColor": "#FFFFFF",
                        "Type": "keyboard",
                        "Buttons": [get_buttons('Артикул и Размеры'),
                                    get_buttons('Артикул и Размеры + Цена'),
                                    get_buttons('Артикул, Размеры, Состав + Цена'),
                                    get_buttons('Все в наличии')]
                    })])
                messege_tokens.append(vrt)
        elif viber_request.message.text == 'Все в наличии':
            vrt = viber_request.message_token
            if not vrt in messege_tokens:
                rows = []
                data_j = requests.get(url_j).json()
                rows = parse(data_j)  # запрос json
                r = rows[0]
                llink = r['link']
                lart = r['title']
                ldescr = r['descr']
                lchar = r['character']
                try:
                    lprice = r['price']
                except:
                    lprice = ''
                time.sleep(1)
                viber.send_messages(viber_request.sender.id, [PictureMessage(media=llink, keyboard={
                    "DefaultHeight": True,
                    "BgColor": "#FFFFFF",
                    "Type": "keyboard",
                    "Buttons": [get_buttons('Далее'),
                                get_buttons('Все в наличии')]
                })])
                # print('all send media')
                messege_tokens.append(vrt)
                if para == 1:
                    ltext_message = f'{lart}\n{ldescr}'
                elif para == 2:
                    ltext_message = f'{lart}\n{ldescr}\n{lchar}'
                else:
                    ltext_message = f'{lart}\n{ldescr}'
                time.sleep(1)
                viber.send_messages(viber_request.sender.id, [
                    TextMessage(text=ltext_message, keyboard={
                        "DefaultHeight": True,
                        "BgColor": "#FFFFFF",
                        "Type": "keyboard",
                        "Buttons": [get_buttons('Далее'),
                                    get_buttons('Все в наличии')]
                    })])
                messege_tokens.append(viber_request.message_token)
                time.sleep(0.5)
                if para:
                    viber.send_messages(viber_request.sender.id, [
                        TextMessage(text=f'Цена {lprice}', keyboard={
                            "DefaultHeight": True,
                            "BgColor": "#FFFFFF",
                            "Type": "keyboard",
                            "Buttons": [get_buttons('Далее'),
                                        get_buttons('Все в наличии')]
                        })])
                    messege_tokens.append(viber_request.message_token)
                time.sleep(0.5)
                rows.pop(0)

                if not rows:
                    viber.send_messages(viber_request.sender.id, [
                        TextMessage(text='Все данные выгружены. Сформируйте новый запрос.', keyboard={
                            "DefaultHeight": True,
                            "BgColor": "#FFFFFF",
                            "Type": "keyboard",
                            "Buttons": [get_buttons('Артикул и Размеры'),
                                        get_buttons('Артикул и Размеры + Цена'),
                                        get_buttons('Артикул, Размеры, Состав + Цена'),
                                        get_buttons('Все в наличии')]
                        })])
                    messege_tokens.append(viber_request.message_token)

        elif viber_request.message.text == 'Далее':
            vrt = viber_request.message_token
            if not vrt in messege_tokens:
                if rows:
                    r = rows[0]
                    llink = r['link']
                    lart = r['title']
                    ldescr = r['descr']
                    lchar = r['character']
                    try:
                        lprice = r['price'].split('.')[0]
                    except:
                        lprice = ''
                    time.sleep(0.5)
                    vrt = viber_request.message_token
                    # if loa_d:
                    viber.send_messages(viber_request.sender.id, [PictureMessage(media=llink, keyboard={
                        "DefaultHeight": True,
                        "BgColor": "#FFFFFF",
                        "Type": "keyboard",
                        "Buttons": [get_buttons('Далее'),
                                    get_buttons('Настройки параметров'),
                                    get_buttons('Все в наличии')]
                    })])
                    messege_tokens.append(viber_request.message_token)
                    if para == 1:
                        ltext_message = f'{lart}\n{ldescr}'
                    elif para == 2:
                        ltext_message = f'{lart}\n{ldescr}\n{lchar}'
                    else:
                        ltext_message = f'{lart}\n{ldescr}'
                    time.sleep(1)
                    viber.send_messages(viber_request.sender.id, [
                        TextMessage(text=ltext_message, keyboard={
                            "DefaultHeight": True,
                            "BgColor": "#FFFFFF",
                            "Type": "keyboard",
                            "Buttons": [get_buttons('Далее'),
                                        get_buttons('Настройки параметров'),
                                        get_buttons('Все в наличии')]
                        })])
                    messege_tokens.append(viber_request.message_token)
                    time.sleep(0.5)
                    if para:
                        viber.send_messages(viber_request.sender.id, [
                            TextMessage(text=f'Цена {lprice}', keyboard={
                                "DefaultHeight": True,
                                "BgColor": "#FFFFFF",
                                "Type": "keyboard",
                                "Buttons": [get_buttons('Далее'),
                                            get_buttons('Настройки параметров'),
                                            get_buttons('Все в наличии')]
                            })])
                    time.sleep(0.5)
                    rows.pop(0)
                    messege_tokens.append(viber_request.message_token)
                else:
                    viber.send_messages(viber_request.sender.id, [
                        TextMessage(text='Все данные выгружены. Сформируйте новый запрос.', keyboard={
                            "DefaultHeight": True,
                            "BgColor": "#FFFFFF",
                            "Type": "keyboard",
                            "Buttons": [get_buttons('Артикул и Размеры'),
                                        get_buttons('Артикул и Размеры + Цена'),
                                        get_buttons('Артикул, Размеры, Состав + Цена'),
                                        get_buttons('Все в наличии')]
                        })])
                    messege_tokens = []
                    messege_tokens.append(viber_request.message_token)
        else:  # Поиск отдельного артикула.
            vrt = viber_request.message_token
            if not vrt in messege_tokens:
                rows = []
                data_j = requests.get(url_j).json()
                r_ows = parse(data_j)  # запрос json
                for r_ow in r_ows:
                    if viber_request.message.text.strip() in r_ow['title']:
                        rows.append(r_ow)
                if rows:
                    r = rows[0]
                    llink = r['link']
                    lart = r['title']
                    ldescr = r['descr']
                    lchar = r['character']
                    try:
                        lprice = r['price']
                    except:
                        lprice = ''
                    time.sleep(0.5)
                    viber.send_messages(viber_request.sender.id, [PictureMessage(media=llink, keyboard={
                        "DefaultHeight": True,
                        "BgColor": "#FFFFFF",
                        "Type": "keyboard",
                        "Buttons": [get_buttons('Далее'),
                                    get_buttons('Все в наличии')]
                    })])
                    messege_tokens.append(vrt)
                    if para == 1:
                        ltext_message = f'{lart}\n{ldescr}'
                    elif para == 2:
                        ltext_message = f'{lart}\n{ldescr}\n{lchar}'
                    else:
                        ltext_message = f'{lart}\n{ldescr}'
                    time.sleep(1)
                    viber.send_messages(viber_request.sender.id, [
                        TextMessage(text=ltext_message, keyboard={
                            "DefaultHeight": True,
                            "BgColor": "#FFFFFF",
                            "Type": "keyboard",
                            "Buttons": [get_buttons('Далее'),
                                        get_buttons('Все в наличии')]
                        })])
                    messege_tokens.append(viber_request.message_token)
                    time.sleep(0.5)
                    if para:
                        viber.send_messages(viber_request.sender.id, [
                            TextMessage(text=f'Цена {lprice}', keyboard={
                                "DefaultHeight": True,
                                "BgColor": "#FFFFFF",
                                "Type": "keyboard",
                                "Buttons": [get_buttons('Далее'),
                                            get_buttons('Все в наличии')]
                            })])
                    time.sleep(0.5)
                    rows.pop(0)
                    messege_tokens.append(viber_request.message_token)
                    if not rows:
                        viber.send_messages(viber_request.sender.id, [
                            TextMessage(text='Все данные выгружены. Сформируйте новый запрос.', keyboard={
                                "DefaultHeight": True,
                                "BgColor": "#FFFFFF",
                                "Type": "keyboard",
                                "Buttons": [get_buttons('Артикул и Размеры'),
                                            get_buttons('Артикул и Размеры + Цена'),
                                            get_buttons('Артикул, Размеры, Состав + Цена'),
                                            get_buttons('Все в наличии')]
                            })])
                    messege_tokens.append(viber_request.message_token)
                elif not rows:
                    viber.send_messages(viber_request.sender.id, [
                        TextMessage(text=f'Артикул {viber_request.message.text} отсутствует.', keyboard={
                            "DefaultHeight": True,
                            "BgColor": "#FFFFFF",
                            "Type": "keyboard",
                            "Buttons": [get_buttons('Артикул и Размеры'),
                                        get_buttons('Артикул и Размеры + Цена'),
                                        get_buttons('Артикул, Размеры, Состав + Цена'),
                                        get_buttons('Все в наличии')]
                        })])
                messege_tokens.append(viber_request.message_token)

    elif isinstance(viber_request, ViberConversationStartedRequest):
        keyboard = {
            "DefaultHeight": True,
            "BgColor": "#FFFFFF",
            "Type": "keyboard",
            "Buttons": [
                {
                    "Columns": 6,
                    "Rows": 1,
                    "BgColor": "#e6f5ff",
                    "BgLoop": True,
                    "ActionType": "reply",
                    "ActionBody": "Настройки параметров",
                    "ReplyType": "message",
                    "Text": "Настройки параметров"
                }
            ]
        }
        vrt = viber_request.message_token
        if not vrt in messege_tokens:
            viber.send_messages(viber_request.user.id, [
                TextMessage(text="Здравствуйте!\n Нажмите\n'Настройки параметров'", keyboard=keyboard)
            ])
            messege_tokens.append(vrt)

    return Response(status=200)


if __name__ == "__main__":
    # context = ('server.crt', 'server.key')
    application.run(host='0.0.0.0', port=5000, debug=True)