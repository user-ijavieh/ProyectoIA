import re
from transformers import pipeline

# Modelo de clasificación Zero-Shot
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Menú extendido unificado
MENU_PRODUCTOS = [
    "pizza", "hamburguesa", "tacos", "ensalada", "zumo", 
    "pasta", "pan", "panes", "perrito caliente", "hot dog", "refresco", "coca cola"
]

def extraer_multiples_pedidos(frase_usuario):
    """Descompone una frase natural en una lista de productos, cantidades y notas."""
    # 1. Normalización de números escritos como palabras
    mapa_numeros = {
        "una": "1", "un": "1", "uno": "1",
        "dos": "2", "tres": "3", "cuatro": "4", "cinco": "5"
    }
    
    texto = frase_usuario.lower().replace(" y ", ", ")
    
    # Reemplazamos palabras por dígitos para que el motor las entienda
    for palabra, numero in mapa_numeros.items():
        texto = re.sub(rf'\b{palabra}\b', numero, texto)
    
    # 2. Segmentación: Dividimos por comas para obtener cada producto por separado
    segmentos = [s.strip() for s in texto.split(",") if s.strip()]
    
    lista_pedidos = []
    for seg in segmentos:
        # Extraer cantidad (ahora que todo son dígitos es más fácil)
        cant_match = re.search(r'\d+', seg)
        cantidad = int(cant_match.group(0)) if cant_match else 1
        
        # 3. Clasificación del producto
        res = classifier(seg, candidate_labels=MENU_PRODUCTOS)
        producto_ia = res['labels'][0] if res['scores'][0] > 0.4 else "Especial/Otro"
        
        # 4. Limpieza profunda de la nota
        # Eliminamos la cantidad y el producto detectado para ver qué sobra
        nota = seg.replace(str(cantidad), "").replace(producto_ia.lower(), "").strip()
        
        # Quitamos conectores y restos de plurales (como la 's' final de 'pizzas')
        nota = re.sub(r'\bs\b', '', nota) # Quita 's' sueltas
        palabras_limpieza = ["quiero", "ponme", " de ", " con ", " por favor"]
        for p in palabras_limpieza:
            nota = nota.replace(p, " ")
        
        lista_pedidos.append({
            "producto": producto_ia.capitalize(),
            "cantidad": cantidad,
            "nota": nota.strip().capitalize() if len(nota.strip()) > 1 else "Sin notas"
        })
    return lista_pedidos