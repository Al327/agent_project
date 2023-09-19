import uuid
from google.cloud import dialogflowcx_v3beta1 as dialogflow

class DialogflowUtils:
    @staticmethod
    def iniciador(argm, session_path):
        try:
            query_input = dialogflow.QueryInput(
                text=dialogflow.TextInput(text=argm),
                language_code="es-419"
            )
            request = dialogflow.DetectIntentRequest(
                session=session_path,
                query_input=query_input
            )
        except Exception as e:
            print("Error:", e)
        

    @staticmethod
    def inijson(info):
        # Implementa el código para el método inijson aquí
        print(f'Iniciando JSON con información: {info}')

    @staticmethod
    def generateDialogFlowSessionId():
        return str(uuid.uuid4())
    
    #*Función que realiza el envío de un request a dialogflow y retorna su respuesta
    @staticmethod
    def dialogFlowInteraction(request, session_path, session_client):
        try:
            query_input = dialogflow.QueryInput(
                text=dialogflow.TextInput(text=request),
                language_code="es-419"
            )
            
            dilogflowRequest = dialogflow.DetectIntentRequest(
                session=session_path,
                query_input=query_input
            )
            
            # Enviar la solicitud y recibir la respuesta
            response = session_client.detect_intent(request=dilogflowRequest)
            
            # Extraer y mostrar la respuesta del agente
            response_texts = []
            if response.query_result.response_messages:
                for message in response.query_result.response_messages:
                    if message.text.text:
                        response_texts.append(message.text.text[0])
                        
            # Unir los textos en un solo texto
            response = None
            
            if response_texts:
                response = " ".join(response_texts)
            
            return response
        
        except Exception as e:
            print("Error:", e)
            return None
