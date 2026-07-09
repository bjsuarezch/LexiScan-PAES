# Implementación CU10 (Recomendaciones) + CU8 (Impulsividad)

Documentación sobre la implementación de dos nuevos servicios en FastAPI para LexiScan PAES.

## Resumen

Se implementaron dos servicios especializados en la carpeta `backend/services/`:

1. **CU10 - Recomendaciones Personalizadas** (`recomendaciones.py`)
   - Endpoint: `GET /usuarios/{rut}/recomendaciones`
   - Identifica las 2 habilidades más débiles del usuario
   - Retorna los 3 errores más frecuentes en esas habilidades
   - Genera sugerencias de práctica para el Módulo GYM
   - Latencia objetivo: **< 2 segundos**

2. **CU8 - Alerta de Impulsividad** (`impulsividad.py`)
   - Endpoint: `GET /preguntas/{id_pregunta}/umbral-impulsividad`
   - Calcula umbral mínimo de lectura basado en cantidad de palabras
   - Fórmula: `umbral = max(2, round(palabras / 15, 1))`
   - Permite que frontend bloquee dinámicamente el botón "Responder"
   - Latencia objetivo: **< 500 ms**

---

## Estructura de Archivos

```
backend/
├── services/                          # NUEVO: módulos de servicios
│   ├── __init__.py                   # Paquete Python
│   ├── recomendaciones.py            # Servicio CU10
│   ├── impulsividad.py               # Servicio CU8
├── tests/
│   ├── test_servicios.py             # NUEVO: tests unitarios con pytest
│   ├── test_endpoints_integracion.py # NUEVO: tests de integración HTTP
│   └── test_api.py                   # Tests existentes
├── models.py                         # Modelos SQLAlchemy (sin cambios)
├── schemas.py                        # MODIFICADO: +3 esquemas Pydantic
├── main.py                           # MODIFICADO: +2 endpoints, +imports
└── crud.py, database.py              # Sin cambios
```

---

## Esquemas Pydantic Nuevos (schemas.py)

### 1. HabilidadDebolItem
```python
{
    "nombre": "Evaluar",
    "nivel_maestria": 25.5,
    "sugerencia": "Mejora tu dominio en 'Evaluar' - Nivel actual: 25.5%"
}
```

### 2. ErrorFrecuenteItem
```python
{
    "id_pregunta": 42,
    "enunciado": "¿Cuál es el tema principal del texto?",
    "veces_fallada": 5
}
```

### 3. RecomendacionesResponse
```json
{
    "rut": "12345678-9",
    "habilidades_debiles": [
        {"nombre": "Evaluar", "nivel_maestria": 25.5, "sugerencia": "..."},
        {"nombre": "Vocabulario", "nivel_maestria": 35.0, "sugerencia": "..."}
    ],
    "errores_frecuentes": [
        {"id_pregunta": 42, "enunciado": "...", "veces_fallada": 5},
        {"id_pregunta": 43, "enunciado": "...", "veces_fallada": 4},
        {"id_pregunta": 44, "enunciado": "...", "veces_fallada": 3}
    ],
    "proxima_practica_sugerida": "Enfócate en el Módulo GYM: 'Evaluar'..."
}
```

### 4. UmbralImpulsividadResponse
```json
{
    "id_pregunta": 42,
    "num_palabras": 87,
    "umbral_segundos": 5.8,
    "mensaje_usuario": "Lee detenidamente. Espera 5.8 segundos antes de responder."
}
```

---

## Endpoints Nuevos

### 1. GET /usuarios/{rut}/recomendaciones

**Descripción**: CU10 - Obtiene recomendaciones personalizadas

**Parámetros**:
- `rut` (path): RUT del usuario (e.g., '12345678-9')

**Respuestas**:
- `200`: RecomendacionesResponse (éxito)
- `404`: Usuario no encontrado
- `500`: Error en base de datos

**Latencia**: < 2 segundos

**Ejemplo**:
```bash
curl -X GET "http://localhost:8001/usuarios/12345678-9/recomendaciones"
```

---

### 2. GET /preguntas/{id_pregunta}/umbral-impulsividad

**Descripción**: CU8 - Calcula umbral mínimo de lectura

**Parámetros**:
- `id_pregunta` (path): ID de la pregunta en tabla preguntas_ia

**Respuestas**:
- `200`: UmbralImpulsividadResponse (éxito)
- `404`: Pregunta no encontrada o no activa
- `500`: Error en base de datos

**Latencia**: < 500 ms

**Ejemplo**:
```bash
curl -X GET "http://localhost:8001/preguntas/42/umbral-impulsividad"
```

---

## Ejecutar Tests

### Tests Unitarios (con pytest)

Requiere: Python 3.8+, pytest, sqlalchemy

```bash
# Instalar dependencias
pip install pytest pytest-asyncio

# Ejecutar todos los tests unitarios
pytest backend/tests/test_servicios.py -v

# Ejecutar solo tests de contar_palabras
pytest backend/tests/test_servicios.py::TestContarPalabras -v

# Ejecutar con cobertura
pytest backend/tests/test_servicios.py --cov=services --cov-report=html
```

**Coverage esperado**: ~95% de las funciones de servicios

---

### Tests de Integración (HTTP)

Requiere: FastAPI server corriendo + BD PostgreSQL

```bash
# Terminal 1: Iniciar servidor FastAPI
cd backend
uvicorn main:app --host 127.0.0.1 --port 8001

# Terminal 2: Ejecutar tests de integración
python backend/tests/test_endpoints_integracion.py
```

**Tests ejecutados**:
- ✓ Recomendaciones con usuario válido (200)
- ✓ Recomendaciones con usuario inválido (404)
- ✓ Umbral con pregunta válida (200)
- ✓ Umbral con pregunta inválida (404)
- ✓ Validación de latencia recomendaciones (< 2s)
- ✓ Validación de latencia umbral (< 500ms)

---

## Validación en Swagger

Una vez que el servidor esté corriendo:

```
http://localhost:8001/docs
```

Buscar en la lista de endpoints:
- `GET /usuarios/{rut}/recomendaciones` (etiqueta: Recomendaciones (CU10))
- `GET /preguntas/{id_pregunta}/umbral-impulsividad` (etiqueta: Impulsividad (CU8))

Puedes ejecutar los endpoints directamente desde Swagger UI.

---

## Índices de Base de Datos Utilizados

Los endpoints aprovechan los índices existentes en PostgreSQL:

| Índice | Tabla | Columnas | Propósito |
|--------|-------|----------|-----------|
| `idx_habilidades_nivel` | historial_habilidades | nivel_maestria | Obtener habilidades ordenadas por maestría |
| `idx_errores_usuario` | errores_favoritos | rut_usuario | Filtrar errores por usuario |
| `idx_errores_veces` | errores_favoritos | veces_fallada DESC | Ordenar por frecuencia |
| `idx_preguntas_ia_habilidad` | preguntas_ia | id_habilidad | Filtrar preguntas por habilidad |

**Recomendación**: Verificar que estos índices existen:
```sql
-- PostgreSQL
SELECT * FROM pg_indexes 
WHERE indexname IN (
    'idx_habilidades_nivel',
    'idx_errores_usuario',
    'idx_errores_veces',
    'idx_preguntas_ia_habilidad'
);
```

---

## Funciones en Servicios

### backend/services/recomendaciones.py

```python
async def get_habilidades_mas_debiles(rut: str, session: Session) -> List[Tuple[str, float]]
    # Retorna: [(nombre_habilidad, nivel_maestria), ...]
    # Máximo 2 items, ordenados ascendente por nivel_maestria

async def get_errores_frecuentes(rut: str, id_habilidades: List[int], session: Session, limit: int = 3) -> List[Dict]
    # Retorna: [{"id_pregunta", "enunciado", "veces_fallada", ...}, ...]
    # Ordenado descendente por veces_fallada

async def generar_respuesta_recomendaciones(rut: str, session: Session) -> Dict
    # Retorna: RecomendacionesResponse (objeto completo)
    # Lógica: combina ambas funciones + genera sugerencias
```

### backend/services/impulsividad.py

```python
def contar_palabras(texto_inedito: str) -> int
    # Retorna: cantidad de palabras (maneja None, vacío, espacios múltiples)

async def calcular_umbral_tiempo_minimo(id_pregunta: int, session: Session) -> Dict
    # Retorna: UmbralImpulsividadResponse
    # Lógica: extrae texto_inedito, cuenta palabras, calcula umbral
```

---

## Fórmulas y Lógica

### Umbral de Impulsividad (CU8)

```
num_palabras = contar_palabras(texto_inedito)
umbral_segundos = max(2.0, round(num_palabras / 15, 1))
```

**Ejemplos**:
- 15 palabras → umbral = max(2, round(1.0, 1)) = 2.0s
- 45 palabras → umbral = max(2, round(3.0, 1)) = 3.0s
- 75 palabras → umbral = max(2, round(5.0, 1)) = 5.0s
- 150 palabras → umbral = max(2, round(10.0, 1)) = 10.0s

**Justificación**: Aproximadamente 1 segundo por cada 15 palabras (~60 palabras/minuto de lectura comprensiva). Mínimo 2 segundos para evitar bloqueos innecesarios.

---

### Identificación de Habilidades Débiles (CU10)

Basado en tabla `historial_habilidades`:
- Obtiene todas las habilidades del usuario
- Ordena por `nivel_maestria ASC`
- Retorna TOP 2

**Ejemplo**:
```
Usuario tiene 6 habilidades con estos niveles:
- Evaluar: 25.5% ← #1 (más débil)
- Vocabulario: 35.0% ← #2
- Localizar: 65.0%
- Interpretar: 70.5%
- Lectura_Critica: 80.0%
- Tipos_de_Texto: 90.0%

Se retornan: [(Evaluar, 25.5), (Vocabulario, 35.0)]
```

---

### Identificación de Errores Frecuentes (CU10)

Basado en tabla `errores_favoritos`:
- Filtra por usuario y habilidades específicas
- Ordena por `veces_fallada DESC`
- Retorna TOP 3

**Ejemplo**:
```
Usuario tiene estos errores en 'Evaluar':
- Pregunta 42: fallada 5 veces ← #1
- Pregunta 43: fallada 4 veces ← #2
- Pregunta 44: fallada 3 veces ← #3
- Pregunta 45: fallada 2 veces

Se retornan: [err_42, err_43, err_44]
```

---

## Restricciones Técnicas

✓ **Asincronía**: Todas las funciones son `async def` para no bloquear el event loop
✓ **Latencia**: CU10 < 2s, CU8 < 500ms (ambas validadas con índices BD)
✓ **Manejo de errores**: Try-catch con logging, HTTPExceptions en endpoints
✓ **Validación de entrada**: RUT y ID pregunta validados antes de consultas BD
✓ **Sin efectos secundarios**: No modifica datos, solo lectura
✓ **Documentación**: Docstrings Google-style para FastAPI autodocs

---

## Troubleshooting

### Error: "módulo 'services' no encontrado"

**Causa**: Python no reconoce `services/` como paquete

**Solución**: Verificar que `backend/services/__init__.py` existe:
```bash
ls -la backend/services/__init__.py
```

Si no existe, crear:
```bash
touch backend/services/__init__.py
```

### Error: "Usuario no encontrado" (404)

**Causa**: El RUT no existe en tabla `usuarios`

**Solución**: 
- Primero registrar un usuario: `POST /register`
- O usar un RUT que ya exista en la BD

### Error: "Pregunta no encontrada" (404)

**Causa**: El ID de pregunta no existe en tabla `preguntas_ia`

**Solución**:
- Generar preguntas primero: `POST /generar-preguntas`
- O consultar qué preguntas existen: `GET /habilidades/{habilidad}`

### Latencia alta (> 2s)

**Causa 1**: Índices no existen
```sql
-- Verificar
SELECT * FROM pg_indexes WHERE tablename = 'errores_favoritos';

-- Crear si falta
CREATE INDEX idx_errores_usuario ON errores_favoritos(rut_usuario);
CREATE INDEX idx_errores_veces ON errores_favoritos(veces_fallada DESC);
```

**Causa 2**: BD tiene muchos registros sin VACUUM
```sql
-- Optimizar
VACUUM ANALYZE historial_habilidades;
VACUUM ANALYZE errores_favoritos;
```

---

## Métricas y Monitoreo

Para monitorear rendimiento, revisar logs:

```bash
# Ver logs de FastAPI (stdout)
uvicorn main:app --host 127.0.0.1 --port 8001 --log-level info

# Buscar tiempos de ejecución
grep "Umbral calculado" backend.log
grep "Recomendaciones generadas" backend.log
```

Las funciones logean tiempos de ejecución con `logging.info()`.

---

## Próximos Pasos

1. **Integración Frontend**:
   - Módulo GYM utiliza `/usuarios/{rut}/recomendaciones` para mostrar sugerencias
   - Component de pregunta utiliza `/preguntas/{id}/umbral-impulsividad` para bloquear botón

2. **Analytics**:
   - Considerar agregar tabla `logs_recomendaciones` para tracking
   - Medir qué prácticas sugieren vs cuáles realiza el usuario

3. **Optimizaciones Futuras**:
   - Cachear recomendaciones por 15 minutos (Redis)
   - Paginación si usuario tiene > 50 errores
   - Filtro por habilidad específica en `/recomendaciones?habilidad=Evaluar`

---

## Autores y Versionado

- **Creación**: Mayo 12, 2026
- **Versión**: 1.0.0
- **Stack**: FastAPI 0.104+, SQLAlchemy 2.0+, Python 3.9+

---

## Contacto y Soporte

Para preguntas sobre implementación, revisar:
- Docstrings en `services/recomendaciones.py`
- Docstrings en `services/impulsividad.py`
- Tests unitarios: `tests/test_servicios.py`
- Tests integración: `tests/test_endpoints_integracion.py`
