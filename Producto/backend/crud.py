import hashlib
from datetime import date, datetime, timedelta, timezone
import bcrypt
import requests
import json

from typing import Optional, List
from sqlalchemy import func
from sqlalchemy.orm import Session

import models, schemas

SKILLS = [
    'Localizar',
    'Interpretar',
    'Evaluar',
    'Lectura_Critica',
    'Vocabulario',
    'Tipos_de_Texto',
]

DISPLAY_NAMES = {
    'Localizar': 'Localizar',
    'Interpretar': 'Interpretar',
    'Evaluar': 'Evaluar',
    'Lectura_Critica': 'Lectura Crítica',
    'Vocabulario': 'Vocabulario',
    'Tipos_de_Texto': 'Tipos de Texto',
}


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, stored_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))


def normalize_habilidad_name(value: str) -> str:
    normalized = value.strip().replace(' ', '_').replace('é', 'e').replace('í', 'i')
    return normalized


def get_user_by_rut(db: Session, rut: str) -> Optional[models.Usuario]:
    return db.query(models.Usuario).filter(models.Usuario.rut == rut).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.Usuario]:
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()


def get_random_questions(db: Session, cantidad: int, id_habilidad: Optional[int] = None) -> List[models.BancoPreguntas]:
    """Obtiene preguntas aleatorias del banco de preguntas."""
    query = db.query(models.BancoPreguntas).filter(models.BancoPreguntas.activa == True)
    if id_habilidad:
        query = query.filter(models.BancoPreguntas.id_habilidad == id_habilidad)
    return query.order_by(func.random()).limit(cantidad).all()


def create_user(db: Session, rut: str, nombre_completo: str, email: str, contrasena: str) -> models.Usuario:
    password_hash = hash_password(contrasena)
    user = models.Usuario(
        rut=rut,
        nombre_completo=nombre_completo,
        email=email,
        password_hash=password_hash,
        xp_total=0,
        racha_actual=0,
        activo=True,
    )
    db.add(user)
    
    for skill in SKILLS:
        habilidad = models.HistorialHabilidades(
            rut_usuario=rut,
            nombre_habilidad=skill,
            nivel_maestria=0.0,
            ultima_actualizacion=datetime.now(timezone.utc),
        )
        db.add(habilidad)

    economia = models.EconomiaMonedas(
        rut_usuario=rut,
        saldo_monedas=0,
        total_acumulado=0,
        ultima_transaccion=datetime.now(timezone.utc),
    )
    db.add(economia)

    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        print(f"Error al crear usuario y habilidades: {e}")
        raise e
        
    return user


def authenticate_user(db: Session, rut: str, contrasena: str) -> Optional[models.Usuario]:
    user = get_user_by_rut(db, rut)
    if user is None:
        return None
    if not verify_password(contrasena, user.password_hash):
        return None
    return user


def build_display_habilidad(item: models.HistorialHabilidades) -> dict:
    return {
        'nombre_habilidad': DISPLAY_NAMES.get(item.nombre_habilidad, item.nombre_habilidad),
        'nivel_maestria': float(item.nivel_maestria),
    }


def get_dashboard_data(db: Session, rut: str) -> Optional[dict]:
    user = get_user_by_rut(db, rut)
    if not user:
        return None

    wallet = db.query(models.EconomiaMonedas).filter(models.EconomiaMonedas.rut_usuario == rut).first()
    habilidades = db.query(models.HistorialHabilidades).filter(models.HistorialHabilidades.rut_usuario == rut).all()

    return {
        'rut': user.rut,
        'nombre_completo': user.nombre_completo,
        'xp_total': user.xp_total,
        'racha_actual': user.racha_actual,
        'saldo_monedas': wallet.saldo_monedas if wallet else 0,
        'habilidades': [build_display_habilidad(h) for h in habilidades],
    }

def get_habilidad_by_nombre(db: Session, nombre_habilidad: str):
    """
    Busca una habilidad en el historial por su nombre para obtener su ID.
    """
    return db.query(models.HistorialHabilidades).filter(
        models.HistorialHabilidades.nombre_habilidad == nombre_habilidad
    ).first()


def get_habilidad_content(db: Session, rut: str, habilidad: str) -> Optional[dict]:
    normalized = normalize_habilidad_name(habilidad)
    if normalized == 'Lectura_Critica':
        normalized = 'Lectura_Critica'
    if normalized == 'Tipos_de_Texto':
        normalized = 'Tipos_de_Texto'

    habilidad_record = (
        db.query(models.HistorialHabilidades)
        .filter(models.HistorialHabilidades.rut_usuario == rut)
        .filter(models.HistorialHabilidades.nombre_habilidad == normalized)
        .first()
    )
    if not habilidad_record:
        return None

    preguntas = db.query(models.BancoPreguntas).filter(
        models.BancoPreguntas.id_habilidad == habilidad_record.id_progreso,
        models.BancoPreguntas.activa == True,
    ).all()

    return {
        'nombre_habilidad': DISPLAY_NAMES.get(normalized, normalized),
        'texto_inedito': preguntas[0].texto_inedito if preguntas else '',
        'preguntas': [
            {
                'id_pregunta': pregunta.id_pregunta,
                'enunciado': pregunta.enunciado,
                'alternativas': pregunta.alternativas,
                'respuesta_correcta': pregunta.respuesta_correcta,
                'justificacion_cot': pregunta.justificacion_cot,
            }
            for pregunta in preguntas
        ],
    }


def update_user_racha(db: Session, user: models.Usuario) -> None:
    today = date.today()
    last_access = user.ultimo_acceso.date() if user.ultimo_acceso else None

    if last_access == today:
        pass
    elif last_access == today - timedelta(days=1):
        user.racha_actual += 1
    else:
        user.racha_actual = 1

    user.ultimo_acceso = datetime.now(timezone.utc)
    db.add(user)
    db.commit()


def update_user_skill_results(db: Session, rut: str, habilidad: str, correct_count: int, total_questions: int) -> int:
    if total_questions <= 0:
        return 0

    user = get_user_by_rut(db, rut)
    if not user:
        raise ValueError('Usuario no encontrado')

    habilidad_record = (
        db.query(models.HistorialHabilidades)
        .filter(models.HistorialHabilidades.rut_usuario == rut)
        .filter(models.HistorialHabilidades.nombre_habilidad == habilidad)
        .first()
    )
    if not habilidad_record:
        raise ValueError('Habilidad no encontrada')

    xp_ganada = correct_count * 10
    user.xp_total += xp_ganada

    porcentaje_aciertos = correct_count / total_questions
    incremento = int(round(porcentaje_aciertos * 15))
    habilidad_record.nivel_maestria = min(100.0, float(habilidad_record.nivel_maestria) + incremento)
    habilidad_record.ultima_actualizacion = datetime.now(timezone.utc)

    db.add(user)
    db.add(habilidad_record)
    db.commit()

    return xp_ganada


def create_exam_session(db: Session, rut: str, cantidad_preguntas: int) -> Optional[dict]:
    if cantidad_preguntas < 10 or cantidad_preguntas > 65:
        raise ValueError('Cantidad de preguntas debe ser entre 10 y 65')

    user = get_user_by_rut(db, rut)
    if not user:
        return None

    # Get random questions from pool
    pool_questions = get_random_questions(db, cantidad_preguntas)
    if len(pool_questions) < cantidad_preguntas:
        raise ValueError('No hay suficientes preguntas en el banco')

    # Create session
    examen = models.SesionExamen(
        rut_usuario=rut,
        cantidad_preguntas=cantidad_preguntas,
        puntaje_maximo=cantidad_preguntas,
        tiempo_total=0,
        es_impulsivo=False,
        completado=False,
    )
    db.add(examen)
    db.flush()

    for pregunta in pool_questions:
        db.add(models.SesionPreguntas(
            id_examen=examen.id_examen,
            id_pregunta=pregunta.id_pregunta,
            respuesta_dada=None,
            es_correcta=None,
        ))

    db.commit()
    db.refresh(examen)

    update_user_racha(db, user)

    return {
        'id_examen': examen.id_examen,
        'rut_usuario': examen.rut_usuario,
        'cantidad_preguntas': examen.cantidad_preguntas,
        'estimated_time': round(examen.cantidad_preguntas * 2.2),
        'preguntas': [
            {
                'id_pregunta': pregunta.id_pregunta,
                'enunciado': pregunta.enunciado,
                'alternativas': pregunta.alternativas,
                'respuesta_correcta': pregunta.respuesta_correcta,
                'justificacion_cot': pregunta.justificacion_cot,
                'texto_inedito': pregunta.texto_inedito,
            }
            for pregunta in pool_questions
        ],
    }


def get_error_frecuente(db: Session, rut: str) -> Optional[dict]:
    """Obtiene el error frecuente (más veces fallado) del usuario que aún no está resuelto."""
    error = (
        db.query(models.ErroresFavoritos)
        .filter(
            models.ErroresFavoritos.rut_usuario == rut,
            models.ErroresFavoritos.resuelta == False
        )
        .order_by(models.ErroresFavoritos.veces_fallada.desc())
        .first()
    )
    
    if not error:
        return None
    
    # Obtener datos de la habilidad
    habilidad = db.query(models.HistorialHabilidades).filter(
        models.HistorialHabilidades.id_progreso == error.id_habilidad
    ).first()
    
    # Obtener datos de la pregunta
    pregunta = db.query(models.BancoPreguntas).filter(
        models.BancoPreguntas.id_pregunta == error.id_pregunta
    ).first()
    
    return {
        'id_error': error.id_error,
        'nombre_habilidad': DISPLAY_NAMES.get(habilidad.nombre_habilidad, habilidad.nombre_habilidad) if habilidad else 'Desconocida',
        'veces_fallada': error.veces_fallada,
        'enunciado': pregunta.enunciado if pregunta else 'Pregunta no disponible',
        'alternativas': pregunta.alternativas if pregunta else {},
        'respuesta_correcta': pregunta.respuesta_correcta if pregunta else '',
        'justificacion_cot': pregunta.justificacion_cot if pregunta else '',
    }


def get_configuracion(db: Session, clave: str) -> Optional[str]:
    config = db.query(models.Configuracion).filter(models.Configuracion.clave == clave).first()
    return config.valor if config else None


def set_configuracion(db: Session, clave: str, valor: str, descripcion: Optional[str] = None) -> models.Configuracion:
    config = db.query(models.Configuracion).filter(models.Configuracion.clave == clave).first()
    if config:
        config.valor = valor
        if descripcion:
            config.descripcion = descripcion
    else:
        config = models.Configuracion(clave=clave, valor=valor, descripcion=descripcion)
        db.add(config)
    db.commit()
    db.refresh(config)
    return config


def get_all_configuracion(db: Session) -> List[dict]:
    configs = db.query(models.Configuracion).all()
    return [
        {
            'clave': c.clave,
            'valor': c.valor,
            'descripcion': c.descripcion,
        }
        for c in configs
    ]

def clonar_pregunta_a_preguntas_ia(
    db: Session, id_pregunta_banco: int) -> models.PreguntaIA:
    """Clona una pregunta del banco a la tabla de errores_favoritos para el usuario."""
    original = db.query(models.BancoPreguntas).filter(
        models.BancoPreguntas.id_pregunta == id_pregunta_banco
    ).first()

    if not original:
        raise ValueError(f"No se encontró la pregunta con ID {id_pregunta_banco} en el banco.")

    # 2. Crear la copia para la tabla de errores (PreguntasIA)
    # IMPORTANTE: Solo los campos de contenido, sin rut ni contadores.
    copia_gym = models.PreguntaIA(
        id_habilidad=original.id_habilidad,
        texto_inedito=original.texto_inedito,
        enunciado=original.enunciado,
        alternativas=original.alternativas,
        respuesta_correcta=original.respuesta_correcta,
        justificacion_cot=original.justificacion_cot,
        modelo_ia='Clonado del Banco'
    )
    
    db.add(copia_gym)
    db.commit()
    db.refresh(copia_gym)
    return copia_gym

def save_generated_question(
    db: Session,
    id_habilidad: int,
    texto_inedito: str,
    enunciado: str,
    alternativas: dict,
    respuesta_correcta: str,
    justificacion_cot: str,
    modelo_ia: str = 'Groq'
) -> models.BancoPreguntas:
    """Guarda una pregunta generada por IA en el banco de preguntas."""
    pregunta = models.BancoPreguntas(
        id_habilidad=id_habilidad,
        texto_inedito=texto_inedito,
        enunciado=enunciado,
        alternativas=alternativas,
        respuesta_correcta=respuesta_correcta,
        justificacion_cot=justificacion_cot,
        dificultad='medio',
        activa=True
    )
    db.add(pregunta)
    db.commit()
    db.refresh(pregunta)
    return pregunta


def register_error(
    db: Session,
    rut_usuario: str,
    id_pregunta: int,
    id_habilidad: int,
) -> models.ErroresFavoritos:
    """Registra un error en la tabla errores_favoritos. Si ya existe, incrementa veces_fallada."""
    # Buscar si ya existe un error para este usuario y pregunta
    error_existente = db.query(models.ErroresFavoritos).filter(
        models.ErroresFavoritos.rut_usuario == rut_usuario,
        models.ErroresFavoritos.id_pregunta == id_pregunta
    ).first()
    
    if error_existente:
        # Incrementar veces_fallada y actualizar fecha_registro
        error_existente.veces_fallada += 1
        error_existente.fecha_registro = datetime.now(timezone.utc)
        error_existente.resuelta = False  # Reiniciar si vuelve a fallar
        db.commit()
        db.refresh(error_existente)
        return error_existente
    else:
        # Crear nuevo error
        nuevo_error = models.ErroresFavoritos(
            rut_usuario=rut_usuario,
            id_pregunta=id_pregunta,
            id_habilidad=id_habilidad,
            veces_fallada=1,
            resuelta=False,
            fecha_registro=datetime.now(timezone.utc)
        )
        db.add(nuevo_error)
        db.commit()
        db.refresh(nuevo_error)
        return nuevo_error


def get_habilidad_id(db: Session, nombre_habilidad: str) -> Optional[int]:
    """Obtiene el id_progreso para una habilidad específica."""
    hab = db.query(models.HistorialHabilidades).filter(
        models.HistorialHabilidades.nombre_habilidad == nombre_habilidad
    ).first()
    return hab.id_progreso if hab else None

def get_user_habilidad_record(db: Session, rut: str, nombre_habilidad: str):
    """
    Busca el registro de progreso de una habilidad específica para un usuario.
    """
    return db.query(models.HistorialHabilidades).filter(
        models.HistorialHabilidades.rut_usuario == rut,
        models.HistorialHabilidades.nombre_habilidad == nombre_habilidad
    ).first()

def generate_exam_questions(cantidad_preguntas: int, api_key: str, modelo: str) -> List[dict]:
    """Genera preguntas para el examen usando Groq AI."""
    import json
    import re

    system_prompt = """Eres la Profesora Sinclair, una experta pedagoga en la PAES chilena con más de 20 años de experiencia. Tu tono es pedagógico, motivador y experto. Debes generar contenido educativo de alta calidad. Responde ÚNICAMENTE con JSON válido, sin texto adicional."""

    user_prompt = f"""Genera {cantidad_preguntas} preguntas de PAES chilena distribuidas en diferentes habilidades: Localizar, Interpretar, Evaluar, Lectura Crítica, Vocabulario, Tipos de Texto.

Para cada pregunta incluye:
- Un texto inédito de 100-200 palabras (narrativo, expositivo, argumentativo, etc.)
- La habilidad que mide
- El enunciado de la pregunta
- 4 alternativas (A, B, C, D)
- La respuesta correcta
- Una justificación pedagógica corta

Devuelve ÚNICAMENTE un JSON válido con esta estructura exacta:
{{
  "preguntas": [
    {{
      "texto_inedito": "El texto completo aquí...",
      "habilidad": "Interpretar",
      "enunciado": "¿Pregunta?",
      "alternativas": {{"A": "Opción A", "B": "Opción B", "C": "Opción C", "D": "Opción D"}},
      "respuesta_correcta": "A",
      "justificacion_cot": "Justificación corta"
    }},
    // más preguntas...
  ]
}}

NO incluyas texto adicional fuera del JSON."""

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"}
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"Error calling Groq: {response.text}")

    result = response.json()
    content = result['choices'][0]['message']['content']

    # Intentar parsear como JSON
    try:
        data = json.loads(content)
        # Si viene envuelto en un objeto, extraer la lista
        if isinstance(data, dict) and 'preguntas' in data:
            return data['preguntas'][:cantidad_preguntas]
        elif isinstance(data, list):
            return data[:cantidad_preguntas]
        else:
            raise ValueError("Formato JSON inesperado")
    except json.JSONDecodeError:
        # Intentar extraer JSON de la respuesta
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group())
                return parsed[:cantidad_preguntas]
            except json.JSONDecodeError:
                # Si está truncado, intentar parsear parcialmente
                try:
                    # Buscar objetos JSON completos
                    objects = re.findall(r'\{[^{}]*\{[^{}]*\}[^{}]*\}', content)
                    parsed_objects = []
                    for obj_str in objects:
                        try:
                            parsed_objects.append(json.loads(obj_str))
                        except:
                            continue
                    return parsed_objects[:cantidad_preguntas]
                except:
                    pass
        raise Exception(f"Respuesta no es JSON válido: {content[:500]}")


def evaluate_exam_session(db: Session, id_examen: int, respuestas: List[dict]) -> dict:
    """Evalúa las respuestas del examen, registra errores y devuelve resultados."""
    # Obtener la sesión del examen
    examen = db.query(models.SesionExamen).filter(models.SesionExamen.id_examen == id_examen).first()
    if not examen:
        raise ValueError('Examen no encontrado')

    # Obtener las preguntas del examen
    preguntas_examen = db.query(models.SesionPreguntas).filter(
        models.SesionPreguntas.id_examen == id_examen
    ).all()

    total_correctas = 0
    rendimiento_habilidades = {}

    for resp in respuestas:
        id_pregunta = resp['id_pregunta']
        respuesta_dada = resp['respuesta_dada']

        # Encontrar la pregunta en la sesión
        pregunta_sesion = next((p for p in preguntas_examen if p.id_pregunta == id_pregunta), None)
        if not pregunta_sesion:
            continue

        # Obtener la pregunta completa
        pregunta = db.query(models.BancoPreguntas).filter(models.BancoPreguntas.id_pregunta == id_pregunta).first()
        if not pregunta:
            continue

        correcta = respuesta_dada == pregunta.respuesta_correcta
        pregunta_sesion.respuesta_dada = respuesta_dada
        pregunta_sesion.es_correcta = correcta

        if correcta:
            total_correctas += 1

        # Obtener habilidad
        habilidad = db.query(models.HistorialHabilidades).filter(
            models.HistorialHabilidades.id_progreso == pregunta.id_habilidad
        ).first()
        nombre_habilidad = habilidad.nombre_habilidad if habilidad else 'Desconocida'

        if nombre_habilidad not in rendimiento_habilidades:
            rendimiento_habilidades[nombre_habilidad] = {'correctas': 0, 'total': 0}

        rendimiento_habilidades[nombre_habilidad]['total'] += 1
        if correcta:
            rendimiento_habilidades[nombre_habilidad]['correctas'] += 1

        # Registrar error si incorrecta
        if not correcta:
            register_error(db, examen.rut_usuario, id_pregunta, pregunta.id_habilidad)

    # Calcular porcentajes
    rendimiento_list = []
    for nombre, data in rendimiento_habilidades.items():
        porcentaje = (data['correctas'] / data['total']) * 100 if data['total'] > 0 else 0
        rendimiento_list.append({
            'nombre_habilidad': nombre,
            'correctas': data['correctas'],
            'total': data['total'],
            'porcentaje': round(porcentaje, 2)
        })

    # Marcar examen como completado
    examen.completado = True
    examen.puntaje_obtenido = total_correctas

    db.commit()

    return {
        'id_examen': id_examen,
        'total_correctas': total_correctas,
        'total_preguntas': len(preguntas_examen),
        'porcentaje': round((total_correctas / len(preguntas_examen)) * 100, 2) if preguntas_examen else 0,
        'rendimiento_habilidades': rendimiento_list
    }


def save_exam_results(db: Session, rut: str, id_examen: int) -> dict:
    """Guarda los resultados del examen actualizando el progreso del usuario."""
    # Obtener el examen
    examen = db.query(models.SesionExamen).filter(models.SesionExamen.id_examen == id_examen).first()
    if not examen or examen.rut_usuario != rut:
        raise ValueError('Examen no encontrado o no pertenece al usuario')

    # Obtener rendimiento del examen
    rendimiento_examen = {}
    preguntas_examen = db.query(models.SesionPreguntas).filter(
        models.SesionPreguntas.id_examen == id_examen
    ).all()

    for pregunta_sesion in preguntas_examen:
        pregunta = db.query(models.BancoPreguntas).filter(
            models.BancoPreguntas.id_pregunta == pregunta_sesion.id_pregunta
        ).first()
        if not pregunta:
            continue

        habilidad = db.query(models.HistorialHabilidades).filter(
            models.HistorialHabilidades.id_progreso == pregunta.id_habilidad
        ).first()
        if not habilidad:
            continue

        nombre_habilidad = normalize_habilidad_name(habilidad.nombre_habilidad)
        if nombre_habilidad not in rendimiento_examen:
            rendimiento_examen[nombre_habilidad] = {'correctas': 0, 'total': 0}

        rendimiento_examen[nombre_habilidad]['total'] += 1
        if pregunta_sesion.es_correcta:
            rendimiento_examen[nombre_habilidad]['correctas'] += 1

    # Calcular porcentajes del examen
    porcentajes_examen = {}
    for nombre, data in rendimiento_examen.items():
        porcentajes_examen[nombre] = (data['correctas'] / data['total']) * 100 if data['total'] > 0 else 0

    # Obtener progreso actual del usuario
    habilidades_usuario = db.query(models.HistorialHabilidades).filter(
        models.HistorialHabilidades.rut_usuario == rut
    ).all()

    # Calcular promedio: (progreso_actual + rendimiento_examen) / 2
    for hab in habilidades_usuario:
        nombre_norm = normalize_habilidad_name(hab.nombre_habilidad)
        rendimiento_examen_pct = porcentajes_examen.get(nombre_norm, 0)
        nuevo_progreso = (hab.nivel_maestria + rendimiento_examen_pct) / 2
        hab.nivel_maestria = min(100.0, nuevo_progreso)
        hab.ultima_actualizacion = datetime.now(timezone.utc)

    db.commit()

    return {"message": "Resultados guardados exitosamente"}


def get_random_questions(db: Session, cantidad: int, id_habilidad: Optional[int] = None) -> List[models.BancoPreguntas]:
    """Obtiene preguntas aleatorias del banco de preguntas."""
    from sqlalchemy.sql import func

    query = db.query(models.BancoPreguntas)
    if id_habilidad:
        query = query.filter(models.BancoPreguntas.id_habilidad == id_habilidad)

    return query.order_by(func.random()).limit(cantidad).all()
