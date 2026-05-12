"""
Servicio de Recomendaciones (CU10): Análisis de habilidades débiles y errores frecuentes.

Responsabilidades:
1. Identificar las 2 habilidades con menor nivel_maestria
2. Consultar los errores más frecuentes para esas habilidades
3. Generar recomendaciones personalizadas en JSON para el frontend (Módulo GYM)

Latencia objetivo: < 2 segundos
"""

from typing import List, Tuple, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import logging

from models import (
    Usuario,
    HistorialHabilidades,
    ErroresFavoritos,
    BancoPreguntas,
)

logger = logging.getLogger(__name__)


async def get_habilidades_mas_debiles(rut: str, session: Session) -> List[Tuple[str, float]]:
    """
    Obtiene las 2 habilidades con menor nivel_maestria para un usuario.

    Args:
        rut: RUT del usuario (e.g., '12345678-9')
        session: Sesión SQLAlchemy

    Returns:
        Lista de tuplas: [(nombre_habilidad: str, nivel_maestria: float), ...]
        Ordenado ascendente por nivel_maestria. Máximo 2 items.

    Raises:
        ValueError: Si rut no existe en base de datos
    """
    try:
        # Verificar que usuario existe
        usuario = session.query(Usuario).filter(Usuario.rut == rut).first()
        if not usuario:
            raise ValueError(f"Usuario con RUT '{rut}' no encontrado")

        # Obtener habilidades del usuario ordenadas por nivel_maestria ASC
        habilidades = (
            session.query(
                HistorialHabilidades.nombre_habilidad,
                HistorialHabilidades.nivel_maestria,
            )
            .filter(HistorialHabilidades.rut_usuario == rut)
            .order_by(HistorialHabilidades.nivel_maestria.asc())
            .limit(2)
            .all()
        )

        # Convertir Enum a string
        resultado = [(h.nombre_habilidad.value, float(h.nivel_maestria)) for h in habilidades]
        logger.info(f"Habilidades débiles para {rut}: {resultado}")
        return resultado

    except Exception as e:
        logger.error(f"Error en get_habilidades_mas_debiles: {str(e)}")
        raise


async def get_errores_frecuentes(
    rut: str,
    id_habilidades: List[int],
    session: Session,
    limit: int = 3,
) -> List[Dict]:
    """
    Obtiene los errores más frecuentes del usuario para habilidades específicas.

    Args:
        rut: RUT del usuario
        id_habilidades: Lista de IDs de habilidades (id_progreso)
        session: Sesión SQLAlchemy
        limit: Máximo de errores a retornar (default: 3)

    Returns:
        Lista de diccionarios con formato:
        [
            {
                'id_pregunta': int,
                'enunciado': str,
                'veces_fallada': int,
                'id_habilidad': int,
                'nombre_habilidad': str,
            },
            ...
        ]
        Ordenado descendente por veces_fallada

    Raises:
        ValueError: Si id_habilidades está vacío o no existen
    """
    try:
        if not id_habilidades:
            logger.warning(f"get_errores_frecuentes: lista id_habilidades vacía para {rut}")
            return []

        # Consulta: errores_favoritos + join con banco_preguntas para obtener enunciado
        errores = (
            session.query(
                ErroresFavoritos.id_pregunta,
                BancoPreguntas.enunciado,
                ErroresFavoritos.veces_fallada,
                ErroresFavoritos.id_habilidad,
                HistorialHabilidades.nombre_habilidad,
            )
            .join(BancoPreguntas, BancoPreguntas.id_pregunta == ErroresFavoritos.id_pregunta)
            .join(
                HistorialHabilidades,
                HistorialHabilidades.id_progreso == ErroresFavoritos.id_habilidad,
            )
            .filter(
                ErroresFavoritos.rut_usuario == rut,
                ErroresFavoritos.id_habilidad.in_(id_habilidades),
            )
            .order_by(ErroresFavoritos.veces_fallada.desc())
            .limit(limit)
            .all()
        )

        resultado = [
            {
                "id_pregunta": e.id_pregunta,
                "enunciado": e.enunciado,
                "veces_fallada": e.veces_fallada,
                "id_habilidad": e.id_habilidad,
                "nombre_habilidad": e.nombre_habilidad.value,
            }
            for e in errores
        ]

        logger.info(f"Errores frecuentes para {rut}: {len(resultado)} encontrados")
        return resultado

    except Exception as e:
        logger.error(f"Error en get_errores_frecuentes: {str(e)}")
        raise


async def generar_respuesta_recomendaciones(rut: str, session: Session) -> Dict:
    """
    Genera respuesta completa de recomendaciones personalizadas para un usuario.

    Lógica:
    1. Obtiene 2 habilidades más débiles
    2. Obtiene 3 errores más frecuentes para esas habilidades
    3. Compila JSON con sugerencias de práctica

    Args:
        rut: RUT del usuario
        session: Sesión SQLAlchemy

    Returns:
        Diccionario con estructura RecomendacionesResponse:
        {
            'rut': str,
            'habilidades_debiles': [
                {
                    'nombre': str,
                    'nivel_maestria': float,
                    'sugerencia': str,
                },
                ...
            ],
            'errores_frecuentes': [
                {
                    'id_pregunta': int,
                    'enunciado': str,
                    'veces_fallada': int,
                },
                ...
            ],
            'proxima_practica_sugerida': str,
        }

    Raises:
        ValueError: Si usuario no existe
    """
    try:
        logger.info(f"Generando recomendaciones para {rut}")

        # Step 1: Obtener habilidades débiles
        habilidades_debiles = await get_habilidades_mas_debiles(rut, session)

        if not habilidades_debiles:
            logger.warning(f"No se encontraron habilidades para {rut}")
            return {
                "rut": rut,
                "habilidades_debiles": [],
                "errores_frecuentes": [],
                "proxima_practica_sugerida": "No hay datos de habilidades registrados",
            }

        # Step 2: Obtener IDs de habilidades desde historial_habilidades
        id_habilidades = (
            session.query(HistorialHabilidades.id_progreso)
            .filter(
                HistorialHabilidades.rut_usuario == rut,
                HistorialHabilidades.nombre_habilidad.in_(
                    [h[0] for h in habilidades_debiles]
                ),
            )
            .all()
        )
        id_habilidades = [h[0] for h in id_habilidades]

        # Step 3: Obtener errores frecuentes
        errores_frecuentes = await get_errores_frecuentes(rut, id_habilidades, session)

        # Step 4: Compilar respuesta
        habilidades_respuesta = [
            {
                "nombre": h[0],
                "nivel_maestria": h[1],
                "sugerencia": f"Mejora tu dominio en '{h[0]}' - Nivel actual: {h[1]:.1f}%",
            }
            for h in habilidades_debiles
        ]

        # Step 5: Generar sugerencia de práctica
        if habilidades_debiles:
            top_habilidad = habilidades_debiles[0][0]
            proxima_practica = (
                f"Enfócate en el Módulo GYM: '{top_habilidad}'. "
                f"Completa todas las prácticas recomendadas para mejorar tu comprensión."
            )
        else:
            proxima_practica = "¡Excelente! Has dominado todas las habilidades."

        respuesta = {
            "rut": rut,
            "habilidades_debiles": habilidades_respuesta,
            "errores_frecuentes": errores_frecuentes,
            "proxima_practica_sugerida": proxima_practica,
        }

        logger.info(f"Recomendaciones generadas exitosamente para {rut}")
        return respuesta

    except ValueError as e:
        logger.error(f"Error de validación en generar_respuesta_recomendaciones: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado en generar_respuesta_recomendaciones: {str(e)}")
        raise
