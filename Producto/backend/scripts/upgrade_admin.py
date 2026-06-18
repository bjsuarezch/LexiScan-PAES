import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, SessionLocal
import models
from sqlalchemy import text
import bcrypt

def upgrade_database():
    print("Iniciando actualización de base de datos para Administrador...")
    
    # 1. Alterar tabla usuarios
    with engine.connect() as conn:
        try:
            print("Agregando columna 'es_admin' a la tabla 'usuarios'...")
            conn.execute(text("ALTER TABLE usuarios ADD COLUMN es_admin BOOLEAN NOT NULL DEFAULT FALSE;"))
            conn.commit()
            print("Columna agregada exitosamente.")
        except Exception as e:
            print(f"Nota (es_admin): La columna ya podría existir o hubo un error: {e}")
            conn.rollback()

    # 2. Crear usuario administrador
    db = SessionLocal()
    try:
        admin_rut = "admin-1"
        admin_email = "admin@lexiscan.cl"
        
        # Verificar si ya existe
        existing_admin = db.query(models.Usuario).filter(models.Usuario.rut == admin_rut).first()
        if not existing_admin:
            print(f"Creando usuario administrador: {admin_email}")
            pass_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            new_admin = models.Usuario(
                rut=admin_rut,
                nombre_completo="Administrador",
                email=admin_email,
                password_hash=pass_hash,
                es_admin=True,
                activo=True
            )
            db.add(new_admin)
            
            # Init wallet and skills for the new user just to be safe
            wallet = models.EconomiaMonedas(rut_usuario=admin_rut, saldo_monedas=9999, total_acumulado=9999)
            db.add(wallet)
            
            from datetime import datetime, timezone
            for skill in ['Localizar', 'Interpretar', 'Evaluar', 'Lectura_Critica', 'Vocabulario', 'Tipos_de_Texto']:
                db.add(models.HistorialHabilidades(
                    rut_usuario=admin_rut,
                    nombre_habilidad=skill,
                    nivel_maestria=100.0,
                    ultima_actualizacion=datetime.now(timezone.utc)
                ))
            
            db.commit()
            print(f"Usuario Administrador creado exitosamente con contraseña 'admin123'.")
        else:
            print(f"El usuario administrador '{admin_email}' ya existe. Asegurando permisos...")
            existing_admin.es_admin = True
            db.commit()

    except Exception as e:
        print(f"Error al crear el administrador: {e}")
        db.rollback()
    finally:
        db.close()
        
    print("Actualización completada.")

if __name__ == "__main__":
    upgrade_database()
