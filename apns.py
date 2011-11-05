from binascii import unhexlify
from APNSWrapper import *

def sendMessage(token, url):
	# format url and token
	url = url.encode('ascii', 'ignore')
	if url.find('://') == -1:
		url = 'http://' + url
	deviceToken = unhexlify(token)
	
	# create wrapper
	wrapper = APNSNotificationWrapper('ck.pem', True)
	
	# create message
	message = APNSNotification()
	message.token(deviceToken)
	
	# just add alert text
	message.alert("Tap to open URL")
	
	# enable sound (default sound if no argument)
	message.sound()
	
	# set the url
	url = APNSProperty("url", url)
	message.appendProperty(url)
	
	# add message to tuple and send it to APNS server
	wrapper.append(message)
	wrapper.notify()