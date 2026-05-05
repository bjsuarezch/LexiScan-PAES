import json
import http.client
import time

BASE_URL = '127.0.0.1'
PORT = 8001
TIMEOUT_SECONDS = 5


def request(method, path, body=None, headers=None):
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


def expect_quick(action_name, start):
    elapsed = time.time() - start
    assert elapsed < 5, f'{action_name} excedió 5 segundos: {elapsed:.2f}s'


def test_login():
    start = time.time()
    status, data = request('POST', '/login', {'rut': '12345678-9', 'contrasena': 'Test1234'})
    expect_quick('Login', start)
    assert status == 200, f'Login fallido: {status} {data}'
    assert data['rut'] == '12345678-9'
    return data


def test_dashboard(rut):
    start = time.time()
    status, data = request('GET', f'/dashboard/{rut}')
    expect_quick('Dashboard', start)
    assert status == 200, f'Dashboard fallido: {status} {data}'
    assert 'habilidades' in data
    return data


def test_habilidad(rut, habilidad):
    start = time.time()
    status, data = request('GET', f'/habilidades/{habilidad}?rut={rut}')
    expect_quick('Habilidad', start)
    assert status == 200, f'Habilidad fallida: {status} {data}'
    assert 'preguntas' in data
    return data


def test_examen(rut):
    start = time.time()
    status, data = request('POST', '/examen', {'rut': rut, 'cantidad_preguntas': 10})
    expect_quick('Examen', start)
    assert status == 200, f'Examen fallido: {status} {data}'
    assert data['cantidad_preguntas'] == 10
    return data


if __name__ == '__main__':
    print('Ejecutando pruebas de integración...')
    login = test_login()
    dashboard = test_dashboard(login['rut'])
    habilidad = test_habilidad(login['rut'], dashboard['habilidades'][0]['nombre_habilidad'])
    examen = test_examen(login['rut'])
    print('Login:', login['rut'])
    print('Dashboard skills:', [h['nombre_habilidad'] for h in dashboard['habilidades']])
    print('Habilidad cargada:', habilidad['nombre_habilidad'])
    print('Examen creado:', examen['id_examen'])
    print('Todas las pruebas pasaron en menos de 5 segundos cada una.')
