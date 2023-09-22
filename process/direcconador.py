#!/usr/bin/env python3
import sys
import os

from asterisk.agi import AGI

# Agregar el directorio principal del script al camino de Python
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.append(project_dir)

# Ahora puedes realizar la importación relativa
from utils.database import Database
from utils.dialogflow_utils import DialogflowUtils


import sqlite3
from models.estados_agentes import EstadoAgente

# Tu código actual aquí

argumento = sys.argv[1]
try:
    database = Database()
    agent = database.getAvailableAgent()
    
    if agent is not None:
        agent.client_identification = argumento
        agent.status = EstadoAgente.INICIANDO.value
        agent.dialogflow_session_id = DialogflowUtils.generateDialogFlowSessionId()

        database.updateAgentById(agent)
        
    else:
        # TODO: Traspaso a la troncal
        pass

except Exception as e:
    error_message = f'Error al direccionar agente: {str(e)}\n'
    
