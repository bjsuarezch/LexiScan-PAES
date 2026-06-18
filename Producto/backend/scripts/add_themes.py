import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, SessionLocal
import models

def add_new_themes():
    print("Agregando nuevos temas a la base de datos...")
    db = SessionLocal()
    try:
        nuevos_nombres = [
            "Mitología Griega",
            "Exploración Espacial",
            "Inteligencia Artificial",
            "Cambio Climático",
            "Cultura Pop Coreana",
            "Literatura Latinoamericana",
            "Biología Marina",
            "Videojuegos Retro",
            "Psicología Humana",
            "Misterios Sin Resolver",
            "Deportes Extremos",
            "Avances Médicos"
        ]

        # Check existing to avoid duplicates
        temas_existentes = db.query(models.Tema.nombre).filter(models.Tema.nombre.in_(nuevos_nombres)).all()
        nombres_existentes = {t[0] for t in temas_existentes}

        nuevos_temas = []
        for nombre in nuevos_nombres:
            if nombre not in nombres_existentes:
                nuevos_temas.append(models.Tema(nombre=nombre, es_custom=False, activo=True))
        
        if nuevos_temas:
            db.add_all(nuevos_temas)
            db.commit()
            print(f"Se agregaron {len(nuevos_temas)} temas nuevos.")
        else:
            print("Todos los temas nuevos ya existen en la base de datos.")

    except Exception as e:
        print(f"Error al agregar temas: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_new_themes()
