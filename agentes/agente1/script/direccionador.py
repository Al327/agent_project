#!/usr/bin/env python3
import sqlite3
from asterisk.agi import AGI
import sys

# Inicializa AGI
agi = AGI()
argumento = sys.argv[1]
canal = agi.env['agi_channel']


try:
    # Conectar a la base de datos
    conn = sqlite3.connect('/home/jordan/agente1/script/database/agentes.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, Agentes, Extension FROM Agentes WHERE Estado = 'Vacio'")
    for fila in cursor.fetchall():
        # Separar los valores en dos variables
        id, agente, extension = fila
        cursor.execute("UPDATE Agentes SET Cedula=?, Extension = ?, Estado = ? WHERE id = ?", (argumento, extension, 'Iniciando', id))
        conn.commit()
        conn.close()
        agi.exec_command('ChannelRedirect', f'{canal},clase,{extension},1')

        break  # Puedes detener el bucle después de la primera transferencia si es necesario
           

except Exception as e:
    # Maneja cualquier excepción que pueda ocurrir durante la lectura del archivo
    agi.verbose(f'Error al leer el archivo CSV: {str(e)}')
