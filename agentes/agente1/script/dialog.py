#!/usr/bin/env python3
import requests
import json
from asterisk.agi import AGI
import speech_recognition as sr
from google.cloud import dialogflowcx_v3beta1 as dialogflow
from google.api_core.client_options import ClientOptions
from google.cloud import texttospeech
import sys
import os
import math
import sqlite3

conn = sqlite3.connect('/home/jordan/agent_project/database/agentes.db')
cursor = conn.cursor()

project_id = 'earnest-smoke-397401' #Variale de entorno
location = 'global'#Variable de entorno
agent_id = '16b8c2b4-0c20-4d29-b4b3-4cc248b4dd89' #Campo tabla agentes
session_id = '0212123032022232000022212222200001' #Campo tabla Conversaciones definir estandar 
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/jordan/agent_project/ApiKey/key.json'#Variable de entorno
client_options = ClientOptions(api_endpoint='dialogflow.googleapis.com')
# Crear una instancia del cliente de sesiones
session_client = dialogflow.SessionsClient(client_options=client_options)

# Iniciar una sesión de conversación
session_path = session_client.session_path(project_id, location, agent_id, session_id)


# Init
agi = AGI()

argumento = sys.argv[1]
if argumento=='':
    agi.exec_command('StartMusicOnHold', 'default')
    
#EN vez de un punto inicio conversacion(EN mayuscula)
def iniciador(argm):
    try:
        query_input = dialogflow.QueryInput(
            text=dialogflow.TextInput(text=argm),
            language_code="es-419"
        )
        request = dialogflow.DetectIntentRequest(
            session=session_path,
            query_input=query_input
        )
        # Enviar la solicitud y recibir la respuesta
        response = session_client.detect_intent(request=request)
        # Extraer y mostrar la respuesta del agente
        response_texts = []
        if response.query_result.response_messages:
            for message in response.query_result.response_messages:
                if message.text.text:
                    response_texts.append(message.text.text[0])
        # Unir los textos en un solo texto
        joined_response = " ".join(response_texts)
        debug_log_file = '/home/jordan/agent_project/agentes/agente1/script/debug_log.txt'
        with open(debug_log_file, 'a') as log_file:
                log_file.write(f"Respuesta del dialog {joined_response}\n")
        
    except Exception as e:
        print("Error:", e)
        print("No entiendo")

def inijson(argm):
    try:
        query_input = dialogflow.QueryInput(
            text=dialogflow.TextInput(text=argm),
            language_code="es-419"
        )
        request = dialogflow.DetectIntentRequest(
            session=session_path,
            query_input=query_input
        )
        # Enviar la solicitud y recibir la respuesta
        response = session_client.detect_intent(request=request)
        # Extraer y mostrar la respuesta del agente
        response_texts = []
        if response.query_result.response_messages:
            for message in response.query_result.response_messages:
                if message.text.text:
                    response_texts.append(message.text.text[0])
        # Unir los textos en un solo texto
        joined_response = " ".join(response_texts)
        debug_log_file = '/home/jordan/agent_project/agentes/agente1/script/debug_log.txt'
        with open(debug_log_file, 'a') as log_file:
                log_file.write(f"Respuesta del dialog {joined_response}\n")
        agi.set_variable("recognition", joined_response)

    except Exception as e:
        print("Error:", e)
        print("No entiendo")


def inicio_codigo():
    try:
        query_input = dialogflow.QueryInput(
            text=dialogflow.TextInput(text=argumento),
            language_code="es-419"
        )
        request = dialogflow.DetectIntentRequest(
            session=session_path,
            query_input=query_input
        )
        # Enviar la solicitud y recibir la respuesta
        response = session_client.detect_intent(request=request)
        # Extraer y mostrar la respuesta del agente
        response_texts = []
        if response.query_result.response_messages:
            for message in response.query_result.response_messages:
                if message.text.text:
                    response_texts.append(message.text.text[0])
        # Unir los textos en un solo texto
        joined_response = " ".join(response_texts)
        debug_log_file = '/home/jordan/agent_project/agentes/agente1/script/debug_log.txt'
        with open(debug_log_file, 'a') as log_file:
                log_file.write(f"Respuesta del dialog {joined_response}\n")
        agi.set_variable("recognition", joined_response)
        
    except Exception as e:
        print("Error:", e)
        print("No entiendo")


while True:

    try:
            # Verifica si el estado es "Sin llamada"
            cursor.execute("SELECT id, Agentes, Extension, Estado,Cedula FROM Agentes WHERE Agentes = 'Agente2'")
            for fila in cursor.fetchall():
                # Separar los valores en dos variables
                id, agente, extension, estado,cedula = fila
                print(fila)
            if estado == 'Iniciando' and agente == 'Agente2':
                cursor.execute("UPDATE Agentes SET Cedula=?, Extension = ?, Estado = ? WHERE id = ?", (cedula, extension, 'Iniciado', id))
                iniciador('.')
            elif( estado == 'Iniciado' and agente == 'Agente2'):
                url = f"https://64753150e607ba4797dbb252.mockapi.io/user?Cedula={cedula}"
                response = requests.get(url)            
                if response.status_code == 200:
                    data = response.json()
                    cursor.execute("UPDATE Agentes SET Cedula=?, Extension = ?, Estado = ? WHERE id = ?", (cedula, extension, 'En llamada', id))
                    conn.commit()
                    conn.close()
                    if data:
                        resultado = data[0]
                        resultado_str = json.dumps(resultado)
                        print(resultado_str)
                        inijson(resultado_str)
                        break
                    else:
                        print("No se encontraron resultados para la cédula", cedula)
                else:
                    print("Error al realizar la solicitud a la API. Código de estado:", response.status_code)
            elif(estado == 'En llamada' and agente == 'Agente2'):
                sys.exit()
    except Exception as e:
        # Maneja cualquier excepción que pueda ocurrir durante la lectura del archivo
        print(f'Error: {str(e)}')


if argumento !='':
    inicio_codigo()