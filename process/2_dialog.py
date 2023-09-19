#!/usr/bin/env python3
import requests
import json
from asterisk.agi import AGI
from models.agent import Agente
from utils.database import Database
from estados_agentes import EstadoAgente
import speech_recognition as sr
from google.cloud import dialogflowcx_v3beta1 as dialogflow
from google.api_core.client_options import ClientOptions
from google.cloud import texttospeech
import sys
import os
import math
import sqlite3

from utils.dialogflow_utils import DialogflowUtils



conn = sqlite3.connect('/home/jordan/agent_project/database/agentes.db')
cursor = conn.cursor()

project_id = os.getenv("PROJECT_ID") #Variale de entorno
location = os.getenv("LOCATION") 

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

def getInfoCliente(identification):
    client_datasource = os.getenv("CLIENT_DATASOURCE")
    endpoint = f"{client_datasource}/user?Cedula={identification}"
    response = requests.get(endpoint)  
    
    data = None
    
    if response.status_code == 200:
        jsonResponse = response.json()
        if jsonResponse:
            data_response = jsonResponse[0]
            data = json.dumps(data_response)
            
    return data

#*Función que envía un request a dialogFlow y obtiene la respuesta a esa solicitud
def generateDialogflowAction(agent: Agente, request: str):
    
    session_id = DialogflowUtils.generateDialogFlowSessionId()

    session_path = session_client.session_path(project_id, location, agent.dialogflow_agent_id, session_id)

    response = DialogflowUtils.dialogFlowInteraction(request=request, session_path=session_path, session_client=session_client)
    
    return response

while True:

    #TODO: investigar si esa es la variable de entorno para obtener la extension
    extention = agi.env['agi_extension']
    
    agent = None
    try:
        
        database = Database()
        agent = database.getAgentByExtention(extention)
        
        if(agent.status == EstadoAgente.INICIANDO):
            
            #*Envía un string inicial al dialogflow para empezar la conversacion y actualiza el estado del agente virtual
            #TODO: DEFINIR BIEN EL NOMBRE DEL PROCESO DE INICIO EN DIALOGFLOW
            generateDialogflowAction(agent=agent, request='COMANDO INICIO CONVERSACION')
            agent.status = EstadoAgente.INICIADO
            database.updateAgentById(agent)
            
        elif (agent.status == EstadoAgente.INICIADO):
            
            info_cliente = getInfoCliente(agent.client_identification)
            
            if info_cliente is not None:
                
                #*Envía el Json con los datos del cliente y obtiene la respuesta de dialogflow para setearla en la variable de asterisk recognition
                response = generateDialogflowAction(agent=agent, request=info_cliente)
                agi.set_variable("recognition", response)

                #*Setea el estado del agente en ocupa 
                agent.status = EstadoAgente.OCUPADO
                database.updateAgentById(agent)
                break
            else:
                #TODO: VALIDAR ESCENARIO EN QUE NO SE PUEDA ENVIAR LA INFO DEL JSON
                pass
                
        elif (agent.status == EstadoAgente.OCUPADO):
            sys.exit()
        
    except Exception as e:
        # Maneja cualquier excepción que pueda ocurrir durante la lectura del archivo
        print(f'Error: {str(e)}')

if argumento and agent is not None:
    
    #*Envía el todo lo que el cliente habla en forma de texto (argumento) y obtiene la respuesta de dialogflow para setearla en la variable de asterisk recognition
    response = generateDialogflowAction(agent=agent, request=argumento)
    agi.set_variable("recognition", response)