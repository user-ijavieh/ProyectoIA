import gradio as gr
import uuid
from ia_engine import extraer_multiples_pedidos, es_saludo_o_despedida
from database import guardar_pedido

# Variable global para mantener el pedido en memoria antes de confirmar
pedido_pendiente = []

def flujo_chatbot(mensaje, historial):
    global pedido_pendiente
    try:
        mensaje_min = mensaje.lower()

        # LÓGICA DE CONFIRMACIÓN
        palabras_confirmacion = ["si", "sí", "vale", "confirmar", "correcto", "perfecto"]
        mensaje_tokenizado = mensaje_min.split()
        if any(palabra in mensaje_tokenizado for palabra in palabras_confirmacion):
            if pedido_pendiente:
                # GENERAMOS UN ID DE TICKET ÚNICO
                ticket_id = str(uuid.uuid4())[:8].upper()
                
                guardado_ok = True
                for item in pedido_pendiente:
                    if not guardar_pedido(ticket_id, item['producto'], item['cantidad'], item['nota']):
                        guardado_ok = False
                
                if guardado_ok:
                    resumen_final = f"✅ **¡Pedido enviado a cocina!**\n\n**Ticket ID:** `{ticket_id}`\n"
                    for item in pedido_pendiente:
                        resumen_final += f"- {item['cantidad']}x {item['producto']}\n"
                else:
                    resumen_final = "❌ Hubo un error al guardar el pedido en la base de datos. Inténtalo de nuevo."
                
                pedido_pendiente = [] # Limpiamos la memoria
                return resumen_final
            else:
                return "No tienes ningún pedido pendiente. ¿Qué te gustaría tomar?"

        # LÓGICA DE NUEVO PEDIDO
        else:
            # 1. Chequeamos si es un saludo/despedida
            from ia_engine import es_saludo_o_despedida # Import local or top level
            tipo_social = es_saludo_o_despedida(mensaje)
            
            if tipo_social == "saludo":
                return "👋 ¡Hola! Soy tu asistente virtual de GastroIA. ¿Qué te gustaría pedir hoy? (Ej: '2 pizzas y una coca cola')"
            elif tipo_social == "despedida":
                return "👋 ¡Hasta luego! Gracias por usar GastroIA. Vuelve pronto."
            
            # 2. Intentamos extraer pedido
            lista_extraida = extraer_multiples_pedidos(mensaje)
            
            if not lista_extraida:
                return "🤔 No he entendido tu pedido. Por favor, indícame la cantidad y el producto. Ej: 'Quiero **2 hamburguesas**'."

            pedido_pendiente = lista_extraida
            
            respuesta = "📋 **He anotado tu comanda:**\n\n"
            for i, item in enumerate(lista_extraida, 1):
                respuesta += f"{i}. **{item['cantidad']}** {item['producto']} — *({item['nota']})*\n"
            
            respuesta += "\n¿Es correcto? (Responde **'Sí'** para confirmar)"
            return respuesta
            
    except Exception as e:
        import traceback
        return f"⚠️ **Error del sistema:**\n\n`{str(e)}`\n\n```\n{traceback.format_exc()}\n```"

# Corregimos el error del tema usando gr.Blocks
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🍕 GastroIA Assistant")
    gr.Markdown("Haz tu pedido de forma natural. Ejemplo: 'Quiero 2 pizzas poco hechas y un zumo'.")
    
    gr.ChatInterface(
        fn=flujo_chatbot,
        examples=["2 hamburguesas muy hechas y una ensalada", "Quiero 3 pizzas carbonara", "Ponme 5 tacos sin picante"]
    )

if __name__ == "__main__":
    demo.launch(share=True)