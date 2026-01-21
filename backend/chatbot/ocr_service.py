"""
Servicio de OCR para procesamiento de imágenes
Extrae texto de imágenes de pedidos escritos a mano
"""

from PIL import Image


class OCRService:
    """Servicio de reconocimiento óptico de caracteres"""
    
    def __init__(self):
        """Inicializa los modelos de OCR"""
        self.reader_detector = None
        self.processor = None
        self.model = None
        self._inicializar_modelos()
    
    def _inicializar_modelos(self):
        """Carga los modelos de OCR (EasyOCR + TrOCR)"""
        try:
            import cv2
            import easyocr
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel
            
            # Guardar cv2 como atributo de la clase
            self.cv2 = cv2
            
            # EasyOCR para detección de texto
            self.reader_detector = easyocr.Reader(['es'], gpu=False)
            
            # TrOCR para reconocimiento de texto manuscrito
            self.processor = TrOCRProcessor.from_pretrained(
                'microsoft/trocr-small-handwritten'
            )
            self.model = VisionEncoderDecoderModel.from_pretrained(
                'microsoft/trocr-small-handwritten',
                use_safetensors=True
            )
            
            print("✅ Modelos OCR cargados correctamente")
            
        except Exception as e:
            print(f"⚠️ OCR no disponible: {e}")
            print("Las imágenes no podrán ser procesadas")
    
    def esta_disponible(self):
        """Verifica si el servicio OCR está disponible"""
        return self.reader_detector is not None
    
    def procesar_imagen(self, ruta_imagen):
        """
        Procesa una imagen y extrae el texto
        
        Args:
            ruta_imagen (str): Ruta al archivo de imagen
            
        Returns:
            str: Texto extraído de la imagen
        """
        if not self.esta_disponible():
            return ""
        
        try:
            # Detectar regiones de texto con EasyOCR
            regiones = self._detectar_regiones_texto(ruta_imagen)
            if not regiones:
                return ""
            
            # Reconocer texto en cada región con TrOCR
            textos_extraidos = self._reconocer_texto_regiones(
                ruta_imagen, 
                regiones
            )
            
            # Combinar textos
            return ", ".join(textos_extraidos)
            
        except Exception as e:
            print(f"Error procesando imagen: {e}")
            return ""
    
    def _detectar_regiones_texto(self, ruta_imagen):
        """
        Detecta regiones que contienen texto en la imagen
        
        Returns:
            list: Lista de regiones detectadas
        """
        img_cv = self.cv2.imread(ruta_imagen)
        if img_cv is None:
            return []
        
        # Detectar regiones de texto
        cajas = self.reader_detector.detect(img_cv)
        
        if not cajas or not cajas[0]:
            return []
        
        return cajas[0]
    
    def _reconocer_texto_regiones(self, ruta_imagen, regiones):
        """
        Reconoce el texto en cada región detectada
        
        Args:
            ruta_imagen (str): Ruta a la imagen
            regiones (list): Lista de regiones de texto
            
        Returns:
            list: Lista de textos reconocidos
        """
        img_pil = Image.open(ruta_imagen).convert("RGB")
        textos = []
        
        # Ordenar regiones por posición vertical
        regiones_ordenadas = sorted(regiones, key=lambda x: x[2])
        
        for region in regiones_ordenadas:
            # Extraer coordenadas de la región
            coords = self._extraer_coordenadas(region)
            
            # Recortar región de la imagen
            crop = img_pil.crop((
                coords['x_min'] - 5,
                coords['y_min'] - 5,
                coords['x_max'] + 5,
                coords['y_max'] + 5
            ))
            
            # Reconocer texto con TrOCR
            texto = self._reconocer_texto_crop(crop)
            
            if texto:
                textos.append(texto)
        
        return textos
    
    def _extraer_coordenadas(self, region):
        """Extrae coordenadas x,y min/max de una región"""
        if isinstance(region[0], list):
            # Formato: [[x1,y1], [x2,y2], ...]
            puntos_x = [p[0] for p in region]
            puntos_y = [p[1] for p in region]
            return {
                'x_min': min(puntos_x),
                'x_max': max(puntos_x),
                'y_min': min(puntos_y),
                'y_max': max(puntos_y)
            }
        else:
            # Formato: (x_min, x_max, y_min, y_max)
            return {
                'x_min': region[0],
                'x_max': region[1],
                'y_min': region[2],
                'y_max': region[3]
            }
    
    def _reconocer_texto_crop(self, imagen_crop):
        """Reconoce texto en una imagen recortada usando TrOCR"""
        try:
            # Preprocesar imagen para el modelo
            pixel_values = self.processor(
                images=imagen_crop,
                return_tensors="pt"
            ).pixel_values
            
            # Generar texto
            generated_ids = self.model.generate(pixel_values)
            
            # Decodificar resultado
            texto = self.processor.batch_decode(
                generated_ids,
                skip_special_tokens=True
            )[0].strip()
            
            return texto
            
        except Exception as e:
            print(f"Error reconociendo texto: {e}")
            return ""


# Instancia global del servicio
ocr_service = OCRService()


def procesar_imagen_pedido(ruta_imagen):
    """
    Función de conveniencia para procesar imágenes
    
    Args:
        ruta_imagen (str): Ruta a la imagen
        
    Returns:
        str: Texto extraído
    """
    return ocr_service.procesar_imagen(ruta_imagen)
