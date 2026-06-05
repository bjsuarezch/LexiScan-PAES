# DESIGN_SYSTEM_AUDIT.md — Inventario de Componentes y Estilos

## Estado Actual del Design System

**No existe un design system formal.** Los estilos están distribuidos en archivos de componentes individuales sin tokens centralizados ni guías de uso.

---

## 1. Variables y Tokens

### `variables.scss` — VACÍO
```scss
// Solo comentario informativo
// https://ionicframework.com/docs/theming/
```

**Problema**: No hay tokens de color, tipografía, espaciado ni sombras definidos.

### `global.scss` — Mínimo
- Importa CSS base de Ionic
- Habilita dark mode system
- Define `max-width: 600px` para contenido centrado

**No hay**: Variables CSS custom, mixins, utilidades reutilizables.

---

## 2. Paleta de Colores (Hardcodeada)

### Colores Primarios Encontrados

| Color | Hex | Uso | Archivo |
|-------|-----|-----|---------|
| Azul oscuro | `#1e3a5f` | Headers, backgrounds, texto | home, habilidades, gym, examen |
| Azul medio | `#2d5a8c` | Gradientes | home, habilidades, gym |
| Azul claro | `#004aad` | Texto h2, stats | home |
| Azul Ionic | `#3880ff` | Primary default | habilidades (bar-fill) |

### Colores de Acción

| Color | Hex | Uso | Archivo |
|-------|-----|-----|---------|
| Verde éxito | `#4CAF50` | Maestria media, correcto, entrenar | habilidades, gym |
| Verde claro | `#8bc34a` | Botón habilidad, entrenar | home, gym |
| Verde oscuro | `#7cb342` | Botones habilidad | habilidades |
| Rojo error | `#f44336` | Maestria baja, eliminar | tab3, habilidades |
| Naranja warning | `#ff9800` | Iconos, monedas | home, gym |
| Amarillo | `#ffeb3b` | Texto destacado | gym |
| Amarillo success | `#ffc107` | Icono estrella | home |

### Colores de Superficie

| Color | Hex | Uso |
|-------|-----|-----|
| Blanco | `#ffffff` | Tarjetas, fondos |
| Gris claro | `#f8f9fa` | Fondos alternos |
| Gris | `#f5f5f5` | Secciones |
| Gris texto | `#666`, `#888`, `#aaa` | Texto secundario |
| Negro | `#222` | Fondos de chart |

### Gradientes

```scss
// Header principal (repetido en todas las páginas)
background: linear-gradient(135deg, #1e3a5f 0%, #2d5a8c 100%);

// Botón habilidades
--background: linear-gradient(to bottom, #8aad49e8, #358d35e8);

// Botón gym
--background: linear-gradient(to bottom, #366db4, #3a1e5f);

// Botón examen
--background: linear-gradient(to bottom, #618eb8, #455a64);

// Stats card
background: linear-gradient(135deg, #1e3a5f 0%, #2d5a8c 100%);

// Daily challenges header
background: linear-gradient(135deg, #1e3a5f 0%, #2d5a8c 100%);
```

---

## 3. Tipografía

### Sistema Actual
- **Fuente**: Sistema Ionic por defecto (Inter/Roboto)
- **Pesos usados**: `400`, `500`, `600`, `700`
- **Tamaños**: Sin escala definida

### Tamaños Encontrados

| Tamaño | Uso |
|--------|-----|
| `0.75rem` | Botones habilidad, labels pequeños |
| `0.8rem` | Texto de progreso |
| `0.85rem` | Texto de gráficos |
| `0.875rem` | Errores de formulario |
| `0.9rem` | Texto secundario, botones |
| `0.95rem` | Texto cuerpo |
| `1rem` | Texto principal |
| `1.05rem` | Títulos de desafíos |
| `1.1rem` | Coaching title |
| `1.2rem` | Ion-title, iconos grandes |
| `1.25rem` | Card titles |
| `1.3rem` | H2 de habilidades |
| `1.4rem` | H2 de examen |
| `1.8rem` | H2 de home |
| `2em` | Score display |

---

## 4. Espaciado

### Valores Encontrados

| Valor | Uso |
|-------|-----|
| `4px` | Gap mínimo |
| `5px` | Margen interno |
| `8px` | Gap de botones |
| `10px` | Gap de grid, bordes |
| `12px` | Gap de inputs |
| `15px` | Margen de cards |
| `16px` | Padding de coaching |
| `20px` | Padding estándar |
| `25px` | Margen de config card |
| `30px` | Padding de examen |
| `50px` | Margin bottom de examen |

### Bordes Redondeados

| Valor | Uso |
|-------|-----|
| `4px` | Progress bars |
| `6px` | Radio items, botones pequeños |
| `8px` | Botones, inputs, datos clave |
| `10px` | Cards, error card |
| `12px` | Habilidades btn, custom tema |
| `15px` | Stats card, chart card |
| `20px` | Welcome section |

---

## 5. Sombras

| Valor | Uso |
|-------|-----|
| `0 2px 8px rgba(0,0,0,0.1)` | Cards estándar |
| `0 4px 12px rgba(0,0,0,0.1)` | Stats card |
| `0 4px 15px rgba(0,0,0,0.2)` | Error card, btn-entrenar |
| `0 10px 20px rgba(0,0,0,0.3)` | Chart card |
| `0 4px 20px rgba(0,0,0,0.3)` | Config card examen |
| `0 2px 16px rgba(0,0,0,0.08)` | Habilidad detail |
| `0 4px 6px rgba(0,0,0,0.2)` | Botones de acción |

---

## 6. Componentes Ionic En Uso

### Componentes de Layout
- `ion-header`, `ion-toolbar`, `ion-title`
- `ion-content`
- `ion-tabs`

### Componentes de Formulario
- `ion-item`, `ion-label`, `ion-input`
- `ion-button`
- `ion-radio-group`, `ion-radio`
- `ion-text` (para errores)

### Componentes de Datos
- `ion-card`, `ion-card-header`, `ion-card-content`
- `ion-list`, `ion-item`
- `ion-badge`, `ion-chip`
- `ion-progress-bar`

### Componentes de Navegación
- `ion-back-button`
- `ion-fab`, `ion-fab-button`
- `ion-buttons`

### Componentes de Feedback
- `ion-spinner`
- `ion-icon`
- `ion-note`

### Componentes No Usados (Potencial)
- `ion-avatar` — Para perfil
- `ion-skeleton-loading` — Para loading states
- `ion-toast` — Para notificaciones
- `ion-alert` — Para confirmaciones
- `ion-modal` — Para modales (solo config-modal)
- `ion-slides` — Para onboarding
- `ion-segment` — Para filtros

---

## 7. Estilos por Página

### Login (tab1.page.scss)
- Formulario flex column con gap
- Items sin padding
- Errores con font-size pequeño
- 35 líneas

### Registro (tab2.page.scss)
- Mismo patrón que Login
- 35 líneas (idéntico)

### Perfil (tab3.page.scss)
- Card con shadow
- Items con labels uppercase
- Responsive grid para botones (768px+)
- 126 líneas

### Home (home.page.scss)
- El más complejo: 413 líneas
- Gradient headers
- Stats card con gradient
- Chart card con SVG
- Botones horizontales con gradientes
- Daily challenges con progress bars

### Habilidades (habilidades.page.scss)
- Grid 3x2 para botones
- Colores por clase CSS
- Chart card oscuro
- Rich text container
- 281 líneas

### GYM (gym.page.scss)
- Glassmorphism en error card
- Coaching card oscura
- Result cards con bordes de color
- 327 líneas

### Examen (examen.page.scss)
- Config card centrada
- Slider personalizado
- 196 líneas

### Examen Simulacro (examen-simulacro.page.scss)
- Estilos mínimos
- Text context card
- 51 líneas

### Examen Resultados (examen-resultados.page.scss)
- Score display
- 70 líneas

### Selección Tema (seleccion-tema.page.scss)
- Grid responsive
- 37 líneas

---

## 8. Patrones de Estilo Repetidos

### Header Gradient (copiado en 6 archivos)
```scss
ion-header {
  ion-toolbar {
    background: linear-gradient(135deg, #1e3a5f 0%, #2d5a8c 100%);
    color: #fff;
    --border-bottom: none;
  }
}
```

### Content Background (copiado en 6 archivos)
```scss
ion-content {
  --background: linear-gradient(135deg, #1e3a5f 0%, #2d5a8c 100%);
  --padding-start: 0;
  --padding-end: 0;
}
```

### Centered Container (copiado en 6 archivos)
```scss
ion-content > * {
  margin: 0 auto;
  max-width: 600px;
  width: 100%;
  padding: 0 20px;
  box-sizing: border-box;
}
```

---

## 9. Recomendaciones de Centralización

### Crear `variables.scss` con:
```scss
// Colors
--primary: #6366F1;
--secondary: #818CF8;
--accent: #F97316;
--success: #10B981;
--error: #EF4444;
--warning: #F59E0B;

// Typography
--font-display: 'Fredoka', sans-serif;
--font-body: 'Nunito', sans-serif;

// Spacing
--space-xs: 4px;
--space-sm: 8px;
--space-md: 16px;
--space-lg: 24px;
--space-xl: 32px;

// Borders
--radius-sm: 8px;
--radius-md: 12px;
--radius-lg: 16px;
--radius-xl: 24px;

// Shadows
--shadow-sm: 0 2px 8px rgba(0,0,0,0.1);
--shadow-md: 0 4px 12px rgba(0,0,0,0.15);
--shadow-lg: 0 8px 24px rgba(0,0,0,0.2);
```

### Crear `_mixins.scss` con:
```scss
@mixin header-gradient {
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
}

@mixin card-style {
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

@mixin centered-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 0 var(--space-md);
}
```
