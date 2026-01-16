import gradio as gr
import uuid
from ia_engine import extraer_multiples_pedidos
from database import guardar_pedido

pedido_pendiente = []

def flujo_chatbot(mensaje, historial):
    global pedido_pendiente
    try:
        mensaje_min = mensaje.lower()
        palabras_confirmacion = ["si", "sí", "vale", "confirmar", "correcto", "perfecto"]
        
        # MEJORA: Tokenización para evitar falsos positivos con palabras como "sin"
        mensaje_tokenizado = mensaje_min.split()
        
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
        
        else:
            pedido_pendiente = extraer_multiples_pedidos(mensaje)
            resp = "📋 **He anotado:**\n\n"
            for i, item in enumerate(pedido_pendiente, 1):
                resp += f"{i}. **{item['cantidad']}** {item['producto']} ({item['nota']})\n"
            return resp + "\n¿Es correcto? (Responde 'Sí')"
            
    except Exception as e:
        return f"⚠️ **Error:** {str(e)}"

# Interfaz Gradio
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🍕 GastroIA Assistant")
    gr.ChatInterface(fn=flujo_chatbot)

if __name__ == "__main__":
    demo.launch()