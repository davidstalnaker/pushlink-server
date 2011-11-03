from binascii import unhexlify
from APNSWrapper import *

def sendMessage(token, url):
	print(token, url)
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