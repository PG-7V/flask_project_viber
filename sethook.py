import requests
import json
# auth_token = '47d949c38ba7d354-26d746d90c8ed71-77df6d1bf9cfaa64' # тут ваш токен полученный в начале #п.2 Артем
auth_token = '4d09a6058027d05d-dba5d816e649c704-c151f2937e2b0164'  # my
hook = 'https://chatapi.viber.com/pa/set_webhook'
headers = {'X-Viber-Auth-Token': auth_token}


sen = dict(url='https://1ddc1d230763.ngrok.io/4d09a6058027d05d-dba5d816e649c704-c151f2937e2b0164/',
           event_types = ['unsubscribed', 'conversation_started', 'message', 'seen', 'delivered'])
# sen - это body запроса для отправки к backend серверов viber
#seen, delivered - можно убрать, но иногда маркетологи хотят знать,
#сколько и кто именно  принял и почитал ваших сообщений,  можете оставить)

r = requests.post(hook, json.dumps(sen), headers=headers)
# r - это пост запрос составленный по требованиям viber
print(r.json())
# в ответном print мы должны увидеть "status_message":"ok" - и это значит,
#  что вебхук установлен
