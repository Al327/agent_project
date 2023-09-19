#!/usr/bin/env python3

from asterisk.agi import AGI
from google.cloud import speech
import os
import io
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/jordan/agent_project/ApiKey/key.json'
client = speech.SpeechClient()
# Init
agi = AGI()
record_file = '/home/jordan/agent_project/agentes/agente1/script/tempor'
language = 'es-es'
out_format = 'wav'
def inicio_codigo():
    # Record audio
    agi.record_file(record_file, timeout=10000, format=out_format, silence=1, escape_digits='0')
    file_name='/home/jordan/agent_project/agentes/agente1/script/tempor.wav'
    with io.open(file_name, "rb") as audio_file:
        content = audio_file.read()
        audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        enable_automatic_punctuation=True,
        audio_channel_count=1,
        language_code="es-es",
        model="phone_call",
    )
    response = client.recognize(request={"config": config, "audio": audio})   
    for result in response.results:
        print("Transcript: {}".format(result.alternatives[0].transcript))
        agi.set_variable("recognition", result.alternatives[0].transcript)

inicio_codigo()
   