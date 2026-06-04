# Plan de Pruebas - LexiScan PAES

## 1. Introducción
El presente documento detalla el Plan de Pruebas del sistema **LexiScan PAES**, una plataforma digital desarrollada para la gamificación y evaluación de habilidades para la prueba PAES. LexiScan está conformado por una aplicación móvil/web desarrollada en Angular y un backend impulsado por FastAPI y PostgreSQL, apoyado por modelos de inteligencia artificial para la generación de preguntas y evaluación adaptativa.

Este plan tiene por finalidad verificar el correcto funcionamiento del sistema en sus distintos módulos, evaluar la calidad general del software y documentar las funcionalidades críticas.

## 2. Alcance del Plan de Pruebas
Este plan contempla la validación de las siguientes áreas:

### 2.1 Aplicación Frontend (Angular)
- Autenticación de usuarios y gestión de sesión.
- Navegación por el mapa interactivo de misiones y selección de temas.
- Módulo de evaluación adaptativa y simulacros.
- Gamificación: economía de monedas, rachas y niveles de maestría.
- Panel de control y visualización de progreso.

### 2.2 Backend y API (FastAPI)
- Endpoints de autenticación (JWT) y registro de usuarios.
- Integración con IA (Sinclair/Gemini) para la generación de preguntas.
- Cálculo de maestría, umbrales de impulsividad y penalizaciones.
- Integridad referencial y triggers en la base de datos PostgreSQL.

## 3. Objetivos del Plan de Pruebas
- Validar el comportamiento correcto del sistema frente a entradas válidas e inválidas.
- Comprobar la integridad de los datos enviados entre frontend y backend.
- Verificar la correcta integración de la IA en la generación y evaluación de respuestas.
- Identificar errores funcionales y de interfaz.

## 4. Entorno de Pruebas
| Recurso | Especificación |
| --- | --- |
| Plataforma Frontend | Angular 18, Ionic, SCSS |
| Plataforma Backend | FastAPI (Python 3.10+), SQLAlchemy |
| Base de Datos | PostgreSQL 15+ |
| Inteligencia Artificial | Google Gemini API / Sinclair |
| Herramientas de Testing | Pytest, coverage, Postman |
| Entorno Local | Windows 11, Node.js, Python |

## 5. Arquitectura de Software
LexiScan PAES está diseñado bajo una arquitectura cliente-servidor:
- **Frontend**: Aplicación Angular (SPA) que interactúa con el usuario, maneja el estado local de la gamificación y presenta interfaces de usuario ricas y adaptables.
- **Backend**: API REST en FastAPI que expone servicios de negocio, maneja la seguridad mediante tokens JWT y orquesta llamadas a la IA.
- **Base de Datos**: PostgreSQL, alojando 9 tablas relacionales con triggers automáticos para recalcular maestría y llevar la economía del juego.

## 6. Matriz de Riesgos
| Riesgo | Fase | Probabilidad | Impacto | Acción de Mitigación |
| --- | --- | --- | --- | --- |
| Latencia en generación de preguntas IA | Desarrollo | Alta | Alto | Implementar caché, usar prompts optimizados y timeouts controlados. |
| Fallo en conexión a BD | QA | Media | Alto | Verificar variables de entorno y configurar pools de conexiones. |
| Cálculo de maestría inconsistente | Desarrollo | Baja | Medio | Escribir pruebas unitarias exhaustivas en los servicios de recálculo. |
| Problemas de renderizado en Angular | QA | Media | Bajo | Pruebas de compatibilidad en diferentes navegadores. |

## 7. Casos de Prueba Planificados

### I. Módulo de Autenticación y Usuarios
- **CP-AUTH-01**: Registro de nuevo usuario con datos válidos.
- **CP-AUTH-02**: Inicio de sesión correcto (generación de token).
- **CP-AUTH-03**: Bloqueo de acceso a endpoints protegidos sin token.

### II. Módulo de Inteligencia Artificial (Integración)
- **CP-IA-01**: Generación de recomendaciones para usuario válido.
- **CP-IA-02**: Cálculo del umbral de impulsividad por tipo de pregunta.
- **CP-IA-03**: Manejo de latencia en la conexión con la API de IA.

### III. Módulo de Servicios y Gamificación
- **CP-SERV-01**: Obtención de habilidades más débiles por usuario.
- **CP-SERV-02**: Obtención de errores frecuentes y actualización de maestría.
- **CP-SERV-03**: Restricción y paginación en el historial de sesiones.
