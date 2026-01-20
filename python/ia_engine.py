import re
from transformers import pipeline

# Cargamos el modelo de clasificación Zero-Shot (especializado en entender etiquetas sin entrenamiento previo)
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Define aquí los productos reales de tu carta
MENU_PRODUCTOS = ["pizza", "hamburguesa", "tacos", "ensalada", "zumo", "pasta", "pan", "perrito caliente", "hot dog", "refresco", "coca cola", "sprite", "fanta", "bebida"]

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

def extraer_multiples_pedidos(frase_usuario):
    """Descompone una frase natural en una lista de productos, cantidades y notas."""
    # Normalizamos un poco el texto
    texto = frase_usuario.lower().replace(" y ", ", ")
    
    # TRUCO: Convertimos palabras de unidad textualles a números para que el regex los pille
    # "dame una pizza" -> "dame 1 pizza"
    texto = re.sub(r'\b(un|una)\b', '1', texto)
    
    # Segmentación: Buscamos patrones que empiecen por un número
    # Esto separa "2 pizzas y 1 zumo" en ["2 pizzas ", " 1 zumo"]
    segmentos = re.findall(r'(\d+[\s\w\sñáéíóú]+)(?:,|$)', texto)
    
    if not segmentos:
        # Si no hay números, pero tampoco es saludo, intentamos ver si menciona productos directamente
        # Ejemplo: "quiero pizza" (sin cantidad)
        segmentos = [texto] 

    lista_pedidos = []

    for seg in segmentos:
        # 1. Extraer cantidad
        cant_match = re.search(r'\d+', seg)
        cantidad = int(cant_match.group(0)) if cant_match else 1
        
        # 2. Clasificar el producto según el menú
        res = classifier(seg, candidate_labels=MENU_PRODUCTOS)
        # Solo aceptamos el producto si la IA está muy segura (confianza > 0.4)
        if res['scores'][0] > 0.4:
            producto_ia = res['labels'][0]
        else:
             # Si no estamos seguros, podría ser texto basura o conversación
             continue 
        
        # 3. Limpiar el resto del texto para obtener la nota
        # Quitamos la cantidad
        nota = seg.replace(str(cantidad), "")
        
        # Quitamos el nombre del producto (y su posible plural simple 's' o 'es')
        # Ejemplo: Si producto es 'pizza', quitamos 'pizza' y 'pizzas'
        nota = re.sub(rf'\b{producto_ia}(es|s)?\b', '', nota, flags=re.IGNORECASE)
        
        # Limpieza de conectores y palabras comunes
        palabras_limpieza = ["quiero", "ponme", " dame ", " de ", " con ", " por favor"]
        for p in palabras_limpieza:
            nota = nota.replace(p, " ")
        
        nota = nota.strip().capitalize()
        # Limpieza extra de puntuación inicial
        nota = nota.lstrip(".,- ")
        
        if not nota: nota = "Sin notas"

        lista_pedidos.append({
            "producto": producto_ia.capitalize(),
            "cantidad": cantidad,
            "nota": nota
        })
    
    return lista_pedidos