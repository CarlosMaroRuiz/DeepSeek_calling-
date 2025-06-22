from typing import Dict, Any, List, Optional, Union
import inspect
from dataclasses import dataclass

@dataclass
class ParameterConfig:
    """Configuración para un parámetro de función"""
    param_type: str  # "string", "number", "integer", "boolean", "array", "object"
    description: str
    required: bool = False
    enum: Optional[List[Any]] = None
    minimum: Optional[Union[int, float]] = None
    maximum: Optional[Union[int, float]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    default: Optional[Any] = None
    items: Optional[Dict[str, Any]] = None  # Para arrays
    properties: Optional[Dict[str, Any]] = None  # Para objects

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

# Schemas predefinidos comunes
class CommonSchemas:
    """Colección de schemas comunes ya definidos"""
    
    @staticmethod
    def get_weather() -> Dict[str, Any]:
        """Schema para función de clima"""
        return SchemaGenerator.create_schema(
            "get_weather",
            "Obtiene información del clima actual",
            {
                "location": ParameterConfig(
                    param_type="string",
                    description="Ciudad y país (ej: 'Madrid, España')",
                    required=True,
                    min_length=2
                ),
                "unit": ParameterConfig(
                    param_type="string",
                    description="Unidad de temperatura",
                    enum=["celsius", "fahrenheit", "kelvin"],
                    default="celsius"
                ),
                "include_forecast": ParameterConfig(
                    param_type="boolean",
                    description="Incluir pronóstico extendido",
                    default=False
                )
            }
        )
    
    @staticmethod
    def calculate_math() -> Dict[str, Any]:
        """Schema para calculadora matemática"""
        return SchemaGenerator.create_schema(
            "calculate_math",
            "Realiza cálculos matemáticos complejos",
            {
                "expression": ParameterConfig(
                    param_type="string",
                    description="Expresión matemática a calcular",
                    required=True,
                    min_length=1
                ),
                "precision": ParameterConfig(
                    param_type="integer",
                    description="Número de decimales en el resultado",
                    minimum=0,
                    maximum=15,
                    default=2
                )
            }
        )
    
    @staticmethod
    def search_database() -> Dict[str, Any]:
        """Schema para búsqueda en base de datos"""
        return SchemaGenerator.create_schema(
            "search_database",
            "Busca registros en la base de datos",
            {
                "table": ParameterConfig(
                    param_type="string",
                    description="Nombre de la tabla a consultar",
                    required=True
                ),
                "filters": ParameterConfig(
                    param_type="object",
                    description="Filtros de búsqueda",
                    properties={
                        "field": {"type": "string"},
                        "value": {"type": "string"},
                        "operator": {"type": "string", "enum": ["=", "!=", ">", "<", "LIKE"]}
                    }
                ),
                "limit": ParameterConfig(
                    param_type="integer",
                    description="Máximo número de resultados",
                    minimum=1,
                    maximum=1000,
                    default=50
                ),
                "order_by": ParameterConfig(
                    param_type="string",
                    description="Campo para ordenar resultados"
                )
            }
        )
    
    @staticmethod
    def send_email() -> Dict[str, Any]:
        """Schema para envío de emails"""
        return SchemaGenerator.create_schema(
            "send_email",
            "Envía un email a destinatarios especificados",
            {
                "to": ParameterConfig(
                    param_type="array",
                    description="Lista de destinatarios",
                    required=True,
                    items={"type": "string", "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"}
                ),
                "subject": ParameterConfig(
                    param_type="string",
                    description="Asunto del email",
                    required=True,
                    min_length=1,
                    max_length=255
                ),
                "body": ParameterConfig(
                    param_type="string",
                    description="Contenido del email",
                    required=True,
                    min_length=1
                ),
                "cc": ParameterConfig(
                    param_type="array",
                    description="Lista de destinatarios en copia",
                    items={"type": "string"}
                ),
                "priority": ParameterConfig(
                    param_type="string",
                    description="Prioridad del email",
                    enum=["low", "normal", "high"],
                    default="normal"
                )
            }
        )
    
    @staticmethod
    def file_operations() -> Dict[str, Any]:
        """Schema para operaciones de archivos"""
        return SchemaGenerator.create_schema(
            "file_operations",
            "Realiza operaciones sobre archivos del sistema",
            {
                "operation": ParameterConfig(
                    param_type="string",
                    description="Tipo de operación a realizar",
                    required=True,
                    enum=["read", "write", "delete", "copy", "move", "list"]
                ),
                "file_path": ParameterConfig(
                    param_type="string",
                    description="Ruta del archivo",
                    required=True
                ),
                "content": ParameterConfig(
                    param_type="string",
                    description="Contenido para operaciones de escritura"
                ),
                "destination": ParameterConfig(
                    param_type="string",
                    description="Ruta de destino para operaciones copy/move"
                ),
                "encoding": ParameterConfig(
                    param_type="string",
                    description="Codificación del archivo",
                    enum=["utf-8", "latin-1", "ascii"],
                    default="utf-8"
                )
            }
        )

# Validador de schemas
class SchemaValidator:
    """Valida schemas antes de usarlos"""
    
    @staticmethod
    def validate(schema: Dict[str, Any]) -> bool:
        """Valida que un schema esté bien formado"""
        try:
            # Verificar estructura básica
            if not isinstance(schema, dict):
                return False
            
            if schema.get("type") != "function":
                return False
            
            function_def = schema.get("function", {})
            
            required_keys = ["name", "description", "parameters"]
            if not all(key in function_def for key in required_keys):
                return False
            
            # Validar parámetros
            params = function_def.get("parameters", {})
            if params.get("type") != "object":
                return False
            
            properties = params.get("properties", {})
            required = params.get("required", [])
            
            # Verificar que todos los required estén en properties
            for req_param in required:
                if req_param not in properties:
                    return False
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def get_validation_errors(schema: Dict[str, Any]) -> List[str]:
        """Retorna lista de errores de validación"""
        errors = []
        
        if not isinstance(schema, dict):
            errors.append("Schema debe ser un diccionario")
            return errors
        
        if schema.get("type") != "function":
            errors.append("Tipo debe ser 'function'")
        
        function_def = schema.get("function")
        if not function_def:
            errors.append("Falta definición de 'function'")
            return errors
        
        required_keys = ["name", "description", "parameters"]
        for key in required_keys:
            if key not in function_def:
                errors.append(f"Falta campo requerido: function.{key}")
        
        params = function_def.get("parameters", {})
        if params.get("type") != "object":
            errors.append("parameters.type debe ser 'object'")
        
        properties = params.get("properties", {})
        required = params.get("required", [])
        
        for req_param in required:
            if req_param not in properties:
                errors.append(f"Parámetro requerido '{req_param}' no está en properties")
        
        return errors