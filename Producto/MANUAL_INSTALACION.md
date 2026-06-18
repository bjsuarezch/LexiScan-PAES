# Manual de Instalación: LexiScan-PAES

LexiScan-PAES es una plataforma de estudio híbrida (Backend en FastAPI, Frontend en Ionic/Angular) enfocada en la preparación de la prueba de Comprensión Lectora PAES en Chile.

## Requisitos Previos

Asegúrate de tener instalados los siguientes programas antes de comenzar:
- **Git**: Para clonar el repositorio.
- **Docker y Docker Compose**: Para levantar la base de datos PostgreSQL.
- **Python 3.12.x**: Requerido por el backend (evitar versiones como 3.13 que pueden romper dependencias binarias).
- **Node.js (LTS)**: Requerido por el frontend (Angular/Ionic).
- **Ionic CLI** (Opcional pero recomendado): `npm install -g @ionic/cli`

---

## 1. Configuración de la Base de Datos

El proyecto utiliza PostgreSQL 15 empaquetado en un contenedor de Docker.

1. Abre una terminal y navega hasta la carpeta raíz del proyecto (`Producto/`).
2. Ejecuta el siguiente comando para levantar el contenedor de la base de datos:
   ```bash
   docker-compose up -d
   ```
   *Nota: Al iniciarse por primera vez, el contenedor ejecutará automáticamente el script `lexiscan_schema.sql` para crear la estructura inicial.*

---

## 2. Configuración del Backend (FastAPI)

1. Navega a la carpeta del backend:
   ```bash
   cd Producto/backend
   ```
2. Crea un entorno virtual usando Python 3.12:
   ```bash
   python -m venv venv
   ```
3. Activa el entorno virtual:
   - En **Windows**: `venv\Scripts\activate`
   - En **Mac/Linux**: `source venv/bin/activate`
4. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```
5. Configura las variables de entorno. Asegúrate de tener un archivo `.env` en la carpeta `backend/` con las credenciales de la API de Groq (`GROQ_API_KEY`). **Este archivo no debe subirse a ningún repositorio.**
6. Pobla la base de datos con la información inicial de temas y datos de prueba:
   ```bash
   python scripts/migrate_and_seed.py
   ```
   *(También puedes agregar temas adicionales corriendo `python scripts/add_themes.py`)*
7. Inicia el servidor de desarrollo:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   *El backend estará respondiendo en `http://localhost:8000`.*

---

## 3. Configuración del Frontend (Ionic/Angular)

1. Abre una nueva terminal y navega a la carpeta del frontend:
   ```bash
   cd Producto/LexiScan_Angular/lexi-scan
   ```
2. Instala las dependencias de Node:
   ```bash
   npm install
   ```
3. Inicia el servidor de desarrollo web:
   ```bash
   ionic serve
   ```
   *La aplicación se abrirá en tu navegador por defecto en `http://localhost:4200`.*

---

## 4. Pruebas y Tests

Para correr las pruebas de integración en el backend (requiere levantar un servidor separado en el puerto 8001):
```bash
cd Producto/backend
python tests/test_api.py
```

Para correr las pruebas del frontend (Jasmine/Karma):
```bash
cd Producto/LexiScan_Angular/lexi-scan
ng test
```

---

## 5. Compilación para Dispositivos Móviles (Android)

El proyecto utiliza Capacitor en lugar de Cordova. Para generar tu aplicación móvil nativa:
1. Compila los recursos web de la aplicación:
   ```bash
   npm run build
   ```
2. Sincroniza los archivos con la carpeta del proyecto Android:
   ```bash
   npx cap sync android
   ```
3. Abre Android Studio para compilar y generar el APK:
   ```bash
   npx cap open android
   ```
