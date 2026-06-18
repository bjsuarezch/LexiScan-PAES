--
-- PostgreSQL database dump
--

\restrict ZxmVdbOWxyufDKCD6FhqfjGFGdahb8OTREwXklpBHX0231FV2i1827URUoVeoDN

-- Dumped from database version 15.17 (Debian 15.17-1.pgdg13+1)
-- Dumped by pg_dump version 18.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: habilidad_lectora; Type: TYPE; Schema: public; Owner: user_lexiscan
--

CREATE TYPE public.habilidad_lectora AS ENUM (
    'Localizar',
    'Interpretar',
    'Evaluar',
    'Lectura_Critica',
    'Vocabulario',
    'Tipos_de_Texto'
);


ALTER TYPE public.habilidad_lectora OWNER TO user_lexiscan;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: banco_preguntas; Type: TABLE; Schema: public; Owner: user_lexiscan
--

CREATE TABLE public.banco_preguntas (
    id_pregunta integer NOT NULL,
    id_habilidad integer NOT NULL,
    texto_inedito text NOT NULL,
    enunciado character varying(500) NOT NULL,
    alternativas jsonb NOT NULL,
    respuesta_correcta character(1) NOT NULL,
    justificacion_cot text NOT NULL,
    dificultad character varying(20) DEFAULT 'medio'::character varying NOT NULL,
    fecha_creacion timestamp with time zone DEFAULT now() NOT NULL,
    activa boolean DEFAULT true NOT NULL,
    CONSTRAINT banco_preguntas_respuesta_correcta_check CHECK ((respuesta_correcta = ANY (ARRAY['A'::bpchar, 'B'::bpchar, 'C'::bpchar, 'D'::bpchar])))
);


ALTER TABLE public.banco_preguntas OWNER TO user_lexiscan;

--
-- Name: banco_preguntas_id_pregunta_seq; Type: SEQUENCE; Schema: public; Owner: user_lexiscan
--

CREATE SEQUENCE public.banco_preguntas_id_pregunta_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.banco_preguntas_id_pregunta_seq OWNER TO user_lexiscan;

--
-- Name: banco_preguntas_id_pregunta_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user_lexiscan
--

ALTER SEQUENCE public.banco_preguntas_id_pregunta_seq OWNED BY public.banco_preguntas.id_pregunta;


--
-- Name: configuracion; Type: TABLE; Schema: public; Owner: user_lexiscan
--

CREATE TABLE public.configuracion (
    id_config integer NOT NULL,
    clave character varying(100) NOT NULL,
    valor character varying(500) NOT NULL,
    descripcion character varying(255)
);


ALTER TABLE public.configuracion OWNER TO user_lexiscan;

--
-- Name: configuracion_id_config_seq; Type: SEQUENCE; Schema: public; Owner: user_lexiscan
--

CREATE SEQUENCE public.configuracion_id_config_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.configuracion_id_config_seq OWNER TO user_lexiscan;

--
-- Name: configuracion_id_config_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user_lexiscan
--

ALTER SEQUENCE public.configuracion_id_config_seq OWNED BY public.configuracion.id_config;


--
-- Name: economia_monedas; Type: TABLE; Schema: public; Owner: user_lexiscan
--

CREATE TABLE public.economia_monedas (
    rut_usuario character varying(12) NOT NULL,
    saldo_monedas integer DEFAULT 0 NOT NULL,
    total_acumulado integer DEFAULT 0 NOT NULL,
    ultima_transaccion timestamp with time zone
);


ALTER TABLE public.economia_monedas OWNER TO user_lexiscan;

--
-- Name: errores_favoritos; Type: TABLE; Schema: public; Owner: user_lexiscan
--

CREATE TABLE public.errores_favoritos (
    id_error integer NOT NULL,
    rut_usuario character varying(12) NOT NULL,
    id_pregunta integer NOT NULL,
    id_habilidad integer NOT NULL,
    veces_fallada integer DEFAULT 1 NOT NULL,
    resuelta boolean DEFAULT false NOT NULL,
    fecha_registro timestamp with time zone DEFAULT now() NOT NULL,
    fecha_resolucion timestamp with time zone,
    CONSTRAINT errores_favoritos_veces_fallada_check CHECK ((veces_fallada > 0))
);


ALTER TABLE public.errores_favoritos OWNER TO user_lexiscan;

--
-- Name: errores_favoritos_id_error_seq; Type: SEQUENCE; Schema: public; Owner: user_lexiscan
--

CREATE SEQUENCE public.errores_favoritos_id_error_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.errores_favoritos_id_error_seq OWNER TO user_lexiscan;

--
-- Name: errores_favoritos_id_error_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user_lexiscan
--

ALTER SEQUENCE public.errores_favoritos_id_error_seq OWNED BY public.errores_favoritos.id_error;


--
-- Name: historial_habilidades; Type: TABLE; Schema: public; Owner: user_lexiscan
--

CREATE TABLE public.historial_habilidades (
    id_progreso integer NOT NULL,
    rut_usuario character varying(12) NOT NULL,
    nombre_habilidad public.habilidad_lectora NOT NULL,
    nivel_maestria numeric(5,2) DEFAULT 0.00 NOT NULL,
    ultima_actualizacion timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT historial_habilidades_nivel_maestria_check CHECK (((nivel_maestria >= (0)::numeric) AND (nivel_maestria <= (100)::numeric)))
);


ALTER TABLE public.historial_habilidades OWNER TO user_lexiscan;

--
-- Name: historial_habilidades_id_progreso_seq; Type: SEQUENCE; Schema: public; Owner: user_lexiscan
--

CREATE SEQUENCE public.historial_habilidades_id_progreso_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.historial_habilidades_id_progreso_seq OWNER TO user_lexiscan;

--
-- Name: historial_habilidades_id_progreso_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user_lexiscan
--

ALTER SEQUENCE public.historial_habilidades_id_progreso_seq OWNED BY public.historial_habilidades.id_progreso;


--
-- Name: preguntas_ia; Type: TABLE; Schema: public; Owner: user_lexiscan
--

CREATE TABLE public.preguntas_ia (
    id_pregunta integer NOT NULL,
    id_pregunta_origen integer,
    id_habilidad integer NOT NULL,
    texto_inedito text NOT NULL,
    enunciado character varying(500) NOT NULL,
    alternativas jsonb NOT NULL,
    respuesta_correcta character(1) NOT NULL,
    justificacion_cot text NOT NULL,
    modelo_ia character varying(60) DEFAULT 'sinclair'::character varying NOT NULL,
    fecha_generacion timestamp with time zone DEFAULT now() NOT NULL,
    activa boolean DEFAULT true NOT NULL,
    CONSTRAINT preguntas_ia_respuesta_correcta_check CHECK ((respuesta_correcta = ANY (ARRAY['A'::bpchar, 'B'::bpchar, 'C'::bpchar, 'D'::bpchar])))
);


ALTER TABLE public.preguntas_ia OWNER TO user_lexiscan;

--
-- Name: preguntas_ia_id_pregunta_seq; Type: SEQUENCE; Schema: public; Owner: user_lexiscan
--

CREATE SEQUENCE public.preguntas_ia_id_pregunta_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.preguntas_ia_id_pregunta_seq OWNER TO user_lexiscan;

--
-- Name: preguntas_ia_id_pregunta_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user_lexiscan
--

ALTER SEQUENCE public.preguntas_ia_id_pregunta_seq OWNED BY public.preguntas_ia.id_pregunta;


--
-- Name: sesion_preguntas; Type: TABLE; Schema: public; Owner: user_lexiscan
--

CREATE TABLE public.sesion_preguntas (
    id_sesion_pregunta integer NOT NULL,
    id_examen integer NOT NULL,
    id_pregunta integer NOT NULL,
    respuesta_dada character(1),
    es_correcta boolean,
    tiempo_respuesta integer,
    CONSTRAINT sesion_preguntas_respuesta_dada_check CHECK ((respuesta_dada = ANY (ARRAY['A'::bpchar, 'B'::bpchar, 'C'::bpchar, 'D'::bpchar])))
);


ALTER TABLE public.sesion_preguntas OWNER TO user_lexiscan;

--
-- Name: sesion_preguntas_id_sesion_pregunta_seq; Type: SEQUENCE; Schema: public; Owner: user_lexiscan
--

CREATE SEQUENCE public.sesion_preguntas_id_sesion_pregunta_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sesion_preguntas_id_sesion_pregunta_seq OWNER TO user_lexiscan;

--
-- Name: sesion_preguntas_id_sesion_pregunta_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user_lexiscan
--

ALTER SEQUENCE public.sesion_preguntas_id_sesion_pregunta_seq OWNED BY public.sesion_preguntas.id_sesion_pregunta;


--
-- Name: sesiones_examen; Type: TABLE; Schema: public; Owner: user_lexiscan
--

CREATE TABLE public.sesiones_examen (
    id_examen integer NOT NULL,
    rut_usuario character varying(12) NOT NULL,
    cantidad_preguntas integer NOT NULL,
    puntaje_obtenido integer,
    puntaje_maximo integer,
    tiempo_total integer,
    es_impulsivo boolean DEFAULT false NOT NULL,
    fecha_inicio timestamp with time zone DEFAULT now() NOT NULL,
    fecha_fin timestamp with time zone,
    completado boolean DEFAULT false NOT NULL
);


ALTER TABLE public.sesiones_examen OWNER TO user_lexiscan;

--
-- Name: sesiones_examen_id_examen_seq; Type: SEQUENCE; Schema: public; Owner: user_lexiscan
--

CREATE SEQUENCE public.sesiones_examen_id_examen_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sesiones_examen_id_examen_seq OWNER TO user_lexiscan;

--
-- Name: sesiones_examen_id_examen_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user_lexiscan
--

ALTER SEQUENCE public.sesiones_examen_id_examen_seq OWNED BY public.sesiones_examen.id_examen;


--
-- Name: transacciones_monedas; Type: TABLE; Schema: public; Owner: user_lexiscan
--

CREATE TABLE public.transacciones_monedas (
    id_transaccion integer NOT NULL,
    rut_usuario character varying(12) NOT NULL,
    monto integer NOT NULL,
    concepto character varying(200) NOT NULL,
    fecha timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.transacciones_monedas OWNER TO user_lexiscan;

--
-- Name: transacciones_monedas_id_transaccion_seq; Type: SEQUENCE; Schema: public; Owner: user_lexiscan
--

CREATE SEQUENCE public.transacciones_monedas_id_transaccion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.transacciones_monedas_id_transaccion_seq OWNER TO user_lexiscan;

--
-- Name: transacciones_monedas_id_transaccion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user_lexiscan
--

ALTER SEQUENCE public.transacciones_monedas_id_transaccion_seq OWNED BY public.transacciones_monedas.id_transaccion;


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: user_lexiscan
--

CREATE TABLE public.usuarios (
    rut character varying(12) NOT NULL,
    nombre_completo character varying(150) NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    xp_total integer DEFAULT 0 NOT NULL,
    racha_actual integer DEFAULT 0 NOT NULL,
    fecha_registro timestamp with time zone DEFAULT now() NOT NULL,
    activo boolean DEFAULT true NOT NULL,
    ultimo_acceso timestamp with time zone,
    es_admin boolean DEFAULT false NOT NULL
);


ALTER TABLE public.usuarios OWNER TO user_lexiscan;

--
-- Name: banco_preguntas id_pregunta; Type: DEFAULT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.banco_preguntas ALTER COLUMN id_pregunta SET DEFAULT nextval('public.banco_preguntas_id_pregunta_seq'::regclass);


--
-- Name: configuracion id_config; Type: DEFAULT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.configuracion ALTER COLUMN id_config SET DEFAULT nextval('public.configuracion_id_config_seq'::regclass);


--
-- Name: errores_favoritos id_error; Type: DEFAULT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.errores_favoritos ALTER COLUMN id_error SET DEFAULT nextval('public.errores_favoritos_id_error_seq'::regclass);


--
-- Name: historial_habilidades id_progreso; Type: DEFAULT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.historial_habilidades ALTER COLUMN id_progreso SET DEFAULT nextval('public.historial_habilidades_id_progreso_seq'::regclass);


--
-- Name: preguntas_ia id_pregunta; Type: DEFAULT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.preguntas_ia ALTER COLUMN id_pregunta SET DEFAULT nextval('public.preguntas_ia_id_pregunta_seq'::regclass);


--
-- Name: sesion_preguntas id_sesion_pregunta; Type: DEFAULT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.sesion_preguntas ALTER COLUMN id_sesion_pregunta SET DEFAULT nextval('public.sesion_preguntas_id_sesion_pregunta_seq'::regclass);


--
-- Name: sesiones_examen id_examen; Type: DEFAULT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.sesiones_examen ALTER COLUMN id_examen SET DEFAULT nextval('public.sesiones_examen_id_examen_seq'::regclass);


--
-- Name: transacciones_monedas id_transaccion; Type: DEFAULT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.transacciones_monedas ALTER COLUMN id_transaccion SET DEFAULT nextval('public.transacciones_monedas_id_transaccion_seq'::regclass);


--
-- Data for Name: banco_preguntas; Type: TABLE DATA; Schema: public; Owner: user_lexiscan
--

COPY public.banco_preguntas (id_pregunta, id_habilidad, texto_inedito, enunciado, alternativas, respuesta_correcta, justificacion_cot, dificultad, fecha_creacion, activa) FROM stdin;
1	2	En 2023, un equipo de científicos chilenos descubrió una nueva especie de orquídea en la Región de la Araucanía. Bautizada como *Orchis patagonica*, esta planta crece exclusivamente en zonas rocosas a más de 1.200 metros de altitud y florece entre mayo y julio. Su característica más destacada es su capacidad para almacenar agua en sus tallos, lo que le permite sobrevivir en climas extremos. Los investigadores señalan que su hábitat está amenazado por la minería y la deforestación, lo que ha motivado a las autoridades a declararla especie protegida.\n\nLa investigación, publicada en la revista *Biodiversidad Chilena*, incluyó el análisis de 120 ejemplares recolectados en tres años. Los científicos utilizaron técnicas de ADN para confirmar que no se trata de una variante de especies ya conocidas. Además, observaron que *Orchis patagonica* depende de un tipo específico de abeja para su polinización, lo que limita su dispersión. Según el líder del estudio, esta orquídea podría ser clave para entender la adaptación de plantas en ecosistemas frágiles.	¿Cuál es la principal característica que permite a *Orchis patagonica* sobrevivir en climas extremos?	{"A": "Su capacidad para almacenar agua en los tallos", "B": "Su florecimiento entre mayo y julio", "C": "Su crecimiento en zonas rocosas", "D": "Su dependencia de un tipo específico de abeja"}	A	El texto menciona explícitamente que 'su característica más destacada es su capacidad para almacenar agua en sus tallos', lo que directamente responde a la pregunta.	medio	2026-05-14 19:20:22.28167+00	t
2	2	En 2023, un equipo de científicos chilenos descubrió una nueva especie de orquídea en la Región de la Araucanía. Bautizada como *Orchis patagonica*, esta planta crece exclusivamente en zonas rocosas a más de 1.200 metros de altitud y florece entre mayo y julio. Su característica más destacada es su capacidad para almacenar agua en sus tallos, lo que le permite sobrevivir en climas extremos. Los investigadores señalan que su hábitat está amenazado por la minería y la deforestación, lo que ha motivado a las autoridades a declararla especie protegida.\n\nLa investigación, publicada en la revista *Biodiversidad Chilena*, incluyó el análisis de 120 ejemplares recolectados en tres años. Los científicos utilizaron técnicas de ADN para confirmar que no se trata de una variante de especies ya conocidas. Además, observaron que *Orchis patagonica* depende de un tipo específico de abeja para su polinización, lo que limita su dispersión. Según el líder del estudio, esta orquídea podría ser clave para entender la adaptación de plantas en ecosistemas frágiles.	¿Cuántos ejemplares de *Orchis patagonica* fueron analizados en la investigación?	{"A": "12 ejemplares", "B": "120 ejemplares", "C": "210 ejemplares", "D": "300 ejemplares"}	B	El texto indica que 'la investigación incluyó el análisis de 120 ejemplares', lo que corresponde a la alternativa B.	medio	2026-05-14 19:20:22.297297+00	t
3	2	En 2023, un equipo de científicos chilenos descubrió una nueva especie de orquídea en la Región de la Araucanía. Bautizada como *Orchis patagonica*, esta planta crece exclusivamente en zonas rocosas a más de 1.200 metros de altitud y florece entre mayo y julio. Su característica más destacada es su capacidad para almacenar agua en sus tallos, lo que le permite sobrevivir en climas extremos. Los investigadores señalan que su hábitat está amenazado por la minería y la deforestación, lo que ha motivado a las autoridades a declararla especie protegida.\n\nLa investigación, publicada en la revista *Biodiversidad Chilena*, incluyó el análisis de 120 ejemplares recolectados en tres años. Los científicos utilizaron técnicas de ADN para confirmar que no se trata de una variante de especies ya conocidas. Además, observaron que *Orchis patagonica* depende de un tipo específico de abeja para su polinización, lo que limita su dispersión. Según el líder del estudio, esta orquídea podría ser clave para entender la adaptación de plantas en ecosistemas frágiles.	¿Qué factor limita la dispersión de *Orchis patagonica* según el texto?	{"A": "La minería", "B": "La deforestación", "C": "La dependencia de un tipo específico de abeja", "D": "La altitud de su hábitat"}	C	El texto establece que 'depende de un tipo específico de abeja para su polinización, lo que limita su dispersión', lo que corresponde a la alternativa C.	medio	2026-05-14 19:20:22.307302+00	t
4	2	En 2023, un equipo de científicos chilenos descubrió una nueva especie de orquídea en la Región de la Araucanía. Bautizada como *Orchis patagonica*, esta planta crece exclusivamente en zonas rocosas a más de 1.200 metros de altitud y florece entre mayo y julio. Su característica más destacada es su capacidad para almacenar agua en sus tallos, lo que le permite sobrevivir en climas extremos. Los investigadores señalan que su hábitat está amenazado por la minería y la deforestación, lo que ha motivado a las autoridades a declararla especie protegida.\n\nLa investigación, publicada en la revista *Biodiversidad Chilena*, incluyó el análisis de 120 ejemplares recolectados en tres años. Los científicos utilizaron técnicas de ADN para confirmar que no se trata de una variante de especies ya conocidas. Además, observaron que *Orchis patagonica* depende de un tipo específico de abeja para su polinización, lo que limita su dispersión. Según el líder del estudio, esta orquídea podría ser clave para entender la adaptación de plantas en ecosistemas frágiles.	¿Cuál es la altura mínima en la que crece *Orchis patagonica*?	{"A": "800 metros", "B": "1.000 metros", "C": "1.200 metros", "D": "1.500 metros"}	C	El texto afirma que 'crece exclusivamente en zonas rocosas a más de 1.200 metros de altitud', lo que corresponde a la alternativa C.	medio	2026-05-14 19:20:22.316562+00	t
5	3	La contaminación lumínica, causada por el exceso de iluminación artificial en espacios nocturnos, afecta profundamente a los ecosistemas. Animales nocturnos como murciélagos, insectos y aves migratorias dependen de la oscuridad para cazar, navegar y reproducirse. La luz artificial altera sus ciclos naturales, desorienta a las crías de tortugas marinas que siguen la luz de la luna para llegar al mar, y atrae a polillas hacia fuentes de luz que no les proporcionan alimento. Además, la contaminación lumínica contribuye al aumento de la temperatura ambiental, afectando la biodiversidad.\n\nPara mitigar estos efectos, se recomienda usar iluminación direccional y de menor intensidad, evitar iluminar áreas no necesarias y promover el uso de fuentes de luz de longitud de onda adecuada. Estudios recientes sugieren que reducir la contaminación lumínica podría revertir hasta un 30% de la disminución en poblaciones de insectos nocturnos. Sin embargo, la implementación de estas medidas requiere conciencia ciudadana y políticas públicas efectivas.	¿Por qué los animales nocturnos son especialmente afectados por la contaminación lumínica?	{"A": "Porque necesitan la oscuridad para cazar y navegar.", "B": "Porque son más sensibles al calor generado por las luces.", "C": "Porque la luz artificial les proporciona alimento adicional.", "D": "Porque prefieren la luz artificial a la natural."}	A	El texto indica que los animales nocturnos dependen de la oscuridad para sus actividades vitales, como cazar y navegar. La luz artificial interfiere con estos procesos, desorientándolos y alterando sus ciclos naturales.	medio	2026-05-14 19:23:30.352514+00	t
6	3	La contaminación lumínica, causada por el exceso de iluminación artificial en espacios nocturnos, afecta profundamente a los ecosistemas. Animales nocturnos como murciélagos, insectos y aves migratorias dependen de la oscuridad para cazar, navegar y reproducirse. La luz artificial altera sus ciclos naturales, desorienta a las crías de tortugas marinas que siguen la luz de la luna para llegar al mar, y atrae a polillas hacia fuentes de luz que no les proporcionan alimento. Además, la contaminación lumínica contribuye al aumento de la temperatura ambiental, afectando la biodiversidad.\n\nPara mitigar estos efectos, se recomienda usar iluminación direccional y de menor intensidad, evitar iluminar áreas no necesarias y promover el uso de fuentes de luz de longitud de onda adecuada. Estudios recientes sugieren que reducir la contaminación lumínica podría revertir hasta un 30% de la disminución en poblaciones de insectos nocturnos. Sin embargo, la implementación de estas medidas requiere conciencia ciudadana y políticas públicas efectivas.	¿Cuál es el propósito principal del segundo párrafo del texto?	{"A": "Explicar las causas de la contaminación lumínica.", "B": "Describir los efectos de la contaminación lumínica en los ecosistemas.", "C": "Proponer soluciones para reducir la contaminación lumínica.", "D": "Argumentar que la contaminación lumínica es irrelevante."}	C	El segundo párrafo se enfoca en sugerir estrategias como el uso de iluminación direccional y políticas públicas para abordar el problema de la contaminación lumínica.	medio	2026-05-14 19:23:30.359555+00	t
8	3	La contaminación lumínica, causada por el exceso de iluminación artificial en espacios nocturnos, afecta profundamente a los ecosistemas. Animales nocturnos como murciélagos, insectos y aves migratorias dependen de la oscuridad para cazar, navegar y reproducirse. La luz artificial altera sus ciclos naturales, desorienta a las crías de tortugas marinas que siguen la luz de la luna para llegar al mar, y atrae a polillas hacia fuentes de luz que no les proporcionan alimento. Además, la contaminación lumínica contribuye al aumento de la temperatura ambiental, afectando la biodiversidad.\n\nPara mitigar estos efectos, se recomienda usar iluminación direccional y de menor intensidad, evitar iluminar áreas no necesarias y promover el uso de fuentes de luz de longitud de onda adecuada. Estudios recientes sugieren que reducir la contaminación lumínica podría revertir hasta un 30% de la disminución en poblaciones de insectos nocturnos. Sin embargo, la implementación de estas medidas requiere conciencia ciudadana y políticas públicas efectivas.	¿Qué se puede inferir sobre la efectividad de las soluciones propuestas en el texto?	{"A": "Que son costosas y difíciles de implementar.", "B": "Que requieren cambios tecnológicos complejos.", "C": "Que dependen de la colaboración ciudadana y estatal.", "D": "Que son temporales y no resuelven el problema a largo plazo."}	C	El texto menciona que la implementación de las soluciones necesitaria 'conciencia ciudadana y políticas públicas efectivas', lo que implica que su éxito depende de múltiples actores.	medio	2026-05-14 19:23:30.371928+00	t
7	3	La contaminación lumínica, causada por el exceso de iluminación artificial en espacios nocturnos, afecta profundamente a los ecosistemas. Animales nocturnos como murciélagos, insectos y aves migratorias dependen de la oscuridad para cazar, navegar y reproducirse. La luz artificial altera sus ciclos naturales, desorienta a las crías de tortugas marinas que siguen la luz de la luna para llegar al mar, y atrae a polillas hacia fuentes de luz que no les proporcionan alimento. Además, la contaminación lumínica contribuye al aumento de la temperatura ambiental, afectando la biodiversidad.\n\nPara mitigar estos efectos, se recomienda usar iluminación direccional y de menor intensidad, evitar iluminar áreas no necesarias y promover el uso de fuentes de luz de longitud de onda adecuada. Estudios recientes sugieren que reducir la contaminación lumínica podría revertir hasta un 30% de la disminución en poblaciones de insectos nocturnos. Sin embargo, la implementación de estas medidas requiere conciencia ciudadana y políticas públicas efectivas.	¿Qué implica el texto al mencionar que 'la contaminación lumínica contribuye al aumento de la temperatura ambiental'?	{"A": "Que la luz artificial genera calor directamente.", "B": "Que la energía consumida por las luces emite CO₂.", "C": "Que la luz artificial afecta la radiación solar.", "D": "Que la oscuridad natural absorbe más calor."}	B	El texto sugiere una relación indirecta entre la contaminación lumínica y el calentamiento global, asociada al consumo energético de las luces artificiales, que emiten gases de efecto invernadero.	medio	2026-05-14 19:23:30.36604+00	t
9	7	La deforestación en la Amazonía ha alcanzado niveles alarmantes en los últimos años. Según estudios recientes, el 17% de la selva ha sido destruido por actividades como la ganadería extensiva, la agricultura de soya y la minería ilegal. Estas prácticas no solo reducen la biodiversidad, sino que también liberan grandes cantidades de dióxido de carbono, agravando el cambio climático. Además, comunidades indígenas que dependen del bosque para su subsistencia enfrentan desplazamientos forzados y pérdida de tradiciones ancestrales.\n\nAnte esta crisis, gobiernos y organizaciones internacionales han impulsado programas de reforestación y monitoreo satelital para controlar las actividades ilegales. Sin embargo, críticos señalan que estas medidas son insuficientes si no se aborda la corrupción y la falta de políticas sostenibles. Expertos recomiendan combinar enfoques tecnológicos con participación comunitaria para garantizar la preservación del ecosistema y el bienestar de sus habitantes.	¿Cuál es el tipo de texto predominante en el fragmento leído?	{"A": "Informativo", "B": "Narrativo", "C": "Argumentativo", "D": "Descriptivo"}	A	El texto presenta datos estadísticos, causas y consecuencias de un fenómeno ambiental, con un enfoque objetivo y basado en hechos. No incluye elementos narrativos (historias), argumentativos (posiciones defendidas) ni descriptivos (detalles sensoriales), lo que caracteriza a un texto informativo.	medio	2026-05-14 19:28:20.007814+00	t
10	4	La transición hacia fuentes renovables de energía es un desafío crucial para mitigar el cambio climático. Según un estudio reciente, el uso de energía solar y eólica podría cubrir el 80% de la demanda eléctrica global para 2040, siempre que se eliminen las barreras tecnológicas y económicas actuales. Sin embargo, críticos señalan que esta estimación ignora la variabilidad de estas fuentes, especialmente en regiones con clima inestable. Por otro lado, expertos en políticas energéticas argumentan que los subsidios a los combustibles fósiles, que aún representan el 60% del presupuesto energético mundial, son un obstáculo principal para la adopción masiva de tecnologías limpias. A pesar de esto, países como Dinamarca y Costa Rica han demostrado que es posible alcanzar un 100% de energía renovable mediante combinaciones innovadoras de hidroeléctrica, eólica y almacenamiento de baterías.	¿Cuál es la principal crítica que se hace al estudio mencionado sobre la energía renovable?	{"A": "No considera el costo de producción de paneles solares.", "B": "Subestima el potencial de la energía geotérmica.", "C": "No aborda la variabilidad de las fuentes renovables en climas inestables.", "D": "Sobreestima la capacidad de almacenamiento de baterías."}	C	El texto indica explícitamente que los críticos señalan que la estimación ignora la variabilidad de las fuentes renovables en regiones con clima inestable, lo que corresponde a la alternativa C.	medio	2026-05-14 19:31:17.354877+00	t
11	4	La transición hacia fuentes renovables de energía es un desafío crucial para mitigar el cambio climático. Según un estudio reciente, el uso de energía solar y eólica podría cubrir el 80% de la demanda eléctrica global para 2040, siempre que se eliminen las barreras tecnológicas y económicas actuales. Sin embargo, críticos señalan que esta estimación ignora la variabilidad de estas fuentes, especialmente en regiones con clima inestable. Por otro lado, expertos en políticas energéticas argumentan que los subsidios a los combustibles fósiles, que aún representan el 60% del presupuesto energético mundial, son un obstáculo principal para la adopción masiva de tecnologías limpias. A pesar de esto, países como Dinamarca y Costa Rica han demostrado que es posible alcanzar un 100% de energía renovable mediante combinaciones innovadoras de hidroeléctrica, eólica y almacenamiento de baterías.	¿Qué factor, según el texto, impide la adopción masiva de tecnologías limpias?	{"A": "La falta de conciencia ciudadana sobre el cambio climático.", "B": "Los subsidios a los combustibles fósiles.", "C": "La escasez de recursos minerales para fabricar paneles solares.", "D": "La resistencia de los gobiernos a cambiar políticas energéticas."}	B	El texto menciona que los subsidios a los combustibles fósiles, que representan el 60% del presupuesto energético mundial, son un obstáculo principal, lo que corresponde a la alternativa B.	medio	2026-05-14 19:31:17.379505+00	t
12	4	La transición hacia fuentes renovables de energía es un desafío crucial para mitigar el cambio climático. Según un estudio reciente, el uso de energía solar y eólica podría cubrir el 80% de la demanda eléctrica global para 2040, siempre que se eliminen las barreras tecnológicas y económicas actuales. Sin embargo, críticos señalan que esta estimación ignora la variabilidad de estas fuentes, especialmente en regiones con clima inestable. Por otro lado, expertos en políticas energéticas argumentan que los subsidios a los combustibles fósiles, que aún representan el 60% del presupuesto energético mundial, son un obstáculo principal para la adopción masiva de tecnologías limpias. A pesar de esto, países como Dinamarca y Costa Rica han demostrado que es posible alcanzar un 100% de energía renovable mediante combinaciones innovadoras de hidroeléctrica, eólica y almacenamiento de baterías.	¿Qué ejemplo del texto respalda la viabilidad de un sistema 100% renovable?	{"A": "La reducción de emisiones en Alemania.", "B": "El uso de hidroeléctrica en Canadá.", "C": "La combinación de fuentes en Dinamarca y Costa Rica.", "D": "El avance tecnológico en baterías de litio."}	C	El texto cita explícitamente a Dinamarca y Costa Rica como países que han logrado un 100% de energía renovable mediante combinaciones innovadoras, lo que corresponde a la alternativa C.	medio	2026-05-14 19:31:17.391412+00	t
13	4	La transición hacia fuentes renovables de energía es un desafío crucial para mitigar el cambio climático. Según un estudio reciente, el uso de energía solar y eólica podría cubrir el 80% de la demanda eléctrica global para 2040, siempre que se eliminen las barreras tecnológicas y económicas actuales. Sin embargo, críticos señalan que esta estimación ignora la variabilidad de estas fuentes, especialmente en regiones con clima inestable. Por otro lado, expertos en políticas energéticas argumentan que los subsidios a los combustibles fósiles, que aún representan el 60% del presupuesto energético mundial, son un obstáculo principal para la adopción masiva de tecnologías limpias. A pesar de esto, países como Dinamarca y Costa Rica han demostrado que es posible alcanzar un 100% de energía renovable mediante combinaciones innovadoras de hidroeléctrica, eólica y almacenamiento de baterías.	¿Cuál es el argumento central del texto sobre la transición energética?	{"A": "Es imposible alcanzar metas ambiciosas de energía renovable sin inversión extranjera.", "B": "La variabilidad climática invalida cualquier plan de transición energética.", "C": "La eliminación de subsidios a combustibles fósiles es clave para avanzar en renovables.", "D": "Las tecnologías actuales no permiten reemplazar más del 50% de la energía actual."}	C	El texto enfatiza que los subsidios a los combustibles fósiles son un obstáculo principal y que su eliminación es clave para avanzar en renovables, lo que corresponde a la alternativa C.	medio	2026-05-14 19:31:17.401179+00	t
14	6	En los últimos años, el fenómeno de la eutrofización ha cobrado relevancia en los estudios ambientales. Este proceso ocurre cuando los nutrientes, especialmente el nitrógeno y el fósforo, se acumulan en exceso en cuerpos de agua, provocando el crecimiento desmesurado de algas. Este fenómeno, conocido como floración algal, puede generar zonas muertas en los ecosistemas acuáticos, donde la vida marina se ve severamente afectada debido a la falta de oxígeno. Para mitigar este problema, se han propuesto soluciones como la implementación de tecnologías de filtrado avanzado y la regulación de vertidos industriales.\n\nParalelamente, el término 'eutrofización' se ha utilizado en contextos urbanos para describir la saturación de espacios públicos con actividades comerciales no reguladas. En esta metáfora, los 'nutrientes' son los negocios que, al multiplicarse sin control, generan congestión y degradan la calidad de vida de los residentes. Esta analogía permite comprender cómo conceptos científicos pueden aplicarse a situaciones sociales complejas.	¿Cuál es el significado contextual de la palabra 'eutrofización' en el primer párrafo?	{"A": "Proceso de purificación de aguas residuales", "B": "Acumulación excesiva de nutrientes en cuerpos de agua", "C": "Desarrollo de especies marinas en ecosistemas saludables", "D": "Transformación de minerales en energía renovable"}	B	El texto define explícitamente la eutrofización como la acumulación excesiva de nutrientes en cuerpos de agua, lo que lleva a consecuencias ecológicas negativas. Las otras opciones no coinciden con la definición dada.	medio	2026-05-14 19:40:45.357021+00	t
15	6	En los últimos años, el fenómeno de la eutrofización ha cobrado relevancia en los estudios ambientales. Este proceso ocurre cuando los nutrientes, especialmente el nitrógeno y el fósforo, se acumulan en exceso en cuerpos de agua, provocando el crecimiento desmesurado de algas. Este fenómeno, conocido como floración algal, puede generar zonas muertas en los ecosistemas acuáticos, donde la vida marina se ve severamente afectada debido a la falta de oxígeno. Para mitigar este problema, se han propuesto soluciones como la implementación de tecnologías de filtrado avanzado y la regulación de vertidos industriales.\n\nParalelamente, el término 'eutrofización' se ha utilizado en contextos urbanos para describir la saturación de espacios públicos con actividades comerciales no reguladas. En esta metáfora, los 'nutrientes' son los negocios que, al multiplicarse sin control, generan congestión y degradan la calidad de vida de los residentes. Esta analogía permite comprender cómo conceptos científicos pueden aplicarse a situaciones sociales complejas.	¿Qué significa la expresión 'zonas muertas' mencionada en el primer párrafo?	{"A": "Áreas donde se prohíbe la pesca", "B": "Regiones geográficas sin vida vegetal", "C": "Espacios acuáticos con escasa o nula vida marina", "D": "Zonas urbanas con alta contaminación sonora"}	C	El texto describe 'zonas muertas' como áreas afectadas por la falta de oxígeno debido a la floración algal, lo que corresponde a espacios acuáticos con escasa vida marina. Las otras opciones no reflejan este contexto.	medio	2026-05-14 19:40:45.372809+00	t
16	6	En los últimos años, el fenómeno de la eutrofización ha cobrado relevancia en los estudios ambientales. Este proceso ocurre cuando los nutrientes, especialmente el nitrógeno y el fósforo, se acumulan en exceso en cuerpos de agua, provocando el crecimiento desmesurado de algas. Este fenómeno, conocido como floración algal, puede generar zonas muertas en los ecosistemas acuáticos, donde la vida marina se ve severamente afectada debido a la falta de oxígeno. Para mitigar este problema, se han propuesto soluciones como la implementación de tecnologías de filtrado avanzado y la regulación de vertidos industriales.\n\nParalelamente, el término 'eutrofización' se ha utilizado en contextos urbanos para describir la saturación de espacios públicos con actividades comerciales no reguladas. En esta metáfora, los 'nutrientes' son los negocios que, al multiplicarse sin control, generan congestión y degradan la calidad de vida de los residentes. Esta analogía permite comprender cómo conceptos científicos pueden aplicarse a situaciones sociales complejas.	En el segundo párrafo, ¿qué se entiende por 'nutrientes' en la metáfora urbana?	{"A": "Alimentos vendidos en mercados locales", "B": "Negocios que saturan los espacios públicos", "C": "Recursos energéticos renovables", "D": "Elementos químicos esenciales para la vida"}	B	El texto utiliza 'nutrientes' como metáfora de los negocios que, al multiplicarse sin control, generan congestión urbana. Esta interpretación se deriva directamente del contexto metafórico presentado.	medio	2026-05-14 19:40:45.383798+00	t
17	6	En los últimos años, el fenómeno de la eutrofización ha cobrado relevancia en los estudios ambientales. Este proceso ocurre cuando los nutrientes, especialmente el nitrógeno y el fósforo, se acumulan en exceso en cuerpos de agua, provocando el crecimiento desmesurado de algas. Este fenómeno, conocido como floración algal, puede generar zonas muertas en los ecosistemas acuáticos, donde la vida marina se ve severamente afectada debido a la falta de oxígeno. Para mitigar este problema, se han propuesto soluciones como la implementación de tecnologías de filtrado avanzado y la regulación de vertidos industriales.\n\nParalelamente, el término 'eutrofización' se ha utilizado en contextos urbanos para describir la saturación de espacios públicos con actividades comerciales no reguladas. En esta metáfora, los 'nutrientes' son los negocios que, al multiplicarse sin control, generan congestión y degradan la calidad de vida de los residentes. Esta analogía permite comprender cómo conceptos científicos pueden aplicarse a situaciones sociales complejas.	¿Cuál es el significado de 'floración algal' según el texto?	{"A": "Crecimiento acelerado de plantas ornamentales", "B": "Multiplicación descontrolada de algas en cuerpos de agua", "C": "Proceso de reproducción de corales en arrecifes", "D": "Transformación de sales minerales en energía"}	B	El texto define 'floración algal' como el crecimiento desmesurado de algas causado por la eutrofización. Las otras opciones no coinciden con la descripción proporcionada.	medio	2026-05-14 19:40:45.390349+00	t
18	4	La educación en Chile ha experimentado cambios significativos en las últimas décadas. Uno de los aspectos más destacados ha sido la implementación de políticas educativas que buscan mejorar la calidad de la educación en todos los niveles. En este sentido, se han establecido metas claras para aumentar la cobertura educativa, reducir la brecha de desigualdad y mejorar los resultados académicos. Sin embargo, a pesar de estos esfuerzos, todavía existen desafíos importantes que deben ser abordados. Por ejemplo, la segregación educativa sigue siendo un problema persistente, ya que muchos estudiantes de escasos recursos siguen asistiendo a establecimientos educacionales con menos recursos y oportunidades. Además, la falta de apoyo a los estudiantes con necesidades especiales y la insuficiente formación de los docentes en áreas como la tecnología y la innovación educativa también son cuestiones que requieren atención inmediata. En este contexto, es fundamental evaluar críticamente las políticas educativas actuales y proponer soluciones efectivas que permitan superar estos desafíos y alcanzar una educación de calidad para todos. La evaluación de estas políticas debe considerar no solo los aspectos cuantitativos, como el aumento en la matrícula o la reducción de la deserción, sino también los aspectos cualitativos, como la mejora en la calidad de la enseñanza y el aprendizaje, y el impacto en la sociedad en general.	¿Cuál es uno de los aspectos más destacados de los cambios en la educación en Chile en las últimas décadas?	{"A": "La disminución de la cobertura educativa", "B": "La implementación de políticas educativas para mejorar la calidad de la educación", "C": "La reducción de la inversión en educación", "D": "La eliminación de la educación pública"}	B	El texto inédito menciona que uno de los aspectos más destacados ha sido la implementación de políticas educativas que buscan mejorar la calidad de la educación en todos los niveles.	medio	2026-05-14 19:45:00.945681+00	t
19	4	La educación en Chile ha experimentado cambios significativos en las últimas décadas. Uno de los aspectos más destacados ha sido la implementación de políticas educativas que buscan mejorar la calidad de la educación en todos los niveles. En este sentido, se han establecido metas claras para aumentar la cobertura educativa, reducir la brecha de desigualdad y mejorar los resultados académicos. Sin embargo, a pesar de estos esfuerzos, todavía existen desafíos importantes que deben ser abordados. Por ejemplo, la segregación educativa sigue siendo un problema persistente, ya que muchos estudiantes de escasos recursos siguen asistiendo a establecimientos educacionales con menos recursos y oportunidades. Además, la falta de apoyo a los estudiantes con necesidades especiales y la insuficiente formación de los docentes en áreas como la tecnología y la innovación educativa también son cuestiones que requieren atención inmediata. En este contexto, es fundamental evaluar críticamente las políticas educativas actuales y proponer soluciones efectivas que permitan superar estos desafíos y alcanzar una educación de calidad para todos. La evaluación de estas políticas debe considerar no solo los aspectos cuantitativos, como el aumento en la matrícula o la reducción de la deserción, sino también los aspectos cualitativos, como la mejora en la calidad de la enseñanza y el aprendizaje, y el impacto en la sociedad en general.	¿Cuál es uno de los desafíos importantes que todavía deben ser abordados en la educación en Chile?	{"A": "La falta de recursos financieros para la educación", "B": "La segregación educativa", "C": "La insuficiente formación de los docentes en áreas como la tecnología y la innovación educativa", "D": "Todas las anteriores"}	D	El texto inédito menciona que la segregación educativa, la falta de apoyo a los estudiantes con necesidades especiales y la insuficiente formación de los docentes en áreas como la tecnología y la innovación educativa son cuestiones que requieren atención inmediata.	medio	2026-05-14 19:45:00.960092+00	t
20	4	La educación en Chile ha experimentado cambios significativos en las últimas décadas. Uno de los aspectos más destacados ha sido la implementación de políticas educativas que buscan mejorar la calidad de la educación en todos los niveles. En este sentido, se han establecido metas claras para aumentar la cobertura educativa, reducir la brecha de desigualdad y mejorar los resultados académicos. Sin embargo, a pesar de estos esfuerzos, todavía existen desafíos importantes que deben ser abordados. Por ejemplo, la segregación educativa sigue siendo un problema persistente, ya que muchos estudiantes de escasos recursos siguen asistiendo a establecimientos educacionales con menos recursos y oportunidades. Además, la falta de apoyo a los estudiantes con necesidades especiales y la insuficiente formación de los docentes en áreas como la tecnología y la innovación educativa también son cuestiones que requieren atención inmediata. En este contexto, es fundamental evaluar críticamente las políticas educativas actuales y proponer soluciones efectivas que permitan superar estos desafíos y alcanzar una educación de calidad para todos. La evaluación de estas políticas debe considerar no solo los aspectos cuantitativos, como el aumento en la matrícula o la reducción de la deserción, sino también los aspectos cualitativos, como la mejora en la calidad de la enseñanza y el aprendizaje, y el impacto en la sociedad en general.	¿Qué aspectos debe considerar la evaluación de las políticas educativas actuales?	{"A": "Solo los aspectos cuantitativos", "B": "Solo los aspectos cualitativos", "C": "Tanto los aspectos cuantitativos como los cualitativos", "D": "Ninguno de los anteriores"}	C	El texto inédito menciona que la evaluación de las políticas educativas actuales debe considerar no solo los aspectos cuantitativos, como el aumento en la matrícula o la reducción de la deserción, sino también los aspectos cualitativos, como la mejora en la calidad de la enseñanza y el aprendizaje, y el impacto en la sociedad en general.	medio	2026-05-14 19:45:00.970707+00	t
21	4	La educación en Chile ha experimentado cambios significativos en las últimas décadas. Uno de los aspectos más destacados ha sido la implementación de políticas educativas que buscan mejorar la calidad de la educación en todos los niveles. En este sentido, se han establecido metas claras para aumentar la cobertura educativa, reducir la brecha de desigualdad y mejorar los resultados académicos. Sin embargo, a pesar de estos esfuerzos, todavía existen desafíos importantes que deben ser abordados. Por ejemplo, la segregación educativa sigue siendo un problema persistente, ya que muchos estudiantes de escasos recursos siguen asistiendo a establecimientos educacionales con menos recursos y oportunidades. Además, la falta de apoyo a los estudiantes con necesidades especiales y la insuficiente formación de los docentes en áreas como la tecnología y la innovación educativa también son cuestiones que requieren atención inmediata. En este contexto, es fundamental evaluar críticamente las políticas educativas actuales y proponer soluciones efectivas que permitan superar estos desafíos y alcanzar una educación de calidad para todos. La evaluación de estas políticas debe considerar no solo los aspectos cuantitativos, como el aumento en la matrícula o la reducción de la deserción, sino también los aspectos cualitativos, como la mejora en la calidad de la enseñanza y el aprendizaje, y el impacto en la sociedad en general.	¿Cuál es el objetivo final de evaluar críticamente las políticas educativas actuales?	{"A": "Reducir la inversión en educación", "B": "Mejorar la calidad de la educación para todos", "C": "Aumentar la segregación educativa", "D": "Disminuir la cobertura educativa"}	B	El texto inédito menciona que es fundamental evaluar críticamente las políticas educativas actuales y proponer soluciones efectivas que permitan superar los desafíos y alcanzar una educación de calidad para todos.	medio	2026-05-14 19:45:00.979183+00	t
23	4	La educación en Chile ha experimentado cambios significativos en las últimas décadas. Uno de los aspectos más destacados es la implementación de políticas educativas que buscan mejorar la calidad de la educación y reducir las brechas de desigualdad. En este sentido, se han implementado programas como el 'Subvención Escolar Preferencial' y el 'Programa de Fortalecimiento de la Educación Pública', que tienen como objetivo mejorar la calidad de la educación en establecimientos educacionales vulnerables. Además, se ha puesto énfasis en la formación docente, con programas de capacitación y actualización para los profesores, con el fin de mejorar la calidad de la enseñanza. Sin embargo, a pesar de estos esfuerzos, todavía existen desafíos importantes que deben ser abordados, como la brecha de desigualdad en el acceso a la educación de calidad y la necesidad de mejorar la infraestructura educativa en algunas regiones del país. En este contexto, es fundamental evaluar críticamente las políticas educativas actuales y proponer soluciones innovadoras que permitan superar estos desafíos y mejorar la calidad de la educación en Chile. La evaluación de las políticas educativas es un proceso complejo que requiere considerar múltiples factores, como el impacto en la calidad de la educación, la equidad y la eficiencia en el uso de los recursos. Por lo tanto, es esencial que los responsables de la toma de decisiones en el ámbito educativo tengan acceso a información precisa y actualizada sobre el desempeño del sistema educativo, para poder tomar decisiones informadas y efectivas.	¿Qué es lo que se ha puesto énfasis en la formación docente?	{"A": "Programas de capacitación y actualización para los profesores", "B": "Programas de educación en línea para los estudiantes", "C": "Desarrollo de infraestructura educativa", "D": "Creación de nuevos establecimientos educacionales"}	A	El texto inédito menciona que se ha puesto énfasis en la formación docente, con programas de capacitación y actualización para los profesores.	medio	2026-05-14 19:58:31.145393+00	t
22	4	La educación en Chile ha experimentado cambios significativos en las últimas décadas. Uno de los aspectos más destacados es la implementación de políticas educativas que buscan mejorar la calidad de la educación y reducir las brechas de desigualdad. En este sentido, se han implementado programas como el 'Subvención Escolar Preferencial' y el 'Programa de Fortalecimiento de la Educación Pública', que tienen como objetivo mejorar la calidad de la educación en establecimientos educacionales vulnerables. Además, se ha puesto énfasis en la formación docente, con programas de capacitación y actualización para los profesores, con el fin de mejorar la calidad de la enseñanza. Sin embargo, a pesar de estos esfuerzos, todavía existen desafíos importantes que deben ser abordados, como la brecha de desigualdad en el acceso a la educación de calidad y la necesidad de mejorar la infraestructura educativa en algunas regiones del país. En este contexto, es fundamental evaluar críticamente las políticas educativas actuales y proponer soluciones innovadoras que permitan superar estos desafíos y mejorar la calidad de la educación en Chile. La evaluación de las políticas educativas es un proceso complejo que requiere considerar múltiples factores, como el impacto en la calidad de la educación, la equidad y la eficiencia en el uso de los recursos. Por lo tanto, es esencial que los responsables de la toma de decisiones en el ámbito educativo tengan acceso a información precisa y actualizada sobre el desempeño del sistema educativo, para poder tomar decisiones informadas y efectivas.	¿Cuál es el objetivo principal del 'Subvención Escolar Preferencial'?	{"A": "Mejorar la calidad de la educación en establecimientos educacionales vulnerables", "B": "Reducir la cantidad de estudiantes en las escuelas públicas", "C": "Aumentar el presupuesto para la educación privada", "D": "Desarrollar programas de educación en línea"}	A	El texto inédito menciona que el 'Subvención Escolar Preferencial' tiene como objetivo mejorar la calidad de la educación en establecimientos educacionales vulnerables.	medio	2026-05-14 19:58:31.124682+00	t
25	4	La educación en Chile ha experimentado cambios significativos en las últimas décadas. Uno de los aspectos más destacados es la implementación de políticas educativas que buscan mejorar la calidad de la educación y reducir las brechas de desigualdad. En este sentido, se han implementado programas como el 'Subvención Escolar Preferencial' y el 'Programa de Fortalecimiento de la Educación Pública', que tienen como objetivo mejorar la calidad de la educación en establecimientos educacionales vulnerables. Además, se ha puesto énfasis en la formación docente, con programas de capacitación y actualización para los profesores, con el fin de mejorar la calidad de la enseñanza. Sin embargo, a pesar de estos esfuerzos, todavía existen desafíos importantes que deben ser abordados, como la brecha de desigualdad en el acceso a la educación de calidad y la necesidad de mejorar la infraestructura educativa en algunas regiones del país. En este contexto, es fundamental evaluar críticamente las políticas educativas actuales y proponer soluciones innovadoras que permitan superar estos desafíos y mejorar la calidad de la educación en Chile. La evaluación de las políticas educativas es un proceso complejo que requiere considerar múltiples factores, como el impacto en la calidad de la educación, la equidad y la eficiencia en el uso de los recursos. Por lo tanto, es esencial que los responsables de la toma de decisiones en el ámbito educativo tengan acceso a información precisa y actualizada sobre el desempeño del sistema educativo, para poder tomar decisiones informadas y efectivas.	¿Qué es fundamental para evaluar críticamente las políticas educativas actuales?	{"A": "Información precisa y actualizada sobre el desempeño del sistema educativo", "B": "La opinión de los estudiantes sobre las políticas educativas", "C": "La cantidad de establecimientos educacionales en el país", "D": "El presupuesto para la educación"}	A	El texto inédito menciona que es fundamental evaluar críticamente las políticas educativas actuales y que para ello es esencial tener acceso a información precisa y actualizada sobre el desempeño del sistema educativo.	medio	2026-05-14 19:58:31.168279+00	t
24	4	La educación en Chile ha experimentado cambios significativos en las últimas décadas. Uno de los aspectos más destacados es la implementación de políticas educativas que buscan mejorar la calidad de la educación y reducir las brechas de desigualdad. En este sentido, se han implementado programas como el 'Subvención Escolar Preferencial' y el 'Programa de Fortalecimiento de la Educación Pública', que tienen como objetivo mejorar la calidad de la educación en establecimientos educacionales vulnerables. Además, se ha puesto énfasis en la formación docente, con programas de capacitación y actualización para los profesores, con el fin de mejorar la calidad de la enseñanza. Sin embargo, a pesar de estos esfuerzos, todavía existen desafíos importantes que deben ser abordados, como la brecha de desigualdad en el acceso a la educación de calidad y la necesidad de mejorar la infraestructura educativa en algunas regiones del país. En este contexto, es fundamental evaluar críticamente las políticas educativas actuales y proponer soluciones innovadoras que permitan superar estos desafíos y mejorar la calidad de la educación en Chile. La evaluación de las políticas educativas es un proceso complejo que requiere considerar múltiples factores, como el impacto en la calidad de la educación, la equidad y la eficiencia en el uso de los recursos. Por lo tanto, es esencial que los responsables de la toma de decisiones en el ámbito educativo tengan acceso a información precisa y actualizada sobre el desempeño del sistema educativo, para poder tomar decisiones informadas y efectivas.	¿Cuál es uno de los desafíos importantes que deben ser abordados en la educación en Chile?	{"A": "La falta de acceso a la educación en línea", "B": "La brecha de desigualdad en el acceso a la educación de calidad", "C": "La falta de presupuesto para la educación", "D": "La cantidad de estudiantes en las escuelas públicas"}	B	El texto inédito menciona que uno de los desafíos importantes que deben ser abordados es la brecha de desigualdad en el acceso a la educación de calidad.	medio	2026-05-14 19:58:31.158494+00	t
26	5	La educación en Chile ha experimentado cambios significativos en las últimas décadas. Uno de los aspectos más destacados ha sido la implementación de políticas educativas que buscan mejorar la calidad de la educación y reducir las brechas de desigualdad. Sin embargo, a pesar de estos esfuerzos, todavía existen desafíos importantes que deben ser abordados. Por ejemplo, la segregación escolar sigue siendo un problema grave, ya que muchos estudiantes de escasos recursos se encuentran en establecimientos educacionales con menos recursos y oportunidades. Además, la falta de acceso a la educación superior para los sectores más vulnerables de la sociedad sigue siendo un obstáculo significativo para la movilidad social. En este contexto, es fundamental que se continúen implementando políticas educativas que promuevan la inclusión y la equidad, y que se trabaje en la mejora de la calidad de la educación en todos los niveles. La comunidad educativa, incluyendo a estudiantes, profesores, padres y autoridades, debe trabajar juntos para abordar estos desafíos y asegurar que todos los estudiantes tengan acceso a una educación de calidad que les permita desarrollar sus potencialidades y alcanzar sus metas. La educación es un derecho fundamental y es responsabilidad de todos garantizar que se respete y se promueva en todas las esferas de la sociedad.	¿Cuál es uno de los principales desafíos que enfrenta la educación en Chile, según el texto?	{"A": "La falta de recursos financieros para las escuelas", "B": "La segregación escolar y la falta de acceso a la educación superior", "C": "La falta de interés de los estudiantes en aprender", "D": "La insuficiente formación de los profesores"}	B	El texto menciona explícitamente que la segregación escolar y la falta de acceso a la educación superior son desafíos importantes que deben ser abordados.	medio	2026-05-14 20:00:12.366544+00	t
27	5	La educación en Chile ha experimentado cambios significativos en las últimas décadas. Uno de los aspectos más destacados ha sido la implementación de políticas educativas que buscan mejorar la calidad de la educación y reducir las brechas de desigualdad. Sin embargo, a pesar de estos esfuerzos, todavía existen desafíos importantes que deben ser abordados. Por ejemplo, la segregación escolar sigue siendo un problema grave, ya que muchos estudiantes de escasos recursos se encuentran en establecimientos educacionales con menos recursos y oportunidades. Además, la falta de acceso a la educación superior para los sectores más vulnerables de la sociedad sigue siendo un obstáculo significativo para la movilidad social. En este contexto, es fundamental que se continúen implementando políticas educativas que promuevan la inclusión y la equidad, y que se trabaje en la mejora de la calidad de la educación en todos los niveles. La comunidad educativa, incluyendo a estudiantes, profesores, padres y autoridades, debe trabajar juntos para abordar estos desafíos y asegurar que todos los estudiantes tengan acceso a una educación de calidad que les permita desarrollar sus potencialidades y alcanzar sus metas. La educación es un derecho fundamental y es responsabilidad de todos garantizar que se respete y se promueva en todas las esferas de la sociedad.	¿Qué se considera fundamental para abordar los desafíos en la educación, según el texto?	{"A": "Implementar políticas educativas que promuevan la competencia entre los estudiantes", "B": "Implementar políticas educativas que promuevan la inclusión y la equidad", "C": "Reducir el número de estudiantes en las aulas", "D": "Aumentar la cantidad de profesores sin experiencia"}	B	El texto indica que es fundamental implementar políticas educativas que promuevan la inclusión y la equidad para abordar los desafíos en la educación.	medio	2026-05-14 20:00:12.378661+00	t
28	5	La educación en Chile ha experimentado cambios significativos en las últimas décadas. Uno de los aspectos más destacados ha sido la implementación de políticas educativas que buscan mejorar la calidad de la educación y reducir las brechas de desigualdad. Sin embargo, a pesar de estos esfuerzos, todavía existen desafíos importantes que deben ser abordados. Por ejemplo, la segregación escolar sigue siendo un problema grave, ya que muchos estudiantes de escasos recursos se encuentran en establecimientos educacionales con menos recursos y oportunidades. Además, la falta de acceso a la educación superior para los sectores más vulnerables de la sociedad sigue siendo un obstáculo significativo para la movilidad social. En este contexto, es fundamental que se continúen implementando políticas educativas que promuevan la inclusión y la equidad, y que se trabaje en la mejora de la calidad de la educación en todos los niveles. La comunidad educativa, incluyendo a estudiantes, profesores, padres y autoridades, debe trabajar juntos para abordar estos desafíos y asegurar que todos los estudiantes tengan acceso a una educación de calidad que les permita desarrollar sus potencialidades y alcanzar sus metas. La educación es un derecho fundamental y es responsabilidad de todos garantizar que se respete y se promueva en todas las esferas de la sociedad.	¿Quiénes deben trabajar juntos para abordar los desafíos en la educación, según el texto?	{"A": "Solo los profesores y los estudiantes", "B": "Solo las autoridades educativas y los padres", "C": "La comunidad educativa, incluyendo a estudiantes, profesores, padres y autoridades", "D": "Solo los estudiantes y las autoridades educativas"}	C	El texto menciona que la comunidad educativa, incluyendo a estudiantes, profesores, padres y autoridades, debe trabajar juntos para abordar los desafíos en la educación.	medio	2026-05-14 20:00:12.387398+00	t
29	5	La educación en Chile ha experimentado cambios significativos en las últimas décadas. Uno de los aspectos más destacados ha sido la implementación de políticas educativas que buscan mejorar la calidad de la educación y reducir las brechas de desigualdad. Sin embargo, a pesar de estos esfuerzos, todavía existen desafíos importantes que deben ser abordados. Por ejemplo, la segregación escolar sigue siendo un problema grave, ya que muchos estudiantes de escasos recursos se encuentran en establecimientos educacionales con menos recursos y oportunidades. Además, la falta de acceso a la educación superior para los sectores más vulnerables de la sociedad sigue siendo un obstáculo significativo para la movilidad social. En este contexto, es fundamental que se continúen implementando políticas educativas que promuevan la inclusión y la equidad, y que se trabaje en la mejora de la calidad de la educación en todos los niveles. La comunidad educativa, incluyendo a estudiantes, profesores, padres y autoridades, debe trabajar juntos para abordar estos desafíos y asegurar que todos los estudiantes tengan acceso a una educación de calidad que les permita desarrollar sus potencialidades y alcanzar sus metas. La educación es un derecho fundamental y es responsabilidad de todos garantizar que se respete y se promueva en todas las esferas de la sociedad.	¿Por qué es importante garantizar que todos los estudiantes tengan acceso a una educación de calidad, según el texto?	{"A": "Para que puedan desarrollar sus habilidades deportivas", "B": "Para que puedan desarrollar sus potencialidades y alcanzar sus metas", "C": "Para que puedan aprender solo materias científicas", "D": "Para que puedan aprender solo materias artísticas"}	B	El texto indica que la educación es un derecho fundamental y que es importante garantizar que todos los estudiantes tengan acceso a una educación de calidad para que puedan desarrollar sus potencialidades y alcanzar sus metas.	medio	2026-05-14 20:00:12.396781+00	t
30	3	La ciudad de Valparaíso, en Chile, es conocida por su arquitectura única y su rica historia. Fundada en el siglo XVI, la ciudad ha sido testigo de numerosos eventos significativos que han moldeado su identidad. Uno de los aspectos más destacados de Valparaíso es su patrimonio cultural, que se refleja en sus coloridas casas, iglesias y edificios históricos. La ciudad también es famosa por sus escaleras y ascensores, que conectan los diferentes barrios y ofrecen vistas impresionantes del puerto y el mar. En la actualidad, Valparaíso es un destino turístico popular, atraendo a visitantes de todo el mundo que buscan experimentar su vibrante atmósfera y explorar sus calles empedradas. La ciudad también ha sido reconocida por su importancia cultural, siendo declarada Patrimonio de la Humanidad por la UNESCO en 2003. Esto ha llevado a esfuerzos para preservar y restaurar sus edificios históricos, asegurando que la ciudad mantenga su encanto y autenticidad para las generaciones futuras. A pesar de los desafíos que enfrenta, como la conservación de su patrimonio en un entorno urbano en constante evolución, Valparaíso sigue siendo un lugar emblemático y querido por sus habitantes y visitantes.	¿Cuál es uno de los aspectos más destacados de la ciudad de Valparaíso?	{"A": "Su ubicación geográfica", "B": "Su patrimonio cultural", "C": "Su tamaño poblacional", "D": "Su producción industrial"}	B	El texto destaca el patrimonio cultural de Valparaíso como uno de sus aspectos más destacados.	medio	2026-05-14 20:09:00.97637+00	t
31	3	La ciudad de Valparaíso, en Chile, es conocida por su arquitectura única y su rica historia. Fundada en el siglo XVI, la ciudad ha sido testigo de numerosos eventos significativos que han moldeado su identidad. Uno de los aspectos más destacados de Valparaíso es su patrimonio cultural, que se refleja en sus coloridas casas, iglesias y edificios históricos. La ciudad también es famosa por sus escaleras y ascensores, que conectan los diferentes barrios y ofrecen vistas impresionantes del puerto y el mar. En la actualidad, Valparaíso es un destino turístico popular, atraendo a visitantes de todo el mundo que buscan experimentar su vibrante atmósfera y explorar sus calles empedradas. La ciudad también ha sido reconocida por su importancia cultural, siendo declarada Patrimonio de la Humanidad por la UNESCO en 2003. Esto ha llevado a esfuerzos para preservar y restaurar sus edificios históricos, asegurando que la ciudad mantenga su encanto y autenticidad para las generaciones futuras. A pesar de los desafíos que enfrenta, como la conservación de su patrimonio en un entorno urbano en constante evolución, Valparaíso sigue siendo un lugar emblemático y querido por sus habitantes y visitantes.	¿Qué reconocimiento internacional ha recibido la ciudad de Valparaíso?	{"A": "Ciudad más grande de Chile", "B": "Patrimonio de la Humanidad por la UNESCO", "C": "Ciudad más poblada de América Latina", "D": "Ciudad con mayor producción económica"}	B	El texto menciona que Valparaíso fue declarada Patrimonio de la Humanidad por la UNESCO en 2003.	medio	2026-05-14 20:09:00.993063+00	t
32	3	La ciudad de Valparaíso, en Chile, es conocida por su arquitectura única y su rica historia. Fundada en el siglo XVI, la ciudad ha sido testigo de numerosos eventos significativos que han moldeado su identidad. Uno de los aspectos más destacados de Valparaíso es su patrimonio cultural, que se refleja en sus coloridas casas, iglesias y edificios históricos. La ciudad también es famosa por sus escaleras y ascensores, que conectan los diferentes barrios y ofrecen vistas impresionantes del puerto y el mar. En la actualidad, Valparaíso es un destino turístico popular, atraendo a visitantes de todo el mundo que buscan experimentar su vibrante atmósfera y explorar sus calles empedradas. La ciudad también ha sido reconocida por su importancia cultural, siendo declarada Patrimonio de la Humanidad por la UNESCO en 2003. Esto ha llevado a esfuerzos para preservar y restaurar sus edificios históricos, asegurando que la ciudad mantenga su encanto y autenticidad para las generaciones futuras. A pesar de los desafíos que enfrenta, como la conservación de su patrimonio en un entorno urbano en constante evolución, Valparaíso sigue siendo un lugar emblemático y querido por sus habitantes y visitantes.	¿Cuál es el propósito de los esfuerzos para preservar y restaurar los edificios históricos de Valparaíso?	{"A": "Aumentar la atracción turística", "B": "Disminuir la población urbana", "C": "Mantener el encanto y la autenticidad de la ciudad para las generaciones futuras", "D": "Reducir la importancia cultural de la ciudad"}	C	El texto indica que el propósito de estos esfuerzos es asegurar que la ciudad mantenga su encanto y autenticidad.	medio	2026-05-14 20:09:01.005642+00	t
33	3	La ciudad de Valparaíso, en Chile, es conocida por su arquitectura única y su rica historia. Fundada en el siglo XVI, la ciudad ha sido testigo de numerosos eventos significativos que han moldeado su identidad. Uno de los aspectos más destacados de Valparaíso es su patrimonio cultural, que se refleja en sus coloridas casas, iglesias y edificios históricos. La ciudad también es famosa por sus escaleras y ascensores, que conectan los diferentes barrios y ofrecen vistas impresionantes del puerto y el mar. En la actualidad, Valparaíso es un destino turístico popular, atraendo a visitantes de todo el mundo que buscan experimentar su vibrante atmósfera y explorar sus calles empedradas. La ciudad también ha sido reconocida por su importancia cultural, siendo declarada Patrimonio de la Humanidad por la UNESCO en 2003. Esto ha llevado a esfuerzos para preservar y restaurar sus edificios históricos, asegurando que la ciudad mantenga su encanto y autenticidad para las generaciones futuras. A pesar de los desafíos que enfrenta, como la conservación de su patrimonio en un entorno urbano en constante evolución, Valparaíso sigue siendo un lugar emblemático y querido por sus habitantes y visitantes.	¿Qué desafío enfrenta la ciudad de Valparaíso en relación con su patrimonio?	{"A": "La falta de turistas", "B": "La conservación de su patrimonio en un entorno urbano en constante evolución", "C": "La competencia con otras ciudades chilenas", "D": "La disminución de su importancia cultural"}	B	El texto menciona que uno de los desafíos que enfrenta Valparaíso es la conservación de su patrimonio en un entorno urbano en constante evolución.	medio	2026-05-14 20:09:01.014054+00	t
35	3	La ciudad de Valparaíso, en Chile, es conocida por su arquitectura única y su rica historia. Fundada en el siglo XVI, la ciudad ha sido testigo de numerosos eventos significativos en la historia del país. Uno de los aspectos más destacados de Valparaíso es su patrimonio cultural, que se refleja en sus coloridas casas, iglesias y edificios históricos. La ciudad también es famosa por sus escaleras y ascensores, que conectan los diferentes barrios y ofrecen vistas impresionantes del puerto y el mar. En la actualidad, Valparaíso es un destino turístico popular, atraendo a visitantes de todo el mundo que buscan experimentar su vibrante atmósfera y explorar sus calles empedradas. La ciudad también ha sido reconocida por su importancia cultural, siendo declarada Patrimonio de la Humanidad por la UNESCO en 2003. Esto ha llevado a esfuerzos para preservar y restaurar sus edificios históricos, asegurando que la ciudad continúe siendo un tesoro cultural para las generaciones futuras. A pesar de los desafíos que enfrenta, como la conservación de su patrimonio en medio del crecimiento urbano, Valparaíso sigue siendo un lugar emblemático y lleno de vida, donde la historia y la cultura se entrelazan en cada rincón.	¿Por qué fue declarada Valparaíso Patrimonio de la Humanidad por la UNESCO?	{"A": "Por su importancia económica", "B": "Por su importancia cultural", "C": "Por su ubicación estratégica", "D": "Por su tamaño territorial"}	B	El texto menciona que Valparaíso fue declarada Patrimonio de la Humanidad por la UNESCO en 2003 debido a su importancia cultural.	medio	2026-05-14 20:11:08.961016+00	t
37	3	La ciudad de Valparaíso, en Chile, es conocida por su arquitectura única y su rica historia. Fundada en el siglo XVI, la ciudad ha sido testigo de numerosos eventos significativos en la historia del país. Uno de los aspectos más destacados de Valparaíso es su patrimonio cultural, que se refleja en sus coloridas casas, iglesias y edificios históricos. La ciudad también es famosa por sus escaleras y ascensores, que conectan los diferentes barrios y ofrecen vistas impresionantes del puerto y el mar. En la actualidad, Valparaíso es un destino turístico popular, atraendo a visitantes de todo el mundo que buscan experimentar su vibrante atmósfera y explorar sus calles empedradas. La ciudad también ha sido reconocida por su importancia cultural, siendo declarada Patrimonio de la Humanidad por la UNESCO en 2003. Esto ha llevado a esfuerzos para preservar y restaurar sus edificios históricos, asegurando que la ciudad continúe siendo un tesoro cultural para las generaciones futuras. A pesar de los desafíos que enfrenta, como la conservación de su patrimonio en medio del crecimiento urbano, Valparaíso sigue siendo un lugar emblemático y lleno de vida, donde la historia y la cultura se entrelazan en cada rincón.	¿Qué ha llevado el reconocimiento de Valparaíso como Patrimonio de la Humanidad?	{"A": "Esfuerzos para aumentar su población", "B": "Esfuerzos para preservar y restaurar sus edificios históricos", "C": "Esfuerzos para expandir su territorio", "D": "Esfuerzos para disminuir su importancia cultural"}	B	El texto menciona que el reconocimiento de Valparaíso como Patrimonio de la Humanidad ha llevado a esfuerzos para preservar y restaurar sus edificios históricos.	medio	2026-05-14 20:11:08.97648+00	t
34	3	La ciudad de Valparaíso, en Chile, es conocida por su arquitectura única y su rica historia. Fundada en el siglo XVI, la ciudad ha sido testigo de numerosos eventos significativos en la historia del país. Uno de los aspectos más destacados de Valparaíso es su patrimonio cultural, que se refleja en sus coloridas casas, iglesias y edificios históricos. La ciudad también es famosa por sus escaleras y ascensores, que conectan los diferentes barrios y ofrecen vistas impresionantes del puerto y el mar. En la actualidad, Valparaíso es un destino turístico popular, atraendo a visitantes de todo el mundo que buscan experimentar su vibrante atmósfera y explorar sus calles empedradas. La ciudad también ha sido reconocida por su importancia cultural, siendo declarada Patrimonio de la Humanidad por la UNESCO en 2003. Esto ha llevado a esfuerzos para preservar y restaurar sus edificios históricos, asegurando que la ciudad continúe siendo un tesoro cultural para las generaciones futuras. A pesar de los desafíos que enfrenta, como la conservación de su patrimonio en medio del crecimiento urbano, Valparaíso sigue siendo un lugar emblemático y lleno de vida, donde la historia y la cultura se entrelazan en cada rincón.	¿Cuál es uno de los aspectos más destacados de la ciudad de Valparaíso?	{"A": "Su ubicación geográfica", "B": "Su patrimonio cultural", "C": "Su tamaño poblacional", "D": "Su producción industrial"}	B	El texto destaca el patrimonio cultural de Valparaíso como uno de sus aspectos más destacados, mencionando sus casas, iglesias y edificios históricos.	medio	2026-05-14 20:11:08.951929+00	t
36	3	La ciudad de Valparaíso, en Chile, es conocida por su arquitectura única y su rica historia. Fundada en el siglo XVI, la ciudad ha sido testigo de numerosos eventos significativos en la historia del país. Uno de los aspectos más destacados de Valparaíso es su patrimonio cultural, que se refleja en sus coloridas casas, iglesias y edificios históricos. La ciudad también es famosa por sus escaleras y ascensores, que conectan los diferentes barrios y ofrecen vistas impresionantes del puerto y el mar. En la actualidad, Valparaíso es un destino turístico popular, atraendo a visitantes de todo el mundo que buscan experimentar su vibrante atmósfera y explorar sus calles empedradas. La ciudad también ha sido reconocida por su importancia cultural, siendo declarada Patrimonio de la Humanidad por la UNESCO en 2003. Esto ha llevado a esfuerzos para preservar y restaurar sus edificios históricos, asegurando que la ciudad continúe siendo un tesoro cultural para las generaciones futuras. A pesar de los desafíos que enfrenta, como la conservación de su patrimonio en medio del crecimiento urbano, Valparaíso sigue siendo un lugar emblemático y lleno de vida, donde la historia y la cultura se entrelazan en cada rincón.	¿Cuál es uno de los desafíos que enfrenta la ciudad de Valparaíso?	{"A": "La conservación de su patrimonio", "B": "El crecimiento de su población", "C": "La expansión de su territorio", "D": "La disminución de su importancia cultural"}	A	El texto menciona que uno de los desafíos que enfrenta Valparaíso es la conservación de su patrimonio en medio del crecimiento urbano.	medio	2026-05-14 20:11:08.968925+00	t
\.


--
-- Data for Name: configuracion; Type: TABLE DATA; Schema: public; Owner: user_lexiscan
--

COPY public.configuracion (id_config, clave, valor, descripcion) FROM stdin;
1	GROQ_API_KEY	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	API Key para Groq
2	GROQ_MODEL	llama-3.3-70b-versatile	Modelo de Groq a utilizar
\.


--
-- Data for Name: economia_monedas; Type: TABLE DATA; Schema: public; Owner: user_lexiscan
--

COPY public.economia_monedas (rut_usuario, saldo_monedas, total_acumulado, ultima_transaccion) FROM stdin;
20144801-8	0	0	2026-05-14 19:20:15.714854+00
\.


--
-- Data for Name: errores_favoritos; Type: TABLE DATA; Schema: public; Owner: user_lexiscan
--

COPY public.errores_favoritos (id_error, rut_usuario, id_pregunta, id_habilidad, veces_fallada, resuelta, fecha_registro, fecha_resolucion) FROM stdin;
6	20144801-8	6	4	1	f	2026-05-14 19:31:24.008821+00	\N
7	20144801-8	7	4	1	f	2026-05-14 19:31:24.024067+00	\N
8	20144801-8	8	6	1	f	2026-05-14 19:43:50.144077+00	\N
9	20144801-8	9	4	1	f	2026-05-14 19:45:25.186525+00	\N
10	20144801-8	10	4	1	f	2026-05-14 19:45:25.208557+00	\N
11	20144801-8	11	4	1	f	2026-05-14 19:45:25.233128+00	\N
12	20144801-8	12	4	1	f	2026-05-14 19:45:25.252322+00	\N
1	20144801-8	1	3	1	t	2026-05-14 19:23:39.148133+00	\N
2	20144801-8	2	3	1	t	2026-05-14 19:23:39.16833+00	\N
3	20144801-8	3	3	1	t	2026-05-14 19:23:39.188618+00	\N
4	20144801-8	4	4	1	t	2026-05-14 19:31:23.975205+00	\N
5	20144801-8	5	4	1	t	2026-05-14 19:31:23.993957+00	\N
13	20144801-8	13	5	1	f	2026-05-14 20:00:22.594123+00	\N
14	20144801-8	14	5	1	f	2026-05-14 20:00:22.613997+00	\N
15	20144801-8	15	5	1	f	2026-05-14 20:00:22.631748+00	\N
16	20144801-8	16	5	1	f	2026-05-14 20:00:22.648873+00	\N
\.


--
-- Data for Name: historial_habilidades; Type: TABLE DATA; Schema: public; Owner: user_lexiscan
--

COPY public.historial_habilidades (id_progreso, rut_usuario, nombre_habilidad, nivel_maestria, ultima_actualizacion) FROM stdin;
2	20144801-8	Localizar	15.00	2026-05-14 19:21:15.089151+00
7	20144801-8	Tipos_de_Texto	15.00	2026-05-14 19:28:33.730101+00
6	20144801-8	Vocabulario	11.00	2026-05-14 19:43:50.155252+00
4	20144801-8	Evaluar	15.00	2026-05-14 19:58:41.566467+00
5	20144801-8	Lectura_Critica	0.00	2026-05-14 20:00:22.658972+00
3	20144801-8	Interpretar	34.00	2026-05-14 20:11:42.564031+00
\.


--
-- Data for Name: preguntas_ia; Type: TABLE DATA; Schema: public; Owner: user_lexiscan
--

COPY public.preguntas_ia (id_pregunta, id_pregunta_origen, id_habilidad, texto_inedito, enunciado, alternativas, respuesta_correcta, justificacion_cot, modelo_ia, fecha_generacion, activa) FROM stdin;
1	6	3	La contaminación lumínica, causada por el exceso de iluminación artificial en espacios nocturnos, afecta profundamente a los ecosistemas. Animales nocturnos como murciélagos, insectos y aves migratorias dependen de la oscuridad para cazar, navegar y reproducirse. La luz artificial altera sus ciclos naturales, desorienta a las crías de tortugas marinas que siguen la luz de la luna para llegar al mar, y atrae a polillas hacia fuentes de luz que no les proporcionan alimento. Además, la contaminación lumínica contribuye al aumento de la temperatura ambiental, afectando la biodiversidad.\n\nPara mitigar estos efectos, se recomienda usar iluminación direccional y de menor intensidad, evitar iluminar áreas no necesarias y promover el uso de fuentes de luz de longitud de onda adecuada. Estudios recientes sugieren que reducir la contaminación lumínica podría revertir hasta un 30% de la disminución en poblaciones de insectos nocturnos. Sin embargo, la implementación de estas medidas requiere conciencia ciudadana y políticas públicas efectivas.	¿Cuál es el propósito principal del segundo párrafo del texto?	{"A": "Explicar las causas de la contaminación lumínica.", "B": "Describir los efectos de la contaminación lumínica en los ecosistemas.", "C": "Proponer soluciones para reducir la contaminación lumínica.", "D": "Argumentar que la contaminación lumínica es irrelevante."}	C	El segundo párrafo se enfoca en sugerir estrategias como el uso de iluminación direccional y políticas públicas para abordar el problema de la contaminación lumínica.	Clonado	2026-05-14 19:23:39.132619+00	t
2	7	3	La contaminación lumínica, causada por el exceso de iluminación artificial en espacios nocturnos, afecta profundamente a los ecosistemas. Animales nocturnos como murciélagos, insectos y aves migratorias dependen de la oscuridad para cazar, navegar y reproducirse. La luz artificial altera sus ciclos naturales, desorienta a las crías de tortugas marinas que siguen la luz de la luna para llegar al mar, y atrae a polillas hacia fuentes de luz que no les proporcionan alimento. Además, la contaminación lumínica contribuye al aumento de la temperatura ambiental, afectando la biodiversidad.\n\nPara mitigar estos efectos, se recomienda usar iluminación direccional y de menor intensidad, evitar iluminar áreas no necesarias y promover el uso de fuentes de luz de longitud de onda adecuada. Estudios recientes sugieren que reducir la contaminación lumínica podría revertir hasta un 30% de la disminución en poblaciones de insectos nocturnos. Sin embargo, la implementación de estas medidas requiere conciencia ciudadana y políticas públicas efectivas.	¿Qué implica el texto al mencionar que 'la contaminación lumínica contribuye al aumento de la temperatura ambiental'?	{"A": "Que la luz artificial genera calor directamente.", "B": "Que la energía consumida por las luces emite CO₂.", "C": "Que la luz artificial afecta la radiación solar.", "D": "Que la oscuridad natural absorbe más calor."}	B	El texto sugiere una relación indirecta entre la contaminación lumínica y el calentamiento global, asociada al consumo energético de las luces artificiales, que emiten gases de efecto invernadero.	Clonado	2026-05-14 19:23:39.159467+00	t
3	8	3	La contaminación lumínica, causada por el exceso de iluminación artificial en espacios nocturnos, afecta profundamente a los ecosistemas. Animales nocturnos como murciélagos, insectos y aves migratorias dependen de la oscuridad para cazar, navegar y reproducirse. La luz artificial altera sus ciclos naturales, desorienta a las crías de tortugas marinas que siguen la luz de la luna para llegar al mar, y atrae a polillas hacia fuentes de luz que no les proporcionan alimento. Además, la contaminación lumínica contribuye al aumento de la temperatura ambiental, afectando la biodiversidad.\n\nPara mitigar estos efectos, se recomienda usar iluminación direccional y de menor intensidad, evitar iluminar áreas no necesarias y promover el uso de fuentes de luz de longitud de onda adecuada. Estudios recientes sugieren que reducir la contaminación lumínica podría revertir hasta un 30% de la disminución en poblaciones de insectos nocturnos. Sin embargo, la implementación de estas medidas requiere conciencia ciudadana y políticas públicas efectivas.	¿Qué se puede inferir sobre la efectividad de las soluciones propuestas en el texto?	{"A": "Que son costosas y difíciles de implementar.", "B": "Que requieren cambios tecnológicos complejos.", "C": "Que dependen de la colaboración ciudadana y estatal.", "D": "Que son temporales y no resuelven el problema a largo plazo."}	C	El texto menciona que la implementación de las soluciones necesitaria 'conciencia ciudadana y políticas públicas efectivas', lo que implica que su éxito depende de múltiples actores.	Clonado	2026-05-14 19:23:39.177731+00	t
4	10	4	La transición hacia fuentes renovables de energía es un desafío crucial para mitigar el cambio climático. Según un estudio reciente, el uso de energía solar y eólica podría cubrir el 80% de la demanda eléctrica global para 2040, siempre que se eliminen las barreras tecnológicas y económicas actuales. Sin embargo, críticos señalan que esta estimación ignora la variabilidad de estas fuentes, especialmente en regiones con clima inestable. Por otro lado, expertos en políticas energéticas argumentan que los subsidios a los combustibles fósiles, que aún representan el 60% del presupuesto energético mundial, son un obstáculo principal para la adopción masiva de tecnologías limpias. A pesar de esto, países como Dinamarca y Costa Rica han demostrado que es posible alcanzar un 100% de energía renovable mediante combinaciones innovadoras de hidroeléctrica, eólica y almacenamiento de baterías.	¿Cuál es la principal crítica que se hace al estudio mencionado sobre la energía renovable?	{"A": "No considera el costo de producción de paneles solares.", "B": "Subestima el potencial de la energía geotérmica.", "C": "No aborda la variabilidad de las fuentes renovables en climas inestables.", "D": "Sobreestima la capacidad de almacenamiento de baterías."}	C	El texto indica explícitamente que los críticos señalan que la estimación ignora la variabilidad de las fuentes renovables en regiones con clima inestable, lo que corresponde a la alternativa C.	Clonado	2026-05-14 19:31:23.960818+00	t
5	11	4	La transición hacia fuentes renovables de energía es un desafío crucial para mitigar el cambio climático. Según un estudio reciente, el uso de energía solar y eólica podría cubrir el 80% de la demanda eléctrica global para 2040, siempre que se eliminen las barreras tecnológicas y económicas actuales. Sin embargo, críticos señalan que esta estimación ignora la variabilidad de estas fuentes, especialmente en regiones con clima inestable. Por otro lado, expertos en políticas energéticas argumentan que los subsidios a los combustibles fósiles, que aún representan el 60% del presupuesto energético mundial, son un obstáculo principal para la adopción masiva de tecnologías limpias. A pesar de esto, países como Dinamarca y Costa Rica han demostrado que es posible alcanzar un 100% de energía renovable mediante combinaciones innovadoras de hidroeléctrica, eólica y almacenamiento de baterías.	¿Qué factor, según el texto, impide la adopción masiva de tecnologías limpias?	{"A": "La falta de conciencia ciudadana sobre el cambio climático.", "B": "Los subsidios a los combustibles fósiles.", "C": "La escasez de recursos minerales para fabricar paneles solares.", "D": "La resistencia de los gobiernos a cambiar políticas energéticas."}	B	El texto menciona que los subsidios a los combustibles fósiles, que representan el 60% del presupuesto energético mundial, son un obstáculo principal, lo que corresponde a la alternativa B.	Clonado	2026-05-14 19:31:23.986921+00	t
6	12	4	La transición hacia fuentes renovables de energía es un desafío crucial para mitigar el cambio climático. Según un estudio reciente, el uso de energía solar y eólica podría cubrir el 80% de la demanda eléctrica global para 2040, siempre que se eliminen las barreras tecnológicas y económicas actuales. Sin embargo, críticos señalan que esta estimación ignora la variabilidad de estas fuentes, especialmente en regiones con clima inestable. Por otro lado, expertos en políticas energéticas argumentan que los subsidios a los combustibles fósiles, que aún representan el 60% del presupuesto energético mundial, son un obstáculo principal para la adopción masiva de tecnologías limpias. A pesar de esto, países como Dinamarca y Costa Rica han demostrado que es posible alcanzar un 100% de energía renovable mediante combinaciones innovadoras de hidroeléctrica, eólica y almacenamiento de baterías.	¿Qué ejemplo del texto respalda la viabilidad de un sistema 100% renovable?	{"A": "La reducción de emisiones en Alemania.", "B": "El uso de hidroeléctrica en Canadá.", "C": "La combinación de fuentes en Dinamarca y Costa Rica.", "D": "El avance tecnológico en baterías de litio."}	C	El texto cita explícitamente a Dinamarca y Costa Rica como países que han logrado un 100% de energía renovable mediante combinaciones innovadoras, lo que corresponde a la alternativa C.	Clonado	2026-05-14 19:31:24.001592+00	t
7	13	4	La transición hacia fuentes renovables de energía es un desafío crucial para mitigar el cambio climático. Según un estudio reciente, el uso de energía solar y eólica podría cubrir el 80% de la demanda eléctrica global para 2040, siempre que se eliminen las barreras tecnológicas y económicas actuales. Sin embargo, críticos señalan que esta estimación ignora la variabilidad de estas fuentes, especialmente en regiones con clima inestable. Por otro lado, expertos en políticas energéticas argumentan que los subsidios a los combustibles fósiles, que aún representan el 60% del presupuesto energético mundial, son un obstáculo principal para la adopción masiva de tecnologías limpias. A pesar de esto, países como Dinamarca y Costa Rica han demostrado que es posible alcanzar un 100% de energía renovable mediante combinaciones innovadoras de hidroeléctrica, eólica y almacenamiento de baterías.	¿Cuál es el argumento central del texto sobre la transición energética?	{"A": "Es imposible alcanzar metas ambiciosas de energía renovable sin inversión extranjera.", "B": "La variabilidad climática invalida cualquier plan de transición energética.", "C": "La eliminación de subsidios a combustibles fósiles es clave para avanzar en renovables.", "D": "Las tecnologías actuales no permiten reemplazar más del 50% de la energía actual."}	C	El texto enfatiza que los subsidios a los combustibles fósiles son un obstáculo principal y que su eliminación es clave para avanzar en renovables, lo que corresponde a la alternativa C.	Clonado	2026-05-14 19:31:24.016076+00	t
8	14	6	En los últimos años, el fenómeno de la eutrofización ha cobrado relevancia en los estudios ambientales. Este proceso ocurre cuando los nutrientes, especialmente el nitrógeno y el fósforo, se acumulan en exceso en cuerpos de agua, provocando el crecimiento desmesurado de algas. Este fenómeno, conocido como floración algal, puede generar zonas muertas en los ecosistemas acuáticos, donde la vida marina se ve severamente afectada debido a la falta de oxígeno. Para mitigar este problema, se han propuesto soluciones como la implementación de tecnologías de filtrado avanzado y la regulación de vertidos industriales.\n\nParalelamente, el término 'eutrofización' se ha utilizado en contextos urbanos para describir la saturación de espacios públicos con actividades comerciales no reguladas. En esta metáfora, los 'nutrientes' son los negocios que, al multiplicarse sin control, generan congestión y degradan la calidad de vida de los residentes. Esta analogía permite comprender cómo conceptos científicos pueden aplicarse a situaciones sociales complejas.	¿Cuál es el significado contextual de la palabra 'eutrofización' en el primer párrafo?	{"A": "Proceso de purificación de aguas residuales", "B": "Acumulación excesiva de nutrientes en cuerpos de agua", "C": "Desarrollo de especies marinas en ecosistemas saludables", "D": "Transformación de minerales en energía renovable"}	B	El texto define explícitamente la eutrofización como la acumulación excesiva de nutrientes en cuerpos de agua, lo que lleva a consecuencias ecológicas negativas. Las otras opciones no coinciden con la definición dada.	Clonado	2026-05-14 19:43:50.130518+00	t
9	18	4	La educación en Chile ha experimentado cambios significativos en las últimas décadas. Uno de los aspectos más destacados ha sido la implementación de políticas educativas que buscan mejorar la calidad de la educación en todos los niveles. En este sentido, se han establecido metas claras para aumentar la cobertura educativa, reducir la brecha de desigualdad y mejorar los resultados académicos. Sin embargo, a pesar de estos esfuerzos, todavía existen desafíos importantes que deben ser abordados. Por ejemplo, la segregación educativa sigue siendo un problema persistente, ya que muchos estudiantes de escasos recursos siguen asistiendo a establecimientos educacionales con menos recursos y oportunidades. Además, la falta de apoyo a los estudiantes con necesidades especiales y la insuficiente formación de los docentes en áreas como la tecnología y la innovación educativa también son cuestiones que requieren atención inmediata. En este contexto, es fundamental evaluar críticamente las políticas educativas actuales y proponer soluciones efectivas que permitan superar estos desafíos y alcanzar una educación de calidad para todos. La evaluación de estas políticas debe considerar no solo los aspectos cuantitativos, como el aumento en la matrícula o la reducción de la deserción, sino también los aspectos cualitativos, como la mejora en la calidad de la enseñanza y el aprendizaje, y el impacto en la sociedad en general.	¿Cuál es uno de los aspectos más destacados de los cambios en la educación en Chile en las últimas décadas?	{"A": "La disminución de la cobertura educativa", "B": "La implementación de políticas educativas para mejorar la calidad de la educación", "C": "La reducción de la inversión en educación", "D": "La eliminación de la educación pública"}	B	El texto inédito menciona que uno de los aspectos más destacados ha sido la implementación de políticas educativas que buscan mejorar la calidad de la educación en todos los niveles.	Clonado	2026-05-14 19:45:25.176173+00	t
10	19	4	La educación en Chile ha experimentado cambios significativos en las últimas décadas. Uno de los aspectos más destacados ha sido la implementación de políticas educativas que buscan mejorar la calidad de la educación en todos los niveles. En este sentido, se han establecido metas claras para aumentar la cobertura educativa, reducir la brecha de desigualdad y mejorar los resultados académicos. Sin embargo, a pesar de estos esfuerzos, todavía existen desafíos importantes que deben ser abordados. Por ejemplo, la segregación educativa sigue siendo un problema persistente, ya que muchos estudiantes de escasos recursos siguen asistiendo a establecimientos educacionales con menos recursos y oportunidades. Además, la falta de apoyo a los estudiantes con necesidades especiales y la insuficiente formación de los docentes en áreas como la tecnología y la innovación educativa también son cuestiones que requieren atención inmediata. En este contexto, es fundamental evaluar críticamente las políticas educativas actuales y proponer soluciones efectivas que permitan superar estos desafíos y alcanzar una educación de calidad para todos. La evaluación de estas políticas debe considerar no solo los aspectos cuantitativos, como el aumento en la matrícula o la reducción de la deserción, sino también los aspectos cualitativos, como la mejora en la calidad de la enseñanza y el aprendizaje, y el impacto en la sociedad en general.	¿Cuál es uno de los desafíos importantes que todavía deben ser abordados en la educación en Chile?	{"A": "La falta de recursos financieros para la educación", "B": "La segregación educativa", "C": "La insuficiente formación de los docentes en áreas como la tecnología y la innovación educativa", "D": "Todas las anteriores"}	D	El texto inédito menciona que la segregación educativa, la falta de apoyo a los estudiantes con necesidades especiales y la insuficiente formación de los docentes en áreas como la tecnología y la innovación educativa son cuestiones que requieren atención inmediata.	Clonado	2026-05-14 19:45:25.198218+00	t
11	20	4	La educación en Chile ha experimentado cambios significativos en las últimas décadas. Uno de los aspectos más destacados ha sido la implementación de políticas educativas que buscan mejorar la calidad de la educación en todos los niveles. En este sentido, se han establecido metas claras para aumentar la cobertura educativa, reducir la brecha de desigualdad y mejorar los resultados académicos. Sin embargo, a pesar de estos esfuerzos, todavía existen desafíos importantes que deben ser abordados. Por ejemplo, la segregación educativa sigue siendo un problema persistente, ya que muchos estudiantes de escasos recursos siguen asistiendo a establecimientos educacionales con menos recursos y oportunidades. Además, la falta de apoyo a los estudiantes con necesidades especiales y la insuficiente formación de los docentes en áreas como la tecnología y la innovación educativa también son cuestiones que requieren atención inmediata. En este contexto, es fundamental evaluar críticamente las políticas educativas actuales y proponer soluciones efectivas que permitan superar estos desafíos y alcanzar una educación de calidad para todos. La evaluación de estas políticas debe considerar no solo los aspectos cuantitativos, como el aumento en la matrícula o la reducción de la deserción, sino también los aspectos cualitativos, como la mejora en la calidad de la enseñanza y el aprendizaje, y el impacto en la sociedad en general.	¿Qué aspectos debe considerar la evaluación de las políticas educativas actuales?	{"A": "Solo los aspectos cuantitativos", "B": "Solo los aspectos cualitativos", "C": "Tanto los aspectos cuantitativos como los cualitativos", "D": "Ninguno de los anteriores"}	C	El texto inédito menciona que la evaluación de las políticas educativas actuales debe considerar no solo los aspectos cuantitativos, como el aumento en la matrícula o la reducción de la deserción, sino también los aspectos cualitativos, como la mejora en la calidad de la enseñanza y el aprendizaje, y el impacto en la sociedad en general.	Clonado	2026-05-14 19:45:25.219738+00	t
12	21	4	La educación en Chile ha experimentado cambios significativos en las últimas décadas. Uno de los aspectos más destacados ha sido la implementación de políticas educativas que buscan mejorar la calidad de la educación en todos los niveles. En este sentido, se han establecido metas claras para aumentar la cobertura educativa, reducir la brecha de desigualdad y mejorar los resultados académicos. Sin embargo, a pesar de estos esfuerzos, todavía existen desafíos importantes que deben ser abordados. Por ejemplo, la segregación educativa sigue siendo un problema persistente, ya que muchos estudiantes de escasos recursos siguen asistiendo a establecimientos educacionales con menos recursos y oportunidades. Además, la falta de apoyo a los estudiantes con necesidades especiales y la insuficiente formación de los docentes en áreas como la tecnología y la innovación educativa también son cuestiones que requieren atención inmediata. En este contexto, es fundamental evaluar críticamente las políticas educativas actuales y proponer soluciones efectivas que permitan superar estos desafíos y alcanzar una educación de calidad para todos. La evaluación de estas políticas debe considerar no solo los aspectos cuantitativos, como el aumento en la matrícula o la reducción de la deserción, sino también los aspectos cualitativos, como la mejora en la calidad de la enseñanza y el aprendizaje, y el impacto en la sociedad en general.	¿Cuál es el objetivo final de evaluar críticamente las políticas educativas actuales?	{"A": "Reducir la inversión en educación", "B": "Mejorar la calidad de la educación para todos", "C": "Aumentar la segregación educativa", "D": "Disminuir la cobertura educativa"}	B	El texto inédito menciona que es fundamental evaluar críticamente las políticas educativas actuales y proponer soluciones efectivas que permitan superar los desafíos y alcanzar una educación de calidad para todos.	Clonado	2026-05-14 19:45:25.243117+00	t
13	26	5	La educación en Chile ha experimentado cambios significativos en las últimas décadas. Uno de los aspectos más destacados ha sido la implementación de políticas educativas que buscan mejorar la calidad de la educación y reducir las brechas de desigualdad. Sin embargo, a pesar de estos esfuerzos, todavía existen desafíos importantes que deben ser abordados. Por ejemplo, la segregación escolar sigue siendo un problema grave, ya que muchos estudiantes de escasos recursos se encuentran en establecimientos educacionales con menos recursos y oportunidades. Además, la falta de acceso a la educación superior para los sectores más vulnerables de la sociedad sigue siendo un obstáculo significativo para la movilidad social. En este contexto, es fundamental que se continúen implementando políticas educativas que promuevan la inclusión y la equidad, y que se trabaje en la mejora de la calidad de la educación en todos los niveles. La comunidad educativa, incluyendo a estudiantes, profesores, padres y autoridades, debe trabajar juntos para abordar estos desafíos y asegurar que todos los estudiantes tengan acceso a una educación de calidad que les permita desarrollar sus potencialidades y alcanzar sus metas. La educación es un derecho fundamental y es responsabilidad de todos garantizar que se respete y se promueva en todas las esferas de la sociedad.	¿Cuál es uno de los principales desafíos que enfrenta la educación en Chile, según el texto?	{"A": "La falta de recursos financieros para las escuelas", "B": "La segregación escolar y la falta de acceso a la educación superior", "C": "La falta de interés de los estudiantes en aprender", "D": "La insuficiente formación de los profesores"}	B	El texto menciona explícitamente que la segregación escolar y la falta de acceso a la educación superior son desafíos importantes que deben ser abordados.	Clonado	2026-05-14 20:00:22.578925+00	t
14	27	5	La educación en Chile ha experimentado cambios significativos en las últimas décadas. Uno de los aspectos más destacados ha sido la implementación de políticas educativas que buscan mejorar la calidad de la educación y reducir las brechas de desigualdad. Sin embargo, a pesar de estos esfuerzos, todavía existen desafíos importantes que deben ser abordados. Por ejemplo, la segregación escolar sigue siendo un problema grave, ya que muchos estudiantes de escasos recursos se encuentran en establecimientos educacionales con menos recursos y oportunidades. Además, la falta de acceso a la educación superior para los sectores más vulnerables de la sociedad sigue siendo un obstáculo significativo para la movilidad social. En este contexto, es fundamental que se continúen implementando políticas educativas que promuevan la inclusión y la equidad, y que se trabaje en la mejora de la calidad de la educación en todos los niveles. La comunidad educativa, incluyendo a estudiantes, profesores, padres y autoridades, debe trabajar juntos para abordar estos desafíos y asegurar que todos los estudiantes tengan acceso a una educación de calidad que les permita desarrollar sus potencialidades y alcanzar sus metas. La educación es un derecho fundamental y es responsabilidad de todos garantizar que se respete y se promueva en todas las esferas de la sociedad.	¿Qué se considera fundamental para abordar los desafíos en la educación, según el texto?	{"A": "Implementar políticas educativas que promuevan la competencia entre los estudiantes", "B": "Implementar políticas educativas que promuevan la inclusión y la equidad", "C": "Reducir el número de estudiantes en las aulas", "D": "Aumentar la cantidad de profesores sin experiencia"}	B	El texto indica que es fundamental implementar políticas educativas que promuevan la inclusión y la equidad para abordar los desafíos en la educación.	Clonado	2026-05-14 20:00:22.605659+00	t
15	28	5	La educación en Chile ha experimentado cambios significativos en las últimas décadas. Uno de los aspectos más destacados ha sido la implementación de políticas educativas que buscan mejorar la calidad de la educación y reducir las brechas de desigualdad. Sin embargo, a pesar de estos esfuerzos, todavía existen desafíos importantes que deben ser abordados. Por ejemplo, la segregación escolar sigue siendo un problema grave, ya que muchos estudiantes de escasos recursos se encuentran en establecimientos educacionales con menos recursos y oportunidades. Además, la falta de acceso a la educación superior para los sectores más vulnerables de la sociedad sigue siendo un obstáculo significativo para la movilidad social. En este contexto, es fundamental que se continúen implementando políticas educativas que promuevan la inclusión y la equidad, y que se trabaje en la mejora de la calidad de la educación en todos los niveles. La comunidad educativa, incluyendo a estudiantes, profesores, padres y autoridades, debe trabajar juntos para abordar estos desafíos y asegurar que todos los estudiantes tengan acceso a una educación de calidad que les permita desarrollar sus potencialidades y alcanzar sus metas. La educación es un derecho fundamental y es responsabilidad de todos garantizar que se respete y se promueva en todas las esferas de la sociedad.	¿Quiénes deben trabajar juntos para abordar los desafíos en la educación, según el texto?	{"A": "Solo los profesores y los estudiantes", "B": "Solo las autoridades educativas y los padres", "C": "La comunidad educativa, incluyendo a estudiantes, profesores, padres y autoridades", "D": "Solo los estudiantes y las autoridades educativas"}	C	El texto menciona que la comunidad educativa, incluyendo a estudiantes, profesores, padres y autoridades, debe trabajar juntos para abordar los desafíos en la educación.	Clonado	2026-05-14 20:00:22.623564+00	t
16	29	5	La educación en Chile ha experimentado cambios significativos en las últimas décadas. Uno de los aspectos más destacados ha sido la implementación de políticas educativas que buscan mejorar la calidad de la educación y reducir las brechas de desigualdad. Sin embargo, a pesar de estos esfuerzos, todavía existen desafíos importantes que deben ser abordados. Por ejemplo, la segregación escolar sigue siendo un problema grave, ya que muchos estudiantes de escasos recursos se encuentran en establecimientos educacionales con menos recursos y oportunidades. Además, la falta de acceso a la educación superior para los sectores más vulnerables de la sociedad sigue siendo un obstáculo significativo para la movilidad social. En este contexto, es fundamental que se continúen implementando políticas educativas que promuevan la inclusión y la equidad, y que se trabaje en la mejora de la calidad de la educación en todos los niveles. La comunidad educativa, incluyendo a estudiantes, profesores, padres y autoridades, debe trabajar juntos para abordar estos desafíos y asegurar que todos los estudiantes tengan acceso a una educación de calidad que les permita desarrollar sus potencialidades y alcanzar sus metas. La educación es un derecho fundamental y es responsabilidad de todos garantizar que se respete y se promueva en todas las esferas de la sociedad.	¿Por qué es importante garantizar que todos los estudiantes tengan acceso a una educación de calidad, según el texto?	{"A": "Para que puedan desarrollar sus habilidades deportivas", "B": "Para que puedan desarrollar sus potencialidades y alcanzar sus metas", "C": "Para que puedan aprender solo materias científicas", "D": "Para que puedan aprender solo materias artísticas"}	B	El texto indica que la educación es un derecho fundamental y que es importante garantizar que todos los estudiantes tengan acceso a una educación de calidad para que puedan desarrollar sus potencialidades y alcanzar sus metas.	Clonado	2026-05-14 20:00:22.640598+00	t
\.


--
-- Data for Name: sesion_preguntas; Type: TABLE DATA; Schema: public; Owner: user_lexiscan
--

COPY public.sesion_preguntas (id_sesion_pregunta, id_examen, id_pregunta, respuesta_dada, es_correcta, tiempo_respuesta) FROM stdin;
1	1	10	\N	\N	\N
2	1	16	\N	\N	\N
3	1	7	\N	\N	\N
4	1	19	\N	\N	\N
5	1	20	\N	\N	\N
6	1	8	\N	\N	\N
7	1	5	\N	\N	\N
8	1	6	\N	\N	\N
9	1	21	\N	\N	\N
10	1	13	\N	\N	\N
11	1	11	\N	\N	\N
12	1	2	\N	\N	\N
13	1	12	\N	\N	\N
14	1	9	\N	\N	\N
15	1	15	\N	\N	\N
\.


--
-- Data for Name: sesiones_examen; Type: TABLE DATA; Schema: public; Owner: user_lexiscan
--

COPY public.sesiones_examen (id_examen, rut_usuario, cantidad_preguntas, puntaje_obtenido, puntaje_maximo, tiempo_total, es_impulsivo, fecha_inicio, fecha_fin, completado) FROM stdin;
1	20144801-8	15	\N	15	0	f	2026-05-14 19:58:18.501346+00	\N	f
\.


--
-- Data for Name: transacciones_monedas; Type: TABLE DATA; Schema: public; Owner: user_lexiscan
--

COPY public.transacciones_monedas (id_transaccion, rut_usuario, monto, concepto, fecha) FROM stdin;
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: user_lexiscan
--

COPY public.usuarios (rut, nombre_completo, email, password_hash, xp_total, racha_actual, fecha_registro, activo, ultimo_acceso) FROM stdin;
20144801-8	Elias Yañez	yeliasdaniel@gmail.com	$2b$12$/WKLdzCaFyCvgYSdQD2zA.kuRgMiXgUSulNB7G.lQRbA2ubtekRnO	210	1	2026-05-14 19:20:15.715854+00	t	2026-05-14 19:58:18.519808+00
\.


--
-- Name: banco_preguntas_id_pregunta_seq; Type: SEQUENCE SET; Schema: public; Owner: user_lexiscan
--

SELECT pg_catalog.setval('public.banco_preguntas_id_pregunta_seq', 37, true);


--
-- Name: configuracion_id_config_seq; Type: SEQUENCE SET; Schema: public; Owner: user_lexiscan
--

SELECT pg_catalog.setval('public.configuracion_id_config_seq', 2, true);


--
-- Name: errores_favoritos_id_error_seq; Type: SEQUENCE SET; Schema: public; Owner: user_lexiscan
--

SELECT pg_catalog.setval('public.errores_favoritos_id_error_seq', 16, true);


--
-- Name: historial_habilidades_id_progreso_seq; Type: SEQUENCE SET; Schema: public; Owner: user_lexiscan
--

SELECT pg_catalog.setval('public.historial_habilidades_id_progreso_seq', 7, true);


--
-- Name: preguntas_ia_id_pregunta_seq; Type: SEQUENCE SET; Schema: public; Owner: user_lexiscan
--

SELECT pg_catalog.setval('public.preguntas_ia_id_pregunta_seq', 16, true);


--
-- Name: sesion_preguntas_id_sesion_pregunta_seq; Type: SEQUENCE SET; Schema: public; Owner: user_lexiscan
--

SELECT pg_catalog.setval('public.sesion_preguntas_id_sesion_pregunta_seq', 15, true);


--
-- Name: sesiones_examen_id_examen_seq; Type: SEQUENCE SET; Schema: public; Owner: user_lexiscan
--

SELECT pg_catalog.setval('public.sesiones_examen_id_examen_seq', 1, true);


--
-- Name: transacciones_monedas_id_transaccion_seq; Type: SEQUENCE SET; Schema: public; Owner: user_lexiscan
--

SELECT pg_catalog.setval('public.transacciones_monedas_id_transaccion_seq', 1, false);


--
-- Name: banco_preguntas banco_preguntas_pkey; Type: CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.banco_preguntas
    ADD CONSTRAINT banco_preguntas_pkey PRIMARY KEY (id_pregunta);


--
-- Name: configuracion configuracion_clave_key; Type: CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.configuracion
    ADD CONSTRAINT configuracion_clave_key UNIQUE (clave);


--
-- Name: configuracion configuracion_pkey; Type: CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.configuracion
    ADD CONSTRAINT configuracion_pkey PRIMARY KEY (id_config);


--
-- Name: economia_monedas economia_monedas_pkey; Type: CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.economia_monedas
    ADD CONSTRAINT economia_monedas_pkey PRIMARY KEY (rut_usuario);


--
-- Name: errores_favoritos errores_favoritos_pkey; Type: CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.errores_favoritos
    ADD CONSTRAINT errores_favoritos_pkey PRIMARY KEY (id_error);


--
-- Name: errores_favoritos errores_favoritos_rut_usuario_id_pregunta_key; Type: CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.errores_favoritos
    ADD CONSTRAINT errores_favoritos_rut_usuario_id_pregunta_key UNIQUE (rut_usuario, id_pregunta);


--
-- Name: historial_habilidades historial_habilidades_pkey; Type: CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.historial_habilidades
    ADD CONSTRAINT historial_habilidades_pkey PRIMARY KEY (id_progreso);


--
-- Name: historial_habilidades historial_habilidades_rut_usuario_nombre_habilidad_key; Type: CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.historial_habilidades
    ADD CONSTRAINT historial_habilidades_rut_usuario_nombre_habilidad_key UNIQUE (rut_usuario, nombre_habilidad);


--
-- Name: preguntas_ia preguntas_ia_pkey; Type: CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.preguntas_ia
    ADD CONSTRAINT preguntas_ia_pkey PRIMARY KEY (id_pregunta);


--
-- Name: sesion_preguntas sesion_preguntas_pkey; Type: CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.sesion_preguntas
    ADD CONSTRAINT sesion_preguntas_pkey PRIMARY KEY (id_sesion_pregunta);


--
-- Name: sesiones_examen sesiones_examen_pkey; Type: CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.sesiones_examen
    ADD CONSTRAINT sesiones_examen_pkey PRIMARY KEY (id_examen);


--
-- Name: transacciones_monedas transacciones_monedas_pkey; Type: CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.transacciones_monedas
    ADD CONSTRAINT transacciones_monedas_pkey PRIMARY KEY (id_transaccion);


--
-- Name: usuarios usuarios_email_key; Type: CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_email_key UNIQUE (email);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (rut);


--
-- Name: idx_banco_activa; Type: INDEX; Schema: public; Owner: user_lexiscan
--

CREATE INDEX idx_banco_activa ON public.banco_preguntas USING btree (activa);


--
-- Name: idx_banco_habilidad; Type: INDEX; Schema: public; Owner: user_lexiscan
--

CREATE INDEX idx_banco_habilidad ON public.banco_preguntas USING btree (id_habilidad);


--
-- Name: idx_errores_resuelta; Type: INDEX; Schema: public; Owner: user_lexiscan
--

CREATE INDEX idx_errores_resuelta ON public.errores_favoritos USING btree (resuelta);


--
-- Name: idx_errores_usuario; Type: INDEX; Schema: public; Owner: user_lexiscan
--

CREATE INDEX idx_errores_usuario ON public.errores_favoritos USING btree (rut_usuario);


--
-- Name: idx_errores_veces; Type: INDEX; Schema: public; Owner: user_lexiscan
--

CREATE INDEX idx_errores_veces ON public.errores_favoritos USING btree (veces_fallada DESC);


--
-- Name: idx_habilidades_nivel; Type: INDEX; Schema: public; Owner: user_lexiscan
--

CREATE INDEX idx_habilidades_nivel ON public.historial_habilidades USING btree (nivel_maestria);


--
-- Name: idx_preguntas_ia_activa; Type: INDEX; Schema: public; Owner: user_lexiscan
--

CREATE INDEX idx_preguntas_ia_activa ON public.preguntas_ia USING btree (activa);


--
-- Name: idx_preguntas_ia_habilidad; Type: INDEX; Schema: public; Owner: user_lexiscan
--

CREATE INDEX idx_preguntas_ia_habilidad ON public.preguntas_ia USING btree (id_habilidad);


--
-- Name: idx_sesion_fecha; Type: INDEX; Schema: public; Owner: user_lexiscan
--

CREATE INDEX idx_sesion_fecha ON public.sesiones_examen USING btree (fecha_inicio DESC);


--
-- Name: idx_sesion_usuario; Type: INDEX; Schema: public; Owner: user_lexiscan
--

CREATE INDEX idx_sesion_usuario ON public.sesiones_examen USING btree (rut_usuario);


--
-- Name: idx_sp_examen; Type: INDEX; Schema: public; Owner: user_lexiscan
--

CREATE INDEX idx_sp_examen ON public.sesion_preguntas USING btree (id_examen);


--
-- Name: idx_sp_pregunta; Type: INDEX; Schema: public; Owner: user_lexiscan
--

CREATE INDEX idx_sp_pregunta ON public.sesion_preguntas USING btree (id_pregunta);


--
-- Name: idx_trans_fecha; Type: INDEX; Schema: public; Owner: user_lexiscan
--

CREATE INDEX idx_trans_fecha ON public.transacciones_monedas USING btree (fecha DESC);


--
-- Name: idx_trans_usuario; Type: INDEX; Schema: public; Owner: user_lexiscan
--

CREATE INDEX idx_trans_usuario ON public.transacciones_monedas USING btree (rut_usuario);


--
-- Name: idx_usuarios_email; Type: INDEX; Schema: public; Owner: user_lexiscan
--

CREATE INDEX idx_usuarios_email ON public.usuarios USING btree (email);


--
-- Name: banco_preguntas banco_preguntas_id_habilidad_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.banco_preguntas
    ADD CONSTRAINT banco_preguntas_id_habilidad_fkey FOREIGN KEY (id_habilidad) REFERENCES public.historial_habilidades(id_progreso);


--
-- Name: economia_monedas economia_monedas_rut_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.economia_monedas
    ADD CONSTRAINT economia_monedas_rut_usuario_fkey FOREIGN KEY (rut_usuario) REFERENCES public.usuarios(rut) ON DELETE CASCADE;


--
-- Name: errores_favoritos errores_favoritos_id_habilidad_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.errores_favoritos
    ADD CONSTRAINT errores_favoritos_id_habilidad_fkey FOREIGN KEY (id_habilidad) REFERENCES public.historial_habilidades(id_progreso);


--
-- Name: errores_favoritos errores_favoritos_id_pregunta_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.errores_favoritos
    ADD CONSTRAINT errores_favoritos_id_pregunta_fkey FOREIGN KEY (id_pregunta) REFERENCES public.banco_preguntas(id_pregunta);


--
-- Name: errores_favoritos errores_favoritos_rut_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.errores_favoritos
    ADD CONSTRAINT errores_favoritos_rut_usuario_fkey FOREIGN KEY (rut_usuario) REFERENCES public.usuarios(rut) ON DELETE CASCADE;


--
-- Name: historial_habilidades historial_habilidades_rut_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.historial_habilidades
    ADD CONSTRAINT historial_habilidades_rut_usuario_fkey FOREIGN KEY (rut_usuario) REFERENCES public.usuarios(rut) ON DELETE CASCADE;


--
-- Name: preguntas_ia preguntas_ia_id_habilidad_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.preguntas_ia
    ADD CONSTRAINT preguntas_ia_id_habilidad_fkey FOREIGN KEY (id_habilidad) REFERENCES public.historial_habilidades(id_progreso);


--
-- Name: sesion_preguntas sesion_preguntas_id_examen_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.sesion_preguntas
    ADD CONSTRAINT sesion_preguntas_id_examen_fkey FOREIGN KEY (id_examen) REFERENCES public.sesiones_examen(id_examen) ON DELETE CASCADE;


--
-- Name: sesion_preguntas sesion_preguntas_id_pregunta_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.sesion_preguntas
    ADD CONSTRAINT sesion_preguntas_id_pregunta_fkey FOREIGN KEY (id_pregunta) REFERENCES public.banco_preguntas(id_pregunta);


--
-- Name: sesiones_examen sesiones_examen_rut_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.sesiones_examen
    ADD CONSTRAINT sesiones_examen_rut_usuario_fkey FOREIGN KEY (rut_usuario) REFERENCES public.usuarios(rut) ON DELETE CASCADE;


--
-- Name: transacciones_monedas transacciones_monedas_rut_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user_lexiscan
--

ALTER TABLE ONLY public.transacciones_monedas
    ADD CONSTRAINT transacciones_monedas_rut_usuario_fkey FOREIGN KEY (rut_usuario) REFERENCES public.usuarios(rut);


--
-- PostgreSQL database dump complete
--

\unrestrict ZxmVdbOWxyufDKCD6FhqfjGFGdahb8OTREwXklpBHX0231FV2i1827URUoVeoDN

