
import config
import requests
import uuid
from flask import Flask, request
import io
import os
import scipy.io.wavfile

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

from detect_emotions import create_vokaturi
from sumy_api import summarize

# Instantiates a client
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'iam.json'
client = speech.SpeechClient()

def fetch_wav(url, filename='a.wav'):
    ogg_filename = filename.replace('wav', 'ogg')
    os.system(f'wget -O {ogg_filename} {url}')
    os.system('ffmpeg -y -i {0} {1}'.format(ogg_filename, filename))

def summarize_sentences(sentences):
    text = '. '.join(sentences)
    if len(sentences) > 5:
        return 'tl;dr: ' + summarize(text)
    else:
        return text
    
def transcribe(wavpath='a.wav'):
    # Loads the audio into memory
    sample_rate, samples = scipy.io.wavfile.read(wavpath)
    with open(wavpath, 'rb') as f:
        audio = types.RecognitionAudio(content=f.read())

    audio_config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sample_rate,
        language_code='en-US')
        
    # Detects speech in the audio file
    response = client.recognize(audio_config, audio)
    print(response)

    sentences = [sent.alternatives[0].transcript for sent in response.results]
    return sentences

def vk(method, **kwargs):
    print(kwargs)
    kwargs['access_token'] = config.vk_access_key
    kwargs['v'] = '5.92'
    response = requests.post(config.vk_api + method, kwargs)
    return response.json()

voice2emoji = create_vokaturi()

def handle_msg(message):
    if 'attachments' in message:
        for attachment in message['attachments']:
            if attachment['type'] == 'audio_message':
                fetch_wav(attachment['audio_message']['link_ogg'])
                t = summarize_sentences(transcribe()) + ' ' + voice2emoji('a.wav')
                print(vk('messages.send', peer_id=message['peer_id'], 
                                          message=t, 
                                          random_id=uuid.uuid4().int))
    if 'fwd_messages' in message:
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