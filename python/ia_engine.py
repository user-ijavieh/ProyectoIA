import re
from transformers import pipeline

# Modelo de clasificación Zero-Shot
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Inicializar EasyOCR (solo para detección de cajas) y TrOCR (para reconocimiento)
try:
    import easyocr
    import cv2
    import numpy as np
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    from PIL import Image
    import torch

    # EASYOCR: Solo para detectar dónde hay texto (Bounding Boxes)
    reader_detector = easyocr.Reader(['es'], gpu=False) 
    
    # TROCR: Modelo especializado en escritura a mano
    print("Cargando modelo TrOCR (esto puede tardar la primera vez)...")
    processor = TrOCRProcessor.from_pretrained('microsoft/trocr-small-handwritten')
    model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-small-handwritten', use_safetensors=True)
    
except Exception as e:
    reader_detector = None
    print(f"⚠️ Error al cargar librerías o modelos OCR: {e}")

# ... (código intermedio sin cambios)

def procesar_imagen_pedido(imagen_path):
    """
    Pipeline Híbrido:
    1. EasyOCR detecta las cajas de texto.
    2. Recortamos cada caja.
    3. TrOCR lee el texto dentro de la caja (SOTA en handwriting).
    """
    if reader_detector is None:
        return ""
    
    try:
        # Cargar imagen
        img_cv = cv2.imread(imagen_path)
        if img_cv is None:
            return ""
            
        # Detección de texto con EasyOCR
        # devolvemos coordenadas de las cajas
        cajas = reader_detector.detect(img_cv)
        
        # 'cajas' tiene formato [[box1, box2...]] o [boxes, conf] dependiendo de la versión
        # Normalmente detect devuelve (horizontal_list, free_list). Usamos horizontal_list.
        if not cajas or not cajas[0]:
             print("DEBUG: No se detectaron cajas de texto.")
             return ""
             
        # Obtenemos la lista de bounding lines
        bounding_boxes = cajas[0] 
        
        # Ordenamos las cajas de arriba a abajo (por la coordenada Y min)
        # box = [x_min, x_max, y_min, y_max] en easyocr detect? 
        # EasyOCR detect returns [x_min, x_max, y_min, y_max] for raw detection?
        # Actually easyocr.Reader.detect returns tuples: (horizontal_list, free_list)
        # horizontal_list elements are [x_min, x_max, y_min, y_max]
        
        bounding_boxes.sort(key=lambda x: x[2]) # Ordenar por Y_min
        
        texto_total = []
        
        # Convertir a PIL para TrOCR
        img_pil_full = Image.open(imagen_path).convert("RGB")
        
        print(f"DEBUG: Detectadas {len(bounding_boxes)} líneas.")
        
        for box in bounding_boxes:
            x_min, x_max, y_min, y_max = box
            
            # Dar un pequeño margen (padding) al recorte para no cortar letras altas
            padding = 5
            x_min = max(0, x_min - padding)
            y_min = max(0, y_min - padding)
            x_max = min(img_cv.shape[1], x_max + padding)
            y_max = min(img_cv.shape[0], y_max + padding)
            
            # Recortar imagen (Crop)
            crop = img_pil_full.crop((x_min, y_min, x_max, y_max))
            
            # Inferencia TrOCR
            pixel_values = processor(images=crop, return_tensors="pt").pixel_values
            generated_ids = model.generate(pixel_values)
            texto_generado = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            print(f"DEBUG TrOCR line: {texto_generado}")
            
            # Limpieza básica
            linea = texto_generado.strip()
            
            # --- CORRECCIÓN DE "1" MAL LEÍDOS ---
            if re.match(r'^[lI|/]\s+[a-zA-Z]', linea) or re.match(r'^[lI|/]$', linea):
                linea = '1' + linea[1:]

            # Heurística de unión (Smart Join)
            match_nuevo = re.match(r'^(\d+|un\b|una\b|[-*])', linea, re.IGNORECASE)
            
            if match_nuevo:
                # Nuevo ítem -> Coma previa si no es el primero
                if texto_total:
                    linea = ", " + linea
            else:
                # Continuación -> Espacio previo
                linea = " " + linea
                
            texto_total.append(linea)
            
        texto_final = "".join(texto_total).strip()
        # Limpiar comas duplicadas o al inicio
        texto_final = texto_final.lstrip(", ")
        
        print(f"DEBUG TrOCR Final: {texto_final}")
        return texto_final

    except Exception as e:
        print(f"Error en TrOCR pipeline: {e}")
        import traceback
        traceback.print_exc()
        return ""



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
        
        # Validar que el segmento tenga contenido real antes de llamar a la IA
        if not seg.strip() or not re.search(r'[a-zA-Z]', seg):
            continue

        # Clasificar producto con IA
        res = classifier(seg, candidate_labels=MENU_PRODUCTOS)
        
        # Solo aceptamos el producto si la IA está razonablemente segura
        if res['scores'][0] > 0.4:
            producto_ia = res['labels'][0]
        else:
             # INTENTO DE RECUPERACIÓN: Fuzzy matching
             # Si la confianza de la IA es baja (probablemente por un typo grave tipo "Pjxca"),
             # intentamos buscar la palabra más parecida en el menú.
             import difflib
             # Tokenizamos el segmento para buscar palabra por palabra
             palabras = seg.split()
             encontrado_fuzzy = None
             
             for palabra in palabras:
                 # Limpiar palabra de basura
                 p_limpia = re.sub(r'[^a-zA-Zñáéíóú]', '', palabra)
                 matches = difflib.get_close_matches(p_limpia, MENU_PRODUCTOS, n=1, cutoff=0.6)
                 if matches:
                     encontrado_fuzzy = matches[0]
                     break
             
             if encontrado_fuzzy:
                 producto_ia = encontrado_fuzzy
             else:
                 # Si ni la IA ni el fuzzy lo encuentran, lo saltamos
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


