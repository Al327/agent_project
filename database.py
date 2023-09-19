import sqlite3
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            # Obtener el nombre de la base de datos desde las variables de entorno
            database_name = os.getenv("DATABASE_PATH")
            cls._instance.connection = sqlite3.connect(database_name)
        return cls._instance

    def get_connection(self):
        return self.connection
