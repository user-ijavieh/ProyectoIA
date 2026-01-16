import re
from transformers import pipeline

# Modelo de clasificación Zero-Shot
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Menú extendido unificado
MENU_PRODUCTOS = [
    "pizza", "hamburguesa", "tacos", "ensalada", "zumo", 
    "pasta", "pan", "perrito caliente", "hot dog", "refresco", "coca cola"
]

def extraer_multiples_pedidos(frase_usuario):
    """Descompone una frase natural en una lista de productos, cantidades y notas."""
    texto = frase_usuario.lower().replace(" y ", ", ")
    
    # Segmentación por números
    segmentos = re.findall(r'(\d+[\s\w\sñáéíóú]+)(?:,|$)', texto)
    if not segmentos:
        segmentos = [texto]

    lista_pedidos = []
    for seg in segmentos:
        cant_match = re.search(r'\d+', seg)
        cantidad = int(cant_match.group(0)) if cant_match else 1
        
        res = classifier(seg, candidate_labels=MENU_PRODUCTOS)
        producto_ia = res['labels'][0] if res['scores'][0] > 0.4 else "Especial/Otro"
        
        # Limpieza de la nota
        nota = seg.replace(str(cantidad), "").replace(producto_ia, "")
        for p in ["quiero", "ponme", "un", "una", " de ", " con ", " por favor"]:
            nota = nota.replace(p, " ")
        
        lista_pedidos.append({
            "producto": producto_ia.capitalize(),
            "cantidad": cantidad,
            "nota": nota.strip().capitalize() if nota.strip() else "Sin notas"
        })
    return lista_pedidos