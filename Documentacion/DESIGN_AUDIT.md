# DESIGN_AUDIT.md — Auditoría de Diseño y UX

## Resumen Ejecutivo

La aplicación tiene una funcionalidad sólida pero presenta **inconsistencia visual significativa**, **falta de identidad de marca definida** y **oportunidades perdidas de gamificación**. El diseño actual es funcional pero no genera engagement emocional ni motivación persistente.

---

## 1. Inconsistencias Visuales Críticas

### 1.1 Paleta de Colores Caótica

| Problema | Ubicación | Colores encontrados |
|----------|-----------|---------------------|
| Sin color primario consistente | Todo el proyecto | `#1e3a5f`, `#004aad`, `#2d5a8c`, `#3880ff` |
| Verde sobreusado como éxito | gym, habilidades | `#4CAF50`, `#8bc34a`, `#7cb342` |
| Gradient headers inconsistentes | Todas las páginas | Mismo gradiente pero sin variable |
| Botones de acción sin armonía | home | Verde, púrpura, gris azulado |

**Hallazgo**: No existe un `variables.scss` personalizado. Los colores están hardcodeados en cada `.page.scss` sin centralized tokens.

### 1.2 Tipografía Inconsistente

| Problema | Detalle |
|----------|---------|
| Sin fuente personalizada | Usa sistema Ionic por defecto |
| Tamaños hardcodeados | `0.75rem`, `0.875rem`, `0.9rem`, `0.95rem`, `1rem`, `1.05rem`, `1.1rem`, `1.2rem`, `1.25rem`, `1.3rem`, `1.4rem`, `1.8rem`, `2em` |
| Pesos variados | `500`, `600`, `700` mezclados sin sistema |
| Textos uppercase innecesarios | Botones y labels usan `text-transform: uppercase` |

### 1.3 Espaciado y Layout

| Problema | Detalle |
|----------|---------|
| `max-width: 600px` hardcodeado | Duplicado en `global.scss` y cada página |
| `padding: 20px` inconsistente | Algunas páginas usan 16px, otras 20px, otras 30px |
| `gap` variable | `8px`, `10px`, `12px`, `15px`, `16px`, `20px` sin sistema |
| `border-radius` variado | `6px`, `8px`, `10px`, `12px`, `15px`, `20px` |

---

## 2. Puntos de Fricción UX

### 2.1 Login (Tab1)

| Fricción | Impacto | Solución sugerida |
|----------|---------|-------------------|
| Formulario genérico sin branding | No genera confianza | Agregar logo + illlustración |
| Botón "Crear Cuenta" confuso | Usuario no sabe qué pasa | Cambiar a "¿No tienes cuenta? Regístrate" |
| FAB de configuración oculto | Descubrimiento difícil | Mover a footer del login o Settings page |
| Sin feedback de carga | Usuario no sabe si funciona | Agregar spinner en botón |

### 2.2 Dashboard (Home)

| Fricción | Impacto | Solución sugerida |
|----------|---------|-------------------|
| Saludo "Hola, Benjamin 😊" hardcodeado fallback | Parece debug | Mejorar mensaje por defecto |
| Emoji en saludo | No profesional para EdTech | Reemplazar con ilustración |
| Botones de acción genéricos | Sin diferenciación visual | Iconos + colores únicos por módulo |
| Desafíos diarios sin animación | No genera excitement | Animar completado y reclamación |
| Gráfico radar difícil de leer | SVG complejo sin tooltip | Simplificar o agregar interactividad |

### 2.3 Habilidades

| Fricción | Impacto | Solución sugerida |
|----------|---------|-------------------|
| Grid 3x2 apretado en móvil | Botones difíciles de tocar | Considerar lista o grid 2x3 |
| Colores de maestría confusos | Verde = éxito Y Verde = maestria media | Usar semáforo consistente |
| Contenido enriquecido denso | Bloques de texto sin jerarquía | Agregar spacing y visuales |
| Preguntas sin progreso | Usuario no sabe cuántas faltan | Agregar indicador "Pregunta 1 de 4" |

### 2.4 GYM (Revancha)

| Fricción | Impacto | Solución sugerida |
|----------|---------|-------------------|
| Nombre "GYM - Revancha" confuso | No claro qué hace | Renombrar a "Práctica de Errores" |
| Botón "Entrenar" genérico | Sin motivación | "Practicar mi debilidad" |
| Feedback solo texto | Poca recompensa visual | Agregar animación de éxito/error |
| Sin streak de práctica | No motiva volver | Agregar "Practicast hace X días" |

### 2.5 Examen

| Fricción | Impacto | Solución sugerida |
|----------|---------|-------------------|
| Slider poco intuitivo | Difícil de usar en móvil | Botones +/- o input numérico |
| Sin preview del examen | Usuario no sabe qué espera | Mostrar "10 preguntas, ~15 min" |
| Descarga PDF oculta | Funcionalidad perdida | Botón más prominente |

### 2.6 Perfil (Tab3)

| Fricción | Impacto | Solución sugerida |
|----------|---------|-------------------|
| Formulario largo | Abandono | Simplificar a campos esenciales |
| Botón "Eliminar Perfil" peligroso | Acción destructiva fácil | Requerir confirmación adicional |
| Sin avatar o personalización | Genérico | Agregar avatar editable |

---

## 3. Flujos de Usuario Críticos

### 3.1 Flujo de Onboarding
```
Login → Home → (sin guía)
```
**Problema**: No hay onboarding. Usuario llega a Home sin saber qué hacer.

**Solución**: Agregar tour guiado de 3-4 pasos:
1. "Bienvenido a LexiScan"
2. "Elige una habilidad para practicar"
3. "Gana monedas completando desafíos"
4. "Usa el GYM para mejorar tus errores"

### 3.2 Flujo de Práctica
```
Home → Habilidades → Seleccionar → Leer texto → Responder → Evaluar
```
**Problema**: No hay feedback de progreso ni recompensa visible.

**Solución**: 
- Barra de progreso en cada paso
- Animación de "+XP" al responder correcto
- Sonido/haptic feedback

### 3.3 Flujo de Examen
```
Home → Examen → Configurar → Simulacro → Resultados → Guardar
```
**Problema**: Examen parece impersonal y sin presión real.

**Solución**:
- Temporizador visible
- Indicador de progreso "3/10"
- Pantalla de resultados con celebración

---

## 4. Gamificación Actual vs Potencial

### Actual
- ✅ Racha de días (streak)
- ✅ Monedas
- ✅ Desafíos diarios
- ✅ Nivel de maestría por habilidad
- ❌ Sin niveles de usuario
- ❌ Sin logros/badges
- ❌ Sin leaderboard
- ❌ Sin animaciones de recompensa
- ❌ Sin sonidos de feedback

### Potencial (Estilo Duolingo)
- 🎯 Sistema de XP con niveles
- 🏆 Logros desbloqueables
- 📊 Ranking semanal
- 🔥 Streak con protección (freeze)
- 🎉 Celebraciones animadas
- 📅 Eventos especiales
- 🎁 Recompensas diarias escalonadas

---

## 5. Accesibilidad

| Problema | Severidad | Solución |
|----------|-----------|----------|
| Sin labels explícitos en radio buttons | Alta | Agregar `aria-label` |
| Contraste insuficiente en texto gris | Media | Usar `#475569` mínimo |
| Sin focus states visibles | Alta | Agregar `:focus-visible` styles |
| Sin `prefers-reduced-motion` | Media | Respetar preferencia |
| Botones sin `cursor-pointer` | Baja | Agregar a todos los interactivos |

---

## 6. Resumen de Prioridades

### Crítico (Fase 1)
1. Definir paleta de colores consistente (sin verde como primario)
2. Crear design tokens en `variables.scss`
3. Unificar tipografía con Google Fonts
4. Corregir contraste y accesibilidad

### Alto (Fase 2)
5. Rediseñar Login con branding
6. Agregar onboarding guiado
7. Mejorar feedback de gamificación
8. Animaciones de transición

### Medio (Fase 3)
9. Sistema de badges/logros
10. Leaderboard
11. Sonidos de feedback
12. Modo oscuro personalizado
