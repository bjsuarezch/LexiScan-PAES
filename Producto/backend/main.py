from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import crud, database, models, schemas

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title='LexiScan API', version='0.1.0')

origins = [
    "http://localhost:4200", # El puerto de tu Angular
    "http://127.0.0.1:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/register', response_model=schemas.UserResponse)
def register(user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_rut = crud.get_user_by_rut(db, user_create.rut)
    if existing_rut:
        raise HTTPException(status_code=400, detail='El RUT ya existe')

    existing_email = crud.get_user_by_email(db, user_create.email)
    if existing_email:
        raise HTTPException(status_code=400, detail='El email ya está registrado')

    user = crud.create_user(
        db,
        rut=user_create.rut,
        nombre_completo=user_create.nombre_completo,
        email=user_create.email,
        contrasena=user_create.contrasena,
    )
    return user


@app.post('/login', response_model=schemas.UserResponse)
def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, login_data.rut, login_data.contrasena)
    if not user:
        raise HTTPException(status_code=401, detail='RUT o contraseña incorrectos')
    return user


@app.get('/dashboard/{rut}', response_model=schemas.DashboardResponse)
def dashboard(rut: str, db: Session = Depends(get_db)):
    data = crud.get_dashboard_data(db, rut)
    if not data:
        raise HTTPException(status_code=404, detail='Usuario no encontrado')
    return data


@app.get('/habilidades/{habilidad}', response_model=schemas.HabilidadDetailResponse)
def habilidad_detail(habilidad: str, rut: str, db: Session = Depends(get_db)):
    data = crud.get_habilidad_content(db, rut, habilidad)
    if not data:
        raise HTTPException(status_code=404, detail='Habilidad no encontrada')
    return data


@app.post('/examen', response_model=schemas.ExamenResponse)
def crear_examen(examen_request: schemas.ExamenRequest, db: Session = Depends(get_db)):
    try:
        data = crud.create_exam_session(db, examen_request.rut, examen_request.cantidad_preguntas)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not data:
        raise HTTPException(status_code=404, detail='Usuario no encontrado')
    return data
