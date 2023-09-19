from enum import Enum

class EstadoAgente(Enum):
    DISPONIBLE = 'DISPONIBLE'
    INICIANDO = 'INICIANDO'
    INICIADO = 'INICIADO'
    OCUPADO = 'OCUPADO'
