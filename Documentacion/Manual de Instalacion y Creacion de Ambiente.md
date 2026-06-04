# Manual de Instalación y Creación de Ambiente - LexiScan PAES

Este manual detalla los pasos necesarios para instalar, configurar y levantar el entorno de desarrollo del sistema LexiScan PAES en una máquina local.

## Requisitos Previos

Para ejecutar el sistema, es necesario tener instalado el siguiente software:
1. **Python 3.10+** (Para el backend FastAPI).
2. **Node.js 18+ y npm** (Para el frontend Angular).
3. **PostgreSQL 15+** (Base de datos relacional).
4. **Git** (Para control de versiones).

---

## 1. Configuración de la Base de Datos (PostgreSQL)

1. Abre la herramienta de administración de PostgreSQL (pgAdmin o psql) y crea una nueva base de datos llamada `lexiscan_db`.
   ```sql
   CREATE DATABASE lexiscan_db;
   ```
2. Ejecuta el script SQL principal para inicializar el esquema de base de datos.
   ```bash
   psql -U postgres -d lexiscan_db -f "Documentacion/lexiscan_schema.sql"
   ```

---

## 2. Configuración del Backend (FastAPI)

1. Abre una terminal y navega al directorio del backend:
   ```bash
   cd Producto/backend
   ```
2. Crea un entorno virtual de Python:
   ```bash
   python -m venv venv
   ```
3. Activa el entorno virtual:
   - **En Windows:**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **En Linux/Mac:**
     ```bash
     source venv/bin/activate
     ```
4. Instala las dependencias del proyecto:
   ```bash
   pip install -r requirements.txt
   ```
5. Configura las variables de entorno. Crea un archivo `.env` en la carpeta `backend` con el siguiente contenido:
   ```env
   DATABASE_URL=postgresql://usuario:contraseña@localhost/lexiscan_db
   SECRET_KEY=tu_clave_secreta_aqui
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   GEMINI_API_KEY=tu_clave_de_api_de_google_gemini
   ```
6. (Opcional) Ejecuta el script de semilla para poblar datos base:
   ```bash
   python scripts/migrate_and_seed.py
   ```
7. Inicia el servidor backend:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   *El servidor estará disponible en `http://localhost:8000` y la documentación interactiva (Swagger UI) en `http://localhost:8000/docs`.*

---

## 3. Configuración del Frontend (Angular/Ionic)

1. Abre otra terminal y navega al directorio del frontend:
   ```bash
   cd Producto/LexiScan_Angular/lexi-scan
   ```
2. Instala las dependencias de Node.js:
   ```bash
   npm install
   ```
   *(Asegúrate de instalar globalmente el CLI de Angular/Ionic si no lo tienes: `npm install -g @angular/cli @ionic/cli`)*
3. Configura la conexión con el backend. Verifica que en `src/environments/environment.ts` la URL del API apunte a `http://localhost:8000`.
4. Inicia el servidor de desarrollo del frontend:
   ```bash
   npm run start
   # o alternativamente
   ionic serve
   ```
   *La aplicación estará disponible en tu navegador en `http://localhost:4200`.*

---

## 4. Solución de Problemas Frecuentes

- **Error de Conexión a Base de Datos (`ConnectionRefusedError`)**: Verifica que PostgreSQL esté corriendo en el puerto 5432 y que las credenciales en tu `.env` sean correctas.
- **Error de CORS en Frontend**: Asegúrate de que FastAPI en `main.py` tiene configurado el middleware `CORSMiddleware` permitiendo el origen `http://localhost:4200`.
- **Fallas en Integración de IA**: Revisa que la variable `GEMINI_API_KEY` esté configurada y sea válida.
