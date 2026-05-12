"""
Tests de integración para endpoints CU10 (recomendaciones) y CU8 (impulsividad).

Ejecutar con: python backend/tests/test_endpoints_integracion.py

Notas:
- Ejecuta requests HTTP contra servidor FastAPI local
- Valida respuestas HTTP 200, 404, 500
- Valida latencia < 2 segundos por endpoint
- Requiere servidor corriendo en http://127.0.0.1:8001

Precondiciones:
1. Base de datos PostgreSQL running
2. FastAPI server running: uvicorn main:app --host 127.0.0.1 --port 8001
3. Usuario con RUT '12345678-9' y al menos 1 pregunta activa en BD
"""

import json
import http.client
import time

BASE_URL = '127.0.0.1'
PORT = 8001
TIMEOUT_SECONDS = 5


def request(method, path, body=None, headers=None):
    """Realiza un request HTTP."""
    conn = http.client.HTTPConnection(BASE_URL, PORT, timeout=TIMEOUT_SECONDS)
    headers = headers or {}
    if body is not None:
        body = json.dumps(body)
        headers['Content-Type'] = 'application/json'
    conn.request(method, path, body=body, headers=headers)
    response = conn.getresponse()
    payload = response.read().decode('utf-8')
    conn.close()
    try:
        data = json.loads(payload) if payload else None
    except json.JSONDecodeError:
        data = payload
    return response.status, data


def expect_quick(action_name, start, max_seconds=5):
    """Valida que la acción completó dentro del tiempo máximo."""
    elapsed = time.time() - start
    assert elapsed < max_seconds, f'{action_name} excedió {max_seconds} segundos: {elapsed:.2f}s'
    print(f"✓ {action_name} completó en {elapsed:.2f}s")


# ============================================================================
# TEST 1: GET /usuarios/{rut}/recomendaciones (CU10)
# ============================================================================

def test_recomendaciones_usuario_valido():
    """Test endpoint de recomendaciones con usuario válido."""
    print("\n" + "="*70)
    print("TEST: GET /usuarios/{rut}/recomendaciones (CU10 - Recomendaciones)")
    print("="*70)
    
    rut = '12345678-9'
    start = time.time()
    
    status, data = request('GET', f'/usuarios/{rut}/recomendaciones')
    
    expect_quick('Recomendaciones (usuario válido)', start, max_seconds=2)
    
    assert status == 200, f'Status esperado 200, obtenido {status}. Response: {data}'
    
    # Validar estructura de respuesta
    assert 'rut' in data, "Campo 'rut' faltante en respuesta"
    assert data['rut'] == rut, f"RUT en respuesta no coincide: {data['rut']} != {rut}"
    
    assert 'habilidades_debiles' in data, "Campo 'habilidades_debiles' faltante"
    assert isinstance(data['habilidades_debiles'], list), "habilidades_debiles debe ser lista"
    assert len(data['habilidades_debiles']) <= 2, "No debe haber más de 2 habilidades débiles"
    
    if len(data['habilidades_debiles']) > 0:
        # Validar estructura de cada habilidad débil
        for hab in data['habilidades_debiles']:
            assert 'nombre' in hab, "Campo 'nombre' faltante en habilidad"
            assert 'nivel_maestria' in hab, "Campo 'nivel_maestria' faltante en habilidad"
            assert 'sugerencia' in hab, "Campo 'sugerencia' faltante en habilidad"
            assert 0 <= hab['nivel_maestria'] <= 100, "nivel_maestria debe estar entre 0-100"
    
    assert 'errores_frecuentes' in data, "Campo 'errores_frecuentes' faltante"
    assert isinstance(data['errores_frecuentes'], list), "errores_frecuentes debe ser lista"
    assert len(data['errores_frecuentes']) <= 3, "No debe haber más de 3 errores frecuentes"
    
    if len(data['errores_frecuentes']) > 0:
        # Validar estructura de cada error frecuente
        for error in data['errores_frecuentes']:
            assert 'id_pregunta' in error, "Campo 'id_pregunta' faltante en error"
            assert 'enunciado' in error, "Campo 'enunciado' faltante en error"
            assert 'veces_fallada' in error, "Campo 'veces_fallada' faltante en error"
            assert error['veces_fallada'] > 0, "veces_fallada debe ser > 0"
    
    assert 'proxima_practica_sugerida' in data, "Campo 'proxima_practica_sugerida' faltante"
    assert isinstance(data['proxima_practica_sugerida'], str), "proxima_practica_sugerida debe ser string"
    
    print(f"✓ Estructura de respuesta validada correctamente")
    print(f"  - Habilidades débiles: {len(data['habilidades_debiles'])}")
    print(f"  - Errores frecuentes: {len(data['errores_frecuentes'])}")
    print(f"  - Sugerencia: {data['proxima_practica_sugerida'][:50]}...")


def test_recomendaciones_usuario_invalido():
    """Test endpoint de recomendaciones con usuario que no existe."""
    print("\n" + "="*70)
    print("TEST: GET /usuarios/{rut}/recomendaciones - Usuario inválido (404)")
    print("="*70)
    
    rut_invalido = '99999999-9'
    start = time.time()
    
    status, data = request('GET', f'/usuarios/{rut_invalido}/recomendaciones')
    
    expect_quick('Recomendaciones (usuario inválido)', start, max_seconds=2)
    
    assert status == 404, f'Status esperado 404, obtenido {status}. Response: {data}'
    assert 'detail' in data, "Campo 'detail' (error) faltante en respuesta 404"
    
    print(f"✓ Endpoint retorna 404 correctamente para usuario inexistente")
    print(f"  - Error: {data['detail']}")


# ============================================================================
# TEST 2: GET /preguntas/{id_pregunta}/umbral-impulsividad (CU8)
# ============================================================================

def test_umbral_impulsividad_pregunta_valida():
    """Test endpoint de umbral de impulsividad con pregunta válida."""
    print("\n" + "="*70)
    print("TEST: GET /preguntas/{id_pregunta}/umbral-impulsividad (CU8 - Impulsividad)")
    print("="*70)
    
    # ID de pregunta que debe existir en BD (ajustar según datos reales)
    id_pregunta = 1
    start = time.time()
    
    status, data = request('GET', f'/preguntas/{id_pregunta}/umbral-impulsividad')
    
    expect_quick('Umbral de impulsividad (pregunta válida)', start, max_seconds=0.5)
    
    assert status == 200, f'Status esperado 200, obtenido {status}. Response: {data}'
    
    # Validar estructura de respuesta
    assert 'id_pregunta' in data, "Campo 'id_pregunta' faltante en respuesta"
    assert data['id_pregunta'] == id_pregunta, f"ID en respuesta no coincide: {data['id_pregunta']} != {id_pregunta}"
    
    assert 'num_palabras' in data, "Campo 'num_palabras' faltante"
    assert isinstance(data['num_palabras'], int), "num_palabras debe ser entero"
    assert data['num_palabras'] >= 0, "num_palabras debe ser >= 0"
    
    assert 'umbral_segundos' in data, "Campo 'umbral_segundos' faltante"
    assert isinstance(data['umbral_segundos'], (int, float)), "umbral_segundos debe ser número"
    assert data['umbral_segundos'] >= 2.0, "umbral_segundos debe ser >= 2 segundos (mínimo)"
    
    # Validar fórmula: umbral = max(2, round(palabras / 15, 1))
    umbral_esperado = max(2.0, round(data['num_palabras'] / 15, 1))
    assert data['umbral_segundos'] == umbral_esperado, \
        f"Umbral incorrecto: {data['umbral_segundos']} != {umbral_esperado}"
    
    assert 'mensaje_usuario' in data, "Campo 'mensaje_usuario' faltante"
    assert isinstance(data['mensaje_usuario'], str), "mensaje_usuario debe ser string"
    assert 'Lee detenidamente' in data['mensaje_usuario'] or 'Espera' in data['mensaje_usuario'], \
        "Mensaje debe contener instrucciones de lectura"
    
    print(f"✓ Estructura de respuesta validada correctamente")
    print(f"  - ID Pregunta: {data['id_pregunta']}")
    print(f"  - Palabras: {data['num_palabras']}")
    print(f"  - Umbral: {data['umbral_segundos']} segundos")
    print(f"  - Mensaje: {data['mensaje_usuario']}")


def test_umbral_impulsividad_pregunta_invalida():
    """Test endpoint de umbral con pregunta que no existe."""
    print("\n" + "="*70)
    print("TEST: GET /preguntas/{id_pregunta}/umbral-impulsividad - Pregunta inválida (404)")
    print("="*70)
    
    id_pregunta_invalido = 999999
    start = time.time()
    
    status, data = request('GET', f'/preguntas/{id_pregunta_invalido}/umbral-impulsividad')
    
    expect_quick('Umbral (pregunta inválida)', start, max_seconds=2)
    
    assert status == 404, f'Status esperado 404, obtenido {status}. Response: {data}'
    assert 'detail' in data, "Campo 'detail' (error) faltante en respuesta 404"
    
    print(f"✓ Endpoint retorna 404 correctamente para pregunta inexistente")
    print(f"  - Error: {data['detail']}")


# ============================================================================
# TESTS DE LATENCIA
# ============================================================================

def test_latencia_recomendaciones():
    """Valida que recomendaciones responde en < 2 segundos."""
    print("\n" + "="*70)
    print("TEST: Validación de latencia - Recomendaciones (objetivo: < 2s)")
    print("="*70)
    
    rut = '12345678-9'
    tiempos = []
    
    for i in range(5):
        start = time.time()
        status, data = request('GET', f'/usuarios/{rut}/recomendaciones')
        elapsed = time.time() - start
        tiempos.append(elapsed)
        
        assert status == 200, f"Request {i+1} retornó status {status}"
        print(f"  - Request {i+1}: {elapsed:.3f}s")
    
    promedio = sum(tiempos) / len(tiempos)
    maximo = max(tiempos)
    
    print(f"\nPromedio: {promedio:.3f}s")
    print(f"Máximo: {maximo:.3f}s")
    
    assert maximo < 2.0, f"Latencia máxima excedió 2 segundos: {maximo:.3f}s"
    print(f"✓ Latencia dentro de especificación (<2s)")


def test_latencia_umbral():
    """Valida que umbral-impulsividad responde en < 500ms."""
    print("\n" + "="*70)
    print("TEST: Validación de latencia - Impulsividad (objetivo: < 500ms)")
    print("="*70)
    
    id_pregunta = 1
    tiempos = []
    
    for i in range(5):
        start = time.time()
        status, data = request('GET', f'/preguntas/{id_pregunta}/umbral-impulsividad')
        elapsed = time.time() - start
        tiempos.append(elapsed)
        
        assert status == 200, f"Request {i+1} retornó status {status}"
        print(f"  - Request {i+1}: {elapsed:.3f}s")
    
    promedio = sum(tiempos) / len(tiempos)
    maximo = max(tiempos)
    
    print(f"\nPromedio: {promedio:.3f}s")
    print(f"Máximo: {maximo:.3f}s")
    
    assert maximo < 0.5, f"Latencia máxima excedió 500ms: {maximo:.3f}s"
    print(f"✓ Latencia dentro de especificación (<500ms)")


# ============================================================================
# MAIN: Ejecutar todos los tests
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("TESTS DE INTEGRACIÓN: CU10 (Recomendaciones) + CU8 (Impulsividad)")
    print("="*70)
    
    try:
        # Tests de funcionalidad
        test_recomendaciones_usuario_valido()
        test_recomendaciones_usuario_invalido()
        test_umbral_impulsividad_pregunta_valida()
        test_umbral_impulsividad_pregunta_invalida()
        
        # Tests de latencia
        test_latencia_recomendaciones()
        test_latencia_umbral()
        
        print("\n" + "="*70)
        print("✓ TODOS LOS TESTS PASARON CORRECTAMENTE")
        print("="*70 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FALLIDO: {str(e)}\n")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        raise
