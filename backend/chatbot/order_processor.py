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
            "ocho": "8", "nueve": "9", "diez": "10",
            "media": "0.5", "docena": "12"
        }
        
        # Palabras que indican modificadores/notas, NO productos separados
        self.modificadores = [
            "con", "sin", "extra", "mucho", "poco", "más", "menos",
            "doble", "triple", "bien", "muy", "bastante", "nada de"
        ]
        
        # Sinónimos y variaciones comunes (expandidos desde dataset)
        self.sinonimos = {
            # Plurales
            "pizzas": "pizza", 
            "hamburguesas": "hamburguesa",
            "ensaladas": "ensalada", 
            "pastas": "pasta",
            "panes": "pan",
            "refrescos": "refresco",
            "zumos": "zumo",
            
            # Variaciones coca cola
            "coca": "coca cola",
            "cocas": "coca cola",
            "coca colas": "coca cola",
            "cocacola": "coca cola",
            "cocacolas": "coca cola",
            
            # Variaciones hot dog
            "hotdog": "hot dog",
            "hotdogs": "hot dog",
            "hot dogs": "hot dog",
            "perrito": "hot dog",
            "perritos": "hot dog",
            "perrito caliente": "hot dog",
            "perritos calientes": "hot dog",
            
            # Variaciones zumo/jugo
            "jugo": "zumo",
            "jugos": "zumo",
            
            # Variaciones taco
            "taco": "tacos",
            
            # Bebidas genéricas
            "bebida": "refresco",
            "bebidas": "refresco"
        }
        
        # Productos que NO deben matchear solos (son parte de otros)
        self.palabras_ignorar = ["cola", "colas", "dog", "hot", "caliente", "calientes"]
    
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
        
        # Segmentar inteligentemente (respetando modificadores)
        segmentos = self._segmentar_inteligente(texto)
        
        # Procesar cada segmento
        lista_pedidos = []
        productos_detectados = set()  # Para evitar duplicados
        
        for segmento in segmentos:
            pedido = self._procesar_segmento(segmento)
            if pedido:
                producto_key = pedido['producto'].lower()
                
                # Evitar duplicados del mismo producto
                if producto_key not in productos_detectados:
                    lista_pedidos.append(pedido)
                    productos_detectados.add(producto_key)
                else:
                    # Si ya existe, combinar cantidades o ignorar si es duplicado exacto
                    for p in lista_pedidos:
                        if p['producto'].lower() == producto_key:
                            # Si el existente no tiene nota y el nuevo sí, usar el nuevo
                            if not p['nota'] and pedido['nota']:
                                p['nota'] = pedido['nota']
                            break
        
        return lista_pedidos
    
    def _normalizar_texto(self, texto):
        """Normaliza el texto: minúsculas, números y sinónimos"""
        texto = texto.lower()
        
        # Reemplazar números en texto
        for palabra, numero in self.mapa_numeros.items():
            texto = re.sub(rf'\b{palabra}\b', numero, texto)
        
        # Aplicar sinónimos para normalizar variaciones
        for variacion, producto in self.sinonimos.items():
            texto = re.sub(rf'\b{re.escape(variacion)}\b', producto, texto)
        
        return texto
    
    def _segmentar_inteligente(self, texto):
        """
        Divide el texto en segmentos de pedidos individuales,
        manteniendo los modificadores junto con su producto
        """
        # Primero buscar productos en el texto
        productos_encontrados = []
        for producto in self.menu_productos:
            patron = rf'(\d+\s*)?{re.escape(producto)}(\s+(?:con|sin|extra|mucho|poco)[^,y]*)?'
            for match in re.finditer(patron, texto, re.IGNORECASE):
                productos_encontrados.append({
                    'producto': producto,
                    'texto': match.group(0),
                    'inicio': match.start(),
                    'fin': match.end()
                })
        
        # Si no encontramos productos directamente, dividir por separadores
        if not productos_encontrados:
            # Dividir por "y" o comas, pero respetar modificadores
            partes = re.split(r'\s+y\s+(?!(?:con|sin|extra|mucho|poco))|,\s*(?!(?:con|sin|extra|mucho|poco))', texto)
            return [p.strip() for p in partes if p.strip()]
        
        # Ordenar por posición
        productos_encontrados.sort(key=lambda x: x['inicio'])
        
        # Extraer segmentos con contexto
        segmentos = []
        ultimo_fin = 0
        
        for i, prod in enumerate(productos_encontrados):
            # Buscar cantidad antes del producto
            texto_antes = texto[ultimo_fin:prod['inicio']]
            cantidad_match = re.search(r'(\d+)\s*$', texto_antes)
            
            if cantidad_match:
                inicio = ultimo_fin + cantidad_match.start()
            else:
                inicio = prod['inicio']
            
            # Buscar modificadores después
            if i < len(productos_encontrados) - 1:
                texto_despues = texto[prod['fin']:productos_encontrados[i+1]['inicio']]
                # Buscar separador
                sep_match = re.search(r'\s+y\s+|\s*,\s*', texto_despues)
                if sep_match:
                    fin = prod['fin'] + sep_match.start()
                else:
                    fin = prod['fin']
            else:
                fin = len(texto)
            
            segmento = texto[inicio:fin].strip()
            if segmento:
                segmentos.append(segmento)
            
            ultimo_fin = fin
        
        return segmentos if segmentos else [texto]
    
    def _procesar_segmento(self, segmento):
        """
        Procesa un segmento individual de pedido
        
        Returns:
            dict: {producto, cantidad, nota} o None
        """
        # Extraer cantidad
        cantidad = self._extraer_cantidad(segmento)
        
        # Identificar producto
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
        Identifica el producto usando búsqueda directa primero,
        luego clasificación Zero-Shot como fallback
        
        Returns:
            str: Nombre del producto o None
        """
        segmento_lower = segmento.lower().strip()
        
        # Si el segmento es solo una palabra ignorada, no es producto
        if segmento_lower in self.palabras_ignorar:
            return None
        
        # Primero, búsqueda directa en el texto (prioridad a productos más largos)
        for producto in sorted(self.menu_productos, key=len, reverse=True):
            if producto in segmento_lower:
                return producto
        
        # Verificar si es una palabra que debe ignorarse
        palabras_segmento = segmento_lower.split()
        if len(palabras_segmento) == 1 and palabras_segmento[0] in self.palabras_ignorar:
            return None
        
        # Intentar con clasificador de IA solo si el segmento tiene contenido significativo
        if len(segmento_lower) > 2:
            resultado = self.classifier(segmento, candidate_labels=self.menu_productos)
            
            # Umbral alto para mayor precisión
            if resultado['scores'][0] > 0.6:
                return resultado['labels'][0]
        
        # Fallback: búsqueda difusa con umbral alto
        matches = difflib.get_close_matches(
            segmento_lower, 
            self.menu_productos, 
            n=1, 
            cutoff=0.7
        )
        
        return matches[0] if matches else None
    
    def _extraer_notas(self, segmento, producto, cantidad):
        """Extrae notas especiales del pedido"""
        # Encontrar la posición del producto en el segmento
        segmento_lower = segmento.lower()
        producto_pos = segmento_lower.find(producto.lower())
        
        if producto_pos >= 0:
            # Todo después del producto es potencialmente una nota
            nota = segmento[producto_pos + len(producto):].strip()
        else:
            nota = segmento
        
        # Remover cantidad si aparece
        nota = re.sub(r'^\d+\s*', '', nota)
        
        # Limpiar palabras comunes al inicio y fin
        palabras_a_remover = [
            "quiero", "ponme", "dame", "me das", "por favor", "porfavor",
            "quisiera", "necesito", "pedido", "pedir"
        ]
        
        for palabra in palabras_a_remover:
            nota = re.sub(rf'\b{palabra}\b', '', nota, flags=re.IGNORECASE)
        
        # Limpiar artículos y preposiciones sueltos
        nota = re.sub(r'^(de|el|la|los|las|un|una|unos|unas)\s+', '', nota.strip())
        nota = re.sub(r'\s+(de|el|la|los|las)$', '', nota.strip())
        
        nota = nota.strip()
        
        # Capitalizar si tiene contenido significativo
        if len(nota) > 1:
            return nota.capitalize()
        
        return "Sin notas"
