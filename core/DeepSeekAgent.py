import json
import logging
from typing import List, Dict, Any, Optional, Callable
from openai import OpenAI
from core.config.Config import config

class DeepSeekAgent:
    def __init__(self):
        """
        Inicializa el agente DeepSeek con configuración y herramientas
        """
        # Configuración de API
        self.api_key = config.deepseek_api
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        
    
        self.function_schemas = []
        
        # Diccionario de funciones ejecutables
        self.available_functions = {}
        
        # Configuración de modelos
        self.models = {
            "chat": "deepseek-chat",
            "reasoning": "deepseek-reasoner"
        }
        
        # Configuración de logging
        self.logger = self._setup_logger()
        
        # Historial de conversación
        self.conversation_history = []
        
        # Configuraciones por defecto
        self.default_config = {
            "temperature": 0.7,
            "max_tokens": 2000,
            "model": self.models["chat"]
        }
    
    def _setup_logger(self) -> logging.Logger:
        """Configura el sistema de logging"""
        logger = logging.getLogger('DeepSeekAgent')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def add_function(self, function: Callable, schema: Dict[str, Any]) -> None:
        """
        Agrega una función y su schema al agente
        
        Args:
            function: La función Python a ejecutar
            schema: El schema JSON que describe la función para DeepSeek
        """
        function_name = schema["function"]["name"]
        
        # Validar que el schema esté bien formado
        if not self._validate_schema(schema):
            raise ValueError(f"Schema inválido para función {function_name}")
        
        # Agregar función y schema
        self.available_functions[function_name] = function
        self.function_schemas.append(schema)
        
        self.logger.info(f"Función '{function_name}' agregada exitosamente")
    
    def _validate_schema(self, schema: Dict[str, Any]) -> bool:
        """Valida que el schema tenga la estructura correcta"""
        required_keys = ["type", "function"]
        function_keys = ["name", "description", "parameters"]
        
        if not all(key in schema for key in required_keys):
            return False
        
        if not all(key in schema["function"] for key in function_keys):
            return False
        
        return schema["type"] == "function"
    
    def add_system_message(self, content: str) -> None:
        """Agrega mensaje del sistema al historial"""
        system_message = {"role": "system", "content": content}
        
        # Si ya hay un mensaje del sistema, lo reemplaza
        if self.conversation_history and self.conversation_history[0]["role"] == "system":
            self.conversation_history[0] = system_message
        else:
            self.conversation_history.insert(0, system_message)
    
    def chat(self, message: str, use_functions: bool = True, 
             model_type: str = "chat", **kwargs) -> str:
        """
        Envía un mensaje al agente y obtiene respuesta
        
        Args:
            message: Mensaje del usuario
            use_functions: Si usar function calling
            model_type: "chat" o "reasoning"
            **kwargs: Parámetros adicionales para la API
        """
        # Agregar mensaje del usuario al historial
        self.conversation_history.append({
            "role": "user",
            "content": message
        })
        
        try:
            # Configurar parámetros
            api_params = self._build_api_params(use_functions, model_type, **kwargs)
            
            # Realizar llamada a la API
            response = self.client.chat.completions.create(**api_params)
            
            # Procesar respuesta
            return self._process_response(response, use_functions)
            
        except Exception as e:
            self.logger.error(f"Error en chat: {str(e)}")
            return f"Error: {str(e)}"
    
    def _build_api_params(self, use_functions: bool, model_type: str, **kwargs) -> Dict[str, Any]:
        """Construye parámetros para la llamada API"""
        # Configuración base
        params = {
            "model": self.models.get(model_type, self.models["chat"]),
            "messages": self.conversation_history.copy(),
            **self.default_config,
            **kwargs
        }
        
        # Agregar herramientas si se solicita
        if use_functions and self.function_schemas:
            params["tools"] = self.function_schemas
            params["tool_choice"] = "auto"
        
        return params
    
    def _process_response(self, response, use_functions: bool) -> str:
        """Procesa la respuesta de DeepSeek"""
        message = response.choices[0].message
        
        # Si hay llamadas a funciones
        if use_functions and hasattr(message, 'tool_calls') and message.tool_calls:
            return self._handle_function_calls(message, response)
        
        # Respuesta normal
        assistant_response = message.content
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_response
        })
        
        return assistant_response
    
    def _handle_function_calls(self, message, original_response) -> str:
        """Maneja las llamadas a funciones"""
        # Agregar mensaje del asistente con tool_calls
        self.conversation_history.append(message)
        
        # Ejecutar cada función llamada
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            self.logger.info(f"Ejecutando función: {function_name} con args: {function_args}")
            
            # Ejecutar función
            try:
                if function_name in self.available_functions:
                    result = self.available_functions[function_name](**function_args)
                else:
                    result = f"Error: Función '{function_name}' no encontrada"
                
            except Exception as e:
                result = f"Error ejecutando {function_name}: {str(e)}"
                self.logger.error(result)
            
            # Agregar resultado al historial
            self.conversation_history.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": str(result)
            })
        
        # Obtener respuesta final
        final_response = self.client.chat.completions.create(
            model=self.default_config["model"],
            messages=self.conversation_history
        )
        
        final_content = final_response.choices[0].message.content
        self.conversation_history.append({
            "role": "assistant",
            "content": final_content
        })
        
        return final_content
    
    def reasoning_chat(self, problem: str) -> Dict[str, str]:
        """
        Usa el modelo de razonamiento DeepSeek-R1 para problemas complejos
        
        Args:
            problem: Problema o pregunta compleja
            
        Returns:
            Dict con 'reasoning' y 'answer'
        """
        try:
            response = self.client.chat.completions.create(
                model=self.models["reasoning"],
                messages=[{"role": "user", "content": problem}]
            )
            
            message = response.choices[0].message
            
            return {
                "reasoning": getattr(message, 'reasoning_content', ''),
                "answer": message.content
            }
            
        except Exception as e:
            self.logger.error(f"Error en reasoning: {str(e)}")
            return {
                "reasoning": "",
                "answer": f"Error: {str(e)}"
            }
    
    def stream_chat(self, message: str, use_functions: bool = True) -> str:
        """Chat con streaming de respuesta"""
        self.conversation_history.append({
            "role": "user",
            "content": message
        })
        
        try:
            params = self._build_api_params(use_functions, "chat")
            params["stream"] = True
            
            stream = self.client.chat.completions.create(**params)
            
            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content
            
            self.conversation_history.append({
                "role": "assistant",
                "content": full_response
            })
            
            return full_response
            
        except Exception as e:
            self.logger.error(f"Error en stream: {str(e)}")
            return f"Error: {str(e)}"
    
    def clear_history(self, keep_system: bool = True) -> None:
        """Limpia el historial de conversación"""
        if keep_system and self.conversation_history and self.conversation_history[0]["role"] == "system":
            system_msg = self.conversation_history[0]
            self.conversation_history = [system_msg]
        else:
            self.conversation_history = []
        
        self.logger.info("Historial limpiado")
    
    def get_available_functions(self) -> List[str]:
        """Retorna lista de funciones disponibles"""
        return list(self.available_functions.keys())
    
    def remove_function(self, function_name: str) -> bool:
        """Remueve una función del agente"""
        if function_name in self.available_functions:
            del self.available_functions[function_name]
            
            # Remover schema correspondiente
            self.function_schemas = [
                schema for schema in self.function_schemas 
                if schema["function"]["name"] != function_name
            ]
            
            self.logger.info(f"Función '{function_name}' removida")
            return True
        
        return False
    
    def save_conversation(self, filepath: str) -> bool:
        """Guarda la conversación en un archivo JSON"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error guardando conversación: {str(e)}")
            return False
    
    def load_conversation(self, filepath: str) -> bool:
        """Carga una conversación desde un archivo JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.conversation_history = json.load(f)
            return True
        except Exception as e:
            self.logger.error(f"Error cargando conversación: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del agente"""
        return {
            "functions_count": len(self.available_functions),
            "conversation_length": len(self.conversation_history),
            "available_functions": list(self.available_functions.keys()),
            "models": self.models
        }