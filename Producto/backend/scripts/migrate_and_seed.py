import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, SessionLocal
import models
from sqlalchemy import text

def reset_and_seed():
    print("1. Borrando tablas afectadas y recreando esquema...")
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS errores_favoritos CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS sesion_preguntas CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS preguntas_ia CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS banco_preguntas CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS temas CASCADE;"))
        conn.commit()
    print("2. Creando tablas nuevas/actualizadas...")
    models.Base.metadata.create_all(bind=engine)

    with engine.connect() as conn:
        # Agregamos las columnas a usuarios si no existen
        try:
            conn.execute(text("ALTER TABLE usuarios ADD COLUMN tema_actual_id INTEGER REFERENCES temas(id_tema);"))
        except Exception as e:
            print(f"Nota: (tema_actual_id) {e}")
        try:
            conn.execute(text("ALTER TABLE usuarios ADD COLUMN textos_restantes INTEGER NOT NULL DEFAULT 0;"))
        except Exception as e:
            print(f"Nota: (textos_restantes) {e}")
        conn.commit()

    print("3. Poblando temas fijos y textos de ejemplo...")
    db = SessionLocal()
    try:
        # Crear temas
        tema_tesla = models.Tema(nombre="Tesla", es_custom=False, activo=True)
        tema_musica = models.Tema(nombre="Música de los 70s", es_custom=False, activo=True)
        tema_transformers = models.Tema(nombre="Transformers", es_custom=False, activo=True)
        tema_myhero = models.Tema(nombre="My Hero Academia", es_custom=False, activo=True)
        
        db.add_all([tema_tesla, tema_musica, tema_transformers, tema_myhero])
        db.commit()

        # Agregar un usuario sistema para amarrar las habilidades globales
        system_rut = '00000000-0'
        user_sys = db.query(models.Usuario).filter(models.Usuario.rut == system_rut).first()
        if not user_sys:
            import bcrypt
            pass_hash = bcrypt.hashpw('system'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user_sys = models.Usuario(rut=system_rut, nombre_completo='Sistema', email='sys@lexiscan.cl', password_hash=pass_hash)
            db.add(user_sys)
            
            from datetime import datetime, timezone
            for skill in ['Localizar', 'Interpretar', 'Evaluar', 'Lectura_Critica', 'Vocabulario', 'Tipos_de_Texto']:
                db.add(models.HistorialHabilidades(
                    rut_usuario=system_rut,
                    nombre_habilidad=skill,
                    nivel_maestria=0.0,
                    ultima_actualizacion=datetime.now(timezone.utc)
                ))
            db.commit()

        # Conseguir el id_habilidad de 'Localizar'
        habilidad_localizar = db.query(models.HistorialHabilidades).filter(
            models.HistorialHabilidades.nombre_habilidad == 'Localizar',
            models.HistorialHabilidades.rut_usuario == system_rut
        ).first()

        import json
        if habilidad_localizar:
            # Crear 3 textos de ejemplo para Tesla
            texto_tesla = [
                {"tipo": "parrafo", "contenido": "Tesla, Inc. es una empresa estadounidense con sede en Austin, Texas, liderada por Elon Musk."},
                {"tipo": "dato_clave", "contenido": "Fundada en 2003, Tesla se ha convertido en el fabricante de automóviles más valioso del mundo."},
                {"tipo": "imagen", "concepto": "tesla car"},
                {"tipo": "grafico_barra", "datos": [{"etiqueta": "2020", "valor": 50}, {"etiqueta": "2021", "valor": 80}, {"etiqueta": "2022", "valor": 100}]}
            ]
            for i in range(3):
                pregunta = models.BancoPreguntas(
                    id_habilidad=habilidad_localizar.id_progreso,
                    id_tema=tema_tesla.id_tema,
                    texto_inedito=texto_tesla,  # Es JSON column
                    enunciado=f"Pregunta de prueba Tesla {i+1}",
                    alternativas={"A": "Correcta", "B": "Falsa", "C": "Falsa", "D": "Falsa"},
                    respuesta_correcta="A",
                    justificacion_cot="Porque sí",
                    activa=True
                )
                db.add(pregunta)
            db.commit()
            print("Textos de Tesla insertados correctamente.")

    except Exception as e:
        print(f"Error durante el seed: {e}")
        db.rollback()
    finally:
        db.close()
    
    print("Migración y Seed completado (esquema).")

if __name__ == "__main__":
    reset_and_seed()
