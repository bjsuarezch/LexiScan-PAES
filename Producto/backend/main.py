import os
import json

import requests
from dotenv import load_dotenv  # <--- NUEVO
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

import crud, database, models, schemas

load_dotenv()

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

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
GEMINI_MODEL = 'gemini-1.0'
GEMINI_API_KEY_ENV = 'GEMINI_API_KEY'
VALID_HABILIDADES = {
    'localizar': 'Localizar',
    'interpretar': 'Interpretar',
    'evaluar': 'Evaluar',
    'lectura critica': 'Lectura Crítica',
    'vocabulario': 'Vocabulario',
    'tipos de texto': 'Tipos de Texto',
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
        "Incluye un texto inédito y luego 3 preguntas de selección múltiple, cada una con 4 alternativas (A, B, C, D). "
        "Marca una única respuesta correcta por pregunta y agrega una justificación pedagógica clara en la clave \"justificacion_cot\". "
        "El texto debe ser original y apropiado para la PAES chilena. "
        "Devuelve únicamente un JSON válido con las siguientes claves: \"tipo_habilidad\", \"texto_inedito\", \"preguntas\". "
        "Cada pregunta debe tener: \"enunciado\", \"alternativas\" (objeto con A, B, C, D), \"respuesta_correcta\", \"justificacion_cot\". "
        "No incluyas texto explicativo fuera del JSON. No uses listas numeradas en el objeto JSON."
    )


def parse_gemini_output(raw_text: str) -> dict:
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


def call_gemini_api(habilidad: str) -> dict:
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail='La API KEY de Gemini no está configurada en el .env')

    # Nuevo formato de payload para Gemini 1.5
    payload = {
        "contents": [{
            "parts": [{
                "text": f"{build_system_prompt()}\n\n{build_user_prompt(habilidad)}"
            }]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 1200,
            "responseMimeType": "application/json" # Esto obliga a Gemini a responder en JSON puro
        }
    }

    try:
        response = requests.post(
            GEMINI_URL,
            headers={'Content-Type': 'application/json'},
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail=f'Error en Gemini API: {response.status_code} {response.text}')

        data = response.json()
        
        # Extraer el texto de la nueva estructura de respuesta
        raw_output = data['candidates'][0]['content']['parts'][0]['text']
        
        return parse_gemini_output(raw_output)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno al llamar a la IA: {str(e)}")


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
def generar_preguntas(request: schemas.GenerarPreguntasRequest):
    habilidad_valida = normalize_habilidad_type(request.habilidad)
    if not habilidad_valida:
        raise HTTPException(status_code=400, detail='Tipo de habilidad inválido. Usa Localizar, Interpretar, Evaluar, Lectura Critica, Vocabulario o Tipos de Texto.')

    generacion = call_gemini_api(habilidad_valida)

    if not isinstance(generacion, dict) or 'preguntas' not in generacion:
        raise HTTPException(status_code=502, detail='Respuesta inválida de Gemini: no se encontró el formato esperado.')

    generacion['tipo_habilidad'] = habilidad_valida
    return generacion


@app.get('/error-frecuente/{rut}')
def error_frecuente(rut: str, db: Session = Depends(get_db)):
    data = crud.get_error_frecuente(db, rut)
    if not data:
        return None
    return data
