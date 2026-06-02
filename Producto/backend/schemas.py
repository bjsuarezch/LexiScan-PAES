from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    rut: str = Field(..., example='12345678-9')
    nombre_completo: str
    email: EmailStr
    contrasena: str


class UserLogin(BaseModel):
    rut: str
    contrasena: str


class UserResponse(BaseModel):
    rut: str
    nombre_completo: str
    email: EmailStr
    xp_total: int
    racha_actual: int
    activo: bool
    ultimo_acceso: Optional[datetime] = None
    tema_actual_id: Optional[int] = None
    textos_restantes: int = 0

    class Config:
        from_attributes = True


class HabilidadData(BaseModel):
    nombre_habilidad: str
    nivel_maestria: float


class DashboardResponse(BaseModel):
    rut: str
    nombre_completo: str
    xp_total: int
    racha_actual: int
    saldo_monedas: int
    tema_actual_id: Optional[int] = None
    textos_restantes: int = 0
    habilidades: List[HabilidadData]


class PreguntaItem(BaseModel):
    id_pregunta: int
    enunciado: str
    alternativas: Dict[str, str]
    respuesta_correcta: str
    justificacion_cot: str
    texto_inedito: Optional[str] = None

    class Config:
        from_attributes = True



class HabilidadDetailResponse(BaseModel):
    nombre_habilidad: str
    texto_inedito: str
    preguntas: List[PreguntaItem]


class GenerarPreguntasRequest(BaseModel):
    rut: str
    habilidad: str
    tema: Optional[str] = None
    es_fijo: Optional[bool] = False

class TemaResponse(BaseModel):
    id_tema: int
    nombre: str
    es_custom: bool
    activo: bool

    class Config:
        from_attributes = True

class SeleccionarTemaRequest(BaseModel):
    rut: str
    tema_id: Optional[int] = None
    tema_custom: Optional[str] = None


class GeneratedPreguntaItem(BaseModel):
    id_pregunta: int
    enunciado: str
    alternativas: Dict[str, str]
    respuesta_correcta: str
    justificacion_cot: str


class EvaluarPreguntaUsuario(BaseModel):
    id_pregunta: int
    enunciado: str
    alternativas: Dict[str, str]
    respuesta_usuario: str
    respuesta_correcta: str
    texto_inedito: Optional[Union[str, list]] = None
    justificacion: Optional[str] = None


class EvaluarRespuestasRequest(BaseModel):
    rut: str
    tipo_habilidad: str
    preguntas: List[EvaluarPreguntaUsuario]


class EvaluarResultadoItem(BaseModel):
    index: int
    enunciado: str
    respuesta_usuario: str
    respuesta_correcta: str
    correcta: bool
    feedback: str


class EvaluarRespuestasResponse(BaseModel):
    resultados: List[EvaluarResultadoItem]
    total_correct: int


class ExamenRequest(BaseModel):
    rut: str
    cantidad_preguntas: int


class ExamenResponse(BaseModel):
    id_examen: int
    rut_usuario: str
    cantidad_preguntas: int
    estimated_time: int
    preguntas: List[PreguntaItem]


class RespuestaExamenItem(BaseModel):
    id_pregunta: int
    respuesta_dada: Optional[str]


class EvaluarExamenRequest(BaseModel):
    id_examen: int
    respuestas: List[RespuestaExamenItem]


class RendimientoHabilidad(BaseModel):
    nombre_habilidad: str
    correctas: int
    total: int
    porcentaje: float


class EvaluarExamenResponse(BaseModel):
    id_examen: int
    total_correctas: int
    total_preguntas: int
    porcentaje: float
    rendimiento_habilidades: List[RendimientoHabilidad]


class GuardarResultadosExamenRequest(BaseModel):
    rut: str
    id_examen: int
    #total_preguntas: int
    #puntaje: int
    #xp_ganada: int
    #mensaje: str


class GenerarPreguntasResponse(BaseModel):
    tipo_habilidad: str
    texto_inedito: list  # JSON Array of blocks
    preguntas: List[GeneratedPreguntaItem]


class ConfiguracionItem(BaseModel):
    clave: str
    valor: str
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True


class ConfiguracionUpdate(BaseModel):
    clave: str
    valor: str
    descripcion: Optional[str] = None


class GroqModel(BaseModel):
    id: str
    object: str
    created: int
    owned_by: str


class GroqModelsResponse(BaseModel):
    object: str
    data: List[GroqModel]


# ============================================================================
# NUEVOS ESQUEMAS PARA CU10 (RECOMENDACIONES) Y CU8 (IMPULSIVIDAD)
# ============================================================================


class HabilidadDebolItem(BaseModel):
    """Representa una habilidad débil del usuario."""
    nombre: str = Field(..., description="Nombre de la habilidad (ej: 'Evaluar', 'Vocabulario')")
    nivel_maestria: float = Field(..., ge=0, le=100, description="Nivel de maestría 0-100")
    sugerencia: str = Field(..., description="Sugerencia personalizada para mejorar")


class ErrorFrecuenteItem(BaseModel):
    """Representa un error frecuente del usuario."""
    id_pregunta: int = Field(..., description="ID de la pregunta donde falla")
    enunciado: str = Field(..., description="Texto de la pregunta")
    veces_fallada: int = Field(..., ge=1, description="Cantidad de veces que ha fallado")


class RecomendacionesResponse(BaseModel):
    """
    Respuesta del endpoint GET /usuarios/{rut}/recomendaciones (CU10).
    
    Contiene análisis de habilidades débiles y errores frecuentes.
    Sirve para que el frontend del Módulo GYM sugiera qué practicar.
    """
    rut: str = Field(..., description="RUT del usuario")
    habilidades_debiles: List[HabilidadDebolItem] = Field(
        ..., max_items=2, description="Máximo 2 habilidades con menor nivel_maestria"
    )
    errores_frecuentes: List[ErrorFrecuenteItem] = Field(
        ..., max_items=3, description="Máximo 3 errores más frecuentes en esas habilidades"
    )
    proxima_practica_sugerida: str = Field(
        ..., description="Texto descriptivo sugiriendo qué habilidad practicar primero"
    )

    class Config:
        from_attributes = True


class UmbralImpulsividadResponse(BaseModel):
    """
    Respuesta del endpoint GET /preguntas/{id_pregunta}/umbral-impulsividad (CU8).
    
    Contiene el umbral de tiempo mínimo de lectura para evitar impulsividad.
    El frontend debe bloquear el botón 'Responder' por este tiempo.
    """
    id_pregunta: int = Field(..., description="ID de la pregunta")
    num_palabras: int = Field(..., ge=0, description="Cantidad de palabras en texto_inedito")
    umbral_segundos: float = Field(
        ..., ge=2.0, description="Segundos mínimos a esperar antes de responder (mín: 2)"
    )
    mensaje_usuario: str = Field(
        ..., description="Mensaje descriptivo para mostrar al usuario (ej: 'Lee detenidamente...')"
    )

    class Config:
        from_attributes = True
