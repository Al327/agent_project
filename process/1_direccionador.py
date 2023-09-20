#!/usr/bin/env python3
import sys
import os

from asterisk.agi import AGI

# Add the parent directory of the script to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.append(project_dir)

# Now you can perform the relative import
from utils.database import Database

# Rest of your script

import sqlite3
import sys
from models.estados_agentes import EstadoAgente



#! Script que inicia el proceso de agentes virtuales: Obtiene el agente disponible y actualiza su estado a iniciado para luego redirgir a la extesion que ejecuta el segundo paso: 2_dialog
agi = AGI()
argumento = sys.argv[1]
canal = agi.env['agi_channel']

try:
    database = Database()
    agent = database.getAvailableAgent()
    
    if agent is not None:
        agent.client_identification = argumento
        agent.status = EstadoAgente.INICIADO.value
        
        database.updateAgentById(agent)
        
        agi.exec_command('ChannelRedirect', f'{canal},clase,{agent.extention},1')
        
    else:
        #TODO: Traspaso a la troncal
        pass

except Exception as e:
    agi.verbose(f'Error al direccionar agente: {str(e)}')
