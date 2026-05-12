from datetime import datetime
from typing import Dict, List, Optional

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
    habilidad: str


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
    texto_inedito: Optional[str] = None
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
    texto_inedito: str
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
