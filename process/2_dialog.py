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
    endpoint = client_datasource
    body = {
        "cedula": identification
    }
    data = None
    try:
        # Realizar la solicitud
        response = requests.post(endpoint, json=body, verify=False)  # Usar "verify=False" si no se verifica el certificado SSL

        # Verificar si la solicitud fue exitosa (código de respuesta 200)
        if response.status_code == 200:
            # Parsear la respuesta JSON
            respuesta_json = response.json()

            # Obtener el valor de la clave "result" del diccionario JSON
            resultado = respuesta_json.get("result")

            if resultado is not None:
                # Obtener el valor de la clave "puntos" del diccionario "result"
                puntos = resultado.get("puntos")

                if puntos is not None:
                    # Obtener el valor de la clave "facturas" del diccionario "puntos"
                    if "facturas" in puntos:
                        primer_elemento = puntos["facturas"][0]
                        nombre_cliente = resultado.get("cliente")
                        ciclo_facturacion = resultado.get("ciclo_facturacion")
                        total = resultado.get("total")
                        json_final = {
                            "nombre_cliente": nombre_cliente,
                            "ciclo_facturacion": ciclo_facturacion,
                            "total": total,
                            "Ultima_factura": primer_elemento
                        }
                        data = json.dumps(json_final)
                        return data
        else:
            return f"La solicitud no fue exitosa. Código de respuesta: {response.status_code}"
    except Exception as e:
        return f"Error al realizar la solicitud: {str(e)}"


#*Función que envía un request a dialogFlow y obtiene la respuesta a esa solicitud
def generateDialogflowAction(agent: Agente, request: str):

    session_path = session_client.session_path(project_id, location, agent.dialogflow_agent_id, agent.dialogflow_session_id)

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
        if(agent.status == EstadoAgente.INICIANDO.value):
            #*Envía un string inicial al dialogflow para empezar la conversacion y actualiza el estado del agente virtual
            #TODO: DEFINIR BIEN EL NOMBRE DEL PROCESO DE INICIO EN DIALOGFLOW
            response=generateDialogflowAction(agent=agent, request='COMANDO INICIO CONVERSACION')
            agent.status = EstadoAgente.INICIADO.value
            database.updateAgentById(agent)
            
        elif (agent.status == EstadoAgente.INICIADO.value):
            
            info_cliente = getInfoCliente(agent.client_identification)
            
            if info_cliente is not None:
                
                #*Envía el Json con los datos del cliente y obtiene la respuesta de dialogflow para setearla en la variable de asterisk recognition
                response = generateDialogflowAction(agent=agent, request=info_cliente)
                agi.set_variable(f"{agent.name}_response", response)

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
        agi.verbose(f'Error: {str(e)}')

if argumento and agent is not None:
    
    #*Envía el todo lo que el cliente habla en forma de texto (argumento) y obtiene la respuesta de dialogflow para setearla en la variable de asterisk recognition
    response = generateDialogflowAction(agent=agent, request=argumento)
    agi.set_variable(f"{agent.name}_response", response)
    