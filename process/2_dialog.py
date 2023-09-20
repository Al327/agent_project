#!/usr/bin/env python3
import requests
import json
from asterisk.agi import AGI
from models.agent import Agente
from utils.database import Database
from models.estados_agentes import EstadoAgente
from google.cloud import dialogflowcx_v3beta1 as dialogflow
from google.api_core.client_options import ClientOptions
from google.cloud import texttospeech
from utils.dialogflow_utils import DialogflowUtils
import sys
import os

project_id = os.getenv("PROJECT_ID") #Variale de entorno
location = os.getenv("LOCATION") 
client_options = ClientOptions(api_endpoint='dialogflow.googleapis.com')
session_client = dialogflow.SessionsClient(client_options=client_options)

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


#! Script que realiza acciones de acuerdo al estado del agente, la interaccion con el cliente se hace una vez el agente se encuentra en estado ocupado 
agi = AGI()

argumento = sys.argv[1]

if argumento=='':
    agi.exec_command('StartMusicOnHold', 'default')
    
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
        
        #TODO: VALIDAR SI ESTA VALIDACION ES NECESARIA
        elif (agent.status == EstadoAgente.OCUPADO):
            sys.exit()
        
    except Exception as e:
        # Maneja cualquier excepción que pueda ocurrir durante la lectura del archivo
        print(f'Error: {str(e)}')

if argumento and agent is not None:
    
    #*Envía el todo lo que el cliente habla en forma de texto (argumento) y obtiene la respuesta de dialogflow para setearla en la variable de asterisk recognition
    response = generateDialogflowAction(agent=agent, request=argumento)
    agi.set_variable(f"{agent.name}_response", response)