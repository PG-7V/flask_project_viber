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
            print('Error parse "gallery"')
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

    #logging.getLogger().debug("received request. post data: {0}".format(request.get_data()))
    # every viber message is signed, you can verify the signature using this method
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data().decode('utf8'))
    # def v_r(texxt):
    #     viber.send_messages(viber_request.sender.id, [
    #         TextMessage(text=texxt, keyboard={
    #             "DefaultHeight": True,
    #             "BgColor": "#FFFFFF",
    #             "Type": "keyboard",
    #             "Buttons": [get_buttons('Артикул и Размеры'),
    #                         get_buttons('Артикул и Размеры + Цена'),
    #                         get_buttons('Артикул, Размеры, Состав + Цена'),
    #                         get_buttons('Все в наличии')]
    #         })])

    if isinstance(viber_request, ViberFailedRequest):
        logging.getLogger().warning("client failed receiving message. failure: {0}".format(viber_request))

    elif isinstance(viber_request, ViberMessageRequest):
        if viber_request.message.text == 'Настройки параметров':
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
            #v_r('Выберите параметры отображения.')
        elif viber_request.message.text == 'Артикул и Размеры':
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
            #v_r('Установлены параметры "Артикул и Размеры". Введите Артикул.')
        elif viber_request.message.text == 'Артикул и Размеры + Цена':
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
            #v_r('Установлены параметры "Артикул и Размеры + Цена". Введите Артикул.')
        elif viber_request.message.text == 'Артикул, Размеры, Состав + Цена':
            # global para
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
            #v_r('Установлены параметры "Артикул, Размеры, Состав + Цена". Введите Артикул.')

        # elif isinstance(viber_request, ViberFailedRequest):
        #     logging.getLogger().warn(
        #         "client failed receiving message. failure: {0}".format(viber_request))



        # else:
            # url_j = 'https://store.tildacdn.com/api/getproductslist/?storepartuid=133030198409&recid=132953886&getparts=true&getoptions=true&size=500'
            # data_j = requests.get(url_j).json()
            # with open('cat.json') as f_j:
            #     data_j = json.load(f_j)

        elif viber_request.message.text == 'Все в наличии':
            rows = []
            # data_j = json.load(open('cat.json'))
            with open('cat.json') as f_j:
                data_j = json.load(f_j)
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
            time.sleep(2)
            viber.send_messages(viber_request.sender.id, [PictureMessage(media=llink, keyboard={
                "DefaultHeight": True,
                "BgColor": "#FFFFFF",
                "Type": "keyboard",
                "Buttons": [get_buttons('Далее'),
                            get_buttons('Все в наличии')]
            })])
            print('all send media')
            # if para == 1:
            #     ltext_message = f'{lart}\n{ldescr}'
            # elif para == 2:
            #     ltext_message = f'{lart}\n{ldescr}\n{lchar}'
            # else:
            # ltext_message = f'{lart}\n{ldescr}'
            # time.sleep(2)
            # viber.send_messages(viber_request.sender.id, [
            #     TextMessage(text=ltext_message, keyboard={
            #         "DefaultHeight": True,
            #         "BgColor": "#FFFFFF",
            #         "Type": "keyboard",
            #         "Buttons": [get_buttons('Далее'),
            #                     get_buttons('Все в наличии')]
            #     })])
            # print('all send first text')
            # time.sleep(2)
            # if para:
            #     viber.send_messages(viber_request.sender.id, [
            #         TextMessage(text=f'Цена {lprice}', keyboard={
            #             "DefaultHeight": True,
            #             "BgColor": "#FFFFFF",
            #             "Type": "keyboard",
            #             "Buttons": [get_buttons('Далее'),
            #                         get_buttons('Все в наличии')]
            #         })])
            # print('all send second text')
            time.sleep(2)
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
                #v_r('Все данные выгружены. Сформируйте новый запрос.')

        elif viber_request.message.text == 'Далее':
            loa_d = 0
            with open('cat_tok', 'w') as file_data:
                file_data.write(f'''{viber_request}''')
            vrt = viber_request.message_token
            if not vrt in messege_tokens:
                viber.send_messages(viber_request.sender.id, [
                    TextMessage(text=f'''{viber_request}''', keyboard={
                        "DefaultHeight": True,
                        "BgColor": "#FFFFFF",
                        "Type": "keyboard",
                        "Buttons": [get_buttons('Артикул и Размеры'),
                                    get_buttons('Артикул и Размеры + Цена'),
                                    get_buttons('Артикул, Размеры, Состав + Цена'),
                                    get_buttons('Все в наличии')]
                    })])
                messege_tokens.append(vrt)
                loa_d = 1
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
                time.sleep(2)
                vrt = viber_request.message_token
                if loa_d:
                    viber.send_messages(viber_request.sender.id, [PictureMessage(media=llink, keyboard={
                        "DefaultHeight": True,
                        "BgColor": "#FFFFFF",
                        "Type": "keyboard",
                        "Buttons": [get_buttons('Далее'),
                                    get_buttons('Настройки параметров'),
                                    get_buttons('Все в наличии')]
                    })])
                    if para == 1:
                        ltext_message = f'{lart}\n{ldescr}'
                    elif para == 2:
                        ltext_message = f'{lart}\n{ldescr}\n{lchar}'
                    else:
                        ltext_message = f'{lart}\n{ldescr}'
                    print(ltext_message)
                    time.sleep(2)
                    viber.send_messages(viber_request.sender.id, [
                        TextMessage(text=ltext_message, keyboard={
                            "DefaultHeight": True,
                            "BgColor": "#FFFFFF",
                            "Type": "keyboard",
                            "Buttons": [get_buttons('Далее'),
                                        get_buttons('Настройки параметров'),
                                        get_buttons('Все в наличии')]
                        })])
                    print(f'next send first para{ltext_message}')
                    time.sleep(2)
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
                    print('next send second para')
                    time.sleep(2)
                    rows.pop(0)
                    print(f'{viber_request.message_token}')
                # print(f'next send media{llink}')
                # if para == 1:
                #     ltext_message = f'{lart}\n{ldescr}'
                # elif para == 2:
                #     ltext_message = f'{lart}\n{ldescr}\n{lchar}'
                # else:
                #     ltext_message = f'{lart}\n{ldescr}'
                # print(ltext_message)
                # time.sleep(2)
                # viber.send_messages(viber_request.sender.id, [
                #     TextMessage(text=ltext_message, keyboard={
                #         "DefaultHeight": True,
                #         "BgColor": "#FFFFFF",
                #         "Type": "keyboard",
                #         "Buttons": [get_buttons('Далее'),
                #                     get_buttons('Настройки параметров'),
                #                     get_buttons('Все в наличии')]
                #     })])
                # print(f'next send first para{ltext_message}')
                # time.sleep(2)
                # if para:
                #     viber.send_messages(viber_request.sender.id, [
                #         TextMessage(text=f'Цена {lprice}', keyboard={
                #             "DefaultHeight": True,
                #             "BgColor": "#FFFFFF",
                #             "Type": "keyboard",
                #             "Buttons": [get_buttons('Далее'),
                #                         get_buttons('Настройки параметров'),
                #                         get_buttons('Все в наличии')]
                #         })])
                # print('next send second para')
                # time.sleep(2)
                # rows.pop(0)
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
                #v_r('Все данные выгружены. Сформируйте новый запрос.')


        else:  # Поиск отдельного артикула.
            # data_j = json.load(open('cat.json'))
            with open('cat.json') as f_j:
                data_j = json.load(f_j)
            udatas = search_info(viber_request.message.text.strip(), parse(data_j))
            for udata in udatas:
                time.sleep(5)
                uart_if = udata['title']
                udescr = udata['descr']
                try:
                    uprice = udata['price']
                except:
                    uprice = ''
                ulink = udata['link']
                uchar = udata['character']
                if ulink:
                    viber.send_messages(viber_request.sender.id, [PictureMessage(media=ulink)])
                    text_message = f'{uart_if}\n{udescr}'
                    time.sleep(1)
                    if para == 1:
                        text_message = f'{uart_if}\n{udescr}'
                    elif para == 2:
                        text_message = f'{uart_if}\n{udescr}\n{uchar}'
                else:
                    text_message = f'Артикул {viber_request.message.text} отсутствует.'
                viber.send_messages(viber_request.sender.id, [
                    TextMessage(text=text_message, keyboard={
                        "DefaultHeight": True,
                        "BgColor": "#FFFFFF",
                        "Type": "keyboard",
                        "Buttons": [get_buttons('Артикул и Размеры'),
                                    get_buttons('Артикул и Размеры + Цена'),
                                    get_buttons('Артикул, Размеры, Состав + Цена'),
                                    get_buttons('Все в наличии')]
                    })])
                #v_r(text_message)
                time.sleep(1)
                if ulink and para:
                    viber.send_messages(viber_request.sender.id, [
                        TextMessage(text=f'Цена {uprice}', keyboard={
                            "DefaultHeight": True,
                            "BgColor": "#FFFFFF",
                            "Type": "keyboard",
                            "Buttons": [get_buttons('Артикул и Размеры'),
                                        get_buttons('Артикул и Размеры + Цена'),
                                        get_buttons('Артикул, Размеры, Состав + Цена'),
                                        get_buttons('Все в наличии')]
                        })])
                    #v_r(f'Цена {uprice}')
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

    else:
        print('else')

    return Response(status=200)


if __name__ == "__main__":
    # context = ('server.crt', 'server.key')
    application.run(host='0.0.0.0', port=5000, debug=True)