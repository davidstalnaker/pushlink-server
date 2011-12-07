from binascii import unhexlify
from APNSWrapper import *

	# format url and token
	url = url.encode('ascii', 'ignore')
	if url.find('://') == -1:
		url = 'http://' + url
def send_url(token, url, is_shortened = False):
	deviceToken = unhexlify(token)
	
	# create wrapper
	wrapper = APNSNotificationWrapper('PushLink.pem', True)
	
	# create message
	message = APNSNotification()
	message.token(deviceToken)
	
	# just add alert text
	message.alert("Tap to open URL")
	
	# enable sound (default sound if no argument)
	message.sound()
	
	# set the url
	if is_shortened:
		print('sending shortened url')
		url_prop = APNSProperty("url_id", url)
	else:
		url_prop = APNSProperty("url", url)
	message.appendProperty(url_prop)
	
	# add message to tuple and send it to APNS server
	wrapper.append(message)
	wrapper.notify()