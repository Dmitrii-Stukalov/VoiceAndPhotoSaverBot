import config
import telebot
import flask
import requests
import sys
import os
import librosa
import subprocess
import face_recognition

bot = telebot.TeleBot(config.TOKEN)
app = flask.Flask(__name__)

@app.route('/', methods=['POST'])
def telegram_hook():
	if flask.request.headers.get('content-type') == 'application/json':
		json_string = flask.request.get_data().decode('utf-8')
		update = telebot.types.Update.de_json(json_string)
		bot.process_new_updates([update])
		return flask.make_response('ok', 200)
	else:
		flask.abort(403)

@bot.message_handler(content_types=['voice'])
def voice_saver(message):
	file_path = bot.get_file(message.voice.file_id).file_path
	url = 'https://api.telegram.org/file/bot' + config.TOKEN + '/' + file_path
	voice = requests.get(url)
	
	path = 'voices/' + str(message.chat.id)
	if not os.path.exists(path):
		os.mkdir(path)
	path += '/audio_message_' + str(len(os.listdir(path)))
	open(path + '.oga', 'wb').write(voice.content)
	
	subprocess.run(['ffmpeg', '-i', path + '.oga', '-ar', '16000', path + '.wav'])
	os.remove(path + '.oga')

@bot.message_handler(content_types=['photo'])
def photo_saver(message):
	file_path = bot.get_file(message.photo[2].file_id).file_path
	url = 'https://api.telegram.org/file/bot' + config.TOKEN + '/' + file_path
	picture = requests.get(url)

	path = 'pictures/' + str(message.chat.id)
	if not os.path.exists(path):
		os.mkdir(path)
	path += '/picture_' + str(len(os.listdir(path)))
	open(path + '.jpg', 'wb').write(picture.content)

	image = face_recognition.load_image_file(path + '.jpg')
	face_locations = face_recognition.face_locations(image)
	if (len(face_locations) < 1):
		os.remove(path + '.jpg')


@bot.message_handler(content_types=['text'])
def repeat_all(message):
	bot.send_message(message.chat.id, message.text)

if __name__ == '__main__':
	app.run(host='localhost', debug=True)