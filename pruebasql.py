import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('/home/jordan/agent_project/database/agentes.db')
cursor = conn.cursor()
cedula = '0932560675'  # Asegúrate de que cedula sea una cadena de texto
cursor.execute("SELECT id, Agentes, Extension FROM Agentes WHERE Estado = 'Vacio'")
for fila in cursor.fetchall():
    # Separar los valores en dos variables
    id, agente, extension = fila
    print(fila)
    cursor.execute("UPDATE Agentes SET Cedula=?, Extension = ?, Estado = ? WHERE id = ?", (cedula, extension, 'Iniciando', id))

# Confirmar los cambios y cerrar la conexión
conn.commit()
conn.close()
