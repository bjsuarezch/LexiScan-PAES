"""
Servicio de Alerta de Impulsividad (CU8): Cálculo de umbrales de tiempo mínimo de lectura.

Responsabilidades:
1. Extraer texto_inedito de una pregunta
2. Calcular umbral de tiempo basado en cantidad de palabras
3. Retornar información para bloquear dinámicamente el botón 'Responder' en frontend

Fórmula de cálculo:
  umbral_segundos = max(2, round(cantidad_palabras / 15, 1))
  - Mínimo 2 segundos para evitar bloqueos excesivos
  - 1 segundo por cada ~15 palabras (aproximadamente 60 palabras/minuto)

Latencia objetivo: < 500 ms
"""

import logging
from sqlalchemy.orm import Session

from models import PreguntaIA, Usuario

logger = logging.getLogger(__name__)


def contar_palabras(texto_inedito: str) -> int:
    """
    Cuenta la cantidad de palabras en un texto.

    Algoritmo:
    - Split por espacios en blanco
    - Filtrar strings vacíos
    - Manejar None, strings vacíos

    Args:
        texto_inedito: Texto a contar (puede ser None o vacío)

    Returns:
        Cantidad de palabras. Mínimo 0.

    Ejemplos:
        >>> contar_palabras("Hola mundo")
        2
        >>> contar_palabras("  Hola   mundo  ")
        2
        >>> contar_palabras("")
        0
        >>> contar_palabras(None)
        0
    """
    try:
        if not texto_inedito or not isinstance(texto_inedito, str):
            return 0

        # Split por espacios y filtrar vacíos
        palabras = [p for p in texto_inedito.split() if p.strip()]
        return len(palabras)

    except Exception as e:
        logger.error(f"Error en contar_palabras: {str(e)}")
        return 0


async def calcular_umbral_tiempo_minimo(
    id_pregunta: int,
    session: Session,
) -> dict:
    """
    Calcula el umbral mínimo de tiempo de lectura para una pregunta específica.

    Lógica:
    1. Consulta preguntas_ia por ID
    2. Extrae texto_inedito
    3. Calcula: umbral = max(2, round(palabras / 15, 1))
    4. Retorna objeto con información para frontend

    Args:
        id_pregunta: ID de la pregunta en tabla preguntas_ia
        session: Sesión SQLAlchemy

    Returns:
        Diccionario con estructura UmbralImpulsividadResponse:
        {
            'id_pregunta': int,
            'num_palabras': int,
            'umbral_segundos': float,
            'mensaje_usuario': str,
        }

    Raises:
        ValueError: Si id_pregunta no existe en base de datos

    Ejemplo retorno:
        {
            'id_pregunta': 42,
            'num_palabras': 87,
            'umbral_segundos': 5.8,
            'mensaje_usuario': 'Lee detenidamente. Espera 5.8 segundos antes de responder.'
        }
    """
    try:
        logger.info(f"Calculando umbral de impulsividad para pregunta {id_pregunta}")

        # Step 1: Consultar pregunta
        pregunta = session.query(PreguntaIA).filter(PreguntaIA.id_pregunta == id_pregunta).first()

        if not pregunta:
            logger.error(f"Pregunta con ID {id_pregunta} no encontrada")
            raise ValueError(f"Pregunta con ID {id_pregunta} no existe")

        if not pregunta.activa:
            logger.warning(f"Pregunta {id_pregunta} no está activa")
            raise ValueError(f"Pregunta con ID {id_pregunta} no está activa")

        # Step 2: Contar palabras
        num_palabras = contar_palabras(pregunta.texto_inedito)

        # Step 3: Calcular umbral
        # Fórmula: 1 segundo por cada 15 palabras, mínimo 2 segundos
        umbral_segundos = max(2.0, round(num_palabras / 15, 1))

        # Step 4: Generar mensaje para usuario
        mensaje_usuario = (
            f"Lee detenidamente. Espera {umbral_segundos} segundos antes de responder."
        )

        respuesta = {
            "id_pregunta": id_pregunta,
            "num_palabras": num_palabras,
            "umbral_segundos": umbral_segundos,
            "mensaje_usuario": mensaje_usuario,
        }

        logger.info(
            f"Umbral calculado - Pregunta: {id_pregunta}, Palabras: {num_palabras}, "
            f"Umbral: {umbral_segundos}s"
        )
        return respuesta

    except ValueError as e:
        logger.error(f"Error de validación en calcular_umbral_tiempo_minimo: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado en calcular_umbral_tiempo_minimo: {str(e)}")
        raise
