schema = {
    "type": "function",
    "function": {
        "name": "extract_information_excel",
        "description": "Analiza archivo Excel",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Archivo Excel a analizar",
                    "default": "datos_negocio_simulado.xlsx"
                }
            },
            "required": ["file_path"]
        }
    }
}