#!/usr/bin/env python3
import sys
import os
from asterisk.agi import AGI
from google.cloud import speech
import io
# Add the parent directory of the script to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(script_dir, "../.."))
sys.path.append(project_dir)
from utils.database import Database

client = speech.SpeechClient()
agi = AGI()

def speech_recognition():
    
    try:
        extention = agi.env['agi_extension']
        database = Database()
        agent = database.getAgentByExtention(extention)
        record_file =  f"{agent.audios_directory}/{agent.name}_sr_audio"
        
        # Record audio
        agi.record_file(record_file, timeout=10000, format='wav', silence=1, escape_digits='0')
        
        file_name=f'{record_file}.wav'
        
        with io.open(file_name, "rb") as audio_file:
            content = audio_file.read()
            audio = speech.RecognitionAudio(content=content)
            
        sr_config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            enable_automatic_punctuation=True,
            audio_channel_count=1,
            language_code="es-es",
            model="phone_call",
        )
        
        response = client.recognize(request={"config": sr_config, "audio": audio}) 
        for result in response.results:
            agi.set_variable(f"{agent.name}_response",result.alternatives[0].transcript)
        
    except Exception as e:
        error_message = f'Error en el reconocimiento de voz. Tipo de excepción: {type(e).__name__}, Mensaje: {str(e)}'
        agi.verbose(error_message, 1) 

    
speech_recognition()
   