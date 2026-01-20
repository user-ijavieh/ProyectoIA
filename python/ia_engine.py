import re
from transformers import pipeline

# Modelo de clasificación Zero-Shot
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# --- BLOQUE 1: Configuración y Helpers (Preservado de HEAD) ---

# Define aquí los productos reales de tu carta
MENU_PRODUCTOS = [
    "pizza", "hamburguesa", "tacos", "ensalada", "zumo", 
    "pasta", "pan", "perrito caliente", "hot dog", "refresco", "coca cola"
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

    lista_pedidos = []
    
    for seg in segmentos:
        # Extraer cantidad numérica
        cant_match = re.search(r'\d+', seg)
        cantidad = int(cant_match.group(0)) if cant_match else 1
        
        # Clasificar producto con IA
        res = classifier(seg, candidate_labels=MENU_PRODUCTOS)
        
        # Solo aceptamos el producto si la IA está razonablemente segura
        if res['scores'][0] > 0.4:
            producto_ia = res['labels'][0]
        else:
             # Si la confianza es baja, ignoramos este segmento (evita ruido)
             continue 
        
        # --- Limpieza de la Nota (Lógica avanzada de HEAD) ---
        
        # 1. Quitamos la cantidad numérica del texto original
        nota = seg.replace(str(cantidad), "")
        
        # 2. Quitamos el nombre del producto (y su posible plural simple 's' o 'es')
        # Ejemplo: Si producto es 'pizza', quitamos 'pizza' y 'pizzas' del texto de la nota
        nota = re.sub(rf'\b{producto_ia}(es|s)?\b', '', nota, flags=re.IGNORECASE)
        
        # 3. Limpieza de conectores y palabras comunes ("relleno")
        palabras_limpieza = ["quiero", "ponme", " dame ", " de ", " con ", " por favor", " un ", " una "]
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
            "nota": nota
        })
        
    return lista_pedidos