# -*- coding: utf-8 -*-
import os
import sys
import json
from pathlib import Path

# Forzar UTF-8 en stdout/stderr para evitar errores en Windows con codepage CP1252/CP850
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


import requests
from dotenv import load_dotenv  # <--- NUEVO
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from pydantic import BaseModel

import crud, database, models, schemas
from services.recomendaciones import generar_respuesta_recomendaciones
from services.impulsividad import calcular_umbral_tiempo_minimo

class ConfigAPI(BaseModel):
    api_key: str
    modelo: str
    
class PreguntaEvaluacion(BaseModel):
    enunciado: str
    respuesta_usuario: str
    respuesta_correcta: str
    justificacion: str  # <--- Agregado este campo

# 1. Definir la ruta absoluta al archivo .env
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / ".env"

# 2. Intentar cargar el archivo y verificar si tuvo éxito
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"--- DEBUG: Archivo .env encontrado en: {env_path} ---")
else:
    print(f"--- ERROR: No se encontró el archivo .env en: {env_path} ---")

# 3. Obtener la variable
api_key = os.getenv('GEMINI_API_KEY')

# 4. Verificación de seguridad antes de imprimir/usar
if api_key is not None:
    print(f"DEBUG: API KEY CARGADA: {api_key[:5]}...")
else:
    print("DEBUG: La variable GEMINI_API_KEY es None.")
    # Listar todas las variables cargadas para ver si hay errores de tipeo
    print(f"Variables de entorno actuales: {list(os.environ.keys())[-5:]}")

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title='LexiScan API', version='0.1.0')

origins = [
    "http://localhost:4200", 
    "http://localhost:8100",
    "http://127.0.0.1:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

def fix_sequences(db: Session):
    # Esto busca el valor máximo y actualiza el contador de la secuencia
    db.execute(text("SELECT setval('historial_habilidades_id_progreso_seq', COALESCE((SELECT MAX(id_progreso) FROM historial_habilidades), 1))"))
    db.commit()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
        fix_sequences(db)
    finally:
        db.close()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
GEMINI_API_KEY_ENV = 'GEMINI_API_KEY'

current_config = {
    "api_key": os.getenv("GROQ_API_KEY", ""),
    "modelo": "llama-3.1-70b-versatile"
}

@app.get("/health")
def health_check():
    """Endpoint liviano para verificar que el backend está en línea. No accede a la BD."""
    return {"status": "ok", "version": "0.1.0"}

@app.post("/configurar-ia")
def configurar_ia(config: ConfigAPI, db: Session = Depends(get_db)):
    if not config.api_key.startswith("gsk_"):
        raise HTTPException(status_code=400, detail="API Key de Groq inválida")
    
    current_config["api_key"] = config.api_key
    current_config["modelo"] = config.modelo

    # Opcional: Guardar en BD para que crud.get_configuracion funcione
    crud.set_configuracion(db, 'GROQ_API_KEY', config.api_key)
    crud.set_configuracion(db, 'GROQ_MODEL', config.modelo)
    
    return {"status": "Configuración actualizada"}

@app.get("/modelos-disponibles")
def listar_modelos():
    """Consulta a Groq los modelos que el compañero tiene permitidos con su llave"""
    if not current_config["api_key"]:
        raise HTTPException(status_code=400, detail="Primero debes configurar una API Key")
        
    url = "https://api.groq.com/openai/v1/models"
    headers = {
        "Authorization": f"Bearer {current_config['api_key']}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="No se pudieron obtener los modelos")
        
    return response.json()

VALID_HABILIDADES = {
    'localizar': 'Localizar',
    'interpretar': 'Interpretar',
    'evaluar': 'Evaluar',
    'lectura critica': 'Lectura Crítica',
    'vocabulario': 'Vocabulario',
    'tipos de texto': 'Tipos de Texto',
}

DB_HABILIDADES = {
    'Localizar': 'Localizar',
    'Interpretar': 'Interpretar',
    'Evaluar': 'Evaluar',
    'Lectura Crítica': 'Lectura_Critica',
    'Vocabulario': 'Vocabulario',
    'Tipos de Texto': 'Tipos_de_Texto',
}


def normalize_habilidad_type(value: str) -> str:
    if not value:
        return ''
    normalized = value.strip().lower()
    normalized = normalized.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    normalized = normalized.replace('-', ' ').replace('_', ' ').strip()
    return VALID_HABILIDADES.get(normalized, '')

def normalize_habilidad_db_name(value: str) -> str:
    if not value:
        return ''
    return DB_HABILIDADES.get(value, '')


def build_system_prompt() -> str:
    return (
        'Eres la Profesora Sinclair, una docente experta en la PAES de Competencia Lectora chilena. ' 
        'Respondes con un tono pedagógico, cercano y profesional, cuidando la precisión académica. '
        'Tu función es diseñar material de evaluación riguroso, claro y útil para estudiantes que se preparan para la PAES. '
        'Debes responder ÚNICAMENTE con el objeto JSON válido solicitado, sin texto introductorio ni de cierre, y sin bloques de código markdown (como ```json).'
    )

# Rotación de 15 formatos de texto (narrativo / expositivo / argumentativo)
# según los tipos de texto que aparecen en la PAES de Compresión Lectora
_FORMATO_ROTACION = [
    {"tipo": "narrativo",      "subtipo": "fragmento de cuento clásico",              "descripcion": "Fragmento de un cuento clásico con narrador, personajes y conflicto central."},
    {"tipo": "expositivo",     "subtipo": "artículo de divulgación científica",        "descripcion": "Artículo de divulgación científica con datos, conceptos y explicaciones claras."},
    {"tipo": "argumentativo",  "subtipo": "columna de opinión",                        "descripcion": "Columna de opinión donde el autor defiende una tesis con argumentos y ejemplos."},
    {"tipo": "narrativo",      "subtipo": "fragmento de novela",                       "descripcion": "Fragmento de novela con descripción de ambiente, pensamiento interno y desarrollo de personaje."},
    {"tipo": "expositivo",     "subtipo": "artículo de divulgación científica",        "descripcion": "Artículo de divulgación científica con comparaciones, ejemplos y datos."},
    {"tipo": "argumentativo",  "subtipo": "editorial de periódico",                    "descripcion": "Editorial periodístico que expone la postura de un medio ante un hecho de actualidad."},
    {"tipo": "narrativo",      "subtipo": "fragmento de mito",                         "descripcion": "Fragmento de un mito con dioses o héroes, narrado en tercera persona y con lenguaje elevado."},
    {"tipo": "expositivo",     "subtipo": "capítulo de manual educativo",              "descripcion": "Capítulo de manual con definiciones, clasificaciones y ejemplos didácticos."},
    {"tipo": "argumentativo",  "subtipo": "carta al director",                         "descripcion": "Carta al director de un medio donde un ciudadano argumenta una postura personal."},
    {"tipo": "narrativo",      "subtipo": "fragmento de leyenda",                      "descripcion": "Fragmento de una leyenda popular con elementos sobrenaturales y moraleja implícita."},
    {"tipo": "expositivo",     "subtipo": "infografía textualizada",                  "descripcion": "Texto que describe datos visuales como si fuera el contenido de una infografía (incluye dato_clave y grafico_barra)."},
    {"tipo": "argumentativo",  "subtipo": "crítica de arte o cine",                   "descripcion": "Crítica de una obra artística o película donde el crítico evalúa con criterios estéticos."},
    {"tipo": "narrativo",      "subtipo": "fragmento de crónica literaria",            "descripcion": "Crónica literaria que narra un evento real con recursos narrativos y punto de vista personal."},
    {"tipo": "expositivo",     "subtipo": "biografía",                                "descripcion": "Biografía que expone de forma ordenada los hitos de la vida de una persona relevante."},
    {"tipo": "argumentativo",  "subtipo": "ensayo filosófico o cultural",             "descripcion": "Ensayo que reflexiona sobre una idea filosófica o cultural con tesis, argumentos y conclusión."},
]


def _get_formato_rotacion(seed: int) -> dict:
    """Devuelve el formato de texto según posición en la rotación."""
    return _FORMATO_ROTACION[seed % len(_FORMATO_ROTACION)]


def build_user_prompt(habilidad: str, tema: str) -> str:
    import random

    tema_instruccion = (
        f"El tema central del texto debe ser sobre: '{tema}'."
        if tema
        else "Elige un tema educativo y muy interesante al azar."
    )

    # Semilla aleatoria para: (a) variedad de ángulo temático y (b) rotación de formato
    variante_seed = random.randint(0, 9999)
    subtemas_variantes = [
        "un aspecto poco conocido",
        "una perspectiva histórica",
        "implicancias actuales",
        "datos sorprendentes",
        "un enfoque científico",
        "una dimensión social",
        "consecuencias futuras",
        "una comparación internacional",
    ]
    angulo = subtemas_variantes[variante_seed % len(subtemas_variantes)]
    fmt = _get_formato_rotacion(variante_seed)

    # ---- Instrucciones específicas por habilidad ----
    if habilidad in ("Vocabulario",):
        num_preguntas = 4
        instruccion_habilidad = (
            "HABILIDAD: Vocabulario.\n"
            "Las 4 preguntas DEBEN evaluar el significado de palabras específicas del texto.\n"
            "Formatos aceptados para las preguntas:\n"
            "  - '¿Qué significa la palabra X en el contexto del texto?' con 4 opciones de significado.\n"
            "  - '¿Con qué expresión se puede reemplazar X sin cambiar el sentido?' con 4 opciones.\n"
            "  - '¿En qué sentido se usa la palabra X en el segundo párrafo?' con 4 opciones.\n"
            "PROHIBIDO: No hagas preguntas sobre el tema general, la idea principal ni la estructura del texto.\n"
            "Cada pregunta debe citar la palabra exacta del texto entre comillas."
        )
    elif habilidad in ("Tipos_de_Texto", "Tipos de Texto"):
        num_preguntas = 1
        instruccion_habilidad = (
            "HABILIDAD: Tipos de Texto.\n"
            "DEBES generar EXACTAMENTE 1 pregunta que evalúe la identificación del tipo de texto.\n"
            f"El texto que generes será de tipo '{fmt['tipo']}' ({fmt['subtipo']}).\n"
            "La pregunta DEBE ser: '¿Qué tipo de texto es el que acabas de leer?'\n"
            "Las 4 alternativas deben ser los 4 tipos: Narrativo, Expositivo, Argumentativo, Descriptivo.\n"
            f"La respuesta correcta es: {fmt['tipo'].capitalize()}.\n"
            "La justificacion_cot debe explicar los rasgos del texto que evidencian ese tipo."
        )
    elif habilidad == "Localizar":
        num_preguntas = 4
        instruccion_habilidad = (
            "HABILIDAD: Localizar información.\n"
            "Las 4 preguntas DEBEN requerir que el estudiante encuentre información EXPLÍCITA en el texto.\n"
            "REQUISITO CRÍTICO: La respuesta correcta debe poder ser copiada literalmente o parafraseada directamente del texto, sin necesidad de inferencia.\n"
            "Formatos de pregunta aceptados:\n"
            "  - 'Según el texto, ¿cuál es [dato]?'\n"
            "  - '¿Qué menciona el texto sobre [aspecto]?'\n"
            "  - 'De acuerdo al texto, ¿cuándo/dónde/quién [acción]?'\n"
            "  - '¿Cuál de las siguientes afirmaciones aparece explícitamente en el texto?'\n"
            "Las 3 alternativas incorrectas deben ser plausibles pero NO aparecer en el texto.\n"
            "PROHIBIDO: No hagas preguntas que requieran inferencia, interpretación o juicio crítico.\n"
            "PROHIBIDO: No hagas preguntas sobre la idea principal, el propósito del autor, el tipo de texto ni el significado de palabras."
        )
    elif habilidad == "Interpretar":
        num_preguntas = 4
        instruccion_habilidad = (
            "HABILIDAD: Interpretar e integrar.\n"
            "Las 4 preguntas deben requerir que el estudiante DEDUZCA o INFIERA información que NO aparece explícita en el texto.\n"
            "Sub-tipos de pregunta que DEBES incluir (usa los 4 sub-tipos distintos):\n"
            "  1. Idea principal: '¿Cuál es la idea central que plantea el texto?' (síntesis global, no copiable del texto)\n"
            "  2. Inferencia lógica: '¿Qué se puede concluir / inferir a partir del texto?'\n"
            "  3. Relación entre ideas: '¿Qué relación existe entre [concepto A] y [concepto B] según el texto?' (causal, temporal, contraste)\n"
            "  4. Referente implícito: '¿A qué se refiere el autor cuando menciona \"[frase literal del texto]\"?'\n"
            "Las respuestas correctas NO deben aparecer literales en el texto, sino deducirse de él.\n"
            "PROHIBIDO: No hagas preguntas donde la respuesta esté copiada del texto (eso es Localizar).\n"
            "PROHIBIDO: No hagas preguntas de juicio externo sobre el propósito del autor ni sobre la validez del argumento (eso es Evaluar)."
        )
    elif habilidad == "Evaluar":
        num_preguntas = 4
        instruccion_habilidad = (
            "HABILIDAD: Evaluar y reflexionar.\n"
            "Las 4 preguntas deben pedir al estudiante que JUZGUE o EVALÚE el texto DESDE AFUERA, usando criterios externos al contenido del texto.\n"
            "Sub-tipos de pregunta que DEBES incluir (usa los 4 sub-tipos distintos):\n"
            "  1. Propósito comunicativo: '¿Cuál es el propósito del texto?' con opciones como informar/persuadir/entretener/instruir.\n"
            "  2. Audiencia: '¿A qué tipo de lector va dirigido principalmente el texto?' (deducible del tono, vocabulario y formato).\n"
            "  3. Función estructural: '¿Qué función cumple el párrafo [N] dentro del texto?' con opciones como introducir/ejemplificar/refutar/concluir.\n"
            "  4. Estrategia retórica: '¿Qué recurso utiliza el autor para apoyar su argumento?' con opciones como estadísticas/anécdotas/citas de autoridad/comparaciones.\n"
            "Las respuestas correctas implican un juicio META sobre el texto, no sobre el contenido temático.\n"
            "PROHIBIDO: No hagas preguntas de comprensión del contenido (eso es Localizar o Interpretar).\n"
            "PROHIBIDO: No hagas preguntas sobre el significado de palabras (eso es Vocabulario)."
        )
    elif habilidad in ("Lectura_Critica", "Lectura Crítica"):
        num_preguntas = 4
        instruccion_habilidad = (
            "HABILIDAD: Lectura Crítica.\n"
            "Las 4 preguntas deben situar al estudiante FUERA del texto para cuestionar su discurso, ideología o supuestos implícitos.\n"
            "Sub-tipos de pregunta que DEBES incluir (usa los 4 sub-tipos distintos):\n"
            "  1. Supuesto implícito: '¿Qué supuesto o creencia implícita subyace en el argumento del texto?' (idea que el texto asume como verdadera sin declararla).\n"
            "  2. Postura del enunciador: '¿Qué postura ideológica o valórica adopta el enunciador del texto frente al tema?' con opciones contrastantes.\n"
            "  3. Contraejemplo crítico: '¿Cuál de las siguientes afirmaciones debilitaría el argumento principal del texto?'\n"
            "  4. Sesgo por omisión: '¿Qué perspectiva, grupo o información queda excluida o silenciada en el texto?'\n"
            "Las respuestas correctas exigen que el estudiante reconozca la POSICIÓN DEL TEXTO ante la realidad, no solo entender su contenido.\n"
            "PROHIBIDO: No hagas preguntas de comprensión literal ni de vocabulario.\n"
            "PROHIBIDO: No repitas el estilo de Evaluar (propósito/función/estrategia retórica). Lectura Crítica va más allá: exige cuestionar el discurso mismo."
        )
    else:
        num_preguntas = 4
        instruccion_habilidad = (
            f"HABILIDAD: {habilidad}.\n"
            "Las preguntas deben evaluar rigurosamente esta habilidad según los estándares PAES."
        )

    # ---- Instrucciones de formato de texto (rotación) ----
    # Para Vocabulario y Lectura Crítica no forzamos un formato narrativo específico,
    # pero sí indicamos el ángulo temático para variedad
    if habilidad in ("Tipos_de_Texto", "Tipos de Texto"):
        formato_instruccion = (
            f"FORMATO DEL TEXTO: Debes escribir un '{fmt['subtipo']}' (texto {fmt['tipo']}).\n"
            f"Descripción del formato: {fmt['descripcion']}\n"
        )
    else:
        formato_instruccion = (
            f"FORMATO DEL TEXTO [VARIANTE #{variante_seed}]: Escribe un '{fmt['subtipo']}' (texto {fmt['tipo']}).\n"
            f"Descripción: {fmt['descripcion']}\n"
            f"Ángulo del tema: {angulo}.\n"
            "NO repitas formatos ni ángulos de sesiones anteriores.\n"
        )

    return (
        f"{formato_instruccion}\n"
        f"{instruccion_habilidad}\n\n"
        f"{tema_instruccion}\n\n"
        "Tu tarea: genera un texto inédito de al menos 2 párrafos en el formato indicado.\n\n"
        f"CANTIDAD DE PREGUNTAS: {num_preguntas}. "
        "Basándote EXCLUSIVAMENTE en ese texto, genera las preguntas indicadas.\n\n"
        "Devuelve únicamente un JSON válido con esta estructura:\n"
        "{\n"
        "  \"tipo_habilidad\": \"string\",\n"
        "  \"texto_inedito\": [\n"
        "     {\"tipo\": \"parrafo\", \"contenido\": \"...\"},\n"
        "     {\"tipo\": \"dato_clave\", \"contenido\": \"...\"},\n"
        "     {\"tipo\": \"grafico_barra\", \"titulo\": \"...\", \"datos\": [{\"etiqueta\": \"...\", \"valor\": 80}]},\n"
        "     {\"tipo\": \"imagen\", \"concepto\": \"keyword en ingles para imagen relacionada\"}\n"
        "  ],\n"
        "  \"preguntas\": [\n"
        "    {\"enunciado\": \"...\", \"alternativas\": {\"A\": \"...\", \"B\": \"...\", \"C\": \"...\", \"D\": \"...\"},"
        " \"respuesta_correcta\": \"A\", \"justificacion_cot\": \"...\"}\n"
        "  ]\n"
        "}\n"
        "REGLAS DE ORO:\n"
        "1. 'texto_inedito' DEBE ser un arreglo con bloques. Usa varios 'parrafo'. "
        "Si el formato lo permite, añade 'dato_clave' y/o 'grafico_barra'. SIEMPRE incluye 'imagen'.\n"
        "2. Las preguntas deben ser imposibles de responder sin leer el texto.\n"
        "3. NO generes preguntas genéricas de cultura general."
    )





def parse_gemini_output(raw_text: str | dict | list) -> dict:
    if isinstance(raw_text, dict):
        return raw_text
    if isinstance(raw_text, list):
        return {'resultados': raw_text}
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        start = raw_text.find('{')
        end = raw_text.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(raw_text[start:end + 1])
            except json.JSONDecodeError:
                pass
        raise





def build_evaluation_prompt(tipo_habilidad: str, preguntas: list[dict]) -> str:
    prompt_lines = [
        'Eres la Profesora Sinclair. Tu misión es dar retroalimentación breve y amigable al estudiante.',
        'Para cada respuesta, explica de forma directa por qué la correcta es la que es y por qué la del usuario (si es incorrecta) falla.',
        'NO uses formatos estructurados ni listas como "1. Premisa, 2. Análisis, 3. Conclusión". Escribe un solo párrafo conversacional, como un humano hablando con un alumno.',
        'NO menciones que falta la premisa del texto o que asumes algo. Sé asertiva y directa.',
        f'Debes generar exactamente {len(preguntas)} objetos en "resultados", uno por cada pregunta, en el mismo orden.',
        'IMPORTANTE: pregunta_index empieza en 0. Primera pregunta = 0, segunda = 1, etc.',
        'Devuelve SOLO un objeto JSON estricto con: {"resultados": [{"pregunta_index": 0, "feedback": "string"}, {"pregunta_index": 1, "feedback": "string"}, ...]}',
        f"Habilidad: {tipo_habilidad}",
        '---'
    ]

    for index, pregunta in enumerate(preguntas):
        prompt_lines.append(f"[pregunta_index={index}] {pregunta['enunciado']}")
        prompt_lines.append(f"Usuario marcó: {pregunta['respuesta_usuario']}")
        prompt_lines.append(f"Correcta es: {pregunta['respuesta_correcta']}")
        prompt_lines.append('')

    return '\n'.join(prompt_lines)


def call_groq_feedback(tipo_habilidad: str, preguntas: list[dict], db: Session) -> dict:
    api_key = crud.get_configuracion(db, 'GROQ_API_KEY')
    model = crud.get_configuracion(db, 'GROQ_MODEL')
    if not api_key:
        raise HTTPException(status_code=500, detail='API KEY de Groq no configurada')

    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': build_system_prompt()},
            {'role': 'user', 'content': build_evaluation_prompt(tipo_habilidad, preguntas)}
        ],
        'temperature': 0.2,
        'max_tokens': 6000,
        'response_format': {'type': 'json_object'},
    }

    response = requests.post(
        GROQ_URL,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
        # Justo antes del json.loads() o parse_gemini_output()
        
        json=payload,
        timeout=30,
    )

    if response.status_code != 200:
        print(f'Error de Groq: {response.text}')
        # Detectar rate limit y extraer tiempo de espera
        try:
            err_data = response.json()
            err_msg = err_data.get('error', {}).get('message', '')
            if response.status_code == 429 or 'rate_limit' in err_msg.lower() or 'rate limit' in err_msg.lower():
                import re
                wait_match = re.search(r'try again in ([\d.]+\s*\w+)', err_msg, re.IGNORECASE)
                wait_str = wait_match.group(1) if wait_match else 'unos minutos'
                raise HTTPException(
                    status_code=429,
                    detail=f'Límite de tokens de Groq alcanzado. Espera {wait_str} o cambia a otro modelo en la configuración de la IA.'
                )
        except HTTPException:
            raise
        except Exception:
            pass
        raise HTTPException(status_code=502, detail='Error en la comunicación con Groq')

    data = response.json()
    try:
        raw_output = data['choices'][0]['message']['content']
    except (KeyError, IndexError):
        print(f'Respuesta inesperada de Groq: {data}')
        raise HTTPException(status_code=502, detail='Formato de respuesta inválido de Groq')

    


    parsed = parse_gemini_output(raw_output)
    resultados = parsed.get('resultados')
    if not isinstance(resultados, list):
        raise HTTPException(status_code=502, detail='Formato inválido de feedback de Groq')

    feedback_map = {}
    for item in resultados:
        if isinstance(item, dict) and 'pregunta_index' in item and 'feedback' in item:
            try:
                idx = int(item['pregunta_index'])
                # Normalizar: si el LLM usó base-1 (índice máximo = len(preguntas)), convertir a base-0
                if idx >= len(preguntas) and idx > 0:
                    idx = idx - 1
                feedback_map[idx] = str(item['feedback'])
            except (ValueError, TypeError):
                continue
    return feedback_map


def call_gemini_api(habilidad: str, tema: str, db: Session) -> dict:
    api_key = crud.get_configuracion(db, 'GROQ_API_KEY')
    model = crud.get_configuracion(db, 'GROQ_MODEL') or 'llama-3.1-8b-instant'
    if not api_key:
        raise HTTPException(status_code=500, detail='API KEY de Groq no configurada')

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": build_user_prompt(habilidad, tema)}
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"} # Esto obliga a Groq a dar JSON
    }

    response = requests.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=30
    )

    if response.status_code != 200:
        print(f"Error de Groq: {response.text}")
        # Detectar error de límite de tasa (rate limit) y exponer tiempo de espera
        try:
            err_data = response.json()
            err_msg = err_data.get('error', {}).get('message', '')
            if response.status_code == 429 or 'rate_limit' in err_msg.lower() or 'rate limit' in err_msg.lower():
                # Intentar extraer tiempo de espera del mensaje de Groq
                import re
                wait_match = re.search(r'try again in ([\d.]+\s*\w+)', err_msg, re.IGNORECASE)
                wait_str = wait_match.group(1) if wait_match else 'unos minutos'
                raise HTTPException(
                    status_code=429,
                    detail=f'Límite de tokens de Groq alcanzado. Por favor espera {wait_str} antes de intentarlo de nuevo, o cambia a otro modelo en la configuración de la IA.'
                )
        except HTTPException:
            raise
        except Exception:
            pass
        raise HTTPException(status_code=502, detail="Error en la comunicación con Groq")

    data = response.json()
    
    try:
        raw_output = data['choices'][0]['message']['content']
        return parse_gemini_output(raw_output)
    except (KeyError, IndexError) as e:
        print(f"Respuesta inesperada: {data}")
        raise HTTPException(status_code=502, detail="Formato de respuesta inválido")
    
    

@app.post('/register', response_model=schemas.UserResponse)
def register(user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_rut = crud.get_user_by_rut(db, user_create.rut)
    if existing_rut:
        raise HTTPException(status_code=400, detail='El RUT ya existe')

    existing_email = crud.get_user_by_email(db, user_create.email)
    if existing_email:
        raise HTTPException(status_code=400, detail='El email ya está registrado')

    user = crud.create_user(
        db,
        rut=user_create.rut,
        nombre_completo=user_create.nombre_completo,
        email=user_create.email,
        contrasena=user_create.contrasena,
    )
    return user


@app.post('/login', response_model=schemas.UserResponse)
def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, login_data.rut, login_data.contrasena)
    if not user:
        raise HTTPException(status_code=401, detail='RUT o contraseña incorrectos')
    return user


@app.get('/dashboard/{rut}', response_model=schemas.DashboardResponse)
def dashboard(rut: str, db: Session = Depends(get_db)):
    data = crud.get_dashboard_data(db, rut)
    if not data:
        raise HTTPException(status_code=404, detail='Usuario no encontrado')
    return data


@app.get('/habilidades/{habilidad}', response_model=schemas.HabilidadDetailResponse)
def habilidad_detail(habilidad: str, rut: str, db: Session = Depends(get_db)):
    data = crud.get_habilidad_content(db, rut, habilidad)
    if not data:
        raise HTTPException(status_code=404, detail='Habilidad no encontrada')
    return data

@app.post('/examen', response_model=schemas.ExamenResponse)
def crear_examen(examen_request: schemas.ExamenRequest, db: Session = Depends(get_db)):

    print(f"Recibido: {examen_request.dict()}") # Debug para ver si entra
    # 1. Verificar si la API Key está configurada (usando tu current_config)
    api_key = crud.get_configuracion(db, 'GROQ_API_KEY')
    if not api_key:
        raise HTTPException(status_code=400, detail="API key not configured. Por favor, configura la IA primero.")

    # 2. Crear la sesión en la DB (RUT y metadatos) y obtener preguntas del banco
    try:
        examen_session = crud.create_exam_session(db, examen_request.rut, examen_request.cantidad_preguntas)
    except ValueError as exc:

        raise HTTPException(status_code=400, detail="Hola "+str(exc))

    if not examen_session:
        raise HTTPException(status_code=404, detail='Usuario no encontrado')

    # 3. Las preguntas ya están incluidas en examen_session desde create_exam_session
    return examen_session


@app.post('/evaluar-examen', response_model=schemas.EvaluarExamenResponse)
def evaluar_examen(eval_request: schemas.EvaluarExamenRequest, db: Session = Depends(get_db)):
    try:
        result = crud.evaluate_exam_session(db, eval_request.id_examen, eval_request.respuestas)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post('/guardar-resultados-examen', response_model=schemas.GuardarResultadosExamenResponse)
def guardar_resultados_examen(request: schemas.GuardarResultadosExamenRequest, db: Session = Depends(get_db)):
    try:
        result = crud.save_exam_results(db, request.rut, request.id_examen)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))



@app.get('/temas', response_model=list[schemas.TemaResponse])
def listar_temas(db: Session = Depends(get_db)):
    return crud.get_temas(db)

@app.post('/seleccionar-tema')
def seleccionar_tema(request: schemas.SeleccionarTemaRequest, db: Session = Depends(get_db)):
    try:
        crud.seleccionar_tema(db, request.rut, request.tema_id, request.tema_custom)
        return {"message": "Tema seleccionado exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/acreditar-monedas', response_model=schemas.AcreditarMonedasResponse)
def acreditar_monedas(request: schemas.AcreditarMonedasRequest, db: Session = Depends(get_db)):
    """Acredita monedas ganadas por desafíos/meta diaria al saldo real del usuario en la DB."""
    if request.cantidad <= 0:
        raise HTTPException(status_code=400, detail='La cantidad debe ser mayor a 0')
    try:
        saldo_nuevo = crud.add_monedas(db, request.rut, request.cantidad)
        return {'saldo_nuevo': saldo_nuevo, 'cantidad_acreditada': request.cantidad}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post('/generar-preguntas', response_model=schemas.GenerarPreguntasResponse)
def generar_preguntas(request: schemas.GenerarPreguntasRequest, db: Session = Depends(get_db)):
    habilidad_valida = normalize_habilidad_type(request.habilidad)
    if not habilidad_valida:
        raise HTTPException(status_code=400, detail='Tipo de habilidad inválido.')

    habilidad_db_name = normalize_habilidad_db_name(habilidad_valida)
    if not habilidad_db_name:
        raise HTTPException(status_code=400, detail='Habilidad no reconocida.')

    user = crud.get_user_by_rut(db, request.rut)
    if not user:
        raise HTTPException(status_code=404, detail='Usuario no encontrado.')
    
    if user.textos_restantes <= 0:
        raise HTTPException(status_code=403, detail='No te quedan textos de tu tema actual. Elige un nuevo tema.')

    # Resolver tema actual desde el usuario si no se envía en el request
    if not request.tema and user.tema_actual_id:
        tema_actual = db.query(models.Tema).filter(models.Tema.id_tema == user.tema_actual_id).first()
        if tema_actual:
            request.tema = tema_actual.nombre
            request.es_fijo = not tema_actual.es_custom

    # Si es fijo y pide del pool
    if request.es_fijo:
        # Busca preguntas en el banco que correspondan a esa habilidad y tema
        import random
        # Para esto, necesitamos id_habilidad (usamos la global si existe)
        habilidad_db = crud.get_habilidad_by_nombre(db, habilidad_db_name)
        tema = db.query(models.Tema).filter(models.Tema.nombre.ilike(request.tema)).first() if request.tema else None
        
        if habilidad_db and tema:
            preguntas_banco = db.query(models.BancoPreguntas).filter(
                models.BancoPreguntas.id_habilidad == habilidad_db.id_progreso,
                models.BancoPreguntas.id_tema == tema.id_tema,
                models.BancoPreguntas.activa == True
            ).all()
            
            if preguntas_banco:
                # Agrupar por texto_inedito
                import itertools
                # Como texto_inedito es JSON (list), lo convertimos a string para agrupar o simplemente agarramos el de una
                # Por simplicidad, tomamos un set de preguntas que compartan el mismo texto
                # Tomamos la primera y sacamos las que tengan el mismo texto.
                # (Se podría mejorar seleccionando aleatoriamente un grupo)
                preguntas_seleccionadas = preguntas_banco[:4] if len(preguntas_banco) >= 4 else preguntas_banco
                texto_inedito_json = preguntas_seleccionadas[0].texto_inedito
                
                # Normalizar texto_inedito
                if isinstance(texto_inedito_json, str):
                    try:
                        import json
                        texto_inedito_list = json.loads(texto_inedito_json)
                        if not isinstance(texto_inedito_list, list):
                            texto_inedito_list = [texto_inedito_list]
                    except Exception:
                        texto_inedito_list = [{"tipo": "parrafo", "contenido": texto_inedito_json}]
                elif isinstance(texto_inedito_json, list):
                    texto_inedito_list = texto_inedito_json
                else:
                    texto_inedito_list = [{"tipo": "parrafo", "contenido": str(texto_inedito_json or "Sin texto")}]

                resp = {
                    "tipo_habilidad": habilidad_valida,
                    "texto_inedito": texto_inedito_list,
                    "preguntas": []
                }
                for p in preguntas_seleccionadas:
                    resp["preguntas"].append({
                        "id_pregunta": p.id_pregunta,
                        "enunciado": p.enunciado,
                        "alternativas": p.alternativas,
                        "respuesta_correcta": p.respuesta_correcta,
                        "justificacion_cot": p.justificacion_cot
                    })
                
                # Descontar texto
                user.textos_restantes -= 1
                db.commit()
                return resp

    # 1. Llamada a la IA para generar el contenido
    generacion = call_gemini_api(habilidad_valida, request.tema or "", db)

    if not isinstance(generacion, dict) or 'preguntas' not in generacion:
        raise HTTPException(status_code=502, detail='Respuesta inválida de la IA: formato inesperado.')

    # 2. Obtener el registro de la habilidad para vincular las preguntas (id_progreso)
    # Asumiendo que tienes una función para obtener la habilidad por nombre
    habilidad_db = crud.get_habilidad_by_nombre(db, habilidad_db_name)
    if not habilidad_db:
        raise HTTPException(status_code=404, detail="Habilidad no encontrada en el sistema.")

    # 3. Guardar cada pregunta generada en el banco de preguntas
    preguntas_guardadas_ids = []
    
    try:
        texto_inedito_raw = generacion.get('texto_inedito', [{"tipo": "parrafo", "contenido": "Sin texto"}])
        
        # Normalizar texto_inedito
        if isinstance(texto_inedito_raw, str):
            try:
                import json
                texto_inedito = json.loads(texto_inedito_raw)
                if not isinstance(texto_inedito, list):
                    texto_inedito = [texto_inedito]
            except Exception:
                texto_inedito = [{"tipo": "parrafo", "contenido": texto_inedito_raw}]
        elif isinstance(texto_inedito_raw, list):
            texto_inedito = texto_inedito_raw
        else:
            texto_inedito = [{"tipo": "parrafo", "contenido": str(texto_inedito_raw or "Sin texto")}]

        # Intentar obtener el tema actual
        tema = db.query(models.Tema).filter(models.Tema.nombre.ilike(request.tema)).first() if request.tema else None
        
        for pregunta_data in generacion['preguntas']:
            pregunta = models.BancoPreguntas(
                id_habilidad=habilidad_db.id_progreso,
                id_tema=tema.id_tema if tema else None,
                texto_inedito=texto_inedito,
                enunciado=pregunta_data['enunciado'],
                alternativas=pregunta_data['alternativas'],
                respuesta_correcta=pregunta_data['respuesta_correcta'],
                justificacion_cot=pregunta_data.get('justificacion_cot', ''),
                dificultad='medio',
                activa=True
            )
            db.add(pregunta)
            db.flush() # Para obtener el ID
            pregunta_data['id_pregunta'] = pregunta.id_pregunta
            
        # Descontar texto
        user.textos_restantes -= 1
        db.commit() # Confirmamos todos los guardados
    except Exception as e:
        db.rollback()
        print(f"Error al persistir preguntas en la DB: {str(e)}")
        # Opcional: podrías lanzar una excepción o simplemente devolver las preguntas sin IDs
        texto_inedito = [{"tipo": "parrafo", "contenido": "Sin texto debido a error de persistencia"}]
    
    generacion['tipo_habilidad'] = habilidad_valida
    generacion['texto_inedito'] = texto_inedito
    return generacion


@app.post('/evaluar-preguntas', response_model=schemas.EvaluarRespuestasResponse)
def evaluar_preguntas(request: schemas.EvaluarRespuestasRequest, db: Session = Depends(get_db)):
    if not request.rut:
        raise HTTPException(status_code=400, detail='El RUT es obligatorio para evaluar respuestas.')

    habilidad_valida = normalize_habilidad_type(request.tipo_habilidad)
    if not habilidad_valida:
        raise HTTPException(status_code=400, detail='Tipo de habilidad inválido para evaluación.')

    habilidad_db = normalize_habilidad_db_name(habilidad_valida)
    if not habilidad_db:
        raise HTTPException(status_code=400, detail='No se reconoce la habilidad para la base de datos.')

    if not request.preguntas or len(request.preguntas) == 0:
        raise HTTPException(status_code=400, detail='Debe enviar al menos una pregunta para evaluar.')

    feedback_map = {}
    try:
        feedback_map = call_groq_feedback(habilidad_valida, [
            {
                'enunciado': pregunta.enunciado,
                'alternativas': pregunta.alternativas,
                'respuesta_usuario': pregunta.respuesta_usuario,
                'respuesta_correcta': pregunta.respuesta_correcta,
            }
            for pregunta in request.preguntas
        ], db)
    except HTTPException:
        feedback_map = {}

    resultados = []
    total_correct = 0
    
    # Obtener el registro de habilidad del usuario para guardar errores
    habilidad_record = crud.get_user_habilidad_record(db, request.rut, habilidad_db)
    if not habilidad_record:
        raise HTTPException(status_code=400, detail='Usuario no tiene registro en esta habilidad.')
    
    print(f"DEBUG - Feedback Map recibido: {feedback_map}")
    for index, pregunta in enumerate(request.preguntas):
        respuesta_usuario = pregunta.respuesta_usuario.strip().upper()
        respuesta_correcta = pregunta.respuesta_correcta.strip().upper()
        correcta = respuesta_usuario == respuesta_correcta
        if correcta:
            total_correct += 1

        # Buscar feedback por índice 0-based (normalizado en call_groq_feedback)
        feedback = (
            feedback_map.get(index) or
            'Sin retroalimentación disponible para esta pregunta.'
        )
        if isinstance(feedback, dict):
            feedback = feedback.get('logica_pedagogica') or feedback.get('feedback') or str(feedback)
        resultados.append({
            'index': index,
            'enunciado': pregunta.enunciado,
            'respuesta_usuario': respuesta_usuario,
            'respuesta_correcta': respuesta_correcta,
            'correcta': correcta,
            'feedback': feedback,
        })
        
        # Guardar la pregunta generada y registrar error si es incorrecto
        if not correcta:
            try:
                id_banco = pregunta['id_pregunta'] if isinstance(pregunta, dict) else pregunta.id_pregunta

                # 1. Clonar el contenido a la tabla del GYM (preguntas_ia)
                pregunta_gym = crud.clonar_pregunta_a_preguntas_ia(db, id_banco)
                
                # 2. Registrar la relación del error (quién falló y cuántas veces)
                # Aquí usamos la nueva ID generada en preguntas_ia
                crud.register_error(
                    db,
                    rut_usuario=request.rut,
                    id_pregunta=pregunta_gym.id_pregunta, 
                    id_habilidad=habilidad_record.id_progreso
                )
            except Exception as e:
                db.rollback()
                print(f"Error registrando fallo en pregunta {index}: {str(e)}")

    xp_ganada = 0
    rendimiento_cambio = 0.0
    try:
        resultado_skill = crud.update_user_skill_results(db, request.rut, habilidad_db, total_correct, len(request.preguntas))
        xp_ganada = resultado_skill['xp_ganada']
        rendimiento_cambio = resultado_skill['rendimiento_cambio']
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        'resultados': resultados,
        'total_correct': total_correct,
        'total_preguntas': len(request.preguntas),
        'puntaje': total_correct,
        'xp_ganada': xp_ganada,
        'rendimiento_cambio': rendimiento_cambio,
        'mensaje': 'Evaluación almacenada correctamente.',
    }


@app.get('/error-frecuente/{rut}')
def error_frecuente(rut: str, db: Session = Depends(get_db)):
    data = crud.get_error_frecuente(db, rut)
    if not data:
        return None
    return data


@app.get('/errores-frecuentes/{rut}')
def errores_frecuentes(rut: str, db: Session = Depends(get_db)):
    """Obtiene todos los errores frecuentes del usuario, ordenados por veces fallada (descendente)."""
    try:
        errores = db.query(models.ErroresFavoritos).filter(
            models.ErroresFavoritos.rut_usuario == rut,
            models.ErroresFavoritos.resuelta == False
        ).order_by(models.ErroresFavoritos.veces_fallada.desc()).all()
        
        return [
            {
                'id_error': error.id_error,
                'rut_usuario': error.rut_usuario,
                'id_pregunta': error.id_pregunta,
                'id_habilidad': error.id_habilidad,
                'veces_fallada': error.veces_fallada,
                'fecha_registro': error.fecha_registro.isoformat() if error.fecha_registro else None,
                'pregunta': {
                    'enunciado': error.pregunta.enunciado if error.pregunta else None,
                    'alternativas': error.pregunta.alternativas if error.pregunta else None,
                    'respuesta_correcta': error.pregunta.respuesta_correcta if error.pregunta else None,
                    'justificacion_cot': error.pregunta.justificacion_cot if error.pregunta else None,
                    'texto_inedito': error.pregunta.texto_inedito if error.pregunta else None,
                } if error.pregunta else None,
                'habilidad': {
                    'nombre': error.habilidad.nombre_habilidad if error.habilidad else None,
                    'nivel_maestria': error.habilidad.nivel_maestria if error.habilidad else None,
                } if error.habilidad else None,
            }
            for error in errores
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error al obtener errores frecuentes: {str(e)}')


@app.put('/errores-frecuentes/{error_id}/resolver')
def resolver_error(error_id: int, db: Session = Depends(get_db)):
    """Marca un error como resuelto."""
    try:
        error = db.query(models.ErroresFavoritos).filter(models.ErroresFavoritos.id_error == error_id).first()
        if not error:
            raise HTTPException(status_code=404, detail="Error no encontrado")
        error.resuelta = True
        db.commit()
        return {"message": "Error resuelto"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error al resolver error: {str(e)}')


@app.get('/configuracion')
def get_configuracion(db: Session = Depends(get_db)):
    return crud.get_all_configuracion(db)


@app.post('/configuracion')
def set_configuracion(config: schemas.ConfiguracionUpdate, db: Session = Depends(get_db)):
    crud.set_configuracion(db, config.clave, config.valor, config.descripcion)
    return {'message': 'Configuración actualizada correctamente.'}


@app.get('/groq-models')
def get_groq_models():
    api_key = crud.get_configuracion(next(get_db()), 'GROQ_API_KEY')
    if not api_key:
        raise HTTPException(status_code=400, detail='API Key de Groq no configurada.')

    url = 'https://api.groq.com/openai/v1/models'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail='Error al obtener modelos de Groq.')

    return response.json()


# ============================================================================
# NUEVOS ENDPOINTS PARA CU10 (RECOMENDACIONES) Y CU8 (IMPULSIVIDAD)
# ============================================================================


@app.get(
    '/usuarios/{rut}/recomendaciones',
    response_model=schemas.RecomendacionesResponse,
    summary='Obtener recomendaciones personalizadas',
    tags=['Recomendaciones (CU10)'],
)
async def obtener_recomendaciones(
    rut: str,
    db: Session = Depends(get_db),
):
    """
    **CU10: Recomendaciones Personalizadas**

    Obtiene análisis de habilidades débiles y errores frecuentes del usuario.
    
    Lógica:
    1. Identifica las 2 habilidades con menor nivel_maestria
    2. Consulta los 3 errores más frecuentes en esas habilidades
    3. Retorna sugerencias para que el usuario pratique en el Módulo GYM
    
    Args:
        rut: RUT del usuario (e.g., '12345678-9')
    
    Returns:
        RecomendacionesResponse con:
        - habilidades_debiles: Top 2 habilidades débiles
        - errores_frecuentes: Top 3 errores más fallados
        - proxima_practica_sugerida: Texto sugerencia
    
    Raises:
        404: Usuario no encontrado
        500: Error en base de datos
    
    Latencia: < 2 segundos
    """
    try:
        resultado = await generar_respuesta_recomendaciones(rut, db)
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error al obtener recomendaciones: {str(e)}')


@app.get(
    '/preguntas/{id_pregunta}/umbral-impulsividad',
    response_model=schemas.UmbralImpulsividadResponse,
    summary='Calcular umbral de impulsividad',
    tags=['Impulsividad (CU8)'],
)
async def obtener_umbral_impulsividad(
    id_pregunta: int,
    db: Session = Depends(get_db),
):
    """
    **CU8: Alerta de Impulsividad**

    Calcula el umbral mínimo de tiempo de lectura para una pregunta.
    
    Lógica:
    1. Consulta la pregunta por ID
    2. Extrae texto_inedito y cuenta palabras
    3. Calcula: umbral = max(2, round(palabras / 15, 1))
    4. Retorna información para bloquear botón 'Responder' en el frontend
    
    Args:
        id_pregunta: ID de la pregunta en tabla preguntas_ia
    
    Returns:
        UmbralImpulsividadResponse con:
        - num_palabras: Cantidad de palabras en el texto
        - umbral_segundos: Segundos mínimos antes de permitir responder
        - mensaje_usuario: Texto a mostrar al usuario
    
    Raises:
        404: Pregunta no encontrada o no activa
        500: Error en base de datos
    
    Latencia: < 500 ms
    
    Ejemplo:
        GET /preguntas/42/umbral-impulsividad
        
        Response 200:
        {
            "id_pregunta": 42,
            "num_palabras": 87,
            "umbral_segundos": 5.8,
            "mensaje_usuario": "Lee detenidamente. Espera 5.8 segundos antes de responder."
        }
    """
    try:
        resultado = await calcular_umbral_tiempo_minimo(id_pregunta, db)
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error al calcular umbral de impulsividad: {str(e)}')


@app.get('/ranking', response_model=schemas.RankingResponse)
def get_ranking(rut: str = None, limit: int = 10, db: Session = Depends(get_db)):
    try:
        return crud.get_ranking(db, limit, rut)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error al obtener el ranking: {str(e)}')


# --- ADMIN ENDPOINTS ---

def verificar_admin(rut: str, db: Session):
    user = db.query(models.Usuario).filter(models.Usuario.rut == rut).first()
    if not user or not getattr(user, 'es_admin', False):
        raise HTTPException(status_code=403, detail="No tienes permisos de administrador")
    return user

@app.get('/admin/usuarios', response_model=list[schemas.AdminUsuarioItem])
def get_admin_usuarios(rut_admin: str, db: Session = Depends(get_db)):
    verificar_admin(rut_admin, db)
    return crud.get_all_users_admin(db)

@app.put('/admin/usuarios/{rut_target}/toggle-status')
def toggle_user_status_endpoint(rut_target: str, rut_admin: str, db: Session = Depends(get_db)):
    verificar_admin(rut_admin, db)
    if rut_target == rut_admin:
        raise HTTPException(status_code=400, detail="No puedes desactivarte a ti mismo")
    
    success = crud.toggle_user_status(db, rut_target)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"message": "Estado del usuario actualizado exitosamente"}

@app.delete('/admin/usuarios/{rut_target}')
def delete_user_endpoint(rut_target: str, rut_admin: str, db: Session = Depends(get_db)):
    verificar_admin(rut_admin, db)
    if rut_target == rut_admin:
        raise HTTPException(status_code=400, detail="No puedes eliminarte a ti mismo")
    
    success = crud.delete_user(db, rut_target)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"message": "Usuario eliminado exitosamente"}

# Trigger reload comment
