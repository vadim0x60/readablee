import config
import requests
import uuid
from flask import Flask, request
import io
import os

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

# Instantiates a client
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'iam.json'
client = speech.SpeechClient()

def download(url, filename='a.ogg'):
    os.system(f'wget -O {filename} {url}')

audio_config = types.RecognitionConfig(
    encoding=enums.RecognitionConfig.AudioEncoding.OGG_OPUS,
    sample_rate_hertz=16000,
    language_code='ru-RU')

def transcribe(filename='a.ogg'):
    # Loads the audio into memory
    with io.open(filename, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)
    
    # Detects speech in the audio file
    response = client.recognize(audio_config, audio)
    print(response)

    return response.results[0].alternatives[0].transcript

def vk(method, **kwargs):
    kwargs['access_token'] = config.vk_access_key
    kwargs['v'] = '5.92'
    response = requests.post(config.vk_api + method, kwargs)
    return response.json()

def handle_msg(message):
    if 'attachments' in message:
        for attachment in message['attachments']:
            if attachment['type'] == 'audio_message':
                download(attachment['audio_message']['link_ogg'])
                print(vk('messages.send', user_id=message['from_id'], 
                                          message=transcribe(), 
                                          random_id=uuid.uuid4().int))

    for fwd in message['fwd_messages']:
        handle_msg(fwd)
            
app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_event():
    event = request.get_json()

    print(event)

    if event['type'] == 'confirmation':
        return config.vk_handshake_response

    if event['type'] == 'message_new':
        handle_msg(event['object'])
    
    return 'ok'