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
        orm_mode = True


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

    class Config:
        orm_mode = True


class HabilidadDetailResponse(BaseModel):
    nombre_habilidad: str
    texto_inedito: str
    preguntas: List[PreguntaItem]


class ExamenRequest(BaseModel):
    rut: str
    cantidad_preguntas: int


class ExamenResponse(BaseModel):
    id_examen: int
    rut_usuario: str
    cantidad_preguntas: int
    estimated_time: int
    preguntas: List[PreguntaItem]

    class Config:
        orm_mode = True
