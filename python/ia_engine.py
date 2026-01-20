import re
from transformers import pipeline
import difflib # Importante: Necesario para la corrección de errores tipográficos (Fuzzy)

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
        cajas = reader_detector.detect(img_cv)
        
        if not cajas or not cajas[0]:
             print("DEBUG: No se detectaron cajas de texto.")
             return ""
             
        # Obtenemos la lista de bounding lines
        bounding_boxes = cajas[0] 
        bounding_boxes.sort(key=lambda x: x[2]) # Ordenar por Y_min
        
        texto_total = []
        
        # Convertir a PIL para TrOCR
        img_pil_full = Image.open(imagen_path).convert("RGB")
        
        print(f"DEBUG: Detectadas {len(bounding_boxes)} líneas.")
        
        for box in bounding_boxes:
            # Normalizar coordenadas de la caja
            # EasyOCR detect puede devolver [x_min, x_max, y_min, y_max] O [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            if isinstance(box, list) and len(box) == 4 and isinstance(box[0], list):
                # Es un polígono [[x,y]...], extraemos min/max
                xs = [p[0] for p in box]
                ys = [p[1] for p in box]
                x_min, x_max = min(xs), max(xs)
                y_min, y_max = min(ys), max(ys)
            else:
                # Asumimos formato simple
                x_min, x_max, y_min, y_max = box
            
            # Padding
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
                if texto_total:
                    linea = ", " + linea
            else:
                linea = " " + linea
                
            texto_total.append(linea)
            
        texto_final = "".join(texto_total).strip()
        texto_final = texto_final.lstrip(", ")
        
        print(f"DEBUG TrOCR Final: {texto_final}")
        return texto_final

    except Exception as e:
        print(f"Error en TrOCR pipeline: {e}")
        import traceback
        traceback.print_exc()
        return ""


# --- BLOQUE 1: Configuración y Helpers ---

MENU_PRODUCTOS = [
    "pizza", "hamburguesa", "tacos", "ensalada", "zumo", 
    "pasta", "pan", "panes", "perrito caliente", "hot dog", "refresco", "coca cola"
]

def es_saludo_o_despedida(texto):
    """Detecta si el usuario está saludando o despidiéndose."""
    texto = texto.lower().strip()
    
    saludos = ["hola", "buenas", "buenos dias", "buenos días", "buenas tardes", "buenas noches", "hey", "qué tal", "que tal"]
    despedidas = ["adios", "adiós", "chao", "hasta luego", "nos vemos", "bye", "hasta pronto", "gracias"]
    
    for s in saludos:
        if texto == s or texto.startswith(s + " "):
            return "saludo"
            
    for d in despedidas:
        if texto == d or texto.startswith(d + " "):
            return "despedida"
            
    return None

def detectar_intencion_consulta(texto):
    """
    Detecta si el usuario quiere consultar el estado de un pedido.
    Retorna el ID del ticket si lo encuentra, o True si pregunta pero no da ID.
    """
    texto = texto.lower()
    palabras_clave = ["estado", "como va", "qué tal", "que tal", "estatus", "situacion", "situación", "pedido", "ticket", "comanda"]
    
    # Regex para buscar algo que parezca un ID (ej: 7D06BF25)
    # Al menos 6 caracteres alfanuméricos seguidos
    match_id = re.search(r'\b([a-fA-F0-9]{8})\b', texto)
    
    # ESTRATEGIA:
    # 1. Si encontramos un ID válido, asumimos que es una consulta (¡Directo!)
    if match_id:
        return match_id.group(1).upper()

    # 2. Si no hay ID, miramos si hay palabras clave de pregunta
    if any(p in texto for p in palabras_clave):
        # Regex para buscar algo que parezca un ID (ej: 7D06BF25)
        # Al menos 6 caracteres alfanuméricos seguidos/aislados
        match_id = re.search(r'\b([a-fA-F0-9]{8})\b', texto)
        if match_id:
            return match_id.group(1).upper()
            
        return "SOLICITAR_ID" # Detectó intención pero falta el ID
        
    return None

# --- BLOQUE 2: Lógica Principal (FUSIÓN COMPLETA) ---

def extraer_multiples_pedidos(frase_usuario):
    """Descompone una frase natural en una lista de productos, cantidades y notas."""
    # 1. Normalización de números escritos como palabras
    mapa_numeros = {
        "una": "1", "un": "1", "uno": "1",
        "dos": "2", "tres": "3", "cuatro": "4", "cinco": "5"
    }
    
    texto = frase_usuario.lower().replace(" y ", ", ")
    
    # Convertimos palabras de unidad textuales a números
    texto = re.sub(r'\b(un|una)\b', '1', texto)
    
    # Segmentación: Buscamos patrones que empiecen por un número
    segmentos = re.findall(r'(\d+[\s\w\sñáéíóú]+)(?:,|$)', texto)
    
    if not segmentos:
        segmentos = [texto] 

    # Reemplazamos palabras por dígitos
    for palabra, numero in mapa_numeros.items():
        texto = re.sub(rf'\b{palabra}\b', numero, texto)
    
    # 2. Segmentación final por comas
    segmentos = [s.strip() for s in texto.split(",") if s.strip()]
    
    lista_pedidos = []
    
    for seg in segmentos:
        # Extraer cantidad
        cant_match = re.search(r'\d+', seg)
        cantidad = int(cant_match.group(0)) if cant_match else 1
        
        # --- LÓGICA FUSIONADA ---
        
        # A) Validar contenido real (De HEAD)
        if not seg.strip() or not re.search(r'[a-zA-Z]', seg):
            continue

        # B) Clasificación con IA (Común)
        res = classifier(seg, candidate_labels=MENU_PRODUCTOS)
        producto_ia = None

        # C) Validación de Confianza + Fuzzy Matching (De HEAD - Más robusto)
        if res['scores'][0] > 0.4:
            producto_ia = res['labels'][0]
        else:
             # Recuperación ante typos graves
             palabras = seg.split()
             encontrado_fuzzy = None
             
             for palabra in palabras:
                 p_limpia = re.sub(r'[^a-zA-Zñáéíóú]', '', palabra)
                 matches = difflib.get_close_matches(p_limpia, MENU_PRODUCTOS, n=1, cutoff=0.6)
                 if matches:
                     encontrado_fuzzy = matches[0]
                     break
             
             if encontrado_fuzzy:
                 producto_ia = encontrado_fuzzy
             else:
                 # Si falla IA y falla Fuzzy, ignoramos este segmento
                 continue 
        
        # D) Limpieza profunda de la nota (De Incoming - Mejor formato)
        # Usamos el producto detectado para limpiar la frase original
        nota = seg.replace(str(cantidad), "").replace(producto_ia.lower(), "").strip()
        
        # Quita 's' sueltas (plurales residuales)
        nota = re.sub(r'\bs\b', '', nota) 
        
        palabras_limpieza = ["quiero", "ponme", " de ", " con ", " por favor"]
        for p in palabras_limpieza:
            nota = nota.replace(p, " ")
        
        # E) Formateo final
        nota = nota.strip().capitalize()
        nota = nota.lstrip(".,- ") 
        
        if not nota: 
            nota = "Sin notas"

        lista_pedidos.append({
            "producto": producto_ia.capitalize(),
            "cantidad": cantidad,
            "nota": nota
        })
        
    return lista_pedidos