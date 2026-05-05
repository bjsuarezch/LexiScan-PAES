from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


class Usuario(Base):
    __tablename__ = 'usuarios'

    rut = Column(String(12), primary_key=True, index=True)
    nombre_completo = Column(String(150), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    xp_total = Column(Integer, nullable=False, default=0)
    racha_actual = Column(Integer, nullable=False, default=0)
    fecha_registro = Column(DateTime, nullable=False, default=datetime.utcnow)
    activo = Column(Boolean, nullable=False, default=True)
    ultimo_acceso = Column(DateTime, nullable=True)

    habilidades = relationship('HistorialHabilidades', back_populates='usuario', cascade='all, delete')
    wallet = relationship('EconomiaMonedas', back_populates='usuario', uselist=False, cascade='all, delete')


class HistorialHabilidades(Base):
    __tablename__ = 'historial_habilidades'

    id_progreso = Column(Integer, primary_key=True, index=True)
    rut_usuario = Column(String(12), ForeignKey('usuarios.rut', ondelete='CASCADE'), nullable=False)
    nombre_habilidad = Column(String(50), nullable=False)
    nivel_maestria = Column(Numeric(5, 2), nullable=False, default=0.00)
    ultima_actualizacion = Column(DateTime, nullable=False, default=datetime.utcnow)

    usuario = relationship('Usuario', back_populates='habilidades')
    preguntas = relationship('PreguntaIA', back_populates='habilidad', cascade='all, delete')

    __table_args__ = (
        UniqueConstraint('rut_usuario', 'nombre_habilidad', name='uix_rut_habilidad'),
        CheckConstraint('nivel_maestria >= 0 AND nivel_maestria <= 100', name='nivel_maestria_check'),
    )


class EconomiaMonedas(Base):
    __tablename__ = 'economia_monedas'

    rut_usuario = Column(String(12), ForeignKey('usuarios.rut', ondelete='CASCADE'), primary_key=True)
    saldo_monedas = Column(Integer, nullable=False, default=0)
    total_acumulado = Column(Integer, nullable=False, default=0)
    ultima_transaccion = Column(DateTime, nullable=True)

    usuario = relationship('Usuario', back_populates='wallet')


class PreguntaIA(Base):
    __tablename__ = 'preguntas_ia'

    id_pregunta = Column(Integer, primary_key=True, index=True)
    id_habilidad = Column(Integer, ForeignKey('historial_habilidades.id_progreso'), nullable=False)
    texto_inedito = Column(Text, nullable=False)
    enunciado = Column(String(500), nullable=False)
    alternativas = Column(JSON, nullable=False)
    respuesta_correcta = Column(String(1), nullable=False)
    justificacion_cot = Column(Text, nullable=False)
    modelo_ia = Column(String(60), nullable=False, default='sinclair')
    fecha_generacion = Column(DateTime, nullable=False, default=datetime.utcnow)
    activa = Column(Boolean, nullable=False, default=True)

    habilidad = relationship('HistorialHabilidades', back_populates='preguntas')

    __table_args__ = (
        CheckConstraint("respuesta_correcta IN ('A','B','C','D')", name='respuesta_check'),
    )


class SesionExamen(Base):
    __tablename__ = 'sesiones_examen'

    id_examen = Column(Integer, primary_key=True, index=True)
    rut_usuario = Column(String(12), ForeignKey('usuarios.rut', ondelete='CASCADE'), nullable=False)
    cantidad_preguntas = Column(Integer, nullable=False)
    puntaje_obtenido = Column(Integer, nullable=True)
    puntaje_maximo = Column(Integer, nullable=True)
    tiempo_total = Column(Integer, nullable=True)
    es_impulsivo = Column(Boolean, nullable=False, default=False)
    fecha_inicio = Column(DateTime, nullable=False, default=datetime.utcnow)
    fecha_fin = Column(DateTime, nullable=True)
    completado = Column(Boolean, nullable=False, default=False)

    preguntas = relationship('SesionPreguntas', back_populates='sesion', cascade='all, delete')


class SesionPreguntas(Base):
    __tablename__ = 'sesion_preguntas'

    id_sesion_pregunta = Column(Integer, primary_key=True, index=True)
    id_examen = Column(Integer, ForeignKey('sesiones_examen.id_examen', ondelete='CASCADE'), nullable=False)
    id_pregunta = Column(Integer, ForeignKey('preguntas_ia.id_pregunta'), nullable=False)
    respuesta_dada = Column(String(1), nullable=True)
    es_correcta = Column(Boolean, nullable=True)
    tiempo_respuesta = Column(Integer, nullable=True)

    sesion = relationship('SesionExamen', back_populates='preguntas')
