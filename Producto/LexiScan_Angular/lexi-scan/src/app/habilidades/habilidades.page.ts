import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ProfileService } from '../services/profile.service';
import { HabilidadesService } from '../services/habilidades.service';
import {
  DashboardResponse,
  HabilidadData,
  GeneratedHabilidadDetail,
} from '../models/backend.model';
import { IUserProfile } from '../models/auth.model';
import { BehaviorSubject, Observable } from 'rxjs';

interface EvaluacionResultado {
  index: number;
  enunciado: string;
  respuesta_usuario: string;
  respuesta_correcta: string;
  correcta: boolean;
  feedback: string;
}

@Component({
  selector: 'app-habilidades',
  templateUrl: 'habilidades.page.html',
  styleUrls: ['habilidades.page.scss'],
  standalone: false,
})
export class HabilidadesPage implements OnInit {
  habilidades: HabilidadData[] = [];
  selectedHabilidad: GeneratedHabilidadDetail | null = null;
  profile: IUserProfile | null = null;
  selectedAnswers: Record<number, string> = {};
  evaluationResults: EvaluacionResultado[] = [];
  totalCorrect = 0;
  totalQuestions = 0;
  xpGanada = 0;
  submitting = false;
  isSubmitted = false;
  evaluationError: string | null = null;

  constructor(
    private router: Router,
    private profileService: ProfileService,
    private habilidadesService: HabilidadesService,
  ) {}

  ngOnInit() {
    this.profileService.getProfile().subscribe((profile) => {
      this.profile = profile;
      if (profile?.rut) {
        this.loadHabilidades(profile.rut);
      }
    });
  }

  loadHabilidades(rut: string) {
    this.habilidadesService.getDashboard(rut).subscribe({
      next: (data) => {
        this.habilidades = data.habilidades;
      },
      error: (error) => {
        console.error('Error al cargar habilidades:', error);
      },
    });
  }

  getClass(nivel: number): string {
    if (nivel === 100) {
      return 'maestria-full';
    }
    if (nivel >= 50) {
      return 'maestria-media';
    }
    return 'maestria-baja';
  }

  selectSkill(skill: string): void {
    this.selectedHabilidad = null;
    this.selectedAnswers = {};
    this.evaluationResults = [];
    this.totalCorrect = 0;
    this.totalQuestions = 0;
    this.xpGanada = 0;
    this.evaluationError = null;
    this.isSubmitted = false;

    this.habilidadesService.generarPreguntas(skill).subscribe({
      next: (data) => {
        this.selectedHabilidad = data;
        this.totalQuestions = data.preguntas.length;
      },
      error: (error) => {
        console.error('Error al generar preguntas:', error);
        alert('No se pudo generar las preguntas. Inténtalo de nuevo.');
      },
    });
  }

  canSubmit(): boolean {
    return (
      !this.isSubmitted &&
      Boolean(this.selectedHabilidad) &&
      (this.selectedHabilidad?.preguntas.every(
        (_, index) => !!this.selectedAnswers[index],
      ) ??
        false)
    );
  }

  submitAnswers(): void {
    if (this.isSubmitted) return;

    if (!this.selectedHabilidad || !this.profile?.rut) {
      return;
    }

    this.submitting = true;
    this.evaluationError = null;
    this.evaluationResults = [];

    const payload = {
      rut: this.profile.rut,
      tipo_habilidad: this.selectedHabilidad!.tipo_habilidad,
      preguntas: this.selectedHabilidad!.preguntas.map((pregunta, index) => ({
        id_pregunta: pregunta.id_pregunta,
        enunciado: pregunta.enunciado,
        alternativas: pregunta.alternativas,
        respuesta_usuario: this.selectedAnswers[index] || '',
        respuesta_correcta: pregunta.respuesta_correcta,
        justificacion: pregunta.justificacion_cot,
        texto_inedito:
          pregunta.texto_inedito || this.selectedHabilidad?.texto_inedito,
      })),
    };

    this.habilidadesService.evaluarRespuestas(payload).subscribe({
      next: (result) => {
        this.evaluationResults = result.resultados;
        this.totalCorrect = result.total_correct;
        this.totalQuestions = result.total_preguntas;
        this.xpGanada = result.xp_ganada;
        this.submitting = false;
        this.isSubmitted = true;

        if (this.profile?.rut) {
          (this.loadHabilidades(this.profile.rut),
            this.habilidadesService.getDashboard(this.profile.rut).subscribe());
        }
      },
      error: (error) => {
        console.error('Error al evaluar respuestas:', error);
        this.evaluationError =
          'No se pudo evaluar tus respuestas. Intenta de nuevo más tarde.';
        this.submitting = false;
      },
    });
  }

  getRadarPoints(): string {
    if (!this.habilidades) return '';

    const center = { x: 100, y: 100 };
    const vertices: { [key: string]: { x: number; y: number } } = {
      Interpretar: { x: 100, y: 30 },
      Vocabulario: { x: 160, y: 65 },
      Tipos_de_Texto: { x: 160, y: 135 },
      Localizar: { x: 100, y: 170 },
      Lectura_Critica: { x: 40, y: 135 },
      Evaluar: { x: 40, y: 65 },
    };

    const order = [
      'Interpretar',
      'Vocabulario',
      'Tipos_de_Texto',
      'Localizar',
      'Lectura_Critica',
      'Evaluar',
    ];
    const points: string[] = [];

    for (const skill of order) {
      const vertex = vertices[skill];
      const habilidad = this.habilidades.find(
        (h) => h.nombre_habilidad === skill,
      );
      const percent = habilidad ? habilidad.nivel_maestria / 100 : 0;
      const x = center.x + (vertex.x - center.x) * percent;
      const y = center.y + (vertex.y - center.y) * percent;
      points.push(`${x.toFixed(1)},${y.toFixed(1)}`);
    }

    return points.join(' ');
  }
}
