# 🐳 Guía de Docker - GastroIA

## 📋 Requisitos Previos

- Docker Desktop instalado y corriendo
- Docker Compose v2.0 o superior

## 🚀 Inicio Rápido

### 1. Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar las variables (especialmente OPENAI_API_KEY)
# En Windows PowerShell:
notepad .env
```

### 2. Levantar los servicios

```bash
# Construir y levantar todos los servicios
docker-compose up --build

# O en segundo plano (modo detached)
docker-compose up -d --build
```

### 3. Acceder a los servicios

Una vez que los contenedores estén corriendo:

- **Frontend (Tablero)**: http://localhost:8080
- **Chatbot IA**: http://localhost:7860
- **Base de datos**: localhost:3306

## 🏗️ Arquitectura Docker

```
┌─────────────────────────────────────────┐
│         Docker Compose                  │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────┐  ┌──────────┐  ┌───────┐ │
│  │   web    │  │ chatbot  │  │  db   │ │
│  │ (Apache) │  │ (Python) │  │(MySQL)│ │
│  │  :8080   │  │  :7860   │  │ :3306 │ │
│  └──────────┘  └──────────┘  └───────┘ │
│       │             │            │      │
│       └─────────────┴────────────┘      │
│          gastroia_network               │
└─────────────────────────────────────────┘
```

### Servicios

#### 🌐 web (Apache + PHP)
- **Imagen**: php:8.2-apache
- **Puerto**: 8080
- **Función**: Sirve el frontend y la API PHP
- **Volúmenes**: frontend/, backend/api/, backend/config/

#### 🤖 chatbot (Python + Gradio)
- **Imagen**: python:3.11-slim
- **Puerto**: 7860
- **Función**: Chatbot con IA para procesar pedidos
- **Volúmenes**: backend/chatbot/

#### 🗄️ db (MySQL)
- **Imagen**: mysql:8.0
- **Puerto**: 3306
- **Función**: Base de datos
- **Volumen persistente**: db_data

## 📝 Comandos Útiles

### Ver logs

```bash
# Todos los servicios
docker-compose logs -f

# Un servicio específico
docker-compose logs -f chatbot
docker-compose logs -f web
docker-compose logs -f db
```

### Gestión de servicios

```bash
# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes (⚠️ ELIMINA DATOS DE BD)
docker-compose down -v

# Reiniciar un servicio
docker-compose restart chatbot

# Ver estado de los servicios
docker-compose ps
```

### Acceder a los contenedores

```bash
# Shell del contenedor web
docker-compose exec web bash

# Shell del contenedor chatbot
docker-compose exec chatbot bash

# Acceder a MySQL
docker-compose exec db mysql -u restaurante_user -p
# Contraseña: restaurante_pass
```

### Reconstruir servicios

```bash
# Reconstruir todos los servicios
docker-compose build --no-cache

# Reconstruir un servicio específico
docker-compose build --no-cache chatbot

# Reconstruir y levantar
docker-compose up --build -d
```

## 🔧 Desarrollo

### Hot Reload

Los cambios en archivos se reflejan automáticamente gracias a los volúmenes:

- **Frontend (HTML/CSS/JS)**: Refresca el navegador
- **PHP**: Cambios inmediatos
- **Python**: Reinicia el contenedor
  ```bash
  docker-compose restart chatbot
  ```

### Variables de entorno

Edita el archivo `.env` para cambiar:
- Credenciales de base de datos
- Puertos de los servicios
- API keys

Después de cambiar `.env`:
```bash
docker-compose down
docker-compose up -d
```

## 🐛 Solución de Problemas

### La base de datos no se conecta

1. Verificar que el contenedor db esté corriendo:
   ```bash
   docker-compose ps
   ```

2. Ver logs de la base de datos:
   ```bash
   docker-compose logs db
   ```

3. Esperar a que el healthcheck pase:
   ```bash
   docker-compose ps
   # Debe mostrar "healthy" en db
   ```

### El chatbot no arranca

1. Verificar logs:
   ```bash
   docker-compose logs chatbot
   ```

2. Problemas comunes:
   - **OPENAI_API_KEY no configurado**: Edita `.env`
   - **Error de dependencias**: Reconstruir
     ```bash
     docker-compose build --no-cache chatbot
     ```

### Puerto en uso

Si un puerto está ocupado, edita `.env`:
```env
WEB_PORT=8081
CHATBOT_PORT=7861
```

### Resetear todo

```bash
# Detener y eliminar TODO (contenedores, volúmenes, redes)
docker-compose down -v

# Limpiar imágenes no usadas
docker system prune -a

# Volver a construir
docker-compose up --build
```

## 📊 Monitoreo

### Ver uso de recursos

```bash
# Estadísticas en tiempo real
docker stats

# Solo servicios de GastroIA
docker stats gastroia_web gastroia_chatbot gastroia_db
```

### Ver espacio en disco

```bash
# Espacio usado por Docker
docker system df

# Detalles de volúmenes
docker volume ls
docker volume inspect proyectoia_db_data
```

## 🔐 Seguridad

### Para producción:

1. **Cambiar credenciales por defecto** en `.env`
2. **No exponer puertos innecesarios**
3. **Usar secretos de Docker** en lugar de .env
4. **Configurar firewall**
5. **Habilitar SSL/TLS** con nginx reverse proxy

## 📦 Backup y Restauración

### Backup de la base de datos

```bash
# Crear backup
docker-compose exec db mysqldump -u root -p restaurante_db > backup.sql

# O con la contraseña en el comando
docker-compose exec db mysqldump -u root -proot_password restaurante_db > backup.sql
```

### Restaurar base de datos

```bash
# Restaurar desde backup
docker-compose exec -T db mysql -u root -proot_password restaurante_db < backup.sql
```

## 🎓 Siguiente Nivel

### Escalado

```bash
# Escalar el servicio web a 3 instancias
docker-compose up -d --scale web=3
```

### CI/CD

Integrar con GitHub Actions, GitLab CI, o Jenkins para:
- Builds automáticos
- Testing
- Deploy automático

## 📞 Ayuda

Si encuentras problemas:
1. Revisa los logs: `docker-compose logs`
2. Verifica configuración: `docker-compose config`
3. Consulta la documentación oficial: https://docs.docker.com/
