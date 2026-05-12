"""
Tests unitarios para los servicios: recomendaciones e impulsividad (CU10, CU8).

Ejecutar con: pytest backend/tests/test_servicios.py -v

Notas:
- Usa fixtures de pytest para crear sesiones de BD en memoria (sqlite)
- Prueba funciones en aislamiento con mocks de BD
- Cubre edge cases y errores esperados
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from decimal import Decimal

# Importar modelos y servicios
import sys
from pathlib import Path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from models import (
    Base,
    Usuario,
    HistorialHabilidades,
    HabilidadLectora,
    ErroresFavoritos,
    BancoPreguntas,
    PreguntaIA,
)
from services.impulsividad import contar_palabras, calcular_umbral_tiempo_minimo
from services.recomendaciones import (
    get_habilidades_mas_debiles,
    get_errores_frecuentes,
    generar_respuesta_recomendaciones,
)


# ============================================================================
# FIXTURES: Setup BD en memoria para tests
# ============================================================================


@pytest.fixture
def db_session():
    """
    Crea una BD SQLite en memoria para tests.
    Cada test obtiene una sesión nueva aislada.
    """
    # Usar SQLite en memoria
    engine = create_engine('sqlite:///:memory:', echo=False)
    
    # Crear todas las tablas
    Base.metadata.create_all(engine)
    
    # Crear sesión
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    
    yield session
    
    session.close()
    engine.dispose()


@pytest.fixture
def usuario_sample(db_session: Session) -> Usuario:
    """Crea un usuario de prueba."""
    usuario = Usuario(
        rut='12345678-9',
        nombre_completo='Juan Pérez',
        email='juan@example.com',
        password_hash='hash_seguro',
        xp_total=100,
        racha_actual=5,
        activo=True,
    )
    db_session.add(usuario)
    db_session.commit()
    return usuario


@pytest.fixture
def habilidades_sample(db_session: Session, usuario_sample: Usuario) -> list:
    """Crea habilidades de prueba para el usuario."""
    habilidades = []
    
    # Crear 6 habilidades con diferentes niveles
    niveles = [
        (HabilidadLectora.Evaluar, Decimal('25.5')),       # Más débil
        (HabilidadLectora.Vocabulario, Decimal('35.0')),   # Segundo más débil
        (HabilidadLectora.Localizar, Decimal('65.0')),
        (HabilidadLectora.Interpretar, Decimal('70.5')),
        (HabilidadLectora.Lectura_Critica, Decimal('80.0')),
        (HabilidadLectora.Tipos_de_Texto, Decimal('90.0')),
    ]
    
    for nombre, nivel in niveles:
        hab = HistorialHabilidades(
            rut_usuario=usuario_sample.rut,
            nombre_habilidad=nombre,
            nivel_maestria=nivel,
        )
        db_session.add(hab)
        habilidades.append(hab)
    
    db_session.commit()
    return habilidades


@pytest.fixture
def preguntas_sample(db_session: Session, habilidades_sample: list) -> list:
    """Crea preguntas de prueba en banco_preguntas."""
    preguntas = []
    
    # Crear 5 preguntas para la habilidad Evaluar
    evaluar_habilidad_id = habilidades_sample[0].id_progreso
    
    for i in range(5):
        pregunta = BancoPreguntas(
            id_habilidad=evaluar_habilidad_id,
            texto_inedito=f"Texto de prueba {i} con varias palabras para contar",
            enunciado=f"Pregunta de evaluación número {i}",
            alternativas={"A": "Opción A", "B": "Opción B", "C": "Opción C", "D": "Opción D"},
            respuesta_correcta='A',
            justificacion_cot="Porque esta es la respuesta correcta",
            dificultad='medio',
        )
        db_session.add(pregunta)
        preguntas.append(pregunta)
    
    db_session.commit()
    return preguntas


@pytest.fixture
def errores_sample(
    db_session: Session,
    usuario_sample: Usuario,
    habilidades_sample: list,
    preguntas_sample: list,
) -> list:
    """Crea errores favoritos para el usuario."""
    errores = []
    
    # Crear 3 errores para las primeras preguntas
    for i, pregunta in enumerate(preguntas_sample[:3]):
        error = ErroresFavoritos(
            rut_usuario=usuario_sample.rut,
            id_pregunta=pregunta.id_pregunta,
            id_habilidad=habilidades_sample[0].id_progreso,
            veces_fallada=5 - i,  # 5, 4, 3 veces falladas
            resuelta=False,
        )
        db_session.add(error)
        errores.append(error)
    
    db_session.commit()
    return errores


@pytest.fixture
def pregunta_ia_sample(db_session: Session, habilidades_sample: list) -> PreguntaIA:
    """Crea una pregunta en preguntas_ia para test de impulsividad."""
    pregunta = PreguntaIA(
        id_habilidad=habilidades_sample[0].id_progreso,
        texto_inedito=(
            "En el contexto de la literatura contemporánea, el análisis de las obras de "
            "autores latinoamericanos revela patrones recurrentes en la exploración de "
            "identidad y memoria colectiva. Estos temas, fundamentales en la construcción "
            "de narrativas post-coloniales, permiten a los lectores comprender mejor las "
            "dinámicas culturales que moldean las sociedades modernas. Mediante la lectura "
            "crítica de estas obras, podemos identificar cómo los autores utilizan técnicas "
            "literarias innovadoras para transmitir mensajes complejos sobre la experiencia "
            "humana en contextos de cambio social."
        ),
        enunciado="¿Cuál es el tema principal del texto?",
        alternativas={"A": "Historia", "B": "Literatura", "C": "Sociología", "D": "Filosofía"},
        respuesta_correcta='B',
        justificacion_cot="Porque el texto trata sobre análisis literario",
        activa=True,
    )
    db_session.add(pregunta)
    db_session.commit()
    return pregunta


# ============================================================================
# TESTS: contar_palabras()
# ============================================================================


class TestContarPalabras:
    """Tests para la función contar_palabras()."""

    def test_texto_normal(self):
        """Test con texto normal."""
        resultado = contar_palabras("Hola mundo de prueba")
        assert resultado == 4

    def test_texto_vacio(self):
        """Test con texto vacío."""
        assert contar_palabras("") == 0

    def test_texto_none(self):
        """Test con None."""
        assert contar_palabras(None) == 0

    def test_espacios_multiples(self):
        """Test con espacios múltiples entre palabras."""
        resultado = contar_palabras("Hola    mundo   de   prueba")
        assert resultado == 4

    def test_espacios_inicio_fin(self):
        """Test con espacios al inicio y final."""
        resultado = contar_palabras("   Hola mundo   ")
        assert resultado == 2

    def test_solo_espacios(self):
        """Test con solo espacios."""
        assert contar_palabras("     ") == 0

    def test_texto_largo(self):
        """Test con texto largo (simular párrafo)."""
        texto = " ".join(["palabra"] * 100)
        assert contar_palabras(texto) == 100

    def test_entrada_no_string(self):
        """Test con entrada que no es string."""
        assert contar_palabras(123) == 0


# ============================================================================
# TESTS: get_habilidades_mas_debiles()
# ============================================================================


class TestGetHabilidadesDebiles:
    """Tests para obtener habilidades más débiles."""

    @pytest.mark.asyncio
    async def test_obtiene_dos_mas_debiles(
        self,
        db_session: Session,
        usuario_sample: Usuario,
        habilidades_sample: list,
    ):
        """Test obtiene las 2 habilidades más débiles."""
        resultado = await get_habilidades_mas_debiles(usuario_sample.rut, db_session)
        
        assert len(resultado) == 2
        assert resultado[0][0] == 'Evaluar'  # Más débil (25.5%)
        assert resultado[1][0] == 'Vocabulario'  # Segundo más débil (35.0%)
        assert resultado[0][1] == 25.5
        assert resultado[1][1] == 35.0

    @pytest.mark.asyncio
    async def test_usuario_no_existe(self, db_session: Session):
        """Test con usuario que no existe."""
        with pytest.raises(ValueError, match="no encontrado"):
            await get_habilidades_mas_debiles('99999999-9', db_session)

    @pytest.mark.asyncio
    async def test_retorna_tuplas_name_maestria(
        self,
        db_session: Session,
        usuario_sample: Usuario,
        habilidades_sample: list,
    ):
        """Test que el formato retornado es correcto."""
        resultado = await get_habilidades_mas_debiles(usuario_sample.rut, db_session)
        
        for nombre, maestria in resultado:
            assert isinstance(nombre, str)
            assert isinstance(maestria, float)


# ============================================================================
# TESTS: get_errores_frecuentes()
# ============================================================================


class TestGetErroresFrecuentes:
    """Tests para obtener errores frecuentes."""

    @pytest.mark.asyncio
    async def test_obtiene_errores_por_habilidad(
        self,
        db_session: Session,
        usuario_sample: Usuario,
        habilidades_sample: list,
        errores_sample: list,
    ):
        """Test obtiene errores para habilidades específicas."""
        id_habilidades = [habilidades_sample[0].id_progreso]
        resultado = await get_errores_frecuentes(
            usuario_sample.rut, id_habilidades, db_session, limit=3
        )
        
        assert len(resultado) == 3
        # Verificar que está ordenado por veces_fallada (DESC)
        assert resultado[0]['veces_fallada'] == 5
        assert resultado[1]['veces_fallada'] == 4
        assert resultado[2]['veces_fallada'] == 3

    @pytest.mark.asyncio
    async def test_respeta_limit(
        self,
        db_session: Session,
        usuario_sample: Usuario,
        habilidades_sample: list,
        errores_sample: list,
    ):
        """Test que respeta el parámetro limit."""
        id_habilidades = [habilidades_sample[0].id_progreso]
        resultado = await get_errores_frecuentes(
            usuario_sample.rut, id_habilidades, db_session, limit=1
        )
        
        assert len(resultado) == 1

    @pytest.mark.asyncio
    async def test_lista_habilidades_vacia(
        self,
        db_session: Session,
        usuario_sample: Usuario,
    ):
        """Test con lista de habilidades vacía."""
        resultado = await get_errores_frecuentes(
            usuario_sample.rut, [], db_session
        )
        
        assert resultado == []

    @pytest.mark.asyncio
    async def test_estructura_respuesta(
        self,
        db_session: Session,
        usuario_sample: Usuario,
        habilidades_sample: list,
        errores_sample: list,
    ):
        """Test que la estructura de respuesta es correcta."""
        id_habilidades = [habilidades_sample[0].id_progreso]
        resultado = await get_errores_frecuentes(
            usuario_sample.rut, id_habilidades, db_session
        )
        
        for error in resultado:
            assert 'id_pregunta' in error
            assert 'enunciado' in error
            assert 'veces_fallada' in error
            assert 'id_habilidad' in error
            assert 'nombre_habilidad' in error


# ============================================================================
# TESTS: calcular_umbral_tiempo_minimo()
# ============================================================================


class TestCalcularUmbralImpulsividad:
    """Tests para calcular umbral de impulsividad."""

    @pytest.mark.asyncio
    async def test_calcula_umbral_correcto(
        self,
        db_session: Session,
        pregunta_ia_sample: PreguntaIA,
    ):
        """Test calcula umbral correcto basado en palabras."""
        resultado = await calcular_umbral_tiempo_minimo(
            pregunta_ia_sample.id_pregunta, db_session
        )
        
        assert resultado['id_pregunta'] == pregunta_ia_sample.id_pregunta
        assert resultado['num_palabras'] > 0
        assert resultado['umbral_segundos'] >= 2.0  # Mínimo 2 segundos
        assert isinstance(resultado['mensaje_usuario'], str)

    @pytest.mark.asyncio
    async def test_umbral_minimo_dos_segundos(
        self,
        db_session: Session,
        habilidades_sample: list,
    ):
        """Test que umbral mínimo es 2 segundos."""
        # Crear pregunta con texto muy corto (1-2 palabras)
        pregunta = PreguntaIA(
            id_habilidad=habilidades_sample[0].id_progreso,
            texto_inedito="Hola mundo",
            enunciado="¿Qué es esto?",
            alternativas={"A": "A", "B": "B", "C": "C", "D": "D"},
            respuesta_correcta='A',
            justificacion_cot="Prueba",
            activa=True,
        )
        db_session.add(pregunta)
        db_session.commit()
        
        resultado = await calcular_umbral_tiempo_minimo(pregunta.id_pregunta, db_session)
        assert resultado['umbral_segundos'] == 2.0

    @pytest.mark.asyncio
    async def test_pregunta_no_existe(self, db_session: Session):
        """Test con pregunta que no existe."""
        with pytest.raises(ValueError, match="no existe"):
            await calcular_umbral_tiempo_minimo(99999, db_session)

    @pytest.mark.asyncio
    async def test_pregunta_no_activa(
        self,
        db_session: Session,
        habilidades_sample: list,
    ):
        """Test con pregunta inactiva."""
        pregunta = PreguntaIA(
            id_habilidad=habilidades_sample[0].id_progreso,
            texto_inedito="Texto de prueba",
            enunciado="Pregunta",
            alternativas={"A": "A", "B": "B", "C": "C", "D": "D"},
            respuesta_correcta='A',
            justificacion_cot="Prueba",
            activa=False,
        )
        db_session.add(pregunta)
        db_session.commit()
        
        with pytest.raises(ValueError, match="no está activa"):
            await calcular_umbral_tiempo_minimo(pregunta.id_pregunta, db_session)


# ============================================================================
# TESTS: generar_respuesta_recomendaciones()
# ============================================================================


class TestGenerarRecomendaciones:
    """Tests para generar respuesta de recomendaciones."""

    @pytest.mark.asyncio
    async def test_genera_respuesta_completa(
        self,
        db_session: Session,
        usuario_sample: Usuario,
        habilidades_sample: list,
        errores_sample: list,
    ):
        """Test genera respuesta completa con estructura correcta."""
        resultado = await generar_respuesta_recomendaciones(
            usuario_sample.rut, db_session
        )
        
        assert resultado['rut'] == usuario_sample.rut
        assert len(resultado['habilidades_debiles']) == 2
        assert len(resultado['errores_frecuentes']) <= 3
        assert isinstance(resultado['proxima_practica_sugerida'], str)

    @pytest.mark.asyncio
    async def test_habilidades_ordenadas_por_maestria(
        self,
        db_session: Session,
        usuario_sample: Usuario,
        habilidades_sample: list,
        errores_sample: list,
    ):
        """Test que habilidades están ordenadas por maestría (menor primero)."""
        resultado = await generar_respuesta_recomendaciones(
            usuario_sample.rut, db_session
        )
        
        habs = resultado['habilidades_debiles']
        assert habs[0]['nivel_maestria'] < habs[1]['nivel_maestria']

    @pytest.mark.asyncio
    async def test_usuario_no_existe(self, db_session: Session):
        """Test con usuario que no existe."""
        with pytest.raises(ValueError):
            await generar_respuesta_recomendaciones('99999999-9', db_session)
