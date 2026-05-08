#!/usr/bin/env python3
"""
Script para poblar el banco de preguntas con contenido generado por IA.
Genera 50 preguntas distribuidas en las diferentes habilidades.
"""

import os
import sys
import json
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from database import SessionLocal
import crud
import models

def seed_pool():
    """Genera y guarda preguntas en el banco de preguntas."""
    db: Session = SessionLocal()

    try:
        # Obtener configuración
        api_key = crud.get_configuracion(db, 'GROQ_API_KEY')
        modelo = 'llama-3.1-8b-instant'  # Forzar modelo pequeño

        if not api_key:
            print("Error: GROQ_API_KEY no configurada")
            return

        # Generar preguntas para todas las habilidades en un solo call
        habilidades = [
            'Localizar',
            'Interpretar',
            'Evaluar',
            'Lectura_Critica',
            'Vocabulario',
            'Tipos_de_Texto'
        ]

        total_preguntas = 5  # Reducir aún más
        preguntas_por_habilidad = total_preguntas // len(habilidades)

        print(f"Generando {total_preguntas} preguntas distribuidas en {len(habilidades)} habilidades...")

        # Generar textos con preguntas para todas las habilidades
        textos_data = crud.generate_exam_questions(total_preguntas, api_key, modelo)

        for q_data in textos_data:
            # Obtener id_habilidad
            id_habilidad = crud.get_habilidad_id(db, crud.normalize_habilidad_name(q_data['habilidad']))
            if not id_habilidad:
                print(f"Advertencia: Habilidad {q_data['habilidad']} no encontrada, saltando...")
                continue

            # Crear pregunta en el banco
            pregunta = models.BancoPreguntas(
                id_habilidad=id_habilidad,
                texto_inedito=q_data['texto_inedito'],
                enunciado=q_data['enunciado'],
                alternativas=q_data['alternativas'],
                respuesta_correcta=q_data['respuesta_correcta'],
                justificacion_cot=q_data['justificacion_cot'],
                dificultad='medio'  # Por defecto medio
            )
            db.add(pregunta)

        db.commit()
        print("Banco de preguntas poblado exitosamente!")

        # Contar preguntas
        total = db.query(models.BancoPreguntas).count()
        print(f"Total de preguntas en el banco: {total}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_pool()