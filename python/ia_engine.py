import re
from transformers import pipeline
import difflib
from database import obtener_menu_db # Importamos la nueva función

# Modelo de clasificación Zero-Shot
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Inicializar OCR
try:
    import easyocr
    import cv2
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    from PIL import Image
    reader_detector = easyocr.Reader(['es'], gpu=False) 
    processor = TrOCRProcessor.from_pretrained('microsoft/trocr-small-handwritten')
    model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-small-handwritten', use_safetensors=True)
except Exception as e:
    reader_detector = None

# CARGA DINÁMICA: Obtenemos el menú desde la tabla 'menu' de la DB
MENU_PRODUCTOS = obtener_menu_db()

def es_saludo_o_despedida(texto):
    """Detecta saludos o despedidas."""
    texto = texto.lower().strip()
    saludos = ["hola", "buenas", "buenos dias", "hey", "qué tal"]
    despedidas = ["adios", "chao", "hasta luego", "gracias"]
    for s in saludos:
        if texto == s or texto.startswith(s + " "): return "saludo"
    for d in despedidas:
        if texto == d or texto.startswith(d + " "): return "despedida"
    return None

def detectar_intencion_consulta(texto):
    """Identifica si el usuario pregunta por un ticket."""
    texto = texto.lower()
    match_id = re.search(r'\b([a-fA-F0-9]{8})\b', texto)
    if match_id: return match_id.group(1).upper()
    if any(p in texto for p in ["estado", "como va", "ticket", "pedido"]): return "SOLICITAR_ID"
    return None

def extraer_multiples_pedidos(frase_usuario):
    """Extrae productos, cantidades y notas usando el menú de la DB."""
    global MENU_PRODUCTOS
    # Aseguramos que el menú esté cargado
    if not MENU_PRODUCTOS:
        MENU_PRODUCTOS = obtener_menu_db()

    mapa_numeros = {"una": "1", "un": "1", "uno": "1", "dos": "2", "tres": "3", "cuatro": "4", "cinco": "5"}
    texto = frase_usuario.lower().replace(" y ", ", ")
    texto = re.sub(r'\b(un|una)\b', '1', texto)
    for palabra, numero in mapa_numeros.items():
        texto = re.sub(rf'\b{palabra}\b', numero, texto)
    
    segmentos = [s.strip() for s in texto.split(",") if s.strip()]
    lista_pedidos = []
    
    for seg in segmentos:
        if not re.search(r'[a-zA-Z]', seg): continue
        cant_match = re.search(r'\d+', seg)
        cantidad = int(cant_match.group(0)) if cant_match else 1
        
        # Clasificación contra el menú dinámico
        res = classifier(seg, candidate_labels=MENU_PRODUCTOS)
        producto_ia = None

        if res['scores'][0] > 0.4:
            producto_ia = res['labels'][0]
        else:
             matches = difflib.get_close_matches(seg, MENU_PRODUCTOS, n=1, cutoff=0.6)
             if matches: producto_ia = matches[0]
             else: continue 
        
        nota = seg.replace(str(cantidad), "").replace(producto_ia.lower(), "").strip()
        nota = re.sub(r'\bs\b', '', nota) 
        for p in ["quiero", "ponme", " de ", " con ", " por favor"]: nota = nota.replace(p, " ")
        
        lista_pedidos.append({
            "producto": producto_ia.capitalize(),
            "cantidad": cantidad,
            "nota": nota.strip().capitalize() if len(nota.strip()) > 1 else "Sin notas"
        })
    return lista_pedidos

def procesar_imagen_pedido(imagen_path):
    """Procesamiento OCR."""
    if reader_detector is None: return ""
    try:
        img_cv = cv2.imread(imagen_path)
        cajas = reader_detector.detect(img_cv)
        if not cajas or not cajas[0]: return ""
        img_pil = Image.open(imagen_path).convert("RGB")
        texto_total = []
        for box in sorted(cajas[0], key=lambda x: x[2]):
            x_min, x_max, y_min, y_max = (min([p[0] for p in box]), max([p[0] for p in box]), min([p[1] for p in box]), max([p[1] for p in box])) if isinstance(box[0], list) else box
            crop = img_pil.crop((x_min-5, y_min-5, x_max+5, y_max+5))
            pixel_values = processor(images=crop, return_tensors="pt").pixel_values
            generated_ids = model.generate(pixel_values)
            linea = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
            texto_total.append(linea)
        return ", ".join(texto_total)
    except: return ""