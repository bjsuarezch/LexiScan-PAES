export interface HabilidadData {
  nombre_habilidad: string;
  nivel_maestria: number;
}

export interface DashboardResponse {
  rut: string;
  nombre_completo: string;
  xp_total: number;
  racha_actual: number;
  saldo_monedas: number;
  habilidades: HabilidadData[];
}

export interface PreguntaItem {
  id_pregunta: number;
  enunciado: string;
  alternativas: Record<string, string>;
  respuesta_correcta: string;
  justificacion_cot: string;
}

export interface HabilidadDetail {
  nombre_habilidad: string;
  texto_inedito: string;
  preguntas: PreguntaItem[];
}

export interface ExamenResponse {
  id_examen: number;
  rut_usuario: string;
  cantidad_preguntas: number;
  estimated_time: number;
  preguntas: PreguntaItem[];
}
