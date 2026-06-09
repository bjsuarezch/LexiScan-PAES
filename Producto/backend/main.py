import os
import json
from pathlib import Path

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
        'Tu función es diseñar material de evaluación riguroso, claro y útil para estudiantes que se preparan para la PAES.'
    )

def build_user_prompt(habilidad: str, tema: str) -> str:
    num_preguntas = 4
    if habilidad == "Tipos_de_Texto" or habilidad == "Tipos de Texto":
        num_preguntas = 1
    
    tema_instruccion = f"El tema central del texto debe ser sobre: '{tema}'." if tema else "Elige un tema educativo y muy interesante al azar."

    return (
        f"Genera un ejercicio completo para la habilidad de Comprension Lectora PAES '{habilidad}'. "
        f"{tema_instruccion}\n\n"
        "Tu tarea es generar un texto inédito de al menos 2 párrafos.\n\n"
        f"CANTIDAD DE PREGUNTAS A GENERAR: {num_preguntas}.\n\n"
        f"basándote exclusivamente en ese texto inedito y en la habilidad a evaluar, genera exactamente {num_preguntas} pregunta(s) de selección múltiple.\n"
        "Devuelve únicamente un JSON válido con esta estructura exacta: \n"
        "{\n"
        "  \"tipo_habilidad\": \"string\",\n"
        "  \"texto_inedito\": [\n"
        "     {\"tipo\": \"parrafo\", \"contenido\": \"...\"},\n"
        "     {\"tipo\": \"dato_clave\", \"contenido\": \"...\"},\n"
        "     {\"tipo\": \"grafico_barra\", \"datos\": [{\"etiqueta\": \"...\", \"valor\": 80}]},\n"
        "     {\"tipo\": \"imagen\", \"concepto\": \"palabra clave en ingles para buscar imagen relacionada\"}\n"
        "  ],\n"
        "  \"preguntas\": [ \n"
        "    { \"enunciado\": \"...\", \"alternativas\": {\"A\": \"...\", \"B\": \"...\", \"C\": \"...\", \"D\": \"...\"}, \"respuesta_correcta\": \"A\", \"justificacion_cot\": \"...\" }\n"
        "  ]\n"
        "}\n"
        "REGLA DE ORO: El campo 'texto_inedito' DEBE ser un arreglo JSON con los distintos bloques que forman el texto."
        "Puedes usar varios 'parrafo'. Si aplica, añade 'dato_clave' y un 'grafico_barra'. SIEMPRE incluye un bloque 'imagen' con un concepto clave en inglés. "
        "Las preguntas deben ser imposibles de responder sin leer el texto inédito. "
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
        'Devuelve SOLO un objeto JSON estricto con: {"resultados": [{"pregunta_index": int, "feedback": "string"}]}',
        f"Habilidad: {tipo_habilidad}",
        '---'
    ]

    for index, pregunta in enumerate(preguntas):
        # Enviamos solo lo necesario para que la IA "razone"
        prompt_lines.append(f"P{index + 1}: {pregunta['enunciado']}")
        prompt_lines.append(f"Usuario marcó: {pregunta['respuesta_usuario']}")
        prompt_lines.append(f"Correcta es: {pregunta['respuesta_correcta']}")
        # IMPORTANTE: No enviamos las alternativas completas para ahorrar tokens, 
        # la IA ya sabe de qué trata la habilidad y el texto.
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


@app.post('/guardar-resultados-examen')
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
                
                resp = {
                    "tipo_habilidad": habilidad_valida,
                    "texto_inedito": texto_inedito_json,
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
        texto_inedito = generacion.get('texto_inedito', [{"tipo": "parrafo", "contenido": "Sin texto"}])
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

        # Intenta buscar el índice de todas las formas posibles para evitar el desfase
        feedback = (
            feedback_map.get(index) or 
            feedback_map.get(str(index)) or 
            feedback_map.get(index + 1) or 
            feedback_map.get(str(index + 1)) or 
            'Revisa la justificación pedagógica y vuelve a intentarlo si es necesario.'
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
