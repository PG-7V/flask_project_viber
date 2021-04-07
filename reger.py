from flask import Flask, request, Response
from flask_sslify import SSLify
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
import logging
import config
import csv
import time
from viberbot.api.viber_requests import ViberConversationStartedRequest

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
viber = Api(BotConfiguration(
    name='createPDF',
    avatar='',
    auth_token=config.token
))


def parse(reader):
    list_info = []
    link = ''  #
    descr = ''  #
    char = ''  #
    for row in reader:
        if 'Размеры' in row['Description']:
            descr = ''  #
            link = ''  #
            art = ''  #
            count_ = 0
            price = ''  #
            char = ''  #
            quant = ''
            descr = row['Description']
            link = row['Photo']
            char = row['Characteristics:Состав']
        elif not row['Description']:
            if row['SKU']:
                if 'д' in row['SKU']:
                    continue
                elif 'т' in row['SKU']:
                    continue
                elif row['Quantity'] == "0":
                    continue
                else:
                    art = row['SKU']
                    if 'Артикул' in row['Title']:
                        art = f'Артикул {row["SKU"]}'
                    price = float(round((float(row['Price'])), 2))
                    price = f'{price}'
                    if row['Quantity']:
                        info_f = {'link': link,
                                  'art': art,
                                  'descr': descr,
                                  'char': char,
                                  'price': price, }
                        list_info.append(info_f)
    return list_info


def search_info(art, reader):
    index = 0
    descr = ''
    art_if = ''
    link = ''
    price = 0
    char = ''
    for row in reader:
        if row['Title'] and row['Description']:
            if art in row['Title']:
                descr = row['Description'].strip()
                char = row['Characteristics:Состав'].strip()
                index = 1
                continue
        elif index:
            if art in row['SKU'].strip():
                if 'Артикул' in row['Title']:
                    art_if = 'Артикул ' + row['SKU'].strip()
                    price = row['Price'].strip()
                    link = row['Photo'].strip()
                    break
                elif row['SKU'].strip().split(' ')[1] == art:
                    art_if = row['SKU'].strip()
                    price = row['Price'].strip()
                    link = row['Photo'].strip()
                    break

    data = {'art_if': art_if,
            'descr': descr,
            'price': price,
            'link': link,
            'char': char,
            }

    return data


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

    logging.getLogger().debug("received request. post data: {0}".format(request.get_data()))
    # every viber message is signed, you can verify the signature using this method
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data().decode('utf8'))
    def v_r(texxt):
        viber.send_messages(viber_request.sender.id, [
            TextMessage(text=texxt, keyboard={
                "DefaultHeight": True,
                "BgColor": "#FFFFFF",
                "Type": "keyboard",
                "Buttons": [get_buttons('Артикул и Размеры'),
                            get_buttons('Артикул и Размеры + Цена'),
                            get_buttons('Артикул, Размеры, Состав + Цена'),
                            get_buttons('Все в наличии')]
            })])

    if isinstance(viber_request, ViberMessageRequest):
        if viber_request.message.text == 'Настройки параметров':
            v_r('Выберите параметры отображения.')
        elif viber_request.message.text == 'Артикул и Размеры':
            para = 0
            v_r('Установлены параметры "Артикул и Размеры". Введите Артикул.')
        elif viber_request.message.text == 'Артикул и Размеры + Цена':
            para = 1
            v_r('Установлены параметры "Артикул и Размеры + Цена". Введите Артикул.')
        elif viber_request.message.text == 'Артикул, Размеры, Состав + Цена':
            # global para
            para = 2
            v_r('Установлены параметры "Артикул, Размеры, Состав + Цена". Введите Артикул.')
        else:
            with open('for_pdf.csv', encoding='utf-8') as f:
                fieldnames = ['Tilda UID', 'Brand', 'SKU', 'Mark', 'Category', 'Title', 'Description', 'Text', 'Photo',
                              'Price', 'Quantity', 'Price Old', 'Editions', 'Modifications', 'External ID',
                              'Parent UID',
                              'Characteristics:Состав', 'Weight', 'Length', 'Width', 'Height', 'SEO title', 'SEO descr',
                              'FB title', 'FB descr']
                reader = csv.DictReader(f, delimiter=";", fieldnames=fieldnames)
                if viber_request.message.text == 'Все в наличии':
                    if not rows:
                        rows = parse(reader)
                    for _ in range(len(rows)):
                        r = rows[0]
                        llink = r['link']
                        lart = r['art']
                        ldescr = r['descr']
                        lchar = r['char']
                        try:
                            lprice = r['price'].split('.')[0]
                        except:
                            lprice = ''
                        time.sleep(1)
                        viber.send_messages(viber_request.sender.id, [PictureMessage(media=llink)])
                        if para == 1:
                            ltext_message = f'{lart}\n{ldescr}'
                        elif para == 2:
                            ltext_message = f'{lart}\n{ldescr}\n{lchar}'
                        time.sleep(1)
                        v_r(ltext_message)
                        time.sleep(1)
                        if para:
                            v_r(f'Цена {lprice}')
                        time.sleep(2)
                        rows.pop(0)
                        if not rows:
                            v_r('Все данные выгружены. Сформируйте новый запрос.')
                else:
                    udata = search_info(viber_request.message.text.strip(), reader)
                    uart_if = udata['art_if']
                    udescr = udata['descr']
                    try:
                        uprice = udata['price'].split('.')[0]
                    except:
                        uprice = ''
                    ulink = udata['link']
                    uchar = udata['char']
                    if ulink:
                        viber.send_messages(viber_request.sender.id, [PictureMessage(media=ulink)])
                        text_message = f'{uart_if}\n{udescr}'
                        time.sleep(0.5)
                        if para == 1:
                            text_message = f'{uart_if}\n{udescr}'
                        elif para == 2:
                            text_message = f'{uart_if}\n{udescr}\n{uchar}'
                    else:
                        text_message = f'Артикул {viber_request.message.text} отсутствует.'
                    v_r(text_message)
                    time.sleep(0.5)
                    if ulink and para:
                        v_r(f'Цена {uprice}')
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
        viber.send_messages(viber_request.user.id, [
            TextMessage(text="Здравствуйте!\n Нажмите\n'Настройки параметров'", keyboard=keyboard)
        ])

    return Response(status=200)


if __name__ == "__main__":
    # context = ('server.crt', 'server.key')
    application.run(host='0.0.0.0', port=5000, debug=True)