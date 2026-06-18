# LexiScan-PAES 📚

Plataforma de preparación para la PAES de Comprensión Lectora con IA.

---

## ⚡ Requisitos previos

Instala esto antes de empezar:

| Herramienta | Versión mínima | Descarga |
|---|---|---|
| Python | **3.12.x** (no uses 3.13+) | [python.org](https://www.python.org/downloads/) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org/) |
| Docker Desktop | Cualquiera | [docker.com](https://www.docker.com/products/docker-desktop/) |

> ⚠️ **Python 3.12 obligatorio.** Las versiones 3.13+ rompen las dependencias binarias (psycopg2, bcrypt).

---

## 🚀 Cómo correr la app (3 terminales)

Necesitas **3 terminales abiertas al mismo tiempo**. Sigue el orden exacto.

---

### Terminal 1 — Base de datos

1. Abre Docker Desktop y espera a que diga **"Engine running"**.
2. Abre una terminal y ejecuta:

```bash
cd Producto
docker-compose up -d
```

✅ Listo cuando veas `lexiscan_db_container` al correr `docker ps`.

---

### Terminal 2 — Backend

**Primero: desbloquear PowerShell (solo la primera vez en Windows)**

Si al activar el entorno virtual te aparece el error `"la ejecución de scripts está deshabilitada"`, corre esto **antes** de cualquier otro comando:

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

Luego ejecuta todo esto en orden:

```bash
cd Producto/backend

# Crear entorno virtual con Python 3.12
py -3.12 -m venv venv

# Activar entorno virtual (Windows)
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Iniciar el servidor
$env:PYTHONIOENCODING="utf-8"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

✅ Listo cuando veas: `Uvicorn running on http://0.0.0.0:8000`

> ⚠️ **No cierres esta terminal.** El backend debe seguir corriendo mientras usas la app.

---

### Terminal 3 — Frontend

Abre **otra terminal nueva** y ejecuta:

```bash
cd Producto/LexiScan_Angular/lexi-scan
npm install
npm start
```

✅ Listo cuando veas: `http://localhost:4200/`

Abre tu navegador en: **http://localhost:4200**

> ⚠️ **No cierres esta terminal.** El frontend debe seguir corriendo.

---

## 🤖 Configurar la IA (una sola vez)

Necesitas una API Key de Groq (gratis en [console.groq.com](https://console.groq.com)).

1. En la pantalla de **login**, toca el ícono ⚙️ en el pie de página.
2. Pega tu API Key (`gsk_...`) y presiona **"Guardar API Key"**.
3. En el mismo panel, selecciona el modelo **`llama-3.3-70b-versatile`** y presiona **"Guardar configuración"**.

---

## 🗃️ Cargar datos de demostración (opcional)

Si quieres ver la app con datos de ejemplo ya cargados:

```bash
# Desde la carpeta Producto
docker exec -i lexiscan_db_container psql -U user_lexiscan -d lexiscan_db < datos_presentacion.sql
```

---

## 🐛 Errores comunes y soluciones

### ❌ `"la ejecución de scripts está deshabilitada"`

PowerShell bloquea los scripts por defecto en Windows. Solución rápida (solo afecta la terminal actual):

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

Luego vuelve a ejecutar `.\venv\Scripts\activate`.

---

### ❌ `UnicodeDecodeError: 'utf-8' codec can't decode byte...` al iniciar el backend

Este error ocurre en Windows cuando el sistema tiene configuración de idioma en español. Solución: **forzar UTF-8 antes de iniciar el servidor**:

```powershell
$env:PYTHONIOENCODING="utf-8"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Si el error persiste, también verifica que ni el usuario ni la contraseña de la base de datos tengan tildes o caracteres especiales en el archivo `.env`.

---

### ❌ El frontend carga pero no hace nada / pantallas en blanco

El backend no está corriendo. Verifica:
- La Terminal 2 (backend) sigue abierta y muestra `Uvicorn running`.
- No hay error en esa terminal.
- Si la cerraste, vuelve a abrirla y corre el servidor de nuevo.

---

### ❌ `Port 5432 already in use`

```bash
docker-compose down
docker-compose up -d
```

---

### ❌ `py -3.12` no funciona / Python no encontrado

Descarga Python 3.12 desde [python.org/downloads](https://www.python.org/downloads/releases/). Durante la instalación, marca **"Add Python to PATH"**.

---

## 📋 Resumen rápido

```
Terminal 1  →  cd Producto  →  docker-compose up -d
Terminal 2  →  cd Producto/backend  →  activar venv  →  uvicorn ...
Terminal 3  →  cd Producto/LexiScan_Angular/lexi-scan  →  npm start
```

Luego abre → **http://localhost:4200**
