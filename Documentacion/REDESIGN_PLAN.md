# REDESIGN_PLAN.md — Propuesta de Rediseño Visual

## Dirección de Arte: "Energía Inteligente"

**Concepto**: Combinar la energía vibrante de Duolingo con la seriedad educativa de una plataforma PAES. Colores de alta energía que motivan sin distracción. UI limpia con micro-animaciones que recompensan cada acción.

---

## 1. Paleta de Colores (NO VERDE como primario)

### Paleta Principal — Indigo Energético + Naranja Acción

| Rol | Hex | Nombre | Uso |
|-----|-----|--------|-----|
| **Primary** | `#6366F1` | Indigo 500 | Headers, botones principales, tabs activos |
| **Primary Light** | `#818CF8` | Indigo 400 | Hover states, iconos activos |
| **Primary Dark** | `#4F46E5` | Indigo 600 | Press states, gradients |
| **Secondary** | `#8B5CF6` | Violet 500 | Acentos, badges, chips |
| **Accent** | `#F97316` | Orange 500 | CTAs, monedas, recompensas, warnings |
| **Accent Light** | `#FB923C` | Orange 400 | Hover de acentos |

### Estados

| Rol | Hex | Nombre | Uso |
|-----|-----|--------|-----|
| **Success** | `#10B981` | Emerald 500 | Respuestas correctas, progreso completado |
| **Success Light** | `#34D399` | Emerald 400 | Backgrounds de éxito |
| **Error** | `#EF4444` | Red 500 | Errores, respuestas incorrectas |
| **Error Light** | `#F87171` | Red 400 | Backgrounds de error |
| **Warning** | `#F59E0B` | Amber 500 | Advertencias, streak |
| **Warning Light** | `#FBBF24` | Amber 400 | Backgrounds de warning |

### Superficies

| Rol | Hex | Nombre | Uso |
|-----|-----|--------|-----|
| **Background** | `#F5F3FF` | Violet 50 | Background general de la app |
| **Surface** | `#FFFFFF` | White | Tarjetas, modales |
| **Surface Variant** | `#EEF2FF` | Indigo 50 | Secciones alternas |
| **Border** | `#E5E7EB` | Gray 200 | Bordes sutiles |

### Texto

| Rol | Hex | Nombre | Uso |
|-----|-----|--------|-----|
| **Text Primary** | `#1E1B4B` | Indigo 950 | Títulos, texto principal |
| **Text Secondary** | `#475569` | Slate 600 | Texto secundario |
| **Text Muted** | `#94A3B8` | Slate 400 | Labels, hints |
| **Text Inverse** | `#FFFFFF` | White | Texto sobre fondos oscuros |

### Gradientes Oficiales

```scss
// Header principal
$gradient-primary: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);

// Stats / Destacados
$gradient-stats: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);

// CTA Button
$gradient-cta: linear-gradient(135deg, #F97316 0%, #EF4444 100%);

// Success
$gradient-success: linear-gradient(135deg, #10B981 0%, #059669 100%);
```

---

## 2. Tipografía

### Fuentes Seleccionadas

| Tipo | Fuente | Peso | Google Fonts |
|------|--------|------|--------------|
| **Display/Heading** | Fredoka | 400-700 | `Fredoka:wght@400;500;600;700` |
| **Body** | Nunito | 300-700 | `Nunito:wght@300;400;500;600;700` |

### Por qué Fredoka + Nunito
- **Fredoka**: Redondeada, juguetona, pero profesional. Perfecta para títulos de EdTech.
- **Nunito**: Excelente legibilidad, amigable, moderna. Ideal para cuerpo de texto.
- Ambas son Google Fonts (gratis, CDN rápido)
- Funcionan excelente en móvil

### Import CSS
```css
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Nunito:wght@300;400;500;600;700&display=swap');
```

### Escala Tipográfica

| Token | Tamaño | Peso | Uso |
|-------|--------|------|-----|
| `--text-display` | 2rem (32px) | 700 | Títulos de pantalla |
| `--text-h1` | 1.5rem (24px) | 700 | Títulos de sección |
| `--text-h2` | 1.25rem (20px) | 600 | Subtítulos |
| `--text-h3` | 1.125rem (18px) | 600 | Títulos de card |
| `--text-body` | 1rem (16px) | 400 | Texto principal |
| `--text-body-lg` | 1.125rem (18px) | 400 | Texto de lectura |
| `--text-caption` | 0.875rem (14px) | 400 | Labels, captions |
| `--text-small` | 0.75rem (12px) | 500 | Badges, hints |

---

## 3. Espaciado y Layout

### Sistema de Espaciado (4px base)

| Token | Valor | Uso |
|-------|-------|-----|
| `--space-1` | 4px | Gap mínimo, iconos inline |
| `--space-2` | 8px | Spacing entre elementos pequeños |
| `--space-3` | 12px | Padding interno de cards pequeñas |
| `--space-4` | 16px | Padding estándar, gaps de grid |
| `--space-5` | 20px | Padding de secciones |
| `--space-6` | 24px | Spacing entre secciones |
| `--space-8` | 32px | Padding de pantallas |
| `--space-10` | 40px | Margen superior de secciones |
| `--space-12` | 48px | Espaciado grande |

### Border Radius

| Token | Valor | Uso |
|-------|-------|-----|
| `--radius-sm` | 8px | Botones pequeños, chips |
| `--radius-md` | 12px | Cards, inputs |
| `--radius-lg` | 16px | Cards grandes, modales |
| `--radius-xl` | 24px | Botones grandes, pill shapes |
| `--radius-full` | 9999px | Avatares, badges circulares |

### Sombras (Estilo Duolingo — sutiles pero con profundidad)

| Token | Valor | Uso |
|-------|-------|-----|
| `--shadow-xs` | `0 1px 2px rgba(0,0,0,0.05)` | Elementos flat |
| `--shadow-sm` | `0 2px 8px rgba(99,102,241,0.1)` | Cards estándar |
| `--shadow-md` | `0 4px 16px rgba(99,102,241,0.15)` | Cards elevados |
| `--shadow-lg` | `0 8px 32px rgba(99,102,241,0.2)` | Modales, overlays |
| `--shadow-button` | `0 4px 0 #4F46E5` | Botones 3D chunky |

---

## 4. Componentes Clave — Estilo Duolingo

### 4.1 Botones 3D Chunky

```scss
// Botón primario con efecto 3D
.ion-button-primary {
  --background: #6366F1;
  --background-activated: #4F46E5;
  --border-radius: 16px;
  --box-shadow: 0 4px 0 #4F46E5;
  --padding-top: 16px;
  --padding-bottom: 16px;
  font-family: 'Fredoka', sans-serif;
  font-weight: 600;
  font-size: 1.1rem;
  text-transform: none;
  letter-spacing: 0;
  transition: transform 0.1s ease, box-shadow 0.1s ease;

  &:active {
    transform: translateY(4px);
    --box-shadow: 0 0 0 #4F46E5;
  }
}
```

### 4.2 Tarjetas de Habilidad (Bento Grid)

```scss
.habilidad-card {
  --background: #FFFFFF;
  --border-radius: 16px;
  --box-shadow: var(--shadow-sm);
  padding: 20px;
  text-align: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;

  &:hover {
    transform: translateY(-2px);
    --box-shadow: var(--shadow-md);
  }

  .habilidad-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 12px;
  }

  .habilidad-name {
    font-family: 'Fredoka', sans-serif;
    font-weight: 600;
    font-size: var(--text-body);
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  .habilidad-level {
    font-family: 'Nunito', sans-serif;
    font-size: var(--text-caption);
    color: var(--text-secondary);
  }
}
```

### 4.3 Barras de Progreso Gamificadas

```scss
.progress-gamified {
  height: 12px;
  border-radius: 6px;
  background: var(--surface-variant);
  overflow: hidden;

  .progress-fill {
    height: 100%;
    border-radius: 6px;
    background: $gradient-primary;
    transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;

    &::after {
      content: '';
      position: absolute;
      top: 2px;
      left: 8px;
      right: 8px;
      height: 4px;
      background: rgba(255,255,255,0.3);
      border-radius: 2px;
    }
  }
}
```

### 4.4 Cards de Desafío

```scss
.challenge-card {
  --background: #FFFFFF;
  --border-radius: 16px;
  --box-shadow: var(--shadow-sm);
  border-left: 4px solid var(--accent);
  padding: 16px;

  .challenge-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;

    .challenge-icon {
      width: 40px;
      height: 40px;
      border-radius: 10px;
      background: var(--primary-light);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
    }
  }

  .challenge-reward {
    display: flex;
    align-items: center;
    gap: 4px;
    font-family: 'Fredoka', sans-serif;
    font-weight: 600;
    color: var(--accent);
  }
}
```

### 4.5 Botón de Reclamar Recompensa

```scss
.btn-claim {
  --background: $gradient-cta;
  --border-radius: 12px;
  --box-shadow: 0 4px 0 #DC2626;
  font-family: 'Fredoka', sans-serif;
  font-weight: 600;
  text-transform: none;
  animation: pulse-glow 2s infinite;

  &:active {
    transform: translateY(4px);
    --box-shadow: 0 0 0 #DC2626;
  }
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 4px 0 #DC2626, 0 0 0 0 rgba(249,115,22,0.4); }
  50% { box-shadow: 0 4px 0 #DC2626, 0 0 0 8px rgba(249,115,22,0); }
}
```

---

## 5. Estrategia de Conversión de Componentes

### Fase 1: Fundamentos (Estilos globales)
1. Actualizar `variables.scss` con todos los tokens
2. Crear `_mixins.scss` con estilos reutilizables
3. Importar Google Fonts en `index.html`
4. Actualizar `global.scss` con estilos base

### Fase 2: Componentes Atómicos
1. Crear componente `atom-button` con estilo 3D
2. Crear componente `atom-card` con variantes
3. Crear componente `atom-progress` gamificado
4. Crear componente `atom-badge` para monedas/XP

### Fase 3: Páginas (Orden de impacto)
1. **Home** — Dashboard con nuevo estilo
2. **Login** — Rediseño completo con branding
3. **Habilidades** — Grid de tarjetas
4. **GYM** — Experiencia de práctica mejorada
5. **Examen** — Configuración moderna
6. **Perfil** — Tarjeta de perfil actualizada

### Fase 4: Gamificación
1. Sistema de XP visible
2. Animaciones de recompensa
3. Streak con protección visual
4. Logros/badges (futuro)

---

## 6. Paleta de Colores por Habilidad

| Habilidad | Color | Hex | Gradiente |
|-----------|-------|-----|-----------|
| Localizar | Turquesa | `#14B8A6` | `#14B8A6 → #0D9488` |
| Interpretar | Púrpura | `#8B5CF6` | `#8B5CF6 → #7C3AED` |
| Evaluar | Rojo coral | `#F43F5E` | `#F43F5E → #E11D48` |
| Lectura Crítica | Azul | `#3B82F6` | `#3B82F6 → #2563EB` |
| Vocabulario | Naranja | `#F97316` | `#F97316 → #EA580C` |
| Tipos de Texto | Rosa | `#EC4899` | `#EC4899 → #DB2777` |

---

## 7. Iconografía

### Recomendación: Lucide Icons
- Moderno, consistente, open source
- 1500+ iconos
- Fácil integración con Ionic

### Instalación
```bash
npm install lucide-static
```

### Uso en Angular
```html
<!-- En lugar de ion-icon genérico -->
<img src="assets/icons/book-open.svg" alt="Habilidad" class="icon">
```

### Iconos Clave por Sección

| Sección | Icono | Nombre |
|---------|-------|--------|
| Home | 🏠 | home |
| Habilidades | 📚 | book-open |
| GYM | 💪 | dumbbell |
| Examen | ✏️ | pen-tool |
| Perfil | 👤 | user |
| Monedas | 🪙 | coins |
| Streak | 🔥 | flame |
| Logro | 🏆 | trophy |
| Progreso | 📊 | bar-chart-2 |

---

## 8. Micro-Animaciones

### Transiciones Base
```scss
// Todos los elementos interactivos
transition: transform 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;

// Botones al presionar
&:active {
  transform: translateY(4px) scale(0.98);
}

// Cards al hover
&:hover {
  transform: translateY(-2px);
}
```

### Animaciones de Recompensa
```scss
@keyframes reward-pop {
  0% { transform: scale(0); opacity: 0; }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); opacity: 1; }
}

@keyframes xp-float {
  0% { transform: translateY(0); opacity: 1; }
  100% { transform: translateY(-50px); opacity: 0; }
}

@keyframes streak-fire {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}
```

### Loading States
```scss
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-md);
}
```

---

## 9. Responsive Breakpoints

| Breakpoint | Ancho | Estrategia |
|------------|-------|------------|
| Mobile | 375px | 1 columna, botones full-width |
| Tablet | 768px | 2 columnas, max-width 600px |
| Desktop | 1024px | Contenido centrado, sidebar opcional |
| Wide | 1440px | Max-width 1200px, más whitespace |

---

## 10. Checklist de Implementación

### Antes de empezar
- [ ] Aprobar paleta de colores
- [ ] Aprobar tipografía (Fredoka + Nunito)
- [ ] Definir prioridades de páginas

### Fase 1: Fundamentos
- [ ] Crear `variables.scss` con tokens
- [ ] Crear `_mixins.scss` con utilidades
- [ ] Importar Google Fonts
- [ ] Actualizar `global.scss`

### Fase 2: Componentes
- [ ] Rediseñar botones (3D chunky)
- [ ] Rediseñar cards
- [ ] Rediseñar progress bars
- [ ] Crear badge de monedas

### Fase 3: Páginas
- [ ] Login con branding
- [ ] Home dashboard
- [ ] Habilidades grid
- [ ] GYM Experience
- [ ] Examen flow
- [ ] Perfil

### Fase 4: Gamificación
- [ ] XP visible
- [ ] Animaciones de recompensa
- [ ] Streak display

### Fase 5: Testing
- [ ] Responsive 375px, 768px, 1024px
- [ ] Contraste WCAG AA
- [ ] Performance (LCP < 2.5s)
- [ ] Touch targets (44px mínimo)
