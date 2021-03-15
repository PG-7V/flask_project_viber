from flask import Flask, request, Response
from flask_sslify import SSLify
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
import logging
import csv
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
viber = Api(BotConfiguration(
    name='createPDF',
    avatar='',
    auth_token='4d09a6058027d05d-dba5d816e649c704-c151f2937e2b0164'
))


def search_info(art):
    with open('for_pdf.csv', encoding='utf-8') as f:
        fieldnames = ['Tilda UID', 'Brand', 'SKU', 'Mark', 'Category', 'Title', 'Description', 'Text', 'Photo',
                      'Price', 'Quantity', 'Price Old', 'Editions', 'Modifications', 'External ID', 'Parent UID',
                      'Characteristics:Состав', 'Weight', 'Length', 'Width', 'Height']
        reader = csv.DictReader(f, delimiter=";", fieldnames=fieldnames)
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


def get_buttons(text_):
    return {
                    "Columns": 6,
                    "Rows": 1,
                    "BgColor": "#e6f5ff",
                    "BgLoop": True,
                    "ActionType": "reply",
                    "ActionBody": text_,
                    "ReplyType": "message",
                    "Text": text_
                }


@application.route('/4d09a6058027d05d-dba5d816e649c704-c151f2937e2b0164/', methods=['POST'])
def incoming():
    logging.getLogger().debug("received request. post data: {0}".format(request.get_data()))
    # every viber message is signed, you can verify the signature using this method
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    # this library supplies a simple way to receive a request object
    viber_request = viber.parse_request(request.get_data().decode('utf8'))
    # PARA = False

    if isinstance(viber_request, ViberMessageRequest):
        print(viber_request)
        if viber_request.message.text == 'Настройки параметров':
            viber.send_messages(viber_request.sender.id, [
                TextMessage(text='Выберите параметры отображения.', keyboard={
            "DefaultHeight": True,
            "BgColor": "#FFFFFF",
            "Type": "keyboard",
            "Buttons": [get_buttons('Пo умолчанию'), get_buttons('Отобразить все')]
                })])
        elif viber_request.message.text == 'Пo умолчанию':

            global para
            para = 0
            viber.send_messages(viber_request.sender.id, [
                TextMessage(text='Установлены параметры "По умолчанию". Введите Артикул.', keyboard={
                    "DefaultHeight": True,
                    "BgColor": "#FFFFFF",
                    "Type": "keyboard",
                    "Buttons": [get_buttons('Пo умолчанию'), get_buttons('Отобразить все')]
                })])
        elif viber_request.message.text == 'Отобразить все':
            # global para
            para = 1
            viber.send_messages(viber_request.sender.id, [
                TextMessage(text='Установлены параметры "Отобразить все". Введите Артикул.', keyboard={
                    "DefaultHeight": True,
                    "BgColor": "#FFFFFF",
                    "Type": "keyboard",
                    "Buttons": [get_buttons('Пo умолчанию'), get_buttons('Отобразить все')]
                })])
        else:
            para=para
            udata = search_info(viber_request.message.text.strip())
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
                text_message = f'{uart_if}\n{uchar}'
                if para:
                    text_message = f'{uart_if}\n{uchar}\nЦена {uprice}\n{udescr}'
            else:
                text_message = f'Артикул {viber_request.message.text} отсутствует.'
            viber.send_messages(viber_request.sender.id, [
                TextMessage(text=text_message, keyboard={
                    "DefaultHeight": True,
                    "BgColor": "#FFFFFF",
                    "Type": "keyboard",
                    "Buttons": [get_buttons('Пo умолчанию'), get_buttons('Отобразить все')]
                })])


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