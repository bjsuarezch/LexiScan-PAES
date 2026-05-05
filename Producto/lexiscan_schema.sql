-- ============================================================
--  LexiScan PAES — Modelo Físico PostgreSQL
--  Stack: FastAPI + SQLAlchemy + PostgreSQL 15+
--  Generado para fase de Diseño y Desarrollo
-- ============================================================

-- Extensiones recomendadas
CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- encriptación
CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- UUIDs opcionales

-- ============================================================
-- ENUM TYPES
-- ============================================================

CREATE TYPE habilidad_lectora AS ENUM (
    'Localizar',
    'Interpretar',
    'Evaluar',
    'Lectura_Critica',
    'Vocabulario',
    'Tipos_de_Texto'
);

CREATE TYPE estado_gym AS ENUM (
    'pendiente',
    'en_progreso',
    'superada'
);

-- ============================================================
-- 1. TABLA: usuarios
-- ============================================================

CREATE TABLE usuarios (
    rut                 VARCHAR(12)     PRIMARY KEY,          -- Ej: 12345678-9
    nombre_completo     VARCHAR(150)    NOT NULL,
    email               VARCHAR(255)    NOT NULL UNIQUE,
    password_hash       VARCHAR(255)    NOT NULL,             -- bcrypt hash
    xp_total            INTEGER         NOT NULL DEFAULT 0 CHECK (xp_total >= 0),
    racha_actual        INTEGER         NOT NULL DEFAULT 0 CHECK (racha_actual >= 0),
    fecha_registro      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    activo              BOOLEAN         NOT NULL DEFAULT TRUE,
    ultimo_acceso       TIMESTAMPTZ
);

COMMENT ON TABLE  usuarios                  IS 'Entidad principal de autenticación (RF01)';
COMMENT ON COLUMN usuarios.rut              IS 'RUN chileno con dígito verificador. PK natural.';
COMMENT ON COLUMN usuarios.password_hash    IS 'Hash bcrypt — nunca almacenar en texto plano.';
COMMENT ON COLUMN usuarios.xp_total        IS 'Puntos de experiencia acumulados (RF03).';
COMMENT ON COLUMN usuarios.racha_actual     IS 'Días consecutivos de actividad (RF09).';

CREATE INDEX idx_usuarios_email ON usuarios(email);

-- ============================================================
-- 2. TABLA: historial_habilidades
-- ============================================================

CREATE TABLE historial_habilidades (
    id_progreso         SERIAL          PRIMARY KEY,
    rut_usuario         VARCHAR(12)     NOT NULL REFERENCES usuarios(rut) ON DELETE CASCADE,
    nombre_habilidad    habilidad_lectora NOT NULL,
    nivel_maestria      NUMERIC(5,2)    NOT NULL DEFAULT 0.00
                            CHECK (nivel_maestria BETWEEN 0 AND 100),
    ultima_actualizacion TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    UNIQUE (rut_usuario, nombre_habilidad)   -- una fila por habilidad por usuario
);

COMMENT ON TABLE  historial_habilidades             IS 'Avance por las 6 áreas técnicas del DEMRE.';
COMMENT ON COLUMN historial_habilidades.nivel_maestria IS 'Porcentaje 0-100 de dominio de la habilidad.';

CREATE INDEX idx_habilidades_rut     ON historial_habilidades(rut_usuario);
CREATE INDEX idx_habilidades_nivel   ON historial_habilidades(nivel_maestria);

-- ============================================================
-- 3. TABLA: preguntas_ia
-- ============================================================

CREATE TABLE preguntas_ia (
    id_pregunta         SERIAL          PRIMARY KEY,
    id_habilidad        INTEGER         NOT NULL REFERENCES historial_habilidades(id_progreso),
    texto_inedito       TEXT            NOT NULL,             -- pasaje generado por LLM
    enunciado           VARCHAR(500)    NOT NULL,
    alternativas        JSONB           NOT NULL,             -- {"A":"...","B":"...","C":"...","D":"..."}
    respuesta_correcta  CHAR(1)         NOT NULL CHECK (respuesta_correcta IN ('A','B','C','D')),
    justificacion_cot   TEXT            NOT NULL,             -- feedback pedagógico Chain-of-Thought
    modelo_ia           VARCHAR(60)     NOT NULL DEFAULT 'sinclair',  -- sinclair | gemini
    fecha_generacion    TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    activa              BOOLEAN         NOT NULL DEFAULT TRUE
);

COMMENT ON TABLE  preguntas_ia                   IS 'Ítems generados por IA Sinclair alineados al DEMRE.';
COMMENT ON COLUMN preguntas_ia.alternativas       IS 'JSONB con claves A,B,C,D y texto de cada alternativa.';
COMMENT ON COLUMN preguntas_ia.justificacion_cot  IS 'Retroalimentación pedagógica via Chain-of-Thought.';
COMMENT ON COLUMN preguntas_ia.modelo_ia          IS 'Motor LLM utilizado para la generación.';

CREATE INDEX idx_preguntas_habilidad ON preguntas_ia(id_habilidad);
CREATE INDEX idx_preguntas_activa    ON preguntas_ia(activa);

-- ============================================================
-- 4. TABLA: sesiones_examen
-- ============================================================

CREATE TABLE sesiones_examen (
    id_examen           SERIAL          PRIMARY KEY,
    rut_usuario         VARCHAR(12)     NOT NULL REFERENCES usuarios(rut) ON DELETE CASCADE,
    cantidad_preguntas  INTEGER         NOT NULL CHECK (cantidad_preguntas BETWEEN 10 AND 65),
    puntaje_obtenido    INTEGER         CHECK (puntaje_obtenido >= 0),
    puntaje_maximo      INTEGER         CHECK (puntaje_maximo > 0),
    tiempo_total        INTEGER         CHECK (tiempo_total >= 0), -- segundos
    es_impulsivo        BOOLEAN         NOT NULL DEFAULT FALSE,    -- alerta de impulsividad
    fecha_inicio        TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    fecha_fin           TIMESTAMPTZ,
    completado          BOOLEAN         NOT NULL DEFAULT FALSE
);

COMMENT ON TABLE  sesiones_examen              IS 'Módulo EXAMEN: simulacros adaptativos.';
COMMENT ON COLUMN sesiones_examen.es_impulsivo IS 'TRUE si el tiempo promedio por pregunta fue bajo el umbral.';
COMMENT ON COLUMN sesiones_examen.tiempo_total IS 'Duración total del simulacro en segundos.';

CREATE INDEX idx_sesion_usuario  ON sesiones_examen(rut_usuario);
CREATE INDEX idx_sesion_fecha    ON sesiones_examen(fecha_inicio DESC);

-- ============================================================
-- 5. TABLA PIVOTE: sesion_preguntas
--    Relaciona SesionExamen ↔ PreguntaIA con la respuesta dada
-- ============================================================

CREATE TABLE sesion_preguntas (
    id_sesion_pregunta  SERIAL          PRIMARY KEY,
    id_examen           INTEGER         NOT NULL REFERENCES sesiones_examen(id_examen) ON DELETE CASCADE,
    id_pregunta         INTEGER         NOT NULL REFERENCES preguntas_ia(id_pregunta),
    respuesta_dada      CHAR(1)         CHECK (respuesta_dada IN ('A','B','C','D')),
    es_correcta         BOOLEAN,
    tiempo_respuesta    INTEGER,        -- segundos por pregunta
    UNIQUE (id_examen, id_pregunta)
);

CREATE INDEX idx_sp_examen   ON sesion_preguntas(id_examen);
CREATE INDEX idx_sp_pregunta ON sesion_preguntas(id_pregunta);

-- ============================================================
-- 6. TABLA: economia_monedas
-- ============================================================

CREATE TABLE economia_monedas (
    rut_usuario         VARCHAR(12)     PRIMARY KEY REFERENCES usuarios(rut) ON DELETE CASCADE,
    saldo_monedas       INTEGER         NOT NULL DEFAULT 0 CHECK (saldo_monedas >= 0),
    total_acumulado     INTEGER         NOT NULL DEFAULT 0 CHECK (total_acumulado >= 0),
    ultima_transaccion  TIMESTAMPTZ
);

COMMENT ON TABLE economia_monedas IS 'Wallet de Monedas PAES por estudiante (gamificación).';

-- ============================================================
-- 7. TABLA: transacciones_monedas  (auditoría de economía)
-- ============================================================

CREATE TABLE transacciones_monedas (
    id_transaccion      SERIAL          PRIMARY KEY,
    rut_usuario         VARCHAR(12)     NOT NULL REFERENCES usuarios(rut),
    monto               INTEGER         NOT NULL,             -- positivo=ingreso, negativo=canje
    concepto            VARCHAR(200)    NOT NULL,
    fecha               TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_trans_usuario ON transacciones_monedas(rut_usuario);
CREATE INDEX idx_trans_fecha   ON transacciones_monedas(fecha DESC);

-- ============================================================
-- 8. TABLA: errores_favoritos
-- ============================================================

CREATE TABLE errores_favoritos (
    id_error            SERIAL          PRIMARY KEY,
    rut_usuario         VARCHAR(12)     NOT NULL REFERENCES usuarios(rut) ON DELETE CASCADE,
    id_pregunta         INTEGER         NOT NULL REFERENCES preguntas_ia(id_pregunta),
    id_habilidad        INTEGER         NOT NULL REFERENCES historial_habilidades(id_progreso),
    veces_fallada       INTEGER         NOT NULL DEFAULT 1 CHECK (veces_fallada > 0),
    resuelta            BOOLEAN         NOT NULL DEFAULT FALSE,
    fecha_registro      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    fecha_resolucion    TIMESTAMPTZ,
    UNIQUE (rut_usuario, id_pregunta)   -- evitar duplicados
);

COMMENT ON TABLE  errores_favoritos             IS 'Módulo de Revancha: ítems de bajo desempeño para el GYM.';
COMMENT ON COLUMN errores_favoritos.veces_fallada IS 'Contador de intentos fallidos. Prioriza el filtro del GYM.';

CREATE INDEX idx_errores_usuario   ON errores_favoritos(rut_usuario);
CREATE INDEX idx_errores_resuelta  ON errores_favoritos(resuelta);
CREATE INDEX idx_errores_veces     ON errores_favoritos(veces_fallada DESC); -- para filtro GYM

-- ============================================================
-- 9. TABLA: sesiones_gym
-- ============================================================

CREATE TABLE sesiones_gym (
    id_gym              SERIAL          PRIMARY KEY,
    rut_usuario         VARCHAR(12)     NOT NULL REFERENCES usuarios(rut) ON DELETE CASCADE,
    id_error            INTEGER         NOT NULL REFERENCES errores_favoritos(id_error),
    intentos            INTEGER         NOT NULL DEFAULT 0 CHECK (intentos >= 0),
    estado              estado_gym      NOT NULL DEFAULT 'pendiente',
    fecha_sesion        TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    fecha_superacion    TIMESTAMPTZ
);

COMMENT ON TABLE sesiones_gym IS 'Misiones de Refuerzo del Módulo GYM.';

CREATE INDEX idx_gym_usuario ON sesiones_gym(rut_usuario);
CREATE INDEX idx_gym_estado  ON sesiones_gym(estado);

-- ============================================================
-- TRIGGER: actualizar nivel_maestria al responder pregunta
-- ============================================================

CREATE OR REPLACE FUNCTION actualizar_maestria()
RETURNS TRIGGER AS $$
BEGIN
    -- Recalcula maestría como % de respuestas correctas en esa habilidad
    UPDATE historial_habilidades h
    SET nivel_maestria = (
        SELECT ROUND(
            100.0 * COUNT(*) FILTER (WHERE sp.es_correcta = TRUE)
            / NULLIF(COUNT(*), 0)
        , 2)
        FROM sesion_preguntas sp
        JOIN preguntas_ia p ON p.id_pregunta = sp.id_pregunta
        WHERE p.id_habilidad = h.id_progreso
          AND h.rut_usuario = (
              SELECT rut_usuario FROM sesiones_examen WHERE id_examen = NEW.id_examen
          )
    ),
    ultima_actualizacion = NOW()
    WHERE h.id_progreso = (
        SELECT id_habilidad FROM preguntas_ia WHERE id_pregunta = NEW.id_pregunta
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_actualizar_maestria
AFTER INSERT OR UPDATE OF es_correcta ON sesion_preguntas
FOR EACH ROW EXECUTE FUNCTION actualizar_maestria();

-- ============================================================
-- TRIGGER: registrar error_favorito al fallar una pregunta
-- ============================================================

CREATE OR REPLACE FUNCTION registrar_error_favorito()
RETURNS TRIGGER AS $$
DECLARE
    v_rut      VARCHAR(12);
    v_habilidad INTEGER;
BEGIN
    IF NEW.es_correcta = FALSE THEN
        SELECT rut_usuario INTO v_rut FROM sesiones_examen WHERE id_examen = NEW.id_examen;
        SELECT id_habilidad INTO v_habilidad FROM preguntas_ia WHERE id_pregunta = NEW.id_pregunta;

        INSERT INTO errores_favoritos (rut_usuario, id_pregunta, id_habilidad, veces_fallada)
        VALUES (v_rut, NEW.id_pregunta, v_habilidad, 1)
        ON CONFLICT (rut_usuario, id_pregunta)
        DO UPDATE SET veces_fallada = errores_favoritos.veces_fallada + 1;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_registrar_error
AFTER INSERT ON sesion_preguntas
FOR EACH ROW EXECUTE FUNCTION registrar_error_favorito();

-- ============================================================
-- DATOS INICIALES: habilidades para nuevo usuario (función)
-- ============================================================

CREATE OR REPLACE FUNCTION inicializar_habilidades(p_rut VARCHAR)
RETURNS VOID AS $$
DECLARE
    habilidad habilidad_lectora;
BEGIN
    FOREACH habilidad IN ARRAY ENUM_RANGE(NULL::habilidad_lectora) LOOP
        INSERT INTO historial_habilidades (rut_usuario, nombre_habilidad, nivel_maestria)
        VALUES (p_rut, habilidad, 0.00)
        ON CONFLICT DO NOTHING;
    END LOOP;
    -- Crear wallet de monedas
    INSERT INTO economia_monedas (rut_usuario) VALUES (p_rut) ON CONFLICT DO NOTHING;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- VISTAS ÚTILES
-- ============================================================

-- Vista: dashboard de maestría por usuario
CREATE VIEW v_dashboard_maestria AS
SELECT
    u.rut,
    u.nombre_completo,
    u.xp_total,
    u.racha_actual,
    h.nombre_habilidad,
    h.nivel_maestria,
    e.saldo_monedas
FROM usuarios u
JOIN historial_habilidades h  ON h.rut_usuario = u.rut
JOIN economia_monedas e       ON e.rut_usuario = u.rut;

-- Vista: errores pendientes para GYM (top por veces fallada)
CREATE VIEW v_gym_errores_pendientes AS
SELECT
    ef.rut_usuario,
    ef.id_error,
    ef.id_pregunta,
    ef.veces_fallada,
    h.nombre_habilidad,
    h.nivel_maestria
FROM errores_favoritos ef
JOIN historial_habilidades h ON h.id_progreso = ef.id_habilidad
WHERE ef.resuelta = FALSE
ORDER BY ef.veces_fallada DESC, h.nivel_maestria ASC;

-- ============================================================
-- FIN DEL ESQUEMA
-- ============================================================
