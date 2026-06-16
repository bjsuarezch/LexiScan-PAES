-- 01_schema.sql
-- Esquema PostgreSQL generado desde los modelos SQLAlchemy actuales.

-- ============================================================
-- 1. ENUM: habilidad_lectora
-- ============================================================
CREATE TYPE habilidad_lectora AS ENUM (
    'Localizar',
    'Interpretar',
    'Evaluar',
    'Lectura_Critica',
    'Vocabulario',
    'Tipos_de_Texto'
);

-- ============================================================
-- 2. TABLA: usuarios
-- ============================================================
CREATE TABLE usuarios (
    rut VARCHAR(12) PRIMARY KEY,
    nombre_completo VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    xp_total INTEGER NOT NULL DEFAULT 0,
    racha_actual INTEGER NOT NULL DEFAULT 0,
    fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    es_admin BOOLEAN NOT NULL DEFAULT FALSE,
    ultimo_acceso TIMESTAMPTZ
);

CREATE INDEX idx_usuarios_email ON usuarios (email);

-- ============================================================
-- 3. TABLA: historial_habilidades
-- ============================================================
CREATE TABLE historial_habilidades (
    id_progreso SERIAL PRIMARY KEY,
    rut_usuario VARCHAR(12) NOT NULL REFERENCES usuarios (rut) ON DELETE CASCADE,
    nombre_habilidad habilidad_lectora NOT NULL,
    nivel_maestria NUMERIC(5,2) NOT NULL DEFAULT 0.00,
    ultima_actualizacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (rut_usuario, nombre_habilidad),
    CHECK (nivel_maestria >= 0 AND nivel_maestria <= 100)
);

CREATE INDEX idx_habilidades_nivel ON historial_habilidades (nivel_maestria);

-- ============================================================
-- 4. TABLA: economia_monedas
-- ============================================================
CREATE TABLE economia_monedas (
    rut_usuario VARCHAR(12) PRIMARY KEY REFERENCES usuarios (rut) ON DELETE CASCADE,
    saldo_monedas INTEGER NOT NULL DEFAULT 0,
    total_acumulado INTEGER NOT NULL DEFAULT 0,
    ultima_transaccion TIMESTAMPTZ
);

-- ============================================================
-- 5. TABLA: transacciones_monedas
-- ============================================================
CREATE TABLE transacciones_monedas (
    id_transaccion SERIAL PRIMARY KEY,
    rut_usuario VARCHAR(12) NOT NULL REFERENCES usuarios (rut),
    monto INTEGER NOT NULL,
    concepto VARCHAR(200) NOT NULL,
    fecha TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_trans_usuario ON transacciones_monedas (rut_usuario);
CREATE INDEX idx_trans_fecha ON transacciones_monedas (fecha DESC);

-- ============================================================
-- 6. TABLA: preguntas_ia
-- ============================================================
CREATE TABLE preguntas_ia (
    id_pregunta SERIAL PRIMARY KEY,
    id_pregunta_origen INTEGER,
    id_habilidad INTEGER NOT NULL REFERENCES historial_habilidades (id_progreso),
    texto_inedito TEXT NOT NULL,
    enunciado VARCHAR(500) NOT NULL,
    alternativas JSONB NOT NULL,
    respuesta_correcta CHAR(1) NOT NULL CHECK (respuesta_correcta IN ('A','B','C','D')),
    justificacion_cot TEXT NOT NULL,
    modelo_ia VARCHAR(60) NOT NULL DEFAULT 'sinclair',
    fecha_generacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    activa BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX idx_preguntas_ia_habilidad ON preguntas_ia (id_habilidad);
CREATE INDEX idx_preguntas_ia_activa ON preguntas_ia (activa);

-- ============================================================
-- 6. TABLA: banco_preguntas
-- ============================================================
CREATE TABLE banco_preguntas (
    id_pregunta SERIAL PRIMARY KEY,
    id_habilidad INTEGER NOT NULL REFERENCES historial_habilidades (id_progreso),
    texto_inedito TEXT NOT NULL,
    enunciado VARCHAR(500) NOT NULL,
    alternativas JSONB NOT NULL,
    respuesta_correcta CHAR(1) NOT NULL CHECK (respuesta_correcta IN ('A','B','C','D')),
    justificacion_cot TEXT NOT NULL,
    dificultad VARCHAR(20) NOT NULL DEFAULT 'medio',
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    activa BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX idx_banco_habilidad ON banco_preguntas (id_habilidad);
CREATE INDEX idx_banco_activa ON banco_preguntas (activa);

-- ============================================================
-- 7. TABLA: sesiones_examen
-- ============================================================
CREATE TABLE sesiones_examen (
    id_examen SERIAL PRIMARY KEY,
    rut_usuario VARCHAR(12) NOT NULL REFERENCES usuarios (rut) ON DELETE CASCADE,
    cantidad_preguntas INTEGER NOT NULL,
    puntaje_obtenido INTEGER,
    puntaje_maximo INTEGER,
    tiempo_total INTEGER,
    es_impulsivo BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_inicio TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_fin TIMESTAMPTZ,
    completado BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX idx_sesion_usuario ON sesiones_examen (rut_usuario);
CREATE INDEX idx_sesion_fecha ON sesiones_examen (fecha_inicio DESC);

-- ============================================================
-- 8. TABLA: sesion_preguntas
-- ============================================================
CREATE TABLE sesion_preguntas (
    id_sesion_pregunta SERIAL PRIMARY KEY,
    id_examen INTEGER NOT NULL REFERENCES sesiones_examen (id_examen) ON DELETE CASCADE,
    id_pregunta INTEGER NOT NULL REFERENCES banco_preguntas (id_pregunta),
    respuesta_dada CHAR(1) CHECK (respuesta_dada IN ('A','B','C','D')),
    es_correcta BOOLEAN,
    tiempo_respuesta INTEGER
);

CREATE INDEX idx_sp_examen ON sesion_preguntas (id_examen);
CREATE INDEX idx_sp_pregunta ON sesion_preguntas (id_pregunta);

-- ============================================================
-- 9. TABLA: errores_favoritos
-- ============================================================
CREATE TABLE errores_favoritos (
    id_error SERIAL PRIMARY KEY,
    rut_usuario VARCHAR(12) NOT NULL REFERENCES usuarios (rut) ON DELETE CASCADE,
    id_pregunta INTEGER NOT NULL REFERENCES banco_preguntas (id_pregunta),
    id_habilidad INTEGER NOT NULL REFERENCES historial_habilidades (id_progreso),
    veces_fallada INTEGER NOT NULL DEFAULT 1,
    resuelta BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_resolucion TIMESTAMPTZ,
    UNIQUE (rut_usuario, id_pregunta),
    CHECK (veces_fallada > 0)
);

CREATE INDEX idx_errores_usuario ON errores_favoritos (rut_usuario);
CREATE INDEX idx_errores_resuelta ON errores_favoritos (resuelta);
CREATE INDEX idx_errores_veces ON errores_favoritos (veces_fallada DESC);

-- ============================================================
-- 10. TABLA: configuracion
-- ============================================================
CREATE TABLE configuracion (
    id_config SERIAL PRIMARY KEY,
    clave VARCHAR(100) NOT NULL UNIQUE,
    valor VARCHAR(500) NOT NULL,
    descripcion VARCHAR(255)
);
