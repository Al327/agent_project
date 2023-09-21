#!/usr/bin/env python3
import requests
import json
from asterisk.agi import AGI
from google.cloud import dialogflowcx_v3beta1 as dialogflow
from google.api_core.client_options import ClientOptions
from google.cloud import texttospeech
import sys
import os
# Add the parent directory of the script to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.append(project_dir)
from models.agent import Agente

from utils.database import Database
from utils.dialogflow_utils import DialogflowUtils
from models.estados_agentes import EstadoAgente
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

argumento = 'Quisiera saber cuanto debo'

if argumento=='':
    print('Hold')
    
while True:

    #TODO: investigar si esa es la variable de entorno para obtener la extension
    extention = '204'
    
    agent = None
    try:
        
        database = Database()
        agent = database.getAgentByExtention(extention)
        print(EstadoAgente.INICIANDO.value)
        if(agent.status == EstadoAgente.INICIANDO.value):
            print('Entra al iniciador')
            #*Envía un string inicial al dialogflow para empezar la conversacion y actualiza el estado del agente virtual
            #TODO: DEFINIR BIEN EL NOMBRE DEL PROCESO DE INICIO EN DIALOGFLOW
            response=generateDialogflowAction(agent=agent, request='COMANDO INICIO CONVERSACION')
            print("recognition", response)
            agent.status = EstadoAgente.INICIADO.value
            database.updateAgentById(agent)
            
        elif (agent.status == EstadoAgente.INICIADO.value):
            
            info_cliente = getInfoCliente(agent.client_identification)
            
            if info_cliente is not None:
                
                #*Envía el Json con los datos del cliente y obtiene la respuesta de dialogflow para setearla en la variable de asterisk recognition
                response = generateDialogflowAction(agent=agent, request=info_cliente)
                print("recognition", response)

                #*Setea el estado del agente en ocupa 
                agent.status = EstadoAgente.OCUPADO.value
                database.updateAgentById(agent)
                break
            else:
                #TODO: VALIDAR ESCENARIO EN QUE NO SE PUEDA ENVIAR LA INFO DEL JSON
                pass
        
        #TODO: VALIDAR SI ESTA VALIDACION ES NECESARIA
        elif (agent.status == EstadoAgente.OCUPADO.value):
            sys.exit()
        
    except Exception as e:
        # Maneja cualquier excepción que pueda ocurrir durante la lectura del archivo
        print(f'Error: {str(e)}')

if argumento and agent is not None:
    
    #*Envía el todo lo que el cliente habla en forma de texto (argumento) y obtiene la respuesta de dialogflow para setearla en la variable de asterisk recognition
    response = generateDialogflowAction(agent=agent, request=argumento)
    print(f"{agent.name}_response", response)