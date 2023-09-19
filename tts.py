#!/usr/bin/env python3
from google.cloud import texttospeech
from asterisk.agi import AGI

import sys
import os
from pydub import AudioSegment

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/jordan/agent_project/ApiKey/key.json'
client = texttospeech.TextToSpeechClient()

# Init
agi = AGI()
language = 'es-es'
out_format = 'wav'
volume_boost = 3.5

# Text to speech
argumento = sys.argv[1]

def Reproducira():
    try:
        agi.exec_command('Playback', '/home/jordan/agent_project/agentes/agente1/script/temp_audio')
    except Exception as e:
        print(f"Error playing WAV file: {e}")


def speak_response(response_texts):
    tts_file = '/home/jordan/agent_project/agentes/agente1/script/temp_audio'

    debug_log_file = '/home/jordan/agent_project/agentes/agente1/script/debug_log.txt'

    texto_lista = []
    for response_text in response_texts:
        texto_lista.append(response_text)
    texto = ''.join(texto_lista)
    print("Bot:", texto)
    synthesis_input = texttospeech.SynthesisInput(text=texto)
    voice = texttospeech.VoiceSelectionParams(
        language_code="es-US", name="es-ES-Standard-B"
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    mp3_file = "/home/jordan/agent_project/agentes/agente1/script/temp_audio.mp3"
    with open(mp3_file, "wb") as out:
        out.write(response.audio_content)
        print('Contenido de audio guardado en el archivo "temp_audio.mp3"')

    # Carga el archivo MP3
    audio = AudioSegment.from_mp3(mp3_file)

    # Cambiar permisos a 777
    os.chmod(mp3_file, 0o777)
    with open(debug_log_file, 'a') as log_file:
        log_file.write(f"Save as {mp3_file}\n")

    audio = AudioSegment.from_mp3(mp3_file)
    audio = audio.apply_gain(volume_boost)

    # Ajustar la frecuencia de muestreo a 8000 Hz
    audio = audio.set_frame_rate(8000)
    audio = audio.set_channels(1)

    # Exportar el archivo WAV
    wav_file = "/home/jordan/agent_project/agentes/agente1/script/temp_audio.wav"
    audio.export(wav_file, format='wav')

    with open(debug_log_file, 'a') as log_file:
        log_file.write(f"Exported {wav_file}\n")
        log_file.write(f"Exported {texto}\n")

    os.chmod(wav_file, 0o777)
    Reproducira()
    

speak_response(argumento)
