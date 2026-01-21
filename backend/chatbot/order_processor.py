"""
Procesador de pedidos usando IA
Extrae productos, cantidades y notas desde texto natural
"""

import re
import difflib
from transformers import pipeline


class OrderProcessor:
    """Procesa y extrae pedidos desde lenguaje natural"""
    
    def __init__(self, menu_productos):
        """
        Inicializa el procesador con el menú disponible
        
        Args:
            menu_productos (list): Lista de productos disponibles
        """
        self.menu_productos = menu_productos
        self.classifier = pipeline(
            "zero-shot-classification", 
            model="facebook/bart-large-mnli"
        )
        
        # Mapeo de números en texto a dígitos
        self.mapa_numeros = {
            "una": "1", "un": "1", "uno": "1",
            "dos": "2", "tres": "3", "cuatro": "4",
            "cinco": "5", "seis": "6", "siete": "7",
            "ocho": "8", "nueve": "9", "diez": "10"
        }
    
    def actualizar_menu(self, nuevos_productos):
        """Actualiza la lista de productos disponibles"""
        self.menu_productos = nuevos_productos
    
    def extraer_pedidos(self, frase_usuario):
        """
        Extrae múltiples pedidos de una frase
        
        Args:
            frase_usuario (str): Texto del usuario
            
        Returns:
            list: Lista de diccionarios con {producto, cantidad, nota}
        """
        if not self.menu_productos:
            return []
        
        # Normalizar texto
        texto = self._normalizar_texto(frase_usuario)
        
        # Dividir en segmentos (por comas o 'y')
        segmentos = self._segmentar_texto(texto)
        
        # Procesar cada segmento
        lista_pedidos = []
        for segmento in segmentos:
            pedido = self._procesar_segmento(segmento)
            if pedido:
                lista_pedidos.append(pedido)
        
        return lista_pedidos
    
    def _normalizar_texto(self, texto):
        """Normaliza el texto: minúsculas y conversión de números"""
        texto = texto.lower().replace(" y ", ", ")
        
        # Reemplazar "un/una" por "1"
        texto = re.sub(r'\b(un|una)\b', '1', texto)
        
        # Reemplazar números en texto
        for palabra, numero in self.mapa_numeros.items():
            texto = re.sub(rf'\b{palabra}\b', numero, texto)
        
        return texto
    
    def _segmentar_texto(self, texto):
        """Divide el texto en segmentos de pedidos individuales"""
        segmentos = [s.strip() for s in texto.split(",") if s.strip()]
        return [s for s in segmentos if re.search(r'[a-zA-Z]', s)]
    
    def _procesar_segmento(self, segmento):
        """
        Procesa un segmento individual de pedido
        
        Returns:
            dict: {producto, cantidad, nota} o None
        """
        # Extraer cantidad
        cantidad = self._extraer_cantidad(segmento)
        
        # Identificar producto usando IA
        producto = self._identificar_producto(segmento)
        if not producto:
            return None
        
        # Extraer notas adicionales
        nota = self._extraer_notas(segmento, producto, cantidad)
        
        return {
            "producto": producto.capitalize(),
            "cantidad": cantidad,
            "nota": nota
        }
    
    def _extraer_cantidad(self, segmento):
        """Extrae la cantidad del segmento"""
        cant_match = re.search(r'\d+', segmento)
        return int(cant_match.group(0)) if cant_match else 1
    
    def _identificar_producto(self, segmento):
        """
        Identifica el producto usando clasificación Zero-Shot
        
        Returns:
            str: Nombre del producto o None
        """
        # Intentar con clasificador de IA
        resultado = self.classifier(segmento, candidate_labels=self.menu_productos)
        
        if resultado['scores'][0] > 0.4:
            return resultado['labels'][0]
        
        # Fallback: búsqueda difusa
        matches = difflib.get_close_matches(
            segmento, 
            self.menu_productos, 
            n=1, 
            cutoff=0.6
        )
        
        return matches[0] if matches else None
    
    def _extraer_notas(self, segmento, producto, cantidad):
        """Extrae notas especiales del pedido"""
        # Remover cantidad y producto del segmento
        nota = segmento.replace(str(cantidad), "").replace(producto.lower(), "").strip()
        
        # Limpiar palabras comunes
        nota = re.sub(r'\bs\b', '', nota)  # Remover 's' suelta
        
        palabras_a_remover = [
            "quiero", "ponme", " de ", " con ", " por favor",
            "dame", "porfavor", "me das"
        ]
        
        for palabra in palabras_a_remover:
            nota = nota.replace(palabra, " ")
        
        nota = nota.strip()
        
        # Capitalizar si tiene contenido significativo
        if len(nota) > 1:
            return nota.capitalize()
        
        return "Sin notas"
