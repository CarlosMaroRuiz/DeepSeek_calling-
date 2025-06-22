from src.deepseek_agent import DeepSeekAgent
from example1.schemas.schema_excel import schema
from example1.tools.extract_information_excel import extract_information_excel

def execute_example1():
    agent = DeepSeekAgent()
    agent.add_system_message("Eres una analista de datos. Analiza archivos Excel y da insights útiles.")
    agent.add_function(extract_information_excel, schema)
    respuesta = agent.chat("Analiza el archivo datos_negocio_simulado.xlsx")
    print(respuesta)