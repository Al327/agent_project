#!/usr/bin/env python3
from google.cloud import texttospeech
from asterisk.agi import AGI

import sys
import os
from pydub import AudioSegment
from utils.database import Database

client = texttospeech.TextToSpeechClient()

# Init
agi = AGI()
#Obtiene el argunmento "recognition"
textToConvertToAudio = sys.argv[1]

def play(audio):
    try:
        agi.exec_command('Playback', audio)
    except Exception as e:
        print(f"Error playing WAV file: {e}")


def text_to_speech(text_to_convert_to_audio):
    
    synthesis_input = texttospeech.SynthesisInput(text=text_to_convert_to_audio)
    
    voice = texttospeech.VoiceSelectionParams(
        language_code="es-US", name=os.getenv("GOOGLE_VOICE")
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    
    extention = agi.env['agi_extension']
    database = Database()
    agent = database.getAgentByExtention(extention)
    
    #TODO: Validad que el directorio del agente no existe, lo cree.
    
    mp3_file = f"{agent.audios_directory}/{agent.name}_audio.mp3"
    
    with open(mp3_file, "wb") as out:
        out.write(response.audio_content)
        print(f'Contenido de audio guardado en el archivo {mp3_file}')

    # Carga el archivo MP3
    audio = AudioSegment.from_mp3(mp3_file)

    # Cambiar permisos a 777
    os.chmod(mp3_file, 0o777)
    
    audio = AudioSegment.from_mp3(mp3_file)

    # Ajustar la parametros del audio
    audio = audio.apply_gain(3.5)
    audio = audio.set_frame_rate(8000)
    audio = audio.set_channels(1)

    # Exportar el archivo WAV
    wav_file = f"{agent.audios_directory}/{agent.name}_audio.wav"
    
    audio.export(wav_file, format='wav')

    os.chmod(wav_file, 0o777)
    
    #Reproduce el wav con asterisk
    play(f"{agent.audios_directory}/{agent.name}_audio")
    
#! Script que realiza el proceso de conversion a audio el texto entregado en la variable recognition
text_to_speech(textToConvertToAudio)
