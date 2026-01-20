import gradio as gr
import uuid
from ia_engine import extraer_multiples_pedidos, es_saludo_o_despedida, procesar_imagen_pedido, detectar_intencion_consulta
from database import guardar_pedido, obtener_estado_pedido, obtener_precio_producto # Nueva importación

pedido_pendiente = []

def flujo_chatbot(mensaje, historial):
    global pedido_pendiente
    texto_usuario = mensaje.get("text", "") if isinstance(mensaje, dict) else str(mensaje)
    archivos = mensaje.get("files", []) if isinstance(mensaje, dict) else []
    
    if archivos:
        texto_ocr = procesar_imagen_pedido(archivos[0])
        if texto_ocr: texto_usuario += " " + texto_ocr

    mensaje_min = texto_usuario.lower()
    
    # 1. Confirmación de Pedido con Precios
    if any(p in mensaje_min.split() for p in ["si", "sí", "vale"]) and pedido_pendiente:
        ticket_id = str(uuid.uuid4())[:8].upper()
        guardado_ok = True
        
        for item in pedido_pendiente:
            # Obtenemos el precio unitario de la DB
            precio = obtener_precio_producto(item['producto'])
            
            # Guardamos el pedido con el precio unitario
            if not guardar_pedido(ticket_id, item['producto'], item['cantidad'], item['nota'], precio):
                guardado_ok = False
        
        if guardado_ok:
            res = f"✅ **¡Enviado!** Ticket: `{ticket_id}`\n"
            for i in pedido_pendiente: res += f"- {i['cantidad']}x {i['producto']}\n"
            pedido_pendiente = []
            return res
        return "❌ Error al conectar con la base de datos."

    # 2. Consulta Estado
    consulta = detectar_intencion_consulta(texto_usuario)
    if consulta:
        if consulta == "SOLICITAR_ID": return "🕵️‍♀️ ¿Me das tu **ID de ticket** (ej: `7D06BF25`)?"
        info = obtener_estado_pedido(consulta)
        if info:
            items = ", ".join([f"{i['cantidad']}x {i['producto']}" for i in info['items']])
            return f"🕒 **Ticket `{consulta}`**: {info['estado'].upper()}\nContiene: {items}"
        return f"❌ Ticket `{consulta}` no encontrado."

    # 3. Social y Extracción
    tipo = es_saludo_o_despedida(texto_usuario)
    if tipo == "saludo": return "👋 ¡Hola! Soy el asistente de GastroIA. ¿Qué te gustaría pedir? (Ej: '2 pizzas y un zumo')"
    if tipo == "despedida": return "👋 ¡Hasta pronto!"

    pedido_pendiente = extraer_multiples_pedidos(texto_usuario)
    if not pedido_pendiente: return "🤔 No entendí el pedido. Prueba algo como: '2 hamburguesas y una coca cola'."
    
    resp = "📋 **He anotado:**\n"
    for i, item in enumerate(pedido_pendiente, 1):
        resp += f"{i}. **{item['cantidad']}** {item['producto']} ({item['nota']})\n"
    return resp + "\n¿Es correcto? (Responde 'Sí' para confirmar)"

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🍕 GastroIA Assistant")
    gr.ChatInterface(fn=flujo_chatbot, multimodal=True)

if __name__ == "__main__":
    demo.launch()