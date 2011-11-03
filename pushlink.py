from pymongo.connection import Connection
from flask import Flask, render_template, request, session, escape, redirect, url_for, g
from random import randint
from json import dumps

app = Flask(__name__)
connection = Connection("localhost")
db = connection.pushlink

@app.route('/register', methods=['POST'])
def register():
	token = request.form['token']
	
	existing = db.devices.find_one({"token":token})
	if existing:
		ret = {
			'token': token,
			'passcode': existing["passcode"],
			'new': False
		}
	else:
		num_words = db.words.count()
		passcode = []
		for i in range(3):
			word = db.words.find_one(skip=randint(0,num_words - 1))
			passcode.append(word['word'])
		db.devices.insert({"token":token, "passcode":' '.join(passcode)})
		ret = {
			'token': token,
			'passcode': ' '.join(passcode),
			'new': True
		}
	
	return dumps(ret)

@app.route('/send', methods=['POST'])
def send():
	passcode = request.form['passcode']
	link = request.form['link']
	device = db.devices.find_one({"passcode":passcode})
	return format("sending %s to %s" % (link, device["token"]))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)
