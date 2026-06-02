import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database import Base


class Tema(Base):
    __tablename__ = 'temas'

    id_tema = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    es_custom = Column(Boolean, nullable=False, default=False)
    activo = Column(Boolean, nullable=False, default=True)


class Usuario(Base):
    __tablename__ = 'usuarios'

    rut = Column(String(12), primary_key=True, index=True)
    nombre_completo = Column(String(150), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    xp_total = Column(Integer, nullable=False, default=0)
    racha_actual = Column(Integer, nullable=False, default=0)
    fecha_registro = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    activo = Column(Boolean, nullable=False, default=True)
    ultimo_acceso = Column(DateTime(timezone=True), nullable=True)
    tema_actual_id = Column(Integer, ForeignKey('temas.id_tema'), nullable=True)
    textos_restantes = Column(Integer, nullable=False, default=0)

    habilidades = relationship('HistorialHabilidades', back_populates='usuario', cascade='all, delete')
    wallet = relationship('EconomiaMonedas', back_populates='usuario', uselist=False, cascade='all, delete')
    tema_actual = relationship('Tema')

class HabilidadLectora(enum.Enum):
    Localizar = "Localizar"
    Interpretar = "Interpretar"
    Evaluar = "Evaluar"
    Lectura_Critica = "Lectura_Critica"
    Vocabulario = "Vocabulario"
    Tipos_de_Texto = "Tipos_de_Texto"

class HistorialHabilidades(Base):
    __tablename__ = 'historial_habilidades'

    id_progreso = Column(Integer, primary_key=True, index=True)
    rut_usuario = Column(String(12), ForeignKey('usuarios.rut', ondelete='CASCADE'), nullable=False)
    nombre_habilidad = Column(Enum(HabilidadLectora, name="habilidad_lectora"), nullable=False)
    nivel_maestria = Column(Numeric(5, 2), nullable=False, default=0.00)
    ultima_actualizacion = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

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
    ultima_transaccion = Column(DateTime(timezone=True), nullable=True)

    usuario = relationship('Usuario', back_populates='wallet')


class PreguntaIA(Base):
    __tablename__ = 'preguntas_ia'

    id_pregunta = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_pregunta_origen = Column(Integer, nullable=True)
    id_habilidad = Column(Integer, ForeignKey('historial_habilidades.id_progreso'), nullable=False)
    id_tema = Column(Integer, ForeignKey('temas.id_tema'), nullable=True)
    texto_inedito = Column(JSON, nullable=False)
    enunciado = Column(String(500), nullable=False)
    alternativas = Column(JSON, nullable=False)
    respuesta_correcta = Column(String(1), nullable=False)
    justificacion_cot = Column(Text, nullable=False)
    modelo_ia = Column(String(60), nullable=False, default='sinclair')
    fecha_generacion = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    activa = Column(Boolean, nullable=False, default=True)

    habilidad = relationship('HistorialHabilidades', back_populates='preguntas')

    __table_args__ = (
        CheckConstraint("respuesta_correcta IN ('A','B','C','D')", name='respuesta_check'),
    )


class BancoPreguntas(Base):
    __tablename__ = 'banco_preguntas'

    id_pregunta = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_habilidad = Column(Integer, ForeignKey('historial_habilidades.id_progreso'), nullable=False)
    id_tema = Column(Integer, ForeignKey('temas.id_tema'), nullable=True)
    texto_inedito = Column(JSON, nullable=False)
    enunciado = Column(String(500), nullable=False)
    alternativas = Column(JSON, nullable=False)
    respuesta_correcta = Column(String(1), nullable=False)
    justificacion_cot = Column(Text, nullable=False)
    dificultad = Column(String(20), nullable=False, default='medio')
    fecha_creacion = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    activa = Column(Boolean, nullable=False, default=True)

    habilidad = relationship('HistorialHabilidades')

    __table_args__ = (
        CheckConstraint("respuesta_correcta IN ('A','B','C','D')", name='banco_respuesta_check'),
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
    fecha_inicio = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    fecha_fin = Column(DateTime(timezone=True), nullable=True)
    completado = Column(Boolean, nullable=False, default=False)

    preguntas = relationship('SesionPreguntas', back_populates='sesion', cascade='all, delete')


class SesionPreguntas(Base):
    __tablename__ = 'sesion_preguntas'

    id_sesion_pregunta = Column(Integer, primary_key=True, index=True)
    id_examen = Column(Integer, ForeignKey('sesiones_examen.id_examen', ondelete='CASCADE'), nullable=False)
    id_pregunta = Column(Integer, ForeignKey('banco_preguntas.id_pregunta'), nullable=False)
    respuesta_dada = Column(String(1), nullable=True)
    es_correcta = Column(Boolean, nullable=True)
    tiempo_respuesta = Column(Integer, nullable=True)

    sesion = relationship('SesionExamen', back_populates='preguntas')
    pregunta = relationship('BancoPreguntas')


class ErroresFavoritos(Base):
    __tablename__ = 'errores_favoritos'

    id_error = Column(Integer, primary_key=True, index=True)
    rut_usuario = Column(String(12), ForeignKey('usuarios.rut', ondelete='CASCADE'), nullable=False)
    id_pregunta = Column(Integer, ForeignKey('banco_preguntas.id_pregunta'), nullable=False)
    id_habilidad = Column(Integer, ForeignKey('historial_habilidades.id_progreso'), nullable=False)
    veces_fallada = Column(Integer, nullable=False, default=1)
    resuelta = Column(Boolean, nullable=False, default=False)
    fecha_registro = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    fecha_resolucion = Column(DateTime(timezone=True), nullable=True)

    usuario = relationship('Usuario')
    pregunta = relationship('BancoPreguntas')
    habilidad = relationship('HistorialHabilidades')

    __table_args__ = (
        UniqueConstraint('rut_usuario', 'id_pregunta', name='uix_usuario_pregunta'),
        CheckConstraint('veces_fallada > 0', name='veces_fallada_check'),
    )


class Configuracion(Base):
    __tablename__ = 'configuracion'

    id_config = Column(Integer, primary_key=True, index=True)
    clave = Column(String(100), nullable=False, unique=True)
    valor = Column(String(500), nullable=False)
    descripcion = Column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint('clave', name='uix_clave_config'),
    )
