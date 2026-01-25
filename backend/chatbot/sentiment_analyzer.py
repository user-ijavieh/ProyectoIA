"""
Analizador de sentimiento para el chatbot
Detecta el estado emocional del usuario para responder de forma empática
"""

from transformers import pipeline
import re


class SentimentAnalyzer:
    """Analiza el sentimiento de los mensajes del usuario"""
    
    # Palabras clave que indican frustración/negatividad
    PALABRAS_NEGATIVAS = [
        "esperando", "espero", "tarda", "demora", "lento", "mucho tiempo",
        "mal", "horrible", "terrible", "asco", "frío", "queja", "problema",
        "error", "equivocado", "incorrecto", "falta", "nunca", "jamás",
        "molesto", "enfadado", "frustrado", "harto", "cansado"
    ]
    
    # Palabras que indican satisfacción/positividad
    PALABRAS_POSITIVAS = [
        "genial", "excelente", "perfecto", "delicioso", "rico", "buenísimo",
        "gracias", "encanta", "increíble", "fantástico", "maravilloso",
        "rápido", "bien", "contento", "feliz", "satisfecho", "recomiendo"
    ]
    
    def __init__(self):
        """Inicializa el modelo de análisis de sentimiento"""
        self.analyzer = pipeline(
            "sentiment-analysis",
            model="nlptown/bert-base-multilingual-uncased-sentiment"
        )
    
    def analizar(self, texto):
        """
        Analiza el sentimiento de un texto usando palabras clave
        y el modelo de IA como respaldo
        
        Args:
            texto (str): Mensaje del usuario
            
        Returns:
            dict: {sentimiento, estrellas, confianza}
        """
        if not texto or len(texto.strip()) < 3:
            return {"sentimiento": "neutral", "estrellas": 3, "confianza": 0.0}
        
        texto_lower = texto.lower()
        
        # Primero: detectar por palabras clave (más preciso para español)
        tiene_negativas = any(palabra in texto_lower for palabra in self.PALABRAS_NEGATIVAS)
        tiene_positivas = any(palabra in texto_lower for palabra in self.PALABRAS_POSITIVAS)
        
        # Si hay palabras negativas claras, es negativo
        if tiene_negativas and not tiene_positivas:
            return {"sentimiento": "negativo", "estrellas": 2, "confianza": 0.9}
        
        # Si hay palabras positivas claras, es positivo
        if tiene_positivas and not tiene_negativas:
            return {"sentimiento": "positivo", "estrellas": 5, "confianza": 0.9}
        
        # Si hay ambas o ninguna, usar el modelo de IA
        try:
            resultado = self.analyzer(texto[:512])[0]
            estrellas = int(resultado['label'].split()[0])
            confianza = resultado['score']
            
            # Solo considerar el resultado del modelo si la confianza es alta
            if confianza > 0.7:
                if estrellas <= 2:
                    sentimiento = "negativo"
                elif estrellas >= 4:
                    sentimiento = "positivo"
                else:
                    sentimiento = "neutral"
            else:
                sentimiento = "neutral"
                estrellas = 3
            
            return {
                "sentimiento": sentimiento,
                "estrellas": estrellas,
                "confianza": confianza
            }
            
        except Exception as e:
            print(f"Error en análisis de sentimiento: {e}")
            return {"sentimiento": "neutral", "estrellas": 3, "confianza": 0.0}
    
    def es_negativo(self, texto):
        """Verifica si el mensaje tiene sentimiento negativo"""
        resultado = self.analizar(texto)
        return resultado["sentimiento"] == "negativo"
    
    def obtener_respuesta_empatica(self, sentimiento):
        """
        Genera un prefijo empático según el sentimiento
        
        Args:
            sentimiento (str): "positivo", "negativo" o "neutral"
            
        Returns:
            str: Prefijo para la respuesta o cadena vacía
        """
        import random
        
        respuestas = {
            "negativo": [
                "Entiendo tu frustración. ",
                "Lamento mucho las molestias. ",
                "Disculpa los inconvenientes. ",
            ],
            "positivo": [
                "¡Me alegra escuchar eso! ",
                "¡Genial! ",
                "¡Qué bien! ",
            ],
            "neutral": [""]
        }
        
        opciones = respuestas.get(sentimiento, [""])
        return random.choice(opciones)
