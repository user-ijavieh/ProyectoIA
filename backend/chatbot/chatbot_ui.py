"""
Interfaz de usuario del chatbot usando Gradio
Maneja la interacción con el usuario y coordina los servicios
"""

import gradio as gr
import uuid

from intent_classifier import IntentClassifier
from order_processor import OrderProcessor
from ocr_service import procesar_imagen_pedido
from db_repository import (
    obtener_menu_db,
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
        
        # Cargar menú y inicializar procesador
        menu_productos = obtener_menu_db()
        self.order_processor = OrderProcessor(menu_productos)
    
    def procesar_mensaje(self, mensaje, historial):
        """
        Procesa un mensaje del usuario
        
        Args:
            mensaje: Mensaje del usuario (texto o multimodal con archivos)
            historial: Historial de conversación (no usado actualmente)
            
        Returns:
            str: Respuesta del chatbot
        """
        # Extraer texto y archivos
        texto_usuario = self._extraer_texto(mensaje)
        archivos = self._extraer_archivos(mensaje)
        
        # Procesar imagen si existe
        if archivos:
            texto_ocr = procesar_imagen_pedido(archivos[0])
            if texto_ocr:
                texto_usuario += " " + texto_ocr
        
        # Procesar según la intención
        return self._procesar_intencion(texto_usuario)
    
    def _extraer_texto(self, mensaje):
        """Extrae el texto del mensaje"""
        if isinstance(mensaje, dict):
            return mensaje.get("text", "")
        return str(mensaje)
    
    def _extraer_archivos(self, mensaje):
        """Extrae los archivos del mensaje multimodal"""
        if isinstance(mensaje, dict):
            return mensaje.get("files", [])
        return []
    
    def _procesar_intencion(self, texto_usuario):
        """Determina la intención y devuelve la respuesta apropiada"""
        
        # 1. Verificar confirmación de pedido pendiente
        if self.pedido_pendiente and self.intent_classifier.es_confirmacion(texto_usuario):
            return self._confirmar_pedido()
        
        # 2. Verificar negación de pedido pendiente
        if self.pedido_pendiente and self.intent_classifier.es_negacion(texto_usuario):
            return self._cancelar_pedido()
        
        # 3. Verificar consulta de estado
        consulta = self.intent_classifier.detectar_consulta_pedido(texto_usuario)
        if consulta:
            return self._procesar_consulta_estado(consulta)
        
        # 4. Verificar saludos/despedidas
        tipo_social = self.intent_classifier.detectar_saludo_o_despedida(texto_usuario)
        if tipo_social:
            return self._respuesta_social(tipo_social)
        
        # 5. Procesar como nuevo pedido
        return self._procesar_nuevo_pedido(texto_usuario)
    
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
            return (
                "👋 ¡Hola! Soy el asistente de **GastroIA**.\n\n"
                "¿Qué te gustaría pedir?\n"
                "_(Ejemplo: '2 pizzas y un zumo')_"
            )
        
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
    
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🍕 GastroIA Assistant")
        gr.Markdown(
            "Asistente inteligente para tomar pedidos. "
            "Puedes escribir tu pedido o subir una imagen."
        )
        
        gr.ChatInterface(
            fn=chatbot.procesar_mensaje,
            multimodal=True,
            examples=[
                "Hola, quiero hacer un pedido",
                "2 pizzas margarita y una coca cola",
                "¿Cuál es el estado de mi pedido?",
            ]
        )
    
    return demo


if __name__ == "__main__":
    demo = crear_interfaz()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
