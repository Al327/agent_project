import sqlite3
import os
from dotenv import load_dotenv

from models.estados_agentes import EstadoAgente
from models.agent import Agente

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            # Obtener el nombre de la base de datos desde las variables de entorno
            database_name = os.getenv("DATABASE_PATH")
            cls._instance.connection = sqlite3.connect(database_name)
        return cls._instance

    def get_connection(self):
        return self.connection
    
    def getAgentByStatus(self, status):
        
        cursor = self.get_connection().cursor()

        result = cursor.execute(f"SELECT id, dialogflow_agent_id, name, extention, status, client_identification, audios_directory FROM agent WHERE status = '${status}'")
        
        agent = None
        
        if result is not None:
            agent = Agente(result[0], result[1], result[2], result[3], result[4], result[5], result[6])
            
        return agent
    
    def getAgentByExtention(self, extention):
        
        cursor = self.get_connection().cursor()
        result = cursor.execute(f"SELECT id, dialogflow_agent_id, name, extention, status, client_identification, audios_directory,dialogflow_session_id FROM agent WHERE extention = '{extention}'")
        result = cursor.fetchone()
        agent = None
        if result is not None:
            agent = Agente(result[0], result[1], result[2], result[3], result[4], result[5],result[6],result[7])
            
        return agent
    
    def getAvailableAgent(self):
        
        cursor = self.get_connection().cursor()
        cursor.execute(f"SELECT id, dialogflow_agent_id, name, extention, status, client_identification, audios_directory,dialogflow_session_id FROM agent WHERE status = '{EstadoAgente.DISPONIBLE.value}'")
        result = cursor.fetchone()
        agent = None
        
        if result is not None:
            agent = Agente(result[0], result[1], result[2], result[3], result[4], result[5], result[6],result[7])
            
            
        return agent

    def updateAgentById(self, agent:Agente):
        
        cursor = self.get_connection().cursor()
        result = cursor.execute("UPDATE agent SET client_identification = ?, extention = ?, status = ?, name = ?, dialogflow_agent_id = ?, dialogflow_session_id = ? WHERE id = ?", (agent.client_identification, agent.extention, agent.status, agent.name, agent.dialogflow_agent_id,agent.dialogflow_session_id ,agent.id))
        self.get_connection().commit()
        return result
    
        
        
        
        
    
