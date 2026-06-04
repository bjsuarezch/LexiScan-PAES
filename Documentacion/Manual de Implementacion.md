# Manual de Usuario e Implementación - LexiScan PAES

## 1. Objetivo
Este manual tiene como objetivo guiar a los usuarios (estudiantes y administradores) en el uso correcto y eficiente de la plataforma **LexiScan PAES**. Describe de forma práctica las funcionalidades disponibles, incluyendo el proceso de autenticación, visualización del mapa de temas, módulo de gamificación (monedas y rachas), simulacros de examen y el sistema de evaluación asistida por Inteligencia Artificial.

Su propósito es asegurar una experiencia fluida y detallar cómo el sistema fue implementado a nivel técnico para su correcta operación.

## 2. Perfiles y Usuarios Involucrados
A continuación, se especifica qué podrá realizar cada usuario según su nivel de acceso al sistema.

### Estudiante (Usuario Principal)
El estudiante accede a la plataforma para entrenar sus habilidades de lectura y evaluación PAES. Puede:
- Registrarse e iniciar sesión de forma segura.
- Visualizar su **Dashboard de Maestría** para entender sus fortalezas y debilidades en áreas clave.
- Acceder al mapa de temas (misiones y gimnasio) para entrenar con preguntas adaptativas.
- Contestar preguntas generadas dinámicamente por la IA y recibir feedback inmediato ("Justificación COT").
- Gestionar su billetera virtual de monedas y rachas de conexión.

---

## 3. Vistas y Funcionalidades Principales

### 3.1 Pantalla de Autenticación e Inicio
El acceso al sistema se realiza ingresando las credenciales (Correo y Contraseña).
- **Consideración Técnica**: Todas las operaciones utilizan autenticación mediante tokens JWT (JSON Web Tokens) gestionados por el backend FastAPI, garantizando seguridad sin estado (stateless).

### 3.2 Dashboard Principal
Una vez autenticado, el usuario es redirigido a la vista de "Resumen de Progreso".
- Muestra el **Nivel de Maestría** actual en competencias específicas (ej. Localizar, Interpretar, Evaluar).
- Muestra la racha actual de días consecutivos estudiando.
- **Implementación Backend**: Los datos son extraídos mediante consultas optimizadas y la vista `v_dashboard_maestria` de PostgreSQL, reduciendo la latencia de carga.

### 3.3 Selección de Tema y "El Gimnasio"
El usuario navega por un mapa visual (basado en componentes interactivos de Angular/SCSS) donde puede seleccionar diferentes "Mundos" o "Misiones".
- **Gimnasio**: Es un módulo enfocado en practicar específicamente los "Errores Favoritos". Los errores se priorizan y se guardan en la tabla `errores_favoritos` gracias a un *trigger* automatizado en la base de datos cuando el usuario se equivoca reiteradamente.

### 3.4 Módulo de Preguntas (IA Integrada)
Al iniciar una misión, la plataforma presenta un texto (muchas veces inédito) seguido de una pregunta con alternativas.
- **Implementación de IA**: Cuando se requiere contenido nuevo, el frontend solicita al backend que genere una pregunta. FastAPI se comunica con el servicio de Google Gemini / Sinclair API, pasándole el contexto y las directrices. La IA devuelve el enunciado, 4 alternativas, la respuesta correcta y la justificación.
- **Control de Impulsividad**: El sistema calcula el tiempo de respuesta del usuario frente al "Umbral de Impulsividad" (calculado a través del tamaño del texto y complejidad). Si responde más rápido que el umbral y se equivoca, el sistema lo califica como una "Respuesta Impulsiva".

### 3.5 Billetera y Gamificación (Economía Monedas)
- **Monedas**: El usuario gana monedas al completar misiones correctamente o mantener su racha. 
- **Implementación**: Las transacciones se registran en `transacciones_monedas` y actualizan la tabla de `economia_monedas`. Esto se usa para desbloquear futuros avatares, temas o ayudas especiales.

---

## 4. Consideraciones Técnicas de la Implementación

- **Frontend (LexiScan_Angular)**: Desarrollado bajo la arquitectura de componentes de Angular 18, utilizando rutas protegidas (Guards) para asegurar que solo usuarios autenticados puedan acceder a los paneles. Se emplean servicios (Services) para encapsular la comunicación HTTP con el backend.
- **Backend (FastAPI)**: Estructurado siguiendo patrones de diseño (CRUD, Schemas Pydantic, Models SQLAlchemy, Routers). Se ha diseñado para que sea altamente concurrente (async/await), mejorando los tiempos de respuesta al comunicarse con la IA.
- **Base de Datos**: Se aprovechó fuertemente el motor de PostgreSQL 15+. La lógica de negocio pesada, como el recálculo de porcentajes de maestría y el registro de fallos constantes, se ha delegado a Triggers (`actualizar_maestria`, `registrar_error_favorito`) para mantener la atomicidad de los datos.
