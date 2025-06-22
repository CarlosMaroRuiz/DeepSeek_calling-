import pandas as pd
import json
def extract_information_excel(file_path: str = "datos_negocio_simulado.xlsx") -> str:
    try:
        df = pd.read_excel(file_path)
        info = {
            "filas": len(df),
            "columnas": list(df.columns),
            "muestra": df.head(2).to_dict('records')
        }
        return json.dumps(info, indent=2, default=str)
    except Exception as e:
        return f"Error: {str(e)}"