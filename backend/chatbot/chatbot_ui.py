"""
Interfaz de usuario del chatbot usando Gradio
Maneja la interacción con el usuario y coordina los servicios
"""

import gradio as gr
import uuid

from intent_classifier import IntentClassifier
from order_processor import OrderProcessor
from sentiment_analyzer import SentimentAnalyzer
from trained_classifier import TrainedIntentClassifier
from db_repository import (
    obtener_menu_db,
    obtener_menu_completo,
    guardar_pedido,
    obtener_estado_pedido,
    obtener_precio_producto
)


class ChatbotUI:
    """Controlador principal del chatbot"""
    
    def __init__(self):
        """Inicializa el chatbot y sus componentes"""
        self.pedido_pendiente = []
        self.intent_classifier = IntentClassifier()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.trained_classifier = TrainedIntentClassifier()
        
        # Cargar menú y inicializar procesador
        menu_productos = obtener_menu_db()
        self.order_processor = OrderProcessor(menu_productos)
    
    def obtener_mensaje_bienvenida(self):
        """Genera el mensaje de bienvenida con el menú"""
        menu = obtener_menu_completo()
        
        mensaje = "👋 ¡Hola! Soy el asistente de **GastroIA**.\n\n"
        mensaje += "📜 **Nuestro menú de hoy:**\n\n"
        
        if menu:
            for item in menu:
                nombre = item['nombre_producto'].capitalize()
                precio = item['precio']
                mensaje += f"• **{nombre}** - €{precio:.2f}\n"
        else:
            mensaje += "_No se pudo cargar el menú_\n"
        
        mensaje += "\n¿Qué te gustaría pedir?\n"
        mensaje += "_(Ejemplo: '2 pizzas con extra queso y una coca cola')_"
        
        return mensaje
    
    def procesar_mensaje(self, mensaje, historial):
        """
        Procesa un mensaje del usuario
        
        Args:
            mensaje: Mensaje de texto del usuario
            historial: Historial de conversación (no usado actualmente)
            
        Returns:
            str: Respuesta del chatbot
        """
        texto_usuario = str(mensaje).strip()
        
        # Procesar según la intención (el feedback se maneja dentro)
        return self._procesar_intencion(texto_usuario)
    
    def _procesar_intencion(self, texto_usuario):
        """Determina la intención y devuelve la respuesta apropiada"""
        
        # 1. Verificar confirmación de pedido pendiente
        if self.pedido_pendiente and self.intent_classifier.es_confirmacion(texto_usuario):
            return self._confirmar_pedido()
        
        # 2. Verificar negación de pedido pendiente
        if self.pedido_pendiente and self.intent_classifier.es_negacion(texto_usuario):
            return self._cancelar_pedido()
        
        # 3. Usar clasificador entrenado si está disponible
        if self.trained_classifier.esta_disponible():
            intencion = self.trained_classifier.clasificar(texto_usuario)
            
            if intencion:
                return self._responder_por_intencion(intencion, texto_usuario)
        
        # Fallback a reglas si el modelo no está disponible
        return self._procesar_con_reglas(texto_usuario)
    
    def _responder_por_intencion(self, intencion, texto_usuario):
        """Responde según la intención clasificada por el modelo"""
        
        if intencion == "pedido":
            return self._procesar_nuevo_pedido(texto_usuario)
        
        elif intencion == "saludo":
            return self._respuesta_social("saludo")
        
        elif intencion == "despedida":
            return self._respuesta_social("despedida")
        
        elif intencion == "consulta_menu":
            return self.obtener_mensaje_bienvenida()
        
        elif intencion == "consulta_precio":
            return ("💰 Los precios varían según el producto. "
                    "¿De qué producto te gustaría saber el precio?")
        
        elif intencion == "consulta_estado":
            return ("🔍 Para consultar el estado de tu pedido, "
                    "por favor dame el número de ticket (8 caracteres).")
        
        elif intencion == "queja":
            return ("😔 Lamento mucho escuchar eso. Tu opinión es muy importante. "
                    "¿Hay algo específico en lo que pueda ayudarte?")
        
        elif intencion == "feedback_positivo":
            return ("😊 ¡Muchas gracias! Nos alegra saber que estás satisfecho. "
                    "¿Hay algo más en lo que pueda ayudarte?")
        
        elif intencion == "confirmacion":
            if self.pedido_pendiente:
                return self._confirmar_pedido()
            return "👍 ¿Hay algo que quieras ordenar?"
        
        elif intencion == "negacion":
            if self.pedido_pendiente:
                return self._cancelar_pedido()
            return "De acuerdo. ¿Puedo ayudarte en algo más?"
        
        # Si no reconoce, usar reglas como fallback
        return self._procesar_con_reglas(texto_usuario)
    
    def _procesar_con_reglas(self, texto_usuario):
        """Procesa usando reglas tradicionales (fallback)"""
        
        # Verificar consulta de estado
        consulta = self.intent_classifier.detectar_consulta_pedido(texto_usuario)
        if consulta:
            return self._procesar_consulta_estado(consulta)
        
        # Verificar si pide ver el menú
        if self._quiere_ver_menu(texto_usuario):
            return self.obtener_mensaje_bienvenida()
        
        # Verificar saludos/despedidas
        tipo_social = self.intent_classifier.detectar_saludo_o_despedida(texto_usuario)
        if tipo_social:
            return self._respuesta_social(tipo_social)
        
        # Verificar si es feedback/comentario
        tipo_feedback = self._detectar_feedback(texto_usuario)
        if tipo_feedback:
            return self._responder_feedback(tipo_feedback, texto_usuario)
        
        # Verificar si parece un pedido
        if self._parece_pedido(texto_usuario):
            return self._procesar_nuevo_pedido(texto_usuario)
        
        # Si no es nada reconocible
        return self._respuesta_ayuda()
    
    def _quiere_ver_menu(self, texto):
        """Detecta si el usuario quiere ver el menú"""
        texto_lower = texto.lower()
        
        indicadores_menu = [
            "menu", "menú", "carta", "ver carta", "ver menu", "ver menú",
            "muestrame", "muéstrame", "mostrar menu", "mostrar menú",
            "que tienen", "qué tienen", "que hay", "qué hay",
            "que ofrecen", "qué ofrecen", "productos", "opciones",
            "platillos", "platos", "comidas", "bebidas"
        ]
        
        return any(p in texto_lower for p in indicadores_menu)
    
    def _detectar_feedback(self, texto):
        """Detecta si el mensaje es feedback/comentario y retorna el tipo"""
        texto_lower = texto.lower()
        
        # Feedback negativo (quejas, críticas)
        palabras_negativas = [
            "terrible", "horrible", "malo", "mal", "pésimo", "asco",
            "esperando", "tarda", "demora", "lento", "mucho tiempo",
            "no llega", "frío", "queja", "molesto", "enfadado",
            "decepcionado", "decepcionante", "inaceptable"
        ]
        
        # Feedback positivo (agradecimientos, elogios)
        palabras_positivas = [
            "gracias", "genial", "excelente", "perfecto", "delicioso",
            "rico", "buenísimo", "increíble", "fantástico", "encanta",
            "satisfecho", "contento", "feliz", "bien hecho", "buen trabajo"
        ]
        
        # Palabras que indican intención de PEDIR (NO es feedback)
        palabras_pedido = [
            "quiero", "dame", "ponme", "tráeme", "traeme", "pido",
            "necesito", "quisiera", "me pones", "me das", "para llevar",
            "ordenar", "pedir"
        ]
        
        # Si tiene palabras de pedido, NO es feedback
        if any(p in texto_lower for p in palabras_pedido):
            return None
        
        # Detectar tipo de feedback
        if any(p in texto_lower for p in palabras_negativas):
            return "negativo"
        
        if any(p in texto_lower for p in palabras_positivas):
            return "positivo"
        
        return None
    
    def _responder_feedback(self, tipo, texto):
        """Responde apropiadamente al feedback del usuario"""
        texto_lower = texto.lower()
        
        if tipo == "negativo":
            # Quejas de espera
            if any(p in texto_lower for p in ["esperando", "tarda", "demora", "mucho tiempo", "lento", "no llega"]):
                return ("😔 Lamento mucho la espera. Entiendo tu frustración. "
                        "¿Tienes el número de ticket? Puedo verificar el estado de tu pedido.")
            # Quejas de calidad/servicio
            else:
                return ("😔 Lamento mucho escuchar eso. Tu opinión es muy importante para nosotros. "
                        "¿Hay algo específico en lo que pueda ayudarte ahora?")
        
        elif tipo == "positivo":
            return ("😊 ¡Muchas gracias por tus palabras! Nos alegra saber que estás satisfecho. "
                    "¿Hay algo más en lo que pueda ayudarte?")
        
        return None
    
    def _parece_pedido(self, texto):
        """Verifica si el texto parece ser un intento de pedido"""
        texto_lower = texto.lower()
        
        # Palabras que indican intención de pedir
        indicadores_pedido = [
            "quiero", "dame", "ponme", "tráeme", "traeme", "pido",
            "necesito", "quisiera", "me pones", "me das", "para llevar",
            "una ", "uno ", "dos ", "tres ", "cuatro ", "cinco ",
            "1 ", "2 ", "3 ", "4 ", "5 ",
            "pizza", "hamburguesa", "coca", "refresco", "agua",
            "papas", "ensalada", "postre", "helado", "taco"
        ]
        
        return any(p in texto_lower for p in indicadores_pedido)
    
    def _respuesta_ayuda(self):
        """Respuesta cuando no se entiende el mensaje"""
        return ("🤔 No estoy seguro de entender. ¿Cómo puedo ayudarte?\n\n"
                "Puedo:\n"
                "- Tomar tu pedido\n"
                "- Mostrar el menú\n"
                "- Verificar el estado de un pedido")
    
    def _confirmar_pedido(self):
        """Confirma y guarda el pedido pendiente en la base de datos"""
        ticket_id = str(uuid.uuid4())[:8].upper()
        guardado_ok = True
        
        for item in self.pedido_pendiente:
            # Obtener precio del producto
            precio = obtener_precio_producto(item['producto'])
            
            # Guardar en BD
            if not guardar_pedido(
                ticket_id,
                item['producto'],
                item['cantidad'],
                item['nota'],
                precio
            ):
                guardado_ok = False
        
        if guardado_ok:
            respuesta = f"✅ **¡Enviado!** Ticket: `{ticket_id}`\n\n"
            for item in self.pedido_pendiente:
                respuesta += f"- {item['cantidad']}x {item['producto']}\n"
            
            self.pedido_pendiente = []
            return respuesta
        
        return "❌ Error al conectar con la base de datos. Intenta de nuevo."
    
    def _cancelar_pedido(self):
        """Cancela el pedido pendiente"""
        self.pedido_pendiente = []
        return "❌ Pedido cancelado. ¿Quieres pedir algo más?"
    
    def _procesar_consulta_estado(self, consulta):
        """Procesa consultas sobre el estado de pedidos"""
        if consulta == "SOLICITAR_ID":
            return "🕵️‍♀️ ¿Me das tu **ID de ticket**? (ejemplo: `7D06BF25`)"
        
        # Buscar ticket en la base de datos
        info = obtener_estado_pedido(consulta)
        
        if info:
            items = ", ".join([
                f"{item['cantidad']}x {item['producto']}" 
                for item in info['items']
            ])
            return (
                f"🕒 **Ticket `{consulta}`**: {info['estado'].upper()}\n"
                f"Contiene: {items}"
            )
        
        return f"❌ Ticket `{consulta}` no encontrado."
    
    def _respuesta_social(self, tipo):
        """Genera respuestas para saludos y despedidas"""
        if tipo == "saludo":
            return self.obtener_mensaje_bienvenida()
        
        if tipo == "despedida":
            return "👋 ¡Hasta pronto! Que disfrutes tu comida."
        
        return None
    
    def _procesar_nuevo_pedido(self, texto_usuario):
        """Procesa un nuevo pedido del usuario"""
        # Extraer pedidos del texto
        self.pedido_pendiente = self.order_processor.extraer_pedidos(texto_usuario)
        
        if not self.pedido_pendiente:
            return (
                "🤔 No entendí el pedido.\n\n"
                "Prueba algo como:\n"
                "- '2 hamburguesas y una coca cola'\n"
                "- 'Una pizza margarita sin albahaca'"
            )
        
        # Mostrar resumen del pedido
        respuesta = "📋 **He anotado:**\n\n"
        for i, item in enumerate(self.pedido_pendiente, 1):
            respuesta += (
                f"{i}. **{item['cantidad']}x** {item['producto']}\n"
                f"   _{item['nota']}_\n"
            )
        
        respuesta += "\n¿Es correcto? (Responde 'Sí' para confirmar o 'No' para cancelar)"
        
        return respuesta


def crear_interfaz():
    """Crea y configura la interfaz de Gradio"""
    chatbot = ChatbotUI()
    
    # Obtener mensaje de bienvenida con el menú
    mensaje_inicial = chatbot.obtener_mensaje_bienvenida()
    
    # CSS personalizado con estilo moderno
    custom_css = """
    /* Fondo general */
    .gradio-container {
        max-width: 100% !important;
        width: 100% !important;
        margin: 0 !important;
        padding: 20px 40px !important;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
        min-height: 100vh;
    }
    
    /* Ocultar footer */
    footer { display: none !important; }
    
    /* Título principal */
    h1 {
        text-align: center;
        background: linear-gradient(90deg, #ff6b35, #f7c59f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 5px !important;
    }
    
    /* Área del chat */
    .chatbot {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 107, 53, 0.3) !important;
        border-radius: 20px !important;
        backdrop-filter: blur(10px);
    }
    
    /* Mensajes del asistente */
    .message.bot {
        background: linear-gradient(135deg, #ff6b35 0%, #ff8c42 100%) !important;
        border-radius: 18px 18px 18px 4px !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.3);
    }
    
    /* Mensajes del usuario */
    .message.user {
        background: linear-gradient(135deg, #4a4a6a 0%, #3d3d5c 100%) !important;
        border-radius: 18px 18px 4px 18px !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Input del texto */
    textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 2px solid rgba(255, 107, 53, 0.4) !important;
        border-radius: 15px !important;
        color: white !important;
        font-size: 1rem !important;
    }
    
    textarea:focus {
        border-color: #ff6b35 !important;
        box-shadow: 0 0 20px rgba(255, 107, 53, 0.3) !important;
    }
    
    /* Botón enviar */
    button.primary {
        background: linear-gradient(135deg, #ff6b35 0%, #ff8c42 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    button.primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 107, 53, 0.4) !important;
    }
    
    /* Otros botones */
    button.secondary {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 107, 53, 0.3) !important;
        border-radius: 10px !important;
        color: #ff6b35 !important;
    }
    """
    
    with gr.Blocks(css=custom_css) as demo:
        gr.Markdown("# 🍕 GastroIA Assistant")
        gr.Markdown("<p style='text-align: center; color: #888; font-size: 1.1rem; margin-bottom: 20px;'>Tu asistente virtual para pedidos de comida</p>")
        
        chat = gr.Chatbot(
            value=[{"role": "assistant", "content": mensaje_inicial}],
            height="70vh"
        )
        
        gr.ChatInterface(
            fn=chatbot.procesar_mensaje,
            multimodal=False,
            chatbot=chat
        )
    
    return demo


if __name__ == "__main__":
    demo = crear_interfaz()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
