from pymongo.connection import Connection
from flask import Flask, make_response, render_template, request, session, escape, redirect, url_for, g
from random import randint, choice
from json import dumps
from apns import send_url
from ratelimit import ratelimit
from APNSWrapper.apnsexceptions import APNSPayloadLengthError
import string

app = Flask(__name__)
connection = Connection("localhost")
db = connection.pushlink

@app.route('/')
def index():
	return render_template('send.html') 

@app.route('/reregister', methods=['POST'])
def reregister():
	token = request.form['token']
	
	db.devices.remove({"token": token})
	passcode = gen_unique_passcode()
	db.devices.insert({"token": token, "passcode":passcode})
	
	return make_json_response({
		'token': token,
		'passcode': passcode,
		'new': True
	})
	

@app.route('/register', methods=['POST'])
def register():
	token = request.form['token']
	ret = {
		'token': token,
	}
	
	existing = db.devices.find_one({"token":token})
	if existing:
		ret['passcode'] = existing["passcode"]
		ret['new'] = False
	else:
		passcode = gen_unique_passcode()
		db.devices.insert({"token":token, "passcode":passcode})
		ret['passcode'] = passcode
		ret['new'] = True
	
	return make_json_response(ret)

@app.route('/send', methods=['POST'])
@ratelimit(limit=60, per=60)
def send():
	passcode = request.form['passcode']
	url = request.form['url']
	device = db.devices.find_one({"passcode":passcode})
	if device:
		try:
			send_url(device["token"], url)
		except APNSPayloadLengthError:
			url_id = gen_unique_url_id()
			db.url_ids.insert({'url_id': url_id, 'url': url})
			send_url(device["token"], url_id, is_shortened=True)
		return ""
	else:
		return make_json_response({'error': 'unknown passcode'}, 400)
		
def gen_unique_passcode():
	num_words = db.words.count()
	while True:
		pclist = []
		for i in range(3):
			word = db.words.find_one(skip=randint(0,num_words - 1))
			pclist.append(word['word'])
		passcode = ' '.join(pclist)
		if db.devices.find({'passcode': passcode}).count() == 0:
			break
	return passcode
	
def gen_unique_url_id(size=8, chars=string.ascii_lowercase + string.digits):
	while True:
		url_id = ''.join(choice(chars) for x in range(size))
		if db.url_ids.find({'url_id': url_id}).count() == 0:
			break
	return url_id

def make_json_response(jsonObj, responseCode = 200):
	response = make_response(dumps(jsonObj), responseCode)
	response.headers['content-type'] = 'application/json'
	return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9001, debug=True)
