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
  texto_inedito?: string;
}

export interface GeneratedPreguntaItem {
  enunciado: string;
  alternativas: Record<string, string>;
  respuesta_correcta: string;
  justificacion_cot: string;
  texto_inedito?: string;
}

export interface HabilidadDetail {
  nombre_habilidad: string;
  texto_inedito: string;
  preguntas: PreguntaItem[];
}

export interface GeneratedHabilidadDetail {
  tipo_habilidad: string;
  texto_inedito: string;
  preguntas: GeneratedPreguntaItem[];
}

export interface EvaluacionResultado {
  index: number;
  enunciado: string;
  respuesta_usuario: string;
  respuesta_correcta: string;
  correcta: boolean;
  feedback: string;
}

export interface ConfiguracionItem {
  clave: string;
  valor: string;
  descripcion?: string;
}

export interface ConfiguracionUpdate {
  clave: string;
  valor: string;
  descripcion?: string;
}

export interface GroqModel {
  id: string;
  object: string;
  created: number;
  owned_by: string;
}

export interface GroqModelsResponse {
  object: string;
  data: GroqModel[];
}

export interface EvaluarRespuestasResponse {
  resultados: EvaluacionResultado[];
  total_correct: number;
  total_preguntas: number;
  puntaje: number;
  xp_ganada: number;
  mensaje: string;
}

export interface ExamenResponse {
  id_examen: number;
  rut_usuario: string;
  cantidad_preguntas: number;
  estimated_time: number;
  preguntas: PreguntaItem[];
}
