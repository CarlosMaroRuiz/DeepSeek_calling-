from typing import Dict, Any, List

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