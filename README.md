# Proyecto GastroIA

Sistema inteligente de gestión de pedidos para restaurantes con interfaz de chatbot basada en IA.

## 📋 Características

- 🤖 **Chatbot con IA** - Procesamiento de pedidos en lenguaje natural
- 📸 **OCR** - Reconocimiento de texto en imágenes para pedidos
- 📊 **Tablero Kanban** - Visualización del estado de pedidos en tiempo real
- 📜 **Historial** - Registro completo de pedidos archivados
- 🔄 **Actualizaciones en tiempo real** - Sin necesidad de recargar la página

## 🏗️ Arquitectura

```
ProyectoIA/
├── frontend/                    # Aplicación web cliente
│   ├── public/                  # Páginas HTML
│   │   ├── index.html          # Tablero principal (Kanban)
│   │   └── historial.html      # Historial de pedidos
│   └── assets/
│       ├── css/                # Estilos
│       └── js/                 # Scripts del cliente
├── backend/
│   ├── api/                    # API REST en PHP
│   │   ├── api_pedidos.php    # Endpoints de pedidos
│   │   ├── check_db.php       # Verificación de BD
│   │   └── fix_schema.php     # Mantenimiento de esquema
│   ├── chatbot/                # Servicio Python IA
│   │   ├── main.py            # Aplicación Gradio
│   │   ├── ia_engine.py       # Motor de IA (GPT)
│   │   ├── database.py        # Conexión a BD
│   │   └── check_ocr.py       # Utilidades OCR
│   └── config/                 # Configuración
├── database/
│   └── schemas/                # Esquemas SQL
└── docs/                       # Documentación
```

## 🚀 Instalación

### Requisitos

- PHP 7.4+
- MySQL/MariaDB
- Python 3.8+
- Tesseract OCR
- OpenAI API Key (para GPT)

### Configuración

1. **Base de datos**
   ```bash
   mysql -u root -p < database/schemas/restaurante_db.sql
   ```

2. **Backend Python**
   ```bash
   cd backend/chatbot
   pip install -r requirements.txt
   ```

3. **Variables de entorno**
   - Configura tu API key de OpenAI en las variables de entorno o en `ia_engine.py`

4. **Servidor web**
   - Coloca el proyecto en tu servidor web (Apache/Nginx)
   - Asegúrate de que PHP tenga acceso a MySQL

## 🎯 Uso

### Iniciar el chatbot
```bash
cd backend/chatbot
python main.py
```
El chatbot estará disponible en `http://localhost:7860`

### Acceder al tablero
Abre `frontend/public/index.html` en tu navegador o accede vía servidor web.

### API REST
- **GET** `backend/api/api_pedidos.php` - Lista de pedidos activos
- **GET** `backend/api/api_pedidos.php?mode=historial` - Pedidos archivados
- **POST** `backend/api/api_pedidos.php` - Actualizar estado de pedido

## 🛠️ Tecnologías

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend API**: PHP, MySQL
- **Backend IA**: Python, Gradio, OpenAI GPT
- **OCR**: Tesseract
- **Base de datos**: MySQL

## 📝 Funcionalidades del Chatbot

- Procesamiento de pedidos en lenguaje natural
- Extracción de múltiples productos de un mensaje
- Reconocimiento de cantidades y notas especiales
- Procesamiento de imágenes con OCR
- Consulta de estado de pedidos por ID
- Respuestas contextuales (saludos, despedidas)

## 🔧 Desarrollo

### Estructura de la BD

- **Tabla `pedidos`**: id, id_pedido, producto, cantidad, nota, estado, fecha
- **Tabla `menu`**: id, nombre_producto, precio, disponible

### Estados de pedidos

1. `pendiente` - Pedido recibido, esperando preparación
2. `preparacion` - En cocina
3. `completado` - Listo para entregar
4. `archivado` - Finalizado

## 📄 Licencia

Proyecto educativo/demostración.
