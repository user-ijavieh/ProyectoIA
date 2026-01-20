import re
from transformers import pipeline

# Modelo de clasificación Zero-Shot
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# --- BLOQUE 1: Configuración y Helpers (Preservado de HEAD) ---

# Define aquí los productos reales de tu carta
MENU_PRODUCTOS = [
    "pizza", "hamburguesa", "tacos", "ensalada", "zumo", 
    "pasta", "pan", "panes", "perrito caliente", "hot dog", "refresco", "coca cola"
]

def es_saludo_o_despedida(texto):
    """Detecta si el usuario está saludando o despidiéndose."""
    texto = texto.lower().strip()
    
    saludos = ["hola", "buenas", "buenos dias", "buenos días", "buenas tardes", "buenas noches", "hey", "qué tal", "que tal"]
    despedidas = ["adios", "adiós", "chao", "hasta luego", "nos vemos", "bye", "hasta pronto", "gracias"]
    
    # Si el texto es EXACTAMENTE un saludo/despedida o empieza por uno muy común
    for s in saludos:
        if texto == s or texto.startswith(s + " "):
            return "saludo"
            
    for d in despedidas:
        if texto == d or texto.startswith(d + " "):
            return "despedida"
            
    return None

# --- BLOQUE 2: Lógica Principal (Fusión priorizando la robustez de HEAD) ---

def extraer_multiples_pedidos(frase_usuario):
    """Descompone una frase natural en una lista de productos, cantidades y notas."""
    # 1. Normalización de números escritos como palabras
    mapa_numeros = {
        "una": "1", "un": "1", "uno": "1",
        "dos": "2", "tres": "3", "cuatro": "4", "cinco": "5"
    }
    
    texto = frase_usuario.lower().replace(" y ", ", ")
    
    # TRUCO: Convertimos palabras de unidad textuales a números para que el regex los pille
    # "dame una pizza" -> "dame 1 pizza"
    texto = re.sub(r'\b(un|una)\b', '1', texto)
    
    # Segmentación: Buscamos patrones que empiecen por un número
    # Esto separa "2 pizzas y 1 zumo" en ["2 pizzas ", " 1 zumo"]
    segmentos = re.findall(r'(\d+[\s\w\sñáéíóú]+)(?:,|$)', texto)
    
    if not segmentos:
        # Si no hay números, intentamos ver si menciona productos directamente
        segmentos = [texto] 

    # Reemplazamos palabras por dígitos para que el motor las entienda
    for palabra, numero in mapa_numeros.items():
        texto = re.sub(rf'\b{palabra}\b', numero, texto)
    
    # 2. Segmentación: Dividimos por comas para obtener cada producto por separado
    segmentos = [s.strip() for s in texto.split(",") if s.strip()]
    
    lista_pedidos = []
    
    for seg in segmentos:

        # Clasificar producto con IA
        # Extraer cantidad (ahora que todo son dígitos es más fácil)
        cant_match = re.search(r'\d+', seg)
        cantidad = int(cant_match.group(0)) if cant_match else 1
        
        # 3. Clasificación del producto
        res = classifier(seg, candidate_labels=MENU_PRODUCTOS)
        
        # 4. Limpieza profunda de la nota
        # Eliminamos la cantidad y el producto detectado para ver qué sobra
        nota = seg.replace(str(cantidad), "").replace(producto_ia.lower(), "").strip()
        
        # Quitamos conectores y restos de plurales (como la 's' final de 'pizzas')
        nota = re.sub(r'\bs\b', '', nota) # Quita 's' sueltas
        palabras_limpieza = ["quiero", "ponme", " de ", " con ", " por favor"]
        for p in palabras_limpieza:
            nota = nota.replace(p, " ")
        
        # 4. Formateo final
        nota = nota.strip().capitalize()
        nota = nota.lstrip(".,- ") # Quitamos puntuación que haya quedado al principio
        
        if not nota: 
            nota = "Sin notas"

        lista_pedidos.append({
            "producto": producto_ia.capitalize(),
            "cantidad": cantidad,
            "nota": nota.strip().capitalize() if len(nota.strip()) > 1 else "Sin notas"
        })
        
    return lista_pedidos