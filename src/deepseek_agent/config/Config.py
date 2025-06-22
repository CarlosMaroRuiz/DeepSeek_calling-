#clase que nos servira para las configuraciones 
from dotenv import load_dotenv
import os

load_dotenv()
"""
En la clase agregaremos configuraciones y variables de entorno 
"""

class Config:
    def __init__(self):
        self.deepseek_api = os.getenv("DEEPSEEK_API_KEY")

#creamos una instancia para compartirlos en la demas parte de nuesto code
config = Config()