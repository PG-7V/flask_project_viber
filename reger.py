from flask import Flask, request, Response
from flask_sslify import SSLify
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import VideoMessage
from viberbot.api.messages.text_message import TextMessage
import logging


from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest
from viberbot.api.messages import (
    TextMessage,
    ContactMessage,
    PictureMessage,
    VideoMessage,
    FileMessage,
    )

app = Flask(__name__)
sslify = SSLify(app)
viber = Api(BotConfiguration(
    name='createPDF',
    avatar='',
    auth_token='4d09a6058027d05d-dba5d816e649c704-c151f2937e2b0164'
))


@app.route('/', methods=['POST'])
def incoming():
    logging.getLogger().debug("received request. post data: {0}".format(request.get_data()))
    # every viber message is signed, you can verify the signature using this method
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    # this library supplies a simple way to receive a request object
    viber_request = viber.parse_request(request.get_data().decode('utf8'))


    if isinstance(viber_request, ViberMessageRequest):
        if viber_request.message.text == 'приветик':


            viber.send_messages(viber_request.sender.id, [
                TextMessage(text=f'{viber_request.message.text}'),
                PictureMessage(media='https://static.tildacdn.com/tild6466-6462-4530-a137-343933333736/1661_0.jpg?s=328&g=1')
                ])
            #

            #
        # print(viber.message.text)

        # message = viber_request.message # Здесь возврат
        # # message = TextMessage(text="my text message")
        #
        #
        # # lets echo back
        # viber.send_messages(viber_request.sender.id, [
        #     message
        # ])
        pass
    #
    # elif isinstance(viber_request, ViberSubscribedRequest):
    #     viber.send_messages(viber_request.get_user().get_id(), [
    #         TextMessage(text="thanks for subscribing!")
    #     ])
    # elif isinstance(viber_request, ViberFailedRequest):
    #     logging.getLogger().warn("client failed receiving message. failure: {0}".format(viber_request))

    return Response(status=200)

if __name__ == "__main__":
    # context = ('server.crt', 'server.key')
    app.run(host='0.0.0.0', port=5000, debug=True)