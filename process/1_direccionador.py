#!/usr/bin/env python3
import sqlite3
from asterisk.agi import AGI
from utils.database import Database
import sys
from estados_agentes import EstadoAgente


#! Script que inicia el proceso de agentes virtuales: Obtiene el agente disponible y actualiza su estado a iniciado para luego redirgir a la extesion que ejecuta el segundo paso: 2_dialog
agi = AGI()
argumento = sys.argv[1]
canal = agi.env['agi_channel']

try:
    database = Database()
    agent = database.getAvailableAgent()
    
    if agent is not None:
        agent.client_identification = argumento
        agent.status = EstadoAgente.INICIADO
        
        database.updateAgentById(agent)
        
        agi.exec_command('ChannelRedirect', f'{canal},clase,{agent.extention},1')
        
    else:
        #TODO: Traspaso a la troncal
        pass

except Exception as e:
    agi.verbose(f'Error al direccionar agente: {str(e)}')
