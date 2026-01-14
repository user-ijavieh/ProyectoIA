import re
from transformers import pipeline

# Cargamos el modelo de clasificación Zero-Shot (especializado en entender etiquetas sin entrenamiento previo)
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Define aquí los productos reales de tu carta
MENU_PRODUCTOS = ["pizza", "hamburguesa", "tacos", "ensalada", "zumo", "pasta", "pan"]

def extraer_multiples_pedidos(frase_usuario):
    """Descompone una frase natural en una lista de productos, cantidades y notas."""
    # Normalizamos un poco el texto
    texto = frase_usuario.lower().replace(" y ", ", ")
    
    # Segmentación: Buscamos patrones que empiecen por un número
    # Esto separa "2 pizzas y 1 zumo" en ["2 pizzas ", " 1 zumo"]
    segmentos = re.findall(r'(\d+[\s\w\sñáéíóú]+)(?:,|$)', texto)
    
    if not segmentos:
        segmentos = [texto] # Si no hay números, procesamos la frase completa

    lista_pedidos = []

    for seg in segmentos:
        # 1. Extraer cantidad
        cant_match = re.search(r'\d+', seg)
        cantidad = int(cant_match.group(0)) if cant_match else 1
        
        # 2. Clasificar el producto según el menú
        res = classifier(seg, candidate_labels=MENU_PRODUCTOS)
        # Solo aceptamos el producto si la IA está muy segura (confianza > 0.4)
        producto_ia = res['labels'][0] if res['scores'][0] > 0.4 else "Especial/Otro"
        
        # 3. Limpiar el resto del texto para obtener la nota
        # Quitamos la cantidad y el nombre del producto del texto original
        nota = seg.replace(str(cantidad), "").replace(producto_ia, "")
        
        # Limpieza de conectores y palabras comunes
        palabras_limpieza = ["quiero", "ponme", "un", "una", " de ", " con ", " por favor"]
        for p in palabras_limpieza:
            nota = nota.replace(p, " ")
        
        nota = nota.strip().capitalize()
        if not nota: nota = "Sin notas"

        lista_pedidos.append({
            "producto": producto_ia.capitalize(),
            "cantidad": cantidad,
            "nota": nota
        })
    
    return lista_pedidos