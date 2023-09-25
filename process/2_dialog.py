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
agi = AGI()

def getInfoCliente(identification):
    url = os.getenv("CLIENT_DATASOURCE")
    data = {
        "cedula": identification
    }

    # Realizar la solicitud
    response = requests.post(url, json=data, verify=False)  # Usar "verify=False" si no se verifica el certificado SSL

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
                primer_elemento = puntos[0]

                if primer_elemento is not None:
                    # Ahora "facturas" contiene el valor asociado a "facturas"
                    nombre_cliente = resultado.get("cliente")
                    ciclo_facturacion = resultado.get("ciclo_facturacion")
                    total = resultado.get("total")
                    facturas = primer_elemento.get("facturas")

                    if facturas:
                        # Obtener la última factura del cliente
                        ultima_factura = facturas[0]

                        if ultima_factura:
                            # Obtener la fecha de emisión y el valor total de la última factura
                            fe_emision = ultima_factura.get("fe_emision")
                            valor_total = ultima_factura.get("valor_total")

                            # Crear un nuevo diccionario con la información requerida
                            nuevo_json = {
                                "nombre_cliente": nombre_cliente,
                                "ciclo_facturacion": ciclo_facturacion,
                                "total": total,
                                "fe_emision": fe_emision,
                                "valor_total": valor_total
                            }

                            # Convertir el nuevo diccionario a JSON y devolverlo
                            data = json.dumps(nuevo_json)
                            return data
                        else:
                            agi.exec_command('NoOp', "No se encontró información de la última factura.")
                    else:
                        agi.exec_command('NoOp', "La clave 'facturas' no se encontró en el diccionario 'puntos'.")
                else:
                    agi.exec_command('NoOp', "La clave 'puntos' no se encontró en el diccionario 'result'.")
            else:
                agi.exec_command('NoOp', "La clave 'puntos' no se encontró en el diccionario 'result'.")
        else:
            agi.exec_command('NoOp', "La clave 'result' no se encontró en la respuesta JSON.")
    else:
        agi.exec_command('NoOp', f"La solicitud no fue exitosa. Código de respuesta: {response.status_code}")

#*Función que envía un request a dialogFlow y obtiene la respuesta a esa solicitud
def generateDialogflowAction(agent: Agente, request: str):

    session_path = session_client.session_path(project_id, location, agent.dialogflow_agent_id, agent.dialogflow_session_id)

    response = DialogflowUtils.dialogFlowInteraction(request=request, session_path=session_path, session_client=session_client)
    
    return response


#! Script que realiza acciones de acuerdo al estado del agente, la interaccion con el cliente se hace una vez el agente se encuentra en estado ocupado 

argumento = sys.argv[1]
extention = agi.env['agi_extension']
agi.exec_command('NoOp',argumento)
if argumento=='':
    agi.exec_command('StartMusicOnHold', 'default')
    
while True:

    #TODO: investigar si esa es la variable de entorno para obtener la extension
    
    
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
            break
        
    except Exception as e:
        # Maneja cualquier excepción que pueda ocurrir durante la lectura del archivo
        agi.verbose(f'Error: {str(e)}')

if argumento != '':
    agi.exec_command('NoOp',"Tiene argumento")
    database = Database()
    agent = database.getAgentByExtention(extention)
    #*Envía el todo lo que el cliente habla en forma de texto (argumento) y obtiene la respuesta de dialogflow para setearla en la variable de asterisk recognition
    response = generateDialogflowAction(agent=agent, request=argumento)
    agi.set_variable(f"{agent.name}_response", response)
    