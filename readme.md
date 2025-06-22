# Documentación DeepSeek Agent(core)

## Introducción

El **DeepSeek Agent** es una biblioteca Python diseñada para facilitar la integración con la API de DeepSeek, proporcionando capacidades avanzadas de **function calling**, gestión de esquemas y herramientas personalizadas.

## 📁 Estructura del Core

```
core/
├── __init__.py
├── DeepSeekAgent.py          # Agente principal
├── config/
│   ├── __init__.py
│   └── Config.py             # Configuraciones y variables de entorno
└── utils/
    ├── __init__.py
    └── generator_schema.py   # Generador automático de esquemas
```

---

## 🔧 Function Calling

### ¿Qué es Function Calling?

**Function Calling** es una característica que permite a los modelos de IA ejecutar funciones específicas durante una conversación. En lugar de solo generar texto, el modelo puede:

- Identificar cuándo necesita ejecutar una función
- Extraer los parámetros necesarios del contexto
- Llamar a la función con los parámetros correctos
- Usar el resultado de la función para generar una respuesta más precisa

### Beneficios

- **Precisión**: Acceso a datos en tiempo real
- **Flexibilidad**: Extensión de capacidades del modelo
- **Integración**: Conexión con sistemas externos
- **Automatización**: Ejecución de tareas complejas

---

## 📋 Schemas (Esquemas)

### Propósito de los Schemas

Los **schemas** son definiciones estructuradas que describen:
- Qué hace una función
- Qué parámetros necesita
- Tipos de datos esperados
- Validaciones y restricciones

### Estructura de un Schema

```json
{
  "type": "function",
  "function": {
    "name": "nombre_función",
    "description": "Descripción de qué hace la función",
    "parameters": {
      "type": "object",
      "properties": {
        "parametro1": {
          "type": "string",
          "description": "Descripción del parámetro"
        }
      },
      "required": ["parametro1"]
    }
  }
}
```

### Ejemplo Práctico

```python
schema_clima = {
    "type": "function",
    "function": {
        "name": "obtener_clima",
        "description": "Obtiene información del clima actual",
        "parameters": {
            "type": "object",
            "properties": {
                "ciudad": {
                    "type": "string",
                    "description": "Nombre de la ciudad"
                },
                "unidad": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Unidad de temperatura"
                }
            },
            "required": ["ciudad"]
        }
    }
}
```

---

## 🛠️ Tools (Herramientas)

### Definición

Las **tools** son funciones Python que el agente puede ejecutar. Cada tool debe:
- Tener un schema asociado
- Manejar errores apropiadamente
- Retornar resultados en formato string o serializable

### Ejemplo de Tool

```python
def obtener_clima(ciudad: str, unidad: str = "celsius") -> str:
    """Tool que obtiene información del clima"""
    try:
        # Lógica para obtener clima
        temperatura = 25  # Ejemplo
        return f"La temperatura en {ciudad} es {temperatura}°{unidad[0].upper()}"
    except Exception as e:
        return f"Error obteniendo clima: {str(e)}"
```

### Registro de Tools

```python
agent = DeepSeekAgent()
agent.add_function(obtener_clima, schema_clima)
```

---

## 🤖 DeepSeekAgent - Métodos Principales

### Inicialización

```python
from core.DeepSeekAgent import DeepSeekAgent

# Crear instancia del agente
agent = DeepSeekAgent()
```

**Qué hace**: Inicializa el agente con configuración de API, modelos disponibles, sistema de logging y diccionarios para almacenar funciones y schemas.

### Configuración del Sistema

```python
# Establecer personalidad/contexto del agente
agent.add_system_message("Eres un asistente especializado en análisis de datos.")
```

**Qué hace**: Define el comportamiento y contexto del agente. Este mensaje se mantiene al inicio de todas las conversaciones.

### Gestión de Funciones

```python
# Agregar función
agent.add_function(mi_funcion, mi_schema)
```

**Qué hace**: Registra una función Python y su schema correspondiente para que el agente pueda ejecutarla durante las conversaciones.

```python
# Listar funciones disponibles
funciones = agent.get_available_functions()
```

**Qué hace**: Retorna una lista con los nombres de todas las funciones registradas en el agente.

```python
# Remover función
agent.remove_function("nombre_función")
```

**Qué hace**: Elimina una función específica del agente, incluyendo su schema asociado.

### Chat Básico

```python
# Chat normal
respuesta = agent.chat("¿Cómo está el clima en Madrid?")
```

**Qué hace**: Envía un mensaje al modelo, evalúa si necesita ejecutar funciones, las ejecuta si es necesario y retorna la respuesta final.

```python
# Chat sin usar funciones
respuesta = agent.chat("Explícame qué es Python", use_functions=False)
```

**Qué hace**: Realiza una conversación normal sin evaluar o ejecutar ninguna función, útil para preguntas generales.

```python
# Chat con streaming
respuesta = agent.stream_chat("Analiza estos datos...")
```

**Qué hace**: Igual que chat normal pero muestra la respuesta en tiempo real palabra por palabra, útil para respuestas largas.

### Chat con Razonamiento

```python
# Para problemas complejos que requieren razonamiento paso a paso
resultado = agent.reasoning_chat("Resuelve este problema matemático complejo...")

print("Razonamiento:", resultado["reasoning"])
print("Respuesta:", resultado["answer"])
```

**Qué hace**: Utiliza el modelo DeepSeek-R1 especializado en razonamiento para problemas complejos que requieren análisis paso a paso.

### Gestión del Historial

```python
# Limpiar historial (mantener mensaje del sistema)
agent.clear_history(keep_system=True)
```

**Qué hace**: Elimina todo el historial de conversación, opcionalmente manteniendo el mensaje del sistema.

```python
# Guardar conversación
agent.save_conversation("mi_conversacion.json")
```

**Qué hace**: Exporta todo el historial de conversación a un archivo JSON para futura referencia.

```python
# Cargar conversación
agent.load_conversation("mi_conversacion.json")
```

**Qué hace**: Importa un historial de conversación previo desde un archivo JSON.

### Estadísticas

```python
# Obtener estadísticas del agente
stats = agent.get_stats()
print(f"Funciones registradas: {stats['functions_count']}")
print(f"Longitud de conversación: {stats['conversation_length']}")
```

**Qué hace**: Retorna un diccionario con información sobre el estado actual del agente: número de funciones, longitud del historial, etc.

---

## ⚙️ Configuración (Config.py)

### Propósito

La clase `Config` gestiona:
- Variables de entorno
- Configuraciones globales
- Credenciales de API

### Uso

```python
from core.config.Config import config

# La API key se carga automáticamente desde .env
api_key = config.deepseek_api
```

### Variables de Entorno

Crear archivo `.env`:
```env
DEEPSEEK_API_KEY=tu_api_key_aqui
```

---

## 📁 Estructura de Proyecto Recomendada

### Example1 - Análisis de Excel

```
example1/
├── __init__.py
├── app.py                    # Punto de entrada del ejemplo
├── schemas/
│   ├── __init__.py
│   └── schema_excel.py       # Schema para funciones de Excel
└── tools/
    ├── __init__.py
    └── extract_information_excel.py  # Herramienta de análisis
```

**Ventajas de esta Estructura**:
- **Modularidad**: Cada ejemplo es independiente
- **Escalabilidad**: Fácil agregar nuevos ejemplos
- **Reutilización**: Schemas y tools compartidas
- **Mantenimiento**: Separación clara de responsabilidades

---

## 🔄 Flujo de Trabajo Detallado - Paso a Paso

### Paso 1: Preparación del Entorno

```python
# 1.1 Instalar dependencias
# pip install openai python-dotenv pandas

# 1.2 Configurar variables de entorno
# Crear archivo .env con DEEPSEEK_API_KEY=tu_clave
```

### Paso 2: Importar y Crear el Agente

```python
from core.DeepSeekAgent import DeepSeekAgent

# 2.1 Instanciar el agente
agent = DeepSeekAgent()
```

**Lo que sucede internamente**:
- Se carga la configuración de API
- Se inicializa el cliente OpenAI con la URL de DeepSeek
- Se preparan los diccionarios para funciones y schemas
- Se configura el sistema de logging

### Paso 3: Configurar la Personalidad del Agente

```python
# 3.1 Definir el comportamiento del agente
agent.add_system_message(
    "Eres un analista de datos experto especializado en Excel. "
    "Proporcionas insights claros y análisis detallados."
)
```

**Lo que sucede**:
- Se agrega o reemplaza el mensaje del sistema
- Este mensaje guía todas las respuestas del agente

### Paso 4: Crear y Registrar Tools

```python
# 4.1 Definir la función/tool
def analizar_excel(file_path: str) -> str:
    """Analiza un archivo Excel y retorna información básica"""
    try:
        import pandas as pd
        df = pd.read_excel(file_path)
        
        info = {
            "filas": len(df),
            "columnas": list(df.columns),
            "muestra": df.head(3).to_dict('records')
        }
        return json.dumps(info, indent=2, default=str)
    except Exception as e:
        return f"Error: {str(e)}"

# 4.2 Definir el schema
schema_excel = {
    "type": "function",
    "function": {
        "name": "analizar_excel",
        "description": "Analiza archivo Excel y extrae información básica",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Ruta del archivo Excel a analizar"
                }
            },
            "required": ["file_path"]
        }
    }
}

# 4.3 Registrar la función en el agente
agent.add_function(analizar_excel, schema_excel)
```

**Lo que sucede al registrar**:
- Se valida que el schema esté bien formado
- Se almacena la función en el diccionario de funciones disponibles
- Se agrega el schema a la lista de herramientas del agente

### Paso 5: Iniciar la Conversación

```python
# 5.1 Enviar mensaje del usuario
mensaje_usuario = "Analiza el archivo datos_ventas.xlsx y dame un resumen"
respuesta = agent.chat(mensaje_usuario)
```

**Proceso interno detallado**:

1. **Evaluación del mensaje**: El agente analiza si necesita usar funciones
2. **Construcción de parámetros**: Se prepara la llamada a la API con el historial y las tools disponibles
3. **Llamada al modelo**: DeepSeek evalúa el mensaje y decide ejecutar funciones
4. **Identificación de función**: El modelo identifica que necesita `analizar_excel`
5. **Extracción de parámetros**: Extrae `file_path = "datos_ventas.xlsx"`
6. **Ejecución de función**: Se ejecuta la función Python con los parámetros
7. **Procesamiento de resultado**: Se agrega el resultado al historial
8. **Respuesta final**: Nueva llamada al modelo para generar respuesta basada en los resultados

### Paso 6: Análisis del Resultado

```python
# 6.1 El agente retorna una respuesta integrada
print(respuesta)

# Ejemplo de respuesta:
# "He analizado el archivo datos_ventas.xlsx. El archivo contiene 1,250 filas 
# de datos con las columnas: fecha, producto, ventas, región. Los datos muestran
# ventas de productos tecnológicos en diferentes regiones..."
```

### Paso 7: Conversación Continua

```python
# 7.1 Seguir la conversación
respuesta2 = agent.chat("¿Cuál es la región con más ventas?")

# 7.2 El agente puede volver a usar las funciones o responder basado en contexto previo
```

### Paso 8: Gestión del Historial

```python
# 8.1 Ver estadísticas
stats = agent.get_stats()
print(f"Mensajes en conversación: {stats['conversation_length']}")

# 8.2 Guardar conversación para análisis posterior
agent.save_conversation("sesion_analisis_ventas.json")

# 8.3 Limpiar historial para nueva sesión
agent.clear_history(keep_system=True)
```

### Ejemplo Completo Funcional

```python
# script_completo.py
from core.DeepSeekAgent import DeepSeekAgent
import pandas as pd
import json

def main():
    # Paso 1: Crear agente
    agent = DeepSeekAgent()
    
    # Paso 2: Configurar personalidad
    agent.add_system_message("Eres un analista de datos experto.")
    
    # Paso 3: Definir tool
    def analizar_datos(archivo: str) -> str:
        try:
            df = pd.read_excel(archivo)
            return f"Archivo analizado: {len(df)} filas, columnas: {list(df.columns)}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    # Paso 4: Definir schema
    schema = {
        "type": "function",
        "function": {
            "name": "analizar_datos",
            "description": "Analiza archivos Excel",
            "parameters": {
                "type": "object",
                "properties": {
                    "archivo": {"type": "string", "description": "Ruta del archivo"}
                },
                "required": ["archivo"]
            }
        }
    }
    
    # Paso 5: Registrar función
    agent.add_function(analizar_datos, schema)
    
    # Paso 6: Interactuar
    respuesta = agent.chat("Analiza el archivo ventas.xlsx")
    print(respuesta)

if __name__ == "__main__":
    main()
```

---

## 📝 Mejores Prácticas

### Para Schemas
- Descripciones claras y específicas
- Validaciones apropiadas (min/max, enum, etc.)
- Manejo de parámetros opcionales

### Para Tools
- Manejo robusto de errores
- Retorno de strings descriptivos
- Validación de parámetros de entrada

### Para el Agente
- Mensajes del sistema específicos al dominio
- Limpieza periódica del historial
- Uso apropiado del modelo de razonamiento para problemas complejos

### Para el Flujo de Trabajo
- Siempre validar que las funciones manejen errores
- Testear funciones independientemente antes de registrarlas
- Usar nombres descriptivos para funciones y parámetros
- Mantener el historial organizado con guardado periódico

---

Esta biblioteca proporciona una base sólida para crear asistentes de IA especializados con capacidades extendidas a través de function calling, manteniendo simplicidad en el uso y flexibilidad en la implementación.