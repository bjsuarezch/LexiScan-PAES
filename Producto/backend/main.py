import os
import json

import requests
from dotenv import load_dotenv  # <--- NUEVO
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from pydantic import BaseModel

import crud, database, models, schemas

class ConfigAPI(BaseModel):
    api_key: str
    modelo: str

load_dotenv()
print(f"DEBUG: API KEY CARGADA: {os.getenv('GEMINI_API_KEY')[:5]}...") # Solo muestra los primeros 5 caracteres

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

@app.post("/configurar-ia")
def configurar_ia(config: ConfigAPI):
    """Permite a los compañeros setear su propia API Key y elegir modelo"""
    if not config.api_key.startswith("gsk_"):
        raise HTTPException(status_code=400, detail="API Key de Groq inválida")
    
    current_config["api_key"] = config.api_key
    current_config["modelo"] = config.modelo
    
    return {"status": "Configuración actualizada", "modelo_activo": current_config["modelo"]}

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


def build_system_prompt() -> str:
    return (
        'Eres la Profesora Sinclair, una docente experta en la PAES chilena. ' 
        'Respondes con un tono pedagógico, cercano y profesional, cuidando la precisión académica. '
        'Tu función es diseñar material de evaluación riguroso, claro y útil para estudiantes que se preparan para la PAES.'
    )

def build_user_prompt(habilidad: str) -> str:
    return (
        f"Genera un ejercicio completo para la habilidad de PAES '{habilidad}'. "
        "Devuelve únicamente un JSON válido con esta estructura exacta: "
        "{"
        "  \"tipo_habilidad\": \"string\", "
        "  \"texto_inedito\": \"string\", "
        "  \"preguntas\": [ "  # <--- IMPORTANTE: Usar corchetes aquí
        "    { \"enunciado\": \"...\", \"alternativas\": {\"A\": \"...\", \"B\": \"...\", \"C\": \"...\", \"D\": \"...\"}, \"respuesta_correcta\": \"A\", \"justificacion_cot\": \"...\" }"
        "  ]"
        "}"
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


def normalize_habilidad_db_name(value: str) -> str:
    if not value:
        return ''
    return DB_HABILIDADES.get(value.strip(), '')


def build_evaluation_prompt(tipo_habilidad: str, preguntas: list[dict]) -> str:
    prompt_lines = [
        'Eres la Profesora Sinclair, una correctora experta en la PAES chilena.',
        'Evalúa las respuestas del estudiante con un tono pedagógico, claro y preciso.',
        'Para cada pregunta, determina si la respuesta es correcta o incorrecta y explica por qué lo es.',
        'Devuelve únicamente un JSON válido con las claves: resultados, total_correct, total_preguntas, puntaje, xp_ganada, mensaje.',
        'Cada elemento de resultados debe incluir: pregunta_index, enunciado, respuesta_usuario, respuesta_correcta, correcta y feedback.',
        'No agregues texto adicional fuera del JSON.',
        f"Habilidad: {tipo_habilidad}",
        'Preguntas:'
    ]

    for index, pregunta in enumerate(preguntas):
        prompt_lines.append(f"Pregunta {index + 1}: {pregunta['enunciado']}")
        prompt_lines.append('Alternativas:')
        for key, option in pregunta['alternativas'].items():
            prompt_lines.append(f"  {key}: {option}")
        prompt_lines.append(f"Respuesta del estudiante: {pregunta['respuesta_usuario']}")
        prompt_lines.append(f"Respuesta correcta: {pregunta['respuesta_correcta']}")
        prompt_lines.append('')

    return '\n'.join(prompt_lines)


def call_groq_feedback(tipo_habilidad: str, preguntas: list[dict], db: Session) -> dict:
    api_key = crud.get_configuracion(db, 'GROQ_API_KEY')
    model = crud.get_configuracion(db, 'GROQ_MODEL') or 'llama-3.1-8b-instant'
    if not api_key:
        raise HTTPException(status_code=500, detail='API KEY de Groq no configurada')

    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': build_system_prompt()},
            {'role': 'user', 'content': build_evaluation_prompt(tipo_habilidad, preguntas)}
        ],
        'temperature': 0.2,
        'response_format': {'type': 'json_object'},
    }

    response = requests.post(
        GROQ_URL,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
        json=payload,
        timeout=30,
    )

    if response.status_code != 200:
        print(f'Error de Groq: {response.text}')
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
                feedback_map[int(item['pregunta_index'])] = str(item['feedback'])
            except (ValueError, TypeError):
                continue
    return feedback_map


""" def call_gemini_api(habilidad: str) -> dict:
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail='API KEY no configurada')

    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"{build_system_prompt()}\n\n{build_user_prompt(habilidad)}"
            }]
        }],
        "generation_config": {
            "temperature": 0.2,
            "max_output_tokens": 1200
        }
    }

    response = requests.post(
        GEMINI_URL,
        headers={'Content-Type': 'application/json'},
        json=payload,
        timeout=30
    )

    if response.status_code != 200:
        print(f"Error de Google: {response.text}")
        raise HTTPException(status_code=502, detail="Error en la comunicación con la IA")

    data = response.json()
    
    # Navegamos por la estructura de respuesta de Gemini 2.5
    try:
        raw_output = data['candidates'][0]['content']['parts'][0]['text']
        return parse_gemini_output(raw_output)
    except (KeyError, IndexError) as e:
        print(f"Estructura inesperada: {data}")
        raise HTTPException(status_code=502, detail="La IA respondió en un formato no soportado")
 """
 
def call_gemini_api(habilidad: str, db: Session) -> dict:
    api_key = crud.get_configuracion(db, 'GROQ_API_KEY')
    model = crud.get_configuracion(db, 'GROQ_MODEL') or 'llama-3.1-8b-instant'
    if not api_key:
        raise HTTPException(status_code=500, detail='API KEY de Groq no configurada')

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": build_user_prompt(habilidad)}
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
        raise HTTPException(status_code=502, detail="Error en la comunicación con Groq")

    data = response.json()
    
    try:
        # Groq sigue el formato de OpenAI: choices[0].message.content
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
    try:
        data = crud.create_exam_session(db, examen_request.rut, examen_request.cantidad_preguntas)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not data:
        raise HTTPException(status_code=404, detail='Usuario no encontrado')
    return data


@app.post('/generar-preguntas', response_model=schemas.GenerarPreguntasResponse)
def generar_preguntas(request: schemas.GenerarPreguntasRequest, db: Session = Depends(get_db)):
    habilidad_valida = normalize_habilidad_type(request.habilidad)
    if not habilidad_valida:
        raise HTTPException(status_code=400, detail='Tipo de habilidad inválido. Usa Localizar, Interpretar, Evaluar, Lectura Critica, Vocabulario o Tipos de Texto.')

    generacion = call_gemini_api(habilidad_valida, db)

    if not isinstance(generacion, dict) or 'preguntas' not in generacion:
        raise HTTPException(status_code=502, detail='Respuesta inválida de Gemini: no se encontró el formato esperado.')

    generacion['tipo_habilidad'] = habilidad_valida
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
    for index, pregunta in enumerate(request.preguntas):
        respuesta_usuario = pregunta.respuesta_usuario.strip().upper()
        respuesta_correcta = pregunta.respuesta_correcta.strip().upper()
        correcta = respuesta_usuario == respuesta_correcta
        if correcta:
            total_correct += 1

        feedback = feedback_map.get(index, 'Revisa la justificación pedagógica y vuelve a intentarlo si es necesario.')
        resultados.append({
            'index': index,
            'enunciado': pregunta.enunciado,
            'respuesta_usuario': respuesta_usuario,
            'respuesta_correcta': respuesta_correcta,
            'correcta': correcta,
            'feedback': feedback,
        })

    xp_ganada = 0
    try:
        xp_ganada = crud.update_user_skill_results(db, request.rut, habilidad_db, total_correct, len(request.preguntas))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        'resultados': resultados,
        'total_correct': total_correct,
        'total_preguntas': len(request.preguntas),
        'puntaje': total_correct,
        'xp_ganada': xp_ganada,
        'mensaje': 'Evaluación almacenada correctamente.',
    }


@app.get('/error-frecuente/{rut}')
def error_frecuente(rut: str, db: Session = Depends(get_db)):
    data = crud.get_error_frecuente(db, rut)
    if not data:
        return None
    return data


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
