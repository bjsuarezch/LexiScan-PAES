import sys
import os
import random
import bcrypt
from datetime import datetime, timezone

# Agregar el directorio backend al sys.path para poder importar database y models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
import models

def generate_rut():
    # Genera un RUT ficticio con formato chileno básico 12345678-9
    num = random.randint(10000000, 25000000)
    dv = random.choice('0123456789K')
    return f"{num}-{dv}"

def seed_users():
    db = SessionLocal()
    try:
        print("Empezando a generar 50 usuarios ficticios...")
        pass_hash = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        habilidades_tipos = ['Localizar', 'Interpretar', 'Evaluar', 'Lectura_Critica', 'Vocabulario', 'Tipos_de_Texto']
        
        for i in range(50):
            rut = generate_rut()
            # Asegurar unicidad del RUT generado
            while db.query(models.Usuario).filter(models.Usuario.rut == rut).first():
                rut = generate_rut()
            
            nombre = f"Estudiante Ficticio {i+1}"
            email = f"estudiante{i+1}_{rut}@fake.lexiscan.cl"
            
            # 1. Crear Usuario
            user = models.Usuario(
                rut=rut,
                nombre_completo=nombre,
                email=email,
                password_hash=pass_hash,
                xp_total=random.randint(100, 5000),
                racha_actual=random.randint(0, 30),
                fecha_registro=datetime.now(timezone.utc),
                activo=True,
                es_admin=False,
                textos_restantes=3
            )
            db.add(user)
            db.flush() # Para asegurarnos de que el usuario exista en la transacción
            
            # 2. Crear Billetera (EconomiaMonedas)
            wallet = models.EconomiaMonedas(
                rut_usuario=rut,
                saldo_monedas=random.randint(0, 1000),
                total_acumulado=random.randint(1000, 5000),
                ultima_transaccion=datetime.now(timezone.utc)
            )
            db.add(wallet)
            
            # 3. Crear Historial de Habilidades
            for skill in habilidades_tipos:
                hab = models.HistorialHabilidades(
                    rut_usuario=rut,
                    nombre_habilidad=skill,
                    nivel_maestria=round(random.uniform(10.0, 95.0), 2),
                    ultima_actualizacion=datetime.now(timezone.utc)
                )
                db.add(hab)
                
            db.commit()
            if (i+1) % 10 == 0:
                print(f"Progreso: {i+1}/50 usuarios creados...")
            
        print("\n¡Semilla (seed) de 50 usuarios insertada exitosamente!")
        print("Puedes loguearte con cualquiera de los emails generados y la contraseña: password123")
        
    except Exception as e:
        print(f"Error durante el seed de usuarios: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
