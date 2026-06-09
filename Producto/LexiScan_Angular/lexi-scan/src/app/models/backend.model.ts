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
  tema_actual_id?: number;
  textos_restantes?: number;
  habilidades: HabilidadData[];
}

export interface PreguntaItem {
  id_pregunta: number;
  enunciado: string;
  alternativas: Record<string, string>;
  respuesta_correcta: string;
  justificacion_cot: string;
  texto_inedito?: any[] | string;
}

export interface GeneratedPreguntaItem {
  id_pregunta: number;
  enunciado: string;
  alternativas: Record<string, string>;
  respuesta_correcta: string;
  justificacion_cot: string;
  texto_inedito?: any[] | string;
}

export interface HabilidadDetail {
  nombre_habilidad: string;
  texto_inedito: any[] | string;
  preguntas: PreguntaItem[];
}

export interface GeneratedHabilidadDetail {
  tipo_habilidad: string;
  texto_inedito: any[] | string;
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
  rendimiento_cambio?: number;
  mensaje: string;
}

export interface ExamenResponse {
  id_examen: number;
  rut_usuario: string;
  cantidad_preguntas: number;
  estimated_time: number;
  preguntas: PreguntaItem[];
}

export interface Desafio {
  id: number;
  titulo: string;
  descripcion: string;
  recompensa_monedas: number;
  progreso: number;
  meta: number;
  completado: boolean;
  reclamado: boolean;
  tipo: 'tiempo_habilidades' | 'diversidad_habilidades' | 'habilidad_baja' | 'gym_sin_errores' | 'tiempo_examen';
}

export interface DesafioProgresoLocal {
  fecha: string;
  desafiosActivos: Desafio[];
  habilidadesPracticadas: string[];
  vecesHabilidadBajaPracticada: number;
}

export interface RankingUserItem {
  posicion: number;
  nombre_completo: string;
  xp_total: number;
  rut_parcial: string;
}

export interface RankingResponse {
  ranking: RankingUserItem[];
  usuario_actual?: RankingUserItem;
}
