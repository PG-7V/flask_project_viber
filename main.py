from flask import Flask, request, Response
import logging
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import VideoMessage
from viberbot.api.messages.text_message import TextMessage


from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest

from flask_sslify import SSLify

app = Flask(__name__)
viber = Api(BotConfiguration(
    name='createPDF',
    avatar='',
    auth_token='4d09a6058027d05d-dba5d816e649c704-c151f2937e2b0164'
))
# sslify = SSLify(app)

@app.route('/incoming', methods=['POST'])
def incoming():
    # logger = logging.getLogger()
	logging.getLogger().debug("received request. post data: {0}".format(request.get_data()))
	# handle the request here
	return Response(status=200)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)