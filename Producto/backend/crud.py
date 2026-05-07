import hashlib
from datetime import date, datetime, timedelta, timezone
import bcrypt

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

    preguntas = db.query(models.PreguntaIA).filter(
        models.PreguntaIA.id_habilidad == habilidad_record.id_progreso,
        models.PreguntaIA.activa == True,
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

    preguntas = (
        db.query(models.PreguntaIA)
        .filter(models.PreguntaIA.activa == True)
        .order_by(func.random())
        .limit(cantidad_preguntas)
        .all()
    )

    if len(preguntas) < cantidad_preguntas:
        raise ValueError('No hay suficientes preguntas activas disponibles')

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

    for pregunta in preguntas:
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
            }
            for pregunta in preguntas
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
    pregunta = db.query(models.PreguntaIA).filter(
        models.PreguntaIA.id_pregunta == error.id_pregunta
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
