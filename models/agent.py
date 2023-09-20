class Agente:
    def __init__(self, id, dialogflow_agent_id, name, extention, status, client_identification, audios_directory):
        self.id = id
        self.dialogflow_agent_id = dialogflow_agent_id
        self.name = name
        self.extention = extention
        self.status = status
        self.client_identification = client_identification
        self.audios_directory =audios_directory