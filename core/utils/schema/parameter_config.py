from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Union

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