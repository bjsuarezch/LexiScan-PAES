# LexiScan-PAES

Aplicación diseñada para que estudiantes puedan prepararse y sacar un excelente puntaje en la PAES de Comprensión Lectora. La aplicación proporciona un entorno interactivo con exámenes, seguimiento de habilidades y un gimnasio de práctica personalizado.

---

## 📋 Tabla de Contenidos

- [Descripción del Proyecto](#descripción-del-proyecto)
- [Funcionalidades](#funcionalidades)
- [Requisitos Previos](#requisitos-previos)
- [Instalación y Configuración](#instalación-y-configuración)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [API Endpoints](#api-endpoints)
- [Desarrollo](#desarrollo)
- [Troubleshooting](#troubleshooting)

---

## 📱 Descripción del Proyecto

LexiScan-PAES es una solución completa que combina:
- **Backend**: API REST en FastAPI con base de datos PostgreSQL
- **Frontend**: Aplicación móvil con Ionic (Angular)
- **Funcionalidades**: Autenticación, exámenes, seguimiento de progreso, habilidades personalizadas

### Stack Tecnológico
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: Ionic, Angular, TypeScript
- **Contenedorización**: Docker, Docker Compose
- **Pruebas**: Pytest

---

## ✨ Funcionalidades

### 1. **Autenticación de Usuarios**
   - Registro con validación de RUT y email
   - Login seguro con credenciales
   - Gestión de sesiones

### 2. **Exámenes PAES**
   - Banco de preguntas de comprensión lectora
   - Modo examen simulado
   - Retroalimentación instantánea
   - Corrección automática

### 3. **Seguimiento de Habilidades**
   - Análisis de desempeño por habilidad
   - Identificación de áreas débiles
   - Recomendaciones personalizadas

### 4. **Gimnasio de Práctica**
   - Ejercicios orientados por dificultad
   - Práctica temática
   - Estadísticas de progreso

### 5. **Dashboard del Estudiante**
   - Resumen de avance
   - Historial de exámenes
   - Metas y logros

---

## 🔧 Requisitos Previos

Asegúrate de tener instalado:

- **Docker** (versión 20.10 o superior) - [Descargar](https://www.docker.com/products/docker-desktop)
- **Docker Compose** (incluido en Docker Desktop)
- **Node.js** (versión 18.x o superior) - [Descargar](https://nodejs.org/)
- **npm** (viene con Node.js)
- **Ionic CLI** - Se instala con los comandos que siguen
- **Git** (opcional)

### Verificar instalaciones:
```bash
docker --version
docker-compose --version
node --version
npm --version
```

---

## 🚀 Instalación y Configuración

### **Paso 1: Clonar/Descargar el Proyecto**

```bash
cd c:\Users\yelia\LexiScan-PAES\LexiScan-PAES
```

### **Paso 2: Levantando la Base de Datos con Docker**

La base de datos PostgreSQL se levanta automáticamente con Docker Compose:

```bash
# Abrir Docker-Desktop y verificar que se vea Engine running dentro de docker-desktop
```


```bash
# Navegar a la carpeta Producto
cd Producto

# Levantar los contenedores (PostgreSQL)
docker-compose up -d
```

Este comando:
- ✅ Crea un contenedor de PostgreSQL
- ✅ Carga automáticamente el esquema desde `lexiscan_schema.sql`
- ✅ Expone la base de datos en `localhost:5432`

**Credenciales de la BD:**
- Usuario: `user_lexiscan`
- Contraseña: `password123`
- Base de datos: `lexiscan_db`
- Puerto: `5432`

Verificar que la base de datos está corriendo:
```bash
docker ps
```

Deberías ver algo como: `lexiscan_db_container`

---

### **Paso 3: Configurar e Instalar el Backend (FastAPI)**

```bash
# Desde la carpeta Producto
cd backend

# Crear un entorno virtual (opcional pero recomendado)
python -m venv venv

# Activar el entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
pip install pydantic[email]
```

**Dependencias del Backend:**
- FastAPI - Framework web
- Uvicorn - Servidor ASGI
- SQLAlchemy - ORM
- psycopg2-binary - Conector PostgreSQL

Verificar la instalación:
```bash
pip list
```

---

### **Paso 4: Ejecutar el Backend**

```bash
# Desde la carpeta backend (con el entorno virtual activado)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Salida esperada:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

El backend estará disponible en: **http://localhost:8000**

**Documentación interactiva:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

### **Paso 5: Instalar y Configurar el Frontend (Ionic/Angular)**

En **otra terminal**, navega a la carpeta del frontend:

```bash
cd Producto/LexiScan_Angular/lexi-scan

# Instalar dependencias
npm install

# Instalar Ionic CLI globalmente (si no lo tienes)
npm install -g @ionic/cli
```

Verificar instalación de Ionic:
```bash
ionic --version
```

---

### **Paso 6: Ejecutar el Frontend en Desarrollo**

```bash
# Desde Producto/LexiScan_Angular/lexi-scan
npm start
# o
ionic serve
```

Salida esperada:
```
[INFO] HTTP address: http://localhost:4200/
[INFO] DevServer listening on http://localhost:4200/
```

El frontend estará disponible en: **http://localhost:4200**

---

## 📁 Estructura del Proyecto

```
LexiScan-PAES/
├── README.md                           # Este archivo
├── Gestion/
│   └── Integrantes.txt                # Miembros del equipo
├── Producto/
│   ├── docker-compose.yml             # Configuración de Docker
│   ├── lexiscan_schema.sql            # Esquema de la base de datos
│   ├── poblar_datos.sql               # Script para datos de prueba
│   ├── tmp_hash.py                    # Utilidad de hashing
│   │
│   ├── backend/                       # API FastAPI
│   │   ├── main.py                    # Punto de entrada
│   │   ├── models.py                  # Modelos SQLAlchemy
│   │   ├── schemas.py                 # Esquemas Pydantic
│   │   ├── crud.py                    # Operaciones de BD
│   │   ├── database.py                # Configuración de BD
│   │   ├── requirements.txt           # Dependencias Python
│   │   └── tests/
│   │       └── test_api.py            # Pruebas unitarias
│   │
│   └── LexiScan_Angular/lexi-scan/    # App Ionic/Angular
│       ├── package.json               # Dependencias Node.js
│       ├── angular.json               # Configuración Angular
│       ├── ionic.config.json          # Configuración Ionic
│       ├── capacitor.config.ts        # Configuración Capacitor
│       └── src/
│           ├── app/
│           │   ├── app.module.ts      # Módulo principal
│           │   ├── app-routing.module.ts
│           │   ├── home/              # Página de inicio
│           │   ├── examen/            # Módulo de exámenes
│           │   ├── habilidades/       # Módulo de habilidades
│           │   ├── gym/               # Gimnasio de práctica
│           │   ├── tab1/, tab2/, tab3/# Tabs de navegación
│           │   ├── models/            # Modelos TypeScript
│           │   └── services/          # Servicios
│           ├── assets/                # Imágenes y recursos
│           ├── environments/          # Configuración por entorno
│           └── theme/                 # Estilos globales
```

---

## 🔌 API Endpoints

### Autenticación

**Registro de usuario:**
```
POST /register
Content-Type: application/json

{
  "rut": "12345678-9",
  "nombre_completo": "Juan Pérez",
  "email": "juan@example.com",
  "contrasena": "password123"
}
```

**Login:**
```
POST /login
Content-Type: application/json

{
  "rut": "12345678-9",
  "contrasena": "password123"
}
```

**Dashboard del usuario:**
```
GET /dashboard/{rut}
```

Prueba estos endpoints en: **http://localhost:8000/docs**

---

## 💻 Desarrollo

### Ejecutar Pruebas del Backend

```bash
cd Producto/backend

# Ejecutar todas las pruebas
pytest

# Con cobertura
pytest --cov
```

### Compilar para Android

```bash
cd Producto/LexiScan_Angular/lexi-scan

# Build de producción
npm run build
ionic capacitor build android
```

### Modo Debug en Chrome DevTools

```bash
# El navegador mostrará las DevTools automáticamente
ionic serve --devapp
```

---

## 🌍 Configuración de Entornos

### Backend - Variables de Entorno

Crear un archivo `.env` en `Producto/backend/`:

```
DATABASE_URL=postgresql://user_lexiscan:password123@localhost:5432/lexiscan_db
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=True
```

### Frontend - Configuración de URLs

Editar `Producto/LexiScan_Angular/lexi-scan/src/environments/environment.ts`:

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000'
};
```

---

## 📊 Gestión de Datos

### Poblar la Base de Datos con Datos de Prueba

```bash
# Ejecutar desde la carpeta Producto
docker exec -i lexiscan_db_container psql -U user_lexiscan -d lexiscan_db < poblar_datos.sql
```

### Ver Datos en la Base de Datos

```bash
# Conectar a PostgreSQL
docker exec -it lexiscan_db_container psql -U user_lexiscan -d lexiscan_db

# Comandos SQL útiles:
\dt                          # Listar tablas
SELECT * FROM usuarios;      # Ver usuarios
SELECT * FROM examen;        # Ver exámenes
\q                           # Salir
```

---

## 🛠️ Comandos Útiles

### Docker

```bash
# Ver logs de un contenedor
docker logs lexiscan_db_container -f

# Detener contenedores
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v

# Reiniciar la base de datos
docker-compose restart db
```

### Backend

```bash
# Recargar servidor (ctrl+C y)
uvicorn main:app --reload

# Especificar puerto diferente
uvicorn main:app --port 8001
```

### Frontend

```bash
# Limpiar cache y reinstalar
rm -r node_modules
npm install

# Build de producción
npm run build

# Ver dependencias
npm list
```

---

## 🐛 Troubleshooting

### **Error: "Port 5432 already in use"**
```bash
# Encuentra el contenedor que usa el puerto
docker ps -a | grep 5432

# Detén todos los contenedores
docker-compose down
```

### **Error: "Module not found" en Backend**
```bash
# Asegúrate de activar el entorno virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Reinstala dependencias
pip install -r requirements.txt
```

### **Error: "npm: command not found"**
```bash
# Instala Node.js desde: https://nodejs.org/
# Verifica la instalación
node --version
npm --version
```

### **La app no se conecta al backend**
1. Verifica que el backend está corriendo en `http://localhost:8000`
2. Revisa la URL en `src/environments/environment.ts`
3. Verifica el CORS en `backend/main.py`
4. Abre las DevTools: `F12` en el navegador

### **Base de datos sin datos de prueba**
```bash
# Ejecuta el script de población
docker exec -i lexiscan_db_container psql -U user_lexiscan -d lexiscan_db < poblar_datos.sql
```

---

## 📞 Resumen - Quick Start (5 minutos)

```bash
# Terminal 1: Base de datos
cd Producto
docker-compose up -d

# Terminal 2: Backend
cd Producto/backend
pip install -r requirements.txt
uvicorn main:app --reload

# Terminal 3: Frontend
cd Producto/LexiScan_Angular/lexi-scan
npm install
npm start
```

Luego accede a:
- **Frontend**: http://localhost:4200
- **Backend Docs**: http://localhost:8000/docs
- **Base de datos**: localhost:5432

---

## 📝 Notas

- El proyecto usa CORS habilitado para desarrollo (`allow_origins=['*']`)
- Las contraseñas se almacenan en texto plano (implementar bcrypt en producción)
- Los datos se persisten en volúmenes de Docker
- El servidor se recarga automáticamente con `--reload`

¡Bienvenido a LexiScan-PAES! 🎉 

