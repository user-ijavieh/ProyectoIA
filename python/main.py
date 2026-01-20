import gradio as gr
import uuid
from ia_engine import extraer_multiples_pedidos, es_saludo_o_despedida, procesar_imagen_pedido
from database import guardar_pedido

pedido_pendiente = []

def flujo_chatbot(mensaje, historial):
    global pedido_pendiente
    
    # Soporte multimodal: 'mensaje' puede ser un dict
    texto_usuario = ""
    archivos = []
    
    if isinstance(mensaje, dict):
        texto_usuario = mensaje.get("text", "")
        archivos = mensaje.get("files", [])
    else:
        texto_usuario = str(mensaje)
    
    # Procesar imagen si existe
    if archivos:
        # Se asume que archivos es una lista de paths o URLs
        try:
            texto_ocr = procesar_imagen_pedido(archivos[0])
            if texto_ocr:
                texto_usuario += " " + texto_ocr
        except Exception as e:
            return f"⚠️ Error al procesar imagen: {str(e)}"

    try:
        mensaje_min = texto_usuario.lower()
        palabras_confirmacion = ["si", "sí", "vale", "confirmar", "correcto", "perfecto"]
        
        # MEJORA: Tokenización para evitar falsos positivos con palabras como "sin"
        mensaje_tokenizado = mensaje_min.split()
        
        # --- BLOQUE A: CONFIRMACIÓN DEL PEDIDO ---
        if any(palabra in mensaje_tokenizado for palabra in palabras_confirmacion):
            if pedido_pendiente:
                ticket_id = str(uuid.uuid4())[:8].upper()
                
                # Verificamos que todos los items se guarden correctamente
                guardado_ok = True
                for item in pedido_pendiente:
                    if not guardar_pedido(ticket_id, item['producto'], item['cantidad'], item['nota']):
                        guardado_ok = False
                
                if guardado_ok:
                    resumen = f"✅ **¡Pedido enviado!** (Ticket: `{ticket_id}`)\n"
                    for item in pedido_pendiente:
                        resumen += f"- {item['cantidad']}x {item['producto']}\n"
                    pedido_pendiente = []
                    return resumen
                return "❌ Error al guardar en la base de datos."
            return "No hay pedidos pendientes."
        
        # --- BLOQUE B: INTERPRETACIÓN (Aquí estaba el conflicto) ---
        else:
            # 1. Chequeamos si es un saludo/despedida
            tipo_social = es_saludo_o_despedida(texto_usuario)
            
            if tipo_social == "saludo":
                return "👋 ¡Hola! Soy tu asistente virtual de GastroIA. ¿Qué te gustaría pedir hoy? (Ej: '2 pizzas y una coca cola')"
            elif tipo_social == "despedida":
                return "👋 ¡Hasta luego! Gracias por usar GastroIA. Vuelve pronto."
            
            # 2. Intentamos extraer pedido
            lista_extraida = extraer_multiples_pedidos(texto_usuario)
            
            # Si la IA no encontró ningún producto válido
            if not lista_extraida:
                return "🤔 No he entendido tu pedido. Por favor, indícame la cantidad y el producto. Ej: 'Quiero **2 hamburguesas**'."

            # Guardamos temporalmente para esperar confirmación
            pedido_pendiente = lista_extraida
            
            respuesta = "📋 **He anotado tu comanda:**\n\n"
            for i, item in enumerate(lista_extraida, 1):
                respuesta += f"{i}. **{item['cantidad']}** {item['producto']} — *({item['nota']})*\n"
            
            respuesta += "\n¿Es correcto? (Responde **'Sí'** para confirmar)"
            return respuesta
            
    except Exception as e:
        return f"⚠️ **Error:** {str(e)}"

# Interfaz Gradio
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🍕 GastroIA Assistant")
    # Multimodal: type="messages" es el nuevo estándar
    gr.ChatInterface(fn=flujo_chatbot, multimodal=True)

if __name__ == "__main__":
    demo.launch(share=True)