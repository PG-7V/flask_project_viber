import json
import logging

from viberbot.api.messages import PictureMessage

import template_csv

import requests
from flask import Flask, request, Response
from flask_sslify import SSLify
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.url_message import URLMessage
from viberbot.api.viber_requests import ViberFailedRequest, ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest

app = Flask(__name__)
sslify = SSLify(app)
viber = Api(BotConfiguration(
    name='createPDF',
    avatar='',
    auth_token='4d09a6058027d05d-dba5d816e649c704-c151f2937e2b0164'
))

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

COUNTRIES = (
    ('all_parametrs', 'Дополнительно')
)
PARAMETR_S = 'home'

def get_buttons(action_type, items):
    return [{
        "Columns": 6,
        "Rows": 1,
        "BgColor": "#e6f5ff",
        "BgLoop": True,
        "ActionType": 'reply',
        "ActionBody": "{action_type}|{value}".format(action_type=action_type, value=item[0]),
        "ReplyType": "message",
        "Text": item[1]
    } for item in items]


@app.route('/4d09a6058027d05d-dba5d816e649c704-c151f2937e2b0164/', methods=['POST'])
def incoming():
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data())

    if isinstance(viber_request, ViberMessageRequest):
        message = viber_request.message
        text = message.text
        text = text.strip().split('|')
        text_type = text[0]
        text_message = ''
        ulink = ''

        tracking_data = message.tracking_data
        if tracking_data is None:
            tracking_data = {}
        else:
            tracking_data = json.loads(tracking_data)

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
                    "ActionBody": "home",
                    "ReplyType": "message",
                    "Text": "По умолчанию"
                },
                {
                    "Columns": 6,
                    "Rows": 2,
                    "BgColor": "#e6f5ff",
                    "BgLoop": True,
                    "ActionType": "reply",
                    "ActionBody": "ho",
                    "ReplyType": "message",
                    "Text": "По"
                }
            ]
        }
        is_finished = False
        buttons = {}

        if text_type == 'home':
            PARAMETR_S = 'home'
            text_message = 'Установлены параметры По умолчанию. \n Введите артикул.'

        elif text_type == 'all_parametrs':
            PARAMETR_S = 'all_parametrs'
            text_message = 'Установлены параметры Дополнительно. \n Введите артикул.'

        # elif text_type == 'search_vacancies':
        #     tracking_data = {}
        #     countries = [country[1] for country in COUNTRIES]
        #     text_message = 'Дополнительные параметры: {countries}. Пожалуйста, выберите одну из них.'\
        #         .format(countries=', '.join(countries))
        #     buttons = get_buttons('select_country', COUNTRIES)

        else:
            ulink = ''
            udata = template_csv.search_info(viber_request.message.text.strip())
            uart_if = udata['art_if']
            udescr = udata['descr']
            uprice = udata['price']
            ulink = udata['link']
            uchar = udata['char']

            if not ulink:
                text_message = f'Артикул {text_type} отсутствует.'
            else:
                viber.send_messages(viber_request.sender.id, [PictureMessage(media=ulink)])
                text_message = f'{uart_if}\n{uchar}'
                if PARAMETR_S == 'all_parametrs':
                    text_message = f'{uart_if}\n{uchar}\n{uprice}\n{udescr}'

        messages = []
        keyboard_buttons = keyboard.get('Buttons', [])
        keyboard_buttons.extend(buttons)
        keyboard['Buttons'] = keyboard_buttons
        keyboard = keyboard if keyboard.get('Buttons') else None
        tracking_data = json.dumps(tracking_data)
        messages.append(TextMessage(text=text_message,
                                    keyboard=keyboard,
                                    tracking_data=tracking_data))

        viber.send_messages(viber_request.sender.id, messages)


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
                    "ActionBody": "search_vacancies",
                    "ReplyType": "message",
                    "Text": "Дополнительные параметры"
                }
            ]
        }
        viber.send_messages(viber_request.user.id, [
            TextMessage(text="Здравствуйте!", keyboard=keyboard)
        ])

    return Response(status=200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)