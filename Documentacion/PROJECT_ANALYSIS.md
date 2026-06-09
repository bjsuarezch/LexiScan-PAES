# PROJECT_ANALYSIS.md — Análisis de Estructura del Frontend

## Resumen General

LexiScan-PAES es una aplicación móvil híbrida construida con **Angular 20 + Ionic 8**. Utiliza lazy loading por módulos y un layout de tabs como shell principal.

---

## Arquitectura de Módulos

### Módulo Principal
- **AppModule** (`app.module.ts`) — Bootstrap de la aplicación
- **AppRoutingModule** — Rutas globales con `PreloadAllModules`

### Estructura de Rutas

```
/ (root) → TabsPageModule
├── /tabs/tab1    → LoginPage (Login)
├── /tabs/tab2    → RegistroPage (Registro)
├── /tabs/tab3    → MiPerfilPage (Perfil)
├── /home         → HomePage (Dashboard principal)
├── /habilidades  → HabilidadesPage (Selección de habilidad)
├── /gym          → GymPage (Gimnasio de práctica)
├── /examen       → ExamenPage (Configuración de examen)
├── /examen-simulacro → ExamenSimulacroPage (Ejecución del examen)
├── /examen-resultados → ExamenResultadosPage (Resultados)
└── /seleccion-tema → SeleccionTemaPage (Selección de tema)
```

### Componentes

| Componente | Tipo | Descripción |
|------------|------|-------------|
| `radar-chart` | Componente reutilizable | Gráfico radar de habilidades (SVG inline) |
| `config-modal` | Modal | Configuración de API keys (Groq/Gemini) |
| `explore-container` | Componente Ionic | Contenedor de exploración (probablemente no usado) |

---

## Páginas Principales

### 1. Tab1 — Login (`/tabs/tab1`)
- Formulario RUT + Email + Contraseña
- Botón "Crear Cuenta" → Tab2
- FAB flotante → Modal de configuración
- Validación RUT chileno personalizada

### 2. Tab2 — Registro (`/tabs/tab2`)
- Formulario completo: RUT, Nombre, Email, Contraseña, Confirmar
- Botones: Registrarse, Limpiar
- Back button a Tab1

### 3. Tab3 — Mi Perfil (`/tabs/tab3`)
- Vista tarjeta con datos del perfil
- Modo edición inline
- Botones: Editar, Guardar, Cancelar, Eliminar

### 4. Home — Dashboard (`/home`)
- Saludo personalizado con emoji
- Estadísticas: Racha (días) + Monedas
- **Gráfico Radar SVG** — 6 habilidades PAES
- Botones de acción: HABILIDADES | GYM | Examen
- Desafíos Diarios con progreso y recompensas
- Tarjeta "Tu debilidad hoy"

### 5. Habilidades (`/habilidades`)
- Grid 3x2 de botones de habilidad (colores por maestría)
- Gráfico radar del componente `app-radar-chart`
- Contenido enriquecido: párrafos, datos clave, imágenes (Pollinations AI), gráficos de barra
- Formulario de preguntas con radio buttons
- Evaluación con retroalimentación

### 6. GYM — Revancha (`/gym`)
- Tarjeta de error frecuente con barra de progreso
- Gráfico radar SVG
- Botón "Entrenar"
- Modal de coaching: contexto, pregunta, alternativas
- Resultado: correcto/incorrecto con feedback

### 7. Examen — Configuración (`/examen`)
- Slider para cantidad de preguntas (10-65)
- Estimación de tiempo
- Botón "Iniciar Examen"

### 8. Examen Simulacro (`/examen-simulacro`)
- Texto contextual agrupado por lectura
- Preguntas con radio buttons
- Botón "Descargar PDF"
- Botón "Finalizar Examen"

### 9. Examen Resultados (`/examen-resultados`)
- Score display (correctas/total + porcentaje)
- Gráfico radar de rendimiento
- Desglose por habilidad
- Acciones: Guardar, Descargar PDF, Descartar

### 10. Selección de Tema (`/seleccion-tema`)
- Grid de temas fijos (Tesla, Música 70s, Transformers, My Hero Academia)
- Input para tema personalizado (costo: 50 monedas)

---

## Servicios (Angular)

| Servicio | Responsabilidad |
|----------|----------------|
| `HabilidadesService` | Comunicación HTTP con API backend (login, dashboard, habilidades, exámenes, configuración) |
| `ProfileService` | Gestión de perfil de usuario (localStorage) |
| `DesafiosService` | Desafíos diarios y recompensas |

---

## Modelos de Datos

| Modelo | Archivo | Descripción |
|--------|---------|-------------|
| `ILogin`, `IUserProfile` | `auth.model.ts` | Autenticación y perfil |
| `DashboardResponse`, `HabilidadDetail`, `ExamenResponse`, etc. | `backend.model.ts` | Respuestas de la API |
| `Habilidad` | `habilidad.model.ts` | Modelo de habilidad PAES |

---

## Estilos Globales

- **`global.scss`**: Importa CSS base de Ionic + dark mode system + layout centrado (max-width: 600px)
- **`variables.scss`**: Vacío (sin customización de variables Ionic)
- **Estilos por componente**: Cada página tiene su propio `.page.scss` con estilos scoped

---

## Dependencias Clave

| Paquete | Versión | Uso |
|---------|---------|-----|
| `@angular/core` | ^20.0.0 | Framework principal |
| `@ionic/angular` | ^8.0.0 | UI components |
| `@capacitor/core` | 8.3.1 | Native bridge |
| `jspdf` | ^4.2.1 | Generación de PDF |
| `jspdf-autotable` | ^5.0.8 | Tablas en PDF |
| `ionicons` | ^7.0.0 | Iconos |

---

## Observaciones Técnicas

1. **Lazy loading** correcto en todas las rutas
2. **Ruta duplicada**: `/examen-simulacro` aparece dos veces en `app-routing.module.ts`
3. **SVG inline** para gráficos radar (no usa librería externa)
4. **Pollinations AI** para generación dinámica de imágenes
5. **Diseño responsive** con max-width de 600px para contenido
6. **Dark mode** habilitado via `@ionic/angular/css/palettes/dark.system.css`
