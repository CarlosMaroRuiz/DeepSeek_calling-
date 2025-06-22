from typing import Dict, Any, List, Optional, Union
import inspect
from .parameter_config import ParameterConfig

class SchemaGenerator:
    """Generador automático de schemas para function calling"""
    
    @staticmethod
    def create_schema(
        function_name: str,
        description: str,
        parameters: Dict[str, ParameterConfig]
    ) -> Dict[str, Any]:
        """
        Crea un schema completo para function calling
        
        Args:
            function_name: Nombre de la función
            description: Descripción de qué hace la función
            parameters: Diccionario de configuraciones de parámetros
        
        Returns:
            Schema completo en formato JSON
        """
        schema = {
            "type": "function",
            "function": {
                "name": function_name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
        
        # Procesar cada parámetro
        for param_name, config in parameters.items():
            prop = SchemaGenerator._build_property(config)
            schema["function"]["parameters"]["properties"][param_name] = prop
            
            # Agregar a required si es necesario
            if config.required:
                schema["function"]["parameters"]["required"].append(param_name)
        
        return schema
    
    @staticmethod
    def _build_property(config: ParameterConfig) -> Dict[str, Any]:
        """Construye una propiedad individual del schema"""
        prop = {
            "type": config.param_type,
            "description": config.description
        }
        
        # Agregar validaciones según el tipo
        if config.enum is not None:
            prop["enum"] = config.enum
        
        if config.minimum is not None:
            prop["minimum"] = config.minimum
        
        if config.maximum is not None:
            prop["maximum"] = config.maximum
        
        if config.min_length is not None:
            prop["minLength"] = config.min_length
        
        if config.max_length is not None:
            prop["maxLength"] = config.max_length
        
        if config.pattern is not None:
            prop["pattern"] = config.pattern
        
        if config.default is not None:
            prop["default"] = config.default
        
        # Para arrays
        if config.param_type == "array" and config.items is not None:
            prop["items"] = config.items
        
        # Para objects
        if config.param_type == "object" and config.properties is not None:
            prop["properties"] = config.properties
        
        return prop
    
    @staticmethod
    def from_function(func, description: str, param_descriptions: Dict[str, str]) -> Dict[str, Any]:
        """
        Genera schema automáticamente desde una función Python
        
        Args:
            func: Función Python
            description: Descripción de la función
            param_descriptions: Descripciones de cada parámetro
        
        Returns:
            Schema generado automáticamente
        """
        sig = inspect.signature(func)
        parameters = {}
        
        for param_name, param in sig.parameters.items():
            # Determinar tipo basado en annotation
            param_type = SchemaGenerator._infer_type(param.annotation)
            
            # Determinar si es requerido
            required = param.default == inspect.Parameter.empty
            
            # Crear configuración
            config = ParameterConfig(
                param_type=param_type,
                description=param_descriptions.get(param_name, f"Parámetro {param_name}"),
                required=required
            )
            
            # Agregar default si existe
            if param.default != inspect.Parameter.empty:
                config.default = param.default
            
            parameters[param_name] = config
        
        return SchemaGenerator.create_schema(func.__name__, description, parameters)
    
    @staticmethod
    def _infer_type(annotation) -> str:
        """Infiere el tipo JSON desde type hints de Python"""
        if annotation == inspect.Parameter.empty:
            return "string"  # Default
        
        type_mapping = {
            str: "string",
            int: "integer", 
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object"
        }
        
        return type_mapping.get(annotation, "string")