-- Poblar datos de prueba para LexiScan PAES
-- Incluye usuario de prueba, habilidades, wallet y preguntas base

INSERT INTO
    usuarios (
        rut,
        nombre_completo,
        email,
        password_hash,
        xp_total,
        racha_actual,
        activo,
        ultimo_acceso
    )
VALUES (
        '12345678-9',
        'Benjamín Pérez',
        'benjamin@lexiscan.cl',
        '07480fb9e85b9396af06f006cf1c95024af2531c65fb505cfbd0add1e2f31573',
        420,
        7,
        TRUE,
        NOW()
    ) ON CONFLICT (rut) DO NOTHING;

INSERT INTO
    economia_monedas (
        rut_usuario,
        saldo_monedas,
        total_acumulado,
        ultima_transaccion
    )
VALUES (
        '12345678-9',
        320,
        1120,
        NOW()
    ) ON CONFLICT (rut_usuario) DO NOTHING;

INSERT INTO
    historial_habilidades (
        id_progreso,
        rut_usuario,
        nombre_habilidad,
        nivel_maestria,
        ultima_actualizacion
    )
VALUES (
        1,
        '12345678-9',
        'Localizar',
        85.00,
        NOW()
    ),
    (
        2,
        '12345678-9',
        'Interpretar',
        62.00,
        NOW()
    ),
    (
        3,
        '12345678-9',
        'Evaluar',
        32.00,
        NOW()
    ),
    (
        4,
        '12345678-9',
        'Lectura_Critica',
        75.00,
        NOW()
    ),
    (
        5,
        '12345678-9',
        'Vocabulario',
        90.00,
        NOW()
    ),
    (
        6,
        '12345678-9',
        'Tipos_de_Texto',
        54.00,
        NOW()
    ) ON CONFLICT DO NOTHING;

INSERT INTO
    preguntas_ia (
        id_pregunta,
        id_habilidad,
        texto_inedito,
        enunciado,
        alternativas,
        respuesta_correcta,
        justificacion_cot,
        modelo_ia,
        activa
    )
VALUES (
        1,
        1,
        'Lectura 1 del 1er Ensayo General Nacional: Un pasaje de comprensión lectora sobre un texto informativo que describe un trayecto histórico.',
        '¿Cuál es el objetivo principal del autor en el texto?',
        '{"A":"Criticar el pasado", "B":"Informar sobre el trayecto histórico", "C":"Narrar una historia personal", "D":"Proponer una solución política"}',
        'B',
        'El autor describe un trayecto histórico y su intención es informar.',
        'sinclair',
        TRUE
    ),
    (
        2,
        2,
        'Lectura 2 del 1er Ensayo General Nacional: Un texto de interpretación que compara dos posiciones sobre un problema social.',
        '¿Qué recurso emplea el autor para contrastar las opiniones?',
        '{"A":"Analogía", "B":"Metáfora", "C":"Cita de expertos", "D":"Enumeración"}',
        'A',
        'El autor usa analogías para mostrar las diferencias entre ambas posturas.',
        'sinclair',
        TRUE
    ),
    (
        3,
        3,
        'Lectura 3 del 1er Ensayo General Nacional: Un análisis crítico de un acontecimiento cultural reciente.',
        '¿Cuál es la tesis principal del texto?',
        '{"A":"Los eventos culturales son irrelevantes", "B":"El acontecimiento refleja cambios sociales", "C":"La cultura debe ser aislada", "D":"El evento fue un fracaso"}',
        'B',
        'La tesis es que el acontecimiento refleja cambios sociales importantes.',
        'sinclair',
        TRUE
    ),
    (
        4,
        4,
        'Lectura 4 del 1er Ensayo General Nacional: Un texto sobre estrategias de lectura crítica en contextos académicos.',
        '¿Qué aspecto evalúa el texto con mayor atención?',
        '{"A":"El estilo literario", "B":"La estructura argumentativa", "C":"Los datos estadísticos", "D":"La ambientación"}',
        'B',
        'Se pone énfasis en la estructura argumentativa del texto.',
        'sinclair',
        TRUE
    ),
    (
        5,
        5,
        'Lectura 5 del 1er Ensayo General Nacional: Una sección dedicada al significado de palabras clave en un pasaje complejo.',
        '¿Cuál es la función del vocabulario en el pasaje?',
        '{"A":"Generar confusión", "B":"Enriquecer el tono académico", "C":"Reducir el significado", "D":"Ofrecer ejemplos técnicos"}',
        'B',
        'El vocabulario enriquece el tono académico y refuerza el contenido.',
        'sinclair',
        TRUE
    ),
    (
        6,
        6,
        'Lectura 6 del 1er Ensayo General Nacional: Un texto que describe distintos tipos de texto utilizados en exámenes PAES.',
        '¿Qué tipo de texto presenta principalmente el pasaje?',
        '{"A":"Narrativo", "B":"Argumentativo", "C":"Descriptivo", "D":"Instructivo"}',
        'C',
        'El pasaje describe características de distintos tipos de texto, por lo que es descriptivo.',
        'sinclair',
        TRUE
    );