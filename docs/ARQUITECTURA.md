# 🍕 GastroIA - Documentación Técnica

## Descripción General

GastroIA es un asistente virtual inteligente para restaurantes que permite a los clientes realizar pedidos mediante lenguaje natural. El sistema utiliza **3 modelos de Inteligencia Artificial** para interpretar los pedidos, clasificar intenciones y detectar el estado emocional del usuario.

---

## 🤖 Modelos de IA Utilizados

### 1. **Clasificador de Intención Entrenado** (Naive Bayes + TF-IDF)
- **Tipo:** Clasificación de texto supervisada
- **Propósito:** Determinar qué quiere hacer el usuario (pedir, saludar, quejarse, etc.)
- **Cómo funciona:**
  - Entrenado con dataset balanceado de 150 ejemplos
  - Usa TF-IDF para vectorizar texto y Naive Bayes para clasificar
  - 10 categorías de intención con ~65% de precisión
- **Ubicación:** `backend/chatbot/trained_classifier.py`
- **Dataset:** `backend/chatbot/training_data/pedidos_dataset_balanced.json`
- **Modelo guardado:** `backend/chatbot/training_data/intent_classifier_model.pkl`

```python
# Intenciones soportadas:
intenciones = [
    "pedido",           # Usuario quiere ordenar
    "saludo",           # Hola, buenos días
    "despedida",        # Adiós, hasta luego
    "consulta_menu",    # ¿Qué tienen?
    "consulta_precio",  # ¿Cuánto cuesta?
    "consulta_estado",  # ¿Cómo va mi pedido?
    "queja",            # El servicio es terrible
    "feedback_positivo",# Todo estuvo delicioso
    "confirmacion",     # Sí, correcto
    "negacion"          # No, cancela
]
```

### 2. **BART Large MNLI** (facebook/bart-large-mnli)
- **Tipo:** Clasificación Zero-Shot
- **Propósito:** Identificar productos del menú en el texto del usuario
- **Cómo funciona:** 
  - Recibe el texto del usuario y una lista de productos del menú
  - Clasifica qué producto es más probable que el usuario esté pidiendo
  - No requiere entrenamiento específico (Zero-Shot Learning)
- **Ubicación:** `backend/chatbot/order_processor.py`
- **Tamaño:** ~1.5GB

```python
self.classifier = pipeline(
    "zero-shot-classification", 
    model="facebook/bart-large-mnli"
)
```

### 3. **BERT Multilingual Sentiment** (nlptown/bert-base-multilingual-uncased-sentiment)
- **Tipo:** Análisis de Sentimiento
- **Propósito:** Detectar el estado emocional del usuario para responder de forma empática
- **Cómo funciona:**
  - Analiza el texto del usuario
  - Devuelve una puntuación de 1-5 estrellas
  - Complementado con detección por palabras clave para mayor precisión en español
- **Ubicación:** `backend/chatbot/sentiment_analyzer.py`
- **Tamaño:** ~700MB

**Ejemplo de uso:**
```
Usuario: "Llevo 20 minutos esperando mi pedido"
→ Detecta: palabras clave negativas ("esperando")
→ Intención: queja
→ Respuesta: "😔 Lamento mucho escuchar eso. ¿Tienes el número de ticket?"

Usuario: "¡Genial, la pizza estaba deliciosa!"
→ Detecta: palabras clave positivas ("genial", "deliciosa")
→ Intención: feedback_positivo
→ Respuesta: "😊 ¡Muchas gracias! Nos alegra saber que estás satisfecho."
```

---

## 📚 ¿Cómo funciona el clasificador de intención?

El sistema usa un modelo **entrenado localmente** con scikit-learn:

### Proceso de entrenamiento:
1. **Dataset balanceado:** 150 ejemplos, 15 por cada categoría
2. **Vectorización TF-IDF:** Convierte texto a vectores numéricos
3. **Clasificador Naive Bayes:** Aprende patrones de cada categoría
4. **Validación cruzada:** 65% de precisión promedio

### Re-entrenar el modelo:
```bash
cd backend/chatbot/training_data
python train_model.py
```

### Ventajas:
- ✅ Más rápido que modelos grandes
- ✅ No requiere GPU
- ✅ Fácil de agregar ejemplos nuevos
- ✅ Fallback a reglas si el modelo falla

---

## 📚 ¿Qué es BART y cómo funciona?

**BART** (Bidirectional and Auto-Regressive Transformers) es un modelo de lenguaje desarrollado por Facebook/Meta.

### Características:
- **Arquitectura:** Encoder-Decoder basado en Transformers
- **Entrenamiento:** Pre-entrenado en texto de internet, luego fine-tuned en MNLI
- **Capacidad Zero-Shot:** Puede clasificar texto en categorías que nunca vio

### ¿Cómo clasifica productos?

Cuando el usuario dice "quiero una pizza con queso":

1. BART recibe el texto y las etiquetas candidatas: `["pizza", "hamburguesa", "coca cola"]`
2. Evalúa: "¿Este texto implica que el usuario habla de pizza?"
3. Calcula probabilidad para cada producto
4. Devuelve el producto con mayor puntuación

```
Entrada: "quiero una pizza con queso"
Candidatos: ["pizza", "hamburguesa", "coca cola"]

Resultados:
- pizza: 0.92 ✅
- hamburguesa: 0.05
- coca cola: 0.03
```

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │   Panel Web     │    │      Chatbot Gradio             │ │
│  │  (index.html)   │    │    (localhost:7860)             │ │
│  └────────┬────────┘    └────────────────┬────────────────┘ │
└───────────┼──────────────────────────────┼──────────────────┘
            │                              │
            ▼                              ▼
┌───────────────────────┐    ┌─────────────────────────────────┐
│    Backend PHP        │    │        Backend Python           │
│  ┌─────────────────┐  │    │  ┌─────────────────────────────┐│
│  │ pedidos.controller│  │    │  │      chatbot_ui.py         ││
│  │ pedidos.service  │  │    │  │   (Interfaz Gradio)        ││
│  │ pedidos.repository│  │    │  └──────────┬────────────────┘│
│  └────────┬────────┘  │    │               │                 │
└───────────┼───────────┘    │  ┌────────────┴────────────────┐│
            │                │  │   trained_classifier.py      ││
            │                │  │  (Modelo entrenado sklearn)  ││
            │                │  └──────────────────────────────┘│
            │                │  ┌──────────────────────────────┐│
            │                │  │     order_processor.py       ││
            │                │  │  (IA: BART para productos)   ││
            │                │  └──────────────────────────────┘│
            │                │  ┌──────────────────────────────┐│
            │                │  │   sentiment_analyzer.py      ││
            │                │  │  (IA: BERT para emociones)   ││
            │                │  └──────────────────────────────┘│
            │                │  ┌──────────────────────────────┐│
            │                │  │     db_repository.py         ││
            │                │  │  (Conexión a MySQL)          ││
            │                │  └──────────────────────────────┘│
            │                └─────────────────┬───────────────┘
            │                                  │
            ▼                                  ▼
┌─────────────────────────────────────────────────────────────┐
│                     BASE DE DATOS                            │
│                   MySQL (restaurante_db)                     │
│  ┌─────────────────┐        ┌─────────────────────────────┐ │
│  │     menu        │        │         pedidos             │ │
│  │  - id           │        │  - id, id_pedido            │ │
│  │  - nombre       │        │  - producto, cantidad       │ │
│  │  - precio       │        │  - nota, estado, precio     │ │
│  │  - disponible   │        │  - fecha                    │ │
│  └─────────────────┘        └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura de Archivos

```
ProyectoIA/
├── backend/
│   ├── api/                    # API REST en PHP
│   │   ├── pedidos.controller.php
│   │   ├── pedidos.service.php
│   │   └── pedidos.repository.php
│   │
│   ├── chatbot/                # Chatbot en Python
│   │   ├── chatbot_ui.py       # Interfaz principal Gradio
│   │   ├── trained_classifier.py # Clasificador entrenado (sklearn)
│   │   ├── intent_classifier.py  # Clasificación por reglas (fallback)
│   │   ├── order_processor.py  # Procesamiento con IA (BART)
│   │   ├── sentiment_analyzer.py # Análisis de sentimiento (BERT)
│   │   ├── db_repository.py    # Acceso a base de datos
│   │   ├── requirements.txt    # Dependencias Python
│   │   │
│   │   └── training_data/      # Dataset y entrenamiento
│   │       ├── pedidos_dataset_balanced.json  # 150 ejemplos
│   │       ├── train_model.py  # Script de entrenamiento
│   │       └── intent_classifier_model.pkl    # Modelo guardado
│   │
│   └── config/
│       └── config.php          # Configuración PHP
│
├── frontend/
│   ├── assets/
│   │   ├── css/style.css
│   │   └── js/
│   │       ├── main.js
│   │       ├── api-client.js
│   │       ├── board-renderer.js
│   │       └── ticket-manager.js
│   └── public/
│       ├── index.html          # Panel de gestión
│       └── historial.html      # Historial de pedidos
│
├── database/
│   └── schemas/
│       └── restaurante_db.sql  # Esquema de la BD
│
├── docs/
│   ├── README.md
│   └── ARQUITECTURA.md         # Este archivo
│
├── docker-compose.yml          # Orquestación Docker
├── Dockerfile.chatbot          # Imagen del chatbot
└── Dockerfile.web              # Imagen del servidor web
```

---

## 🔄 Flujo del Chatbot

### 1. Recepción del mensaje
```python
def procesar_mensaje(self, mensaje, historial):
    texto_usuario = str(mensaje).strip()
    return self._procesar_intencion(texto_usuario)
```

### 2. Clasificación de intención (Modelo Entrenado)

El sistema usa primero el modelo sklearn entrenado:

```python
if self.trained_classifier.esta_disponible():
    intencion = self.trained_classifier.clasificar(texto_usuario)
    return self._responder_por_intencion(intencion, texto_usuario)
```

| Intención | Ejemplo | Respuesta |
|-----------|---------|-----------|
| **pedido** | "2 pizzas con queso" | Procesar con BART |
| **saludo** | "Hola" | Bienvenida + menú |
| **despedida** | "Adiós" | Despedida cordial |
| **consulta_menu** | "¿Qué tienen?" | Mostrar menú |
| **consulta_precio** | "¿Cuánto cuesta?" | Indicar precio |
| **queja** | "El servicio es terrible" | Respuesta empática |
| **feedback_positivo** | "Todo perfecto" | Agradecimiento |
| **confirmacion** | "Sí" | Confirmar pedido |
| **negacion** | "No" | Cancelar pedido |

### 3. Procesamiento del pedido con BART

```python
# Segmentación inteligente del texto
texto = "2 pizzas con extra queso y una coca cola"

# El sistema detecta:
# - "2 pizzas con extra queso" → 1 producto con nota
# - "una coca cola" → 1 producto separado

# Clasificación Zero-Shot
resultado = self.classifier(
    segmento, 
    candidate_labels=["pizza", "hamburguesa", "coca cola", ...]
)
```

### 4. Manejo de sinónimos y variaciones

El sistema reconoce variaciones comunes:

```python
sinonimos = {
    "pizzas": "pizza",
    "coca": "coca cola",
    "perrito": "hot dog",
    "jugo": "zumo",
    # ... más variaciones
}
```

---

## 🎨 Interfaz de Usuario (Gradio)

La interfaz se crea con **Gradio** con diseño moderno:

### Características:
- **Tema oscuro** con acentos naranjas
- **Ancho completo** de pantalla
- **Mensaje inicial** con el menú del restaurante
- **Share público** para acceso externo

```python
with gr.Blocks(css=custom_css) as demo:
    gr.Markdown("# 🍕 GastroIA Assistant")
    
    chat = gr.Chatbot(
        value=[{"role": "assistant", "content": mensaje_inicial}],
        height="70vh"
    )
    
    gr.ChatInterface(
        fn=chatbot.procesar_mensaje,
        chatbot=chat
    )

demo.launch(server_name="0.0.0.0", server_port=7860, share=True)
```

---

## 🗄️ Base de Datos

### Tabla `menu`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT | Identificador único |
| nombre_producto | VARCHAR(100) | Nombre del producto |
| precio | DECIMAL(10,2) | Precio en euros |
| disponible | TINYINT(1) | 1=disponible, 0=no |

### Tabla `pedidos`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT | Identificador único |
| id_pedido | VARCHAR(50) | Ticket (8 caracteres hex) |
| producto | VARCHAR(100) | Nombre del producto |
| cantidad | INT | Cantidad pedida |
| precio_unitario | DECIMAL(10,2) | Precio por unidad |
| nota | TEXT | Notas especiales |
| estado | VARCHAR(50) | pendiente/preparacion/completado |
| fecha | TIMESTAMP | Fecha y hora |

---

## 🐳 Docker

El proyecto usa Docker Compose con 3 servicios:

```yaml
services:
  db:          # MySQL 8.0
  web:         # Apache + PHP
  chatbot:     # Python + Gradio + IA
```

### Puertos:
- **7860:** Chatbot (Gradio)
- **80:** Panel web (Apache)
- **3306:** MySQL

---

## 📦 Dependencias

### Python (backend/chatbot/requirements.txt)
| Paquete | Versión | Uso |
|---------|---------|-----|
| gradio | ≥4.0.0 | Interfaz web del chat |
| transformers | ≥4.30.0 | Modelos BART y BERT |
| torch | ≥2.0.0 | Backend de IA (PyTorch) |
| mysql-connector-python | ≥8.3.0 | Conexión a BD |
| sentencepiece | ≥0.1.99 | Tokenización |
| accelerate | ≥0.20.0 | Optimización de modelos |
| scikit-learn | ≥1.3.0 | Clasificador de intención entrenado |

---

## 🚀 Cómo Ejecutar

### Iniciar servicios:
```bash
docker-compose up -d
```

### Ver logs del chatbot:
```bash
docker logs gastroia_chatbot
```

### Reconstruir después de cambios:
```bash
# Limpiar cache de modelos y reconstruir
Remove-Item -Path ".\backend\chatbot\.cache" -Recurse -Force
docker-compose up -d --build chatbot
```

### Re-entrenar el modelo de intención:
```bash
cd backend/chatbot/training_data
pip install scikit-learn
python train_model.py
```

### URLs:
- **Chatbot:** http://localhost:7860
- **Panel de gestión:** http://localhost/frontend/public/index.html

---

## 📝 Notas Importantes

1. **Primera ejecución lenta:** Los modelos BART (~1.5GB) y BERT (~700MB) se descargan la primera vez
2. **CPU:** Actualmente usa CPU, compatible con servidores sin GPU
3. **Caché de modelos:** Se guarda en `.cache/` (incluido en `.dockerignore`)
4. **Share público:** Con `share=True` se genera un enlace temporal de 72 horas
5. **Modelo entrenado:** El clasificador sklearn se carga desde `training_data/intent_classifier_model.pkl`

---

## 🔧 Agregar nuevos ejemplos al dataset

1. Editar `backend/chatbot/training_data/pedidos_dataset_balanced.json`
2. Agregar ejemplos manteniendo el balance (igual cantidad por categoría)
3. Ejecutar `python train_model.py`
4. Copiar el nuevo `.pkl` al contenedor o reconstruir

---

*Documentación actualizada - Enero 2026*
