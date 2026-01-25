# Proyecto GastroIA

Sistema inteligente de gestión de pedidos para restaurantes con interfaz de chatbot basada en IA.

## 📋 Características

- 🤖 **Chatbot con IA** - Procesamiento de pedidos en lenguaje natural
- 🧠 **Clasificador Entrenado** - Modelo sklearn para detectar intenciones
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
│   │   ├── pedidos.controller.php  # Controlador de pedidos
│   │   ├── pedidos.service.php     # Lógica de negocio
│   │   └── pedidos.repository.php  # Acceso a BD
│   ├── chatbot/                # Servicio Python IA
│   │   ├── chatbot_ui.py       # Interfaz Gradio
│   │   ├── trained_classifier.py # Clasificador entrenado
│   │   ├── intent_classifier.py  # Clasificador por reglas
│   │   ├── order_processor.py  # Procesador de pedidos (BART)
│   │   ├── sentiment_analyzer.py # Análisis de sentimiento
│   │   ├── db_repository.py    # Conexión a BD
│   │   └── training_data/      # Datos de entrenamiento
│   └── config/                 # Configuración
├── database/
│   └── schemas/                # Esquemas SQL
└── docs/                       # Documentación
```

## 🚀 Instalación con Docker

### Requisitos
- Docker Desktop
- Docker Compose

### Inicio rápido
```bash
docker-compose up -d
```

### 🌐 Acceso a los servicios

Una vez iniciado Docker, podrás acceder a:

| Servicio | URL | Descripción |
|----------|-----|-------------|
| 📊 **Tablero de Pedidos** | [http://localhost:8080](http://localhost:8080) | Kanban para gestión de pedidos |
| 🤖 **Chatbot IA** | [http://localhost:7860](http://localhost:7860) | Interfaz de chatbot con IA |
| 💾 **Adminer (BD)** | [http://localhost:8081](http://localhost:8081) | Administrador de base de datos |

#### Credenciales de Adminer:
- **Servidor**: `db`
- **Usuario**: `restaurante_user`
- **Contraseña**: `restaurante_pass`
- **Base de datos**: `restaurante_db`

### Detener servicios
```bash
docker-compose down
```

## 🛠️ Instalación manual (sin Docker)

### Requisitos

- PHP 7.4+
- MySQL/MariaDB
- Python 3.8+

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
   - Copia `.env.example` a `.env`
   - Configura las credenciales de la base de datos

4. **Servidor web**
   - Coloca el proyecto en tu servidor web (Apache/Nginx)
   - Asegúrate de que PHP tenga acceso a MySQL

## 🎯 Uso

### Con Docker
Simplemente ejecuta `docker-compose up -d` y accede a las URLs indicadas arriba.

### Sin Docker

#### Iniciar el chatbot
```bash
cd backend/chatbot
python main.py
```
El chatbot estará disponible en `http://localhost:7860`

#### Acceder al tablero
Abre `frontend/public/index.html` en tu navegador o accede vía servidor web.

### API REST
- **GET** `backend/api/pedidos.controller.php` - Lista de pedidos activos
- **GET** `backend/api/pedidos.controller.php?mode=historial` - Pedidos archivados
- **POST** `backend/api/pedidos.controller.php` - Crear pedido
- **PUT** `backend/api/pedidos.controller.php` - Actualizar estado de pedido

## 🛠️ Tecnologías

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla ES6 Modules)
- **Backend API**: PHP 8.2, MySQL 8.0
- **Backend IA**: Python 3.11, Gradio, Hugging Face Transformers
- **OCR**: EasyOCR, TrOCR (Microsoft)
- **IA**: BART (Facebook), Zero-shot Classification
- **Base de datos**: MySQL 8.0
- **Contenedores**: Docker, Docker Compose

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
