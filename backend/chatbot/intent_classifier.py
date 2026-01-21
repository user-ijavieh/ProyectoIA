"""
Clasificador de intenciones del usuario
Maneja la detección de saludos, despedidas y consultas
"""

import re


class IntentClassifier:
    """Clasifica las intenciones del usuario en el chatbot"""
    
    # Palabras clave para diferentes intenciones
    SALUDOS = ["hola", "buenas", "buenos dias", "hey", "qué tal", "buenas tardes", "buenas noches"]
    DESPEDIDAS = ["adios", "chao", "hasta luego", "gracias", "bye", "nos vemos"]
    CONSULTAS = ["estado", "como va", "ticket", "pedido", "donde esta"]
    
    @staticmethod
    def detectar_saludo_o_despedida(texto):
        """
        Detecta si el mensaje es un saludo o despedida
        
        Args:
            texto (str): Mensaje del usuario
            
        Returns:
            str: 'saludo', 'despedida' o None
        """
        texto_lower = texto.lower().strip()
        
        # Verificar saludos
        for saludo in IntentClassifier.SALUDOS:
            if texto_lower == saludo or texto_lower.startswith(saludo + " "):
                return "saludo"
        
        # Verificar despedidas
        for despedida in IntentClassifier.DESPEDIDAS:
            if texto_lower == despedida or texto_lower.startswith(despedida + " "):
                return "despedida"
        
        return None
    
    @staticmethod
    def detectar_consulta_pedido(texto):
        """
        Identifica si el usuario pregunta por el estado de un ticket
        
        Args:
            texto (str): Mensaje del usuario
            
        Returns:
            str: ID del ticket (8 caracteres hex) o 'SOLICITAR_ID' o None
        """
        texto_lower = texto.lower()
        
        # Buscar patrón de ID de ticket (8 caracteres hexadecimales)
        match_id = re.search(r'\b([a-fA-F0-9]{8})\b', texto)
        if match_id:
            return match_id.group(1).upper()
        
        # Verificar si menciona palabras relacionadas con consulta
        for palabra in IntentClassifier.CONSULTAS:
            if palabra in texto_lower:
                return "SOLICITAR_ID"
        
        return None
    
    @staticmethod
    def es_confirmacion(texto):
        """
        Detecta si el mensaje es una confirmación
        
        Args:
            texto (str): Mensaje del usuario
            
        Returns:
            bool: True si es confirmación
        """
        texto_lower = texto.lower().strip()
        confirmaciones = ["si", "sí", "vale", "ok", "okay", "confirmar", "correcto", "exacto"]
        
        palabras = texto_lower.split()
        return any(palabra in confirmaciones for palabra in palabras)
    
    @staticmethod
    def es_negacion(texto):
        """
        Detecta si el mensaje es una negación
        
        Args:
            texto (str): Mensaje del usuario
            
        Returns:
            bool: True si es negación
        """
        texto_lower = texto.lower().strip()
        negaciones = ["no", "nop", "nope", "negativo", "cancelar"]
        
        palabras = texto_lower.split()
        return any(palabra in negaciones for palabra in palabras)
