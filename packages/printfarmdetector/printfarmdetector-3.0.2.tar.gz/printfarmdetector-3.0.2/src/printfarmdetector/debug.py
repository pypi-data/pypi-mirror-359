import builtins
import base64
from openai import OpenAI

client = OpenAI(api_key="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")

def print(*args, **kwargs):
    """
    Reemplaza print para detectar hojas/frutos enfermos
    y añadir diagnóstico de plaga si se detecta 'enferma' en la clase.
    """
    for arg in args:
        if isinstance(arg, list):
            for item in arg:
                if isinstance(item, dict) and "clase" in item and "enferma" in item["clase"].lower():
                    image_bytes = kwargs.get("image_bytes")
                    if image_bytes:
                        try:
                            item["plaga"] = _analizar_con_openai(image_bytes)
                        except Exception as e:
                            item["plaga"] = "error"
                            builtins.print("Error al analizar imagen con OpenAI:", e)

    builtins.print(*args)


def _analizar_con_openai(image_bytes: bytes) -> str:
    """
    Analiza una imagen de granadilla para detectar si está afectada
    por trips o araña roja, según patrones visuales definidos.
    """
    imagen_base64 = base64.b64encode(image_bytes).decode("utf-8")

    prompt = (
        "Esta imagen muestra una hoja o fruto de granadilla enfermo. "
        "Analiza cuidadosamente los patrones visuales y determina si el daño se debe a trips o a araña roja.\n\n"
        "🔍 *Síntomas de trips*: manchas plateadas o bronceadas, deformaciones en hojas jóvenes, cicatrices, puntos negros.\n"
        "🕷️ *Síntomas de araña roja*: punteado clorótico (puntos amarillos), telarañas finas, decoloración progresiva, necrosis.\n\n"
        "Responde únicamente con una palabra en minúsculas: `trips` o `araña`."
    )

    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {"role": "user", "content": prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{imagen_base64}",
                    }
                ]
            }
        ],
    )

    return response.output_text.strip().lower()
