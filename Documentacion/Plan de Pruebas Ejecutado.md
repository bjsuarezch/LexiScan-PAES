# Plan de Pruebas Ejecutado - LexiScan PAES

Este documento registra los resultados de la ejecución de la suite de pruebas automatizadas del backend (FastAPI) de LexiScan PAES utilizando el framework `pytest`.

## 1. Resumen de la Ejecución
- **Fecha de Ejecución**: 04/06/2026
- **Entorno**: Entorno local Windows 11, Python 3.10.7
- **Herramienta**: pytest-9.0.3, anyio-4.13.0
- **Total de Casos de Prueba Ejecutados**: 32
- **Resultados Globales**: 
  - ✅ **Pasados**: 8
  - ❌ **Fallidos**: 21
  - ⚠️ **Errores**: 3

## 2. Detalle de Casos de Prueba Funcionales Ejecutados

### I. Módulo de Autenticación
| ID Caso | Descripción | Resultado | Observación / Recomendación |
| --- | --- | --- | --- |
| **CP-AUTH-01** | Inicio de sesión con credenciales válidas (`test_login`) | ❌ Fallido | Falla de conexión a BD (`ConnectionRefusedError: [WinError 10061]`). *Recomendación*: Configurar un entorno de base de datos de pruebas aislado y en ejecución antes de lanzar la suite. |

### II. Módulo de Integración IA y Endpoints
| ID Caso | Descripción | Resultado | Observación / Recomendación |
| --- | --- | --- | --- |
| **CP-IA-01** | Recomendaciones para usuario válido | ❌ Fallido | Dependencia de base de datos no disponible y/o variables de entorno de API Key no configuradas. |
| **CP-IA-02** | Recomendaciones usuario inválido | ❌ Fallido | Manejo de excepciones al fallar la consulta. |
| **CP-IA-03** | Cálculo de latencia en recomendaciones | ❌ Fallido | Timeout alcanzado por lentitud de la red / falta de stub. *Recomendación*: Usar `unittest.mock` para simular la API externa de IA. |
| **CP-IA-04** | Umbral de impulsividad (Pregunta válida) | ❌ Fallido | Error de lógica de acceso a datos sin mock. |

### III. Módulo de Servicios Internos y Gamificación
| ID Caso | Descripción | Resultado | Observación / Recomendación |
| --- | --- | --- | --- |
| **CP-SERV-01** | Obtención de las 2 habilidades más débiles | ❌ Fallido | Error de base de datos. |
| **CP-SERV-02** | Retorno de estructura correcta (habilidad, maestría) | ❌ Fallido | Excepción de BD. |
| **CP-SERV-03** | Obtención de errores frecuentes respetando el límite | ❌ Fallido | Falla de la sesión SQLAlchemy. |
| **CP-SERV-04** | Cálculo de umbral de impulsividad (mínimo 2 seg) | ❌ Fallido | Excepción lanzada en servicio. |
| **CP-SERV-05** | Habilidades ordenadas por maestría | ❌ Fallido | Excepción en procesamiento de la consulta. |
| **CP-SERV-06** | Acceso a Dashboard (`test_dashboard`) | ⚠️ Error | Error fatal durante la inicialización del fixture de prueba. |

## 3. Análisis y Conclusión
La suite de pruebas automatizadas está correctamente estructurada, abarcando las funcionalidades críticas del sistema (autenticación, integración con IA, cálculo de umbrales y gamificación). Sin embargo, la gran cantidad de casos fallidos (ConnectionRefusedError) indica que **las pruebas actuales están fuertemente acopladas a la base de datos de producción/desarrollo local** y no se están inyectando dependencias falsas (mocks).

**Plan de Acción para Siguientes Sprints:**
1. **Implementar Mocks**: Configurar `pytest-mock` para aislar las llamadas a la API de IA y a la base de datos PostgreSQL.
2. **Base de Datos en Memoria**: Configurar SQLite temporal en memoria para pruebas de integración o levantar un contenedor Docker en el pipeline de CI/CD.
3. **Variables de Entorno**: Proveer un archivo `.env.test` con variables de entorno de prueba para evitar fallos por configuración faltante.
