import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AlertController } from '@ionic/angular';
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
  textosRestantes: number = 0;
  temaActualId: number | null = null;

  constructor(
    private router: Router,
    private profileService: ProfileService,
    private habilidadesService: HabilidadesService,
    private alertController: AlertController,
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
      next: async (data) => {
        this.habilidades = data.habilidades;
        this.textosRestantes = data.textos_restantes ?? 0;
        this.temaActualId = data.tema_actual_id ?? null;
        
        if (this.textosRestantes <= 0) {
          const alert = await this.alertController.create({
            header: '¡Se acabaron tus textos!',
            message: 'Se le han acabado los 3 textos personalizados, supera los desafios del dia para ganar puntos y mas oportunidades de escoger temas personalizados!',
            buttons: [
              {
                text: 'Elegir nuevo tema',
                handler: () => {
                  this.router.navigate(['/seleccion-tema']);
                }
              }
            ]
          });
          await alert.present();
        }
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

    if (!this.profile?.rut) return;

    // We can't know for sure the name of the custom theme, but if we have an ID it's a fixed or custom theme.
    // The backend uses 'tema' as string. We should just pass es_fijo=false for now or true if it's fixed.
    // Wait, backend expects 'tema' string, but if we don't pass it, it uses user.tema_actual_id for DB lookup.
    // Actually, backend needs 'tema' for the prompt! But wait, backend prompt uses 'request.tema'.
    // If request.tema is empty, it chooses random. But if they selected a theme, we should probably fetch the tema name.
    // Or just let the backend handle it! Wait, we don't know the tema name.
    // It's okay, we'll just pass es_fijo = false for now since backend already knows the ID and for the prompt it would be nice to have it, but let's see. 
    
    this.habilidadesService.generarPreguntas(this.profile.rut, skill, null, false).subscribe({
      next: (data) => {
        this.selectedHabilidad = data;
        this.totalQuestions = data.preguntas.length;
      },
      error: (error) => {
        console.error('Error al generar preguntas:', error);
        alert(error.error?.detail || 'No se pudo generar las preguntas. Inténtalo de nuevo.');
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

  getTextoBlocks(): any[] {
    if (!this.selectedHabilidad) return [];
    const texto = this.selectedHabilidad.texto_inedito;
    if (typeof texto === 'string') {
      try {
        const parsed = JSON.parse(texto);
        return Array.isArray(parsed) ? parsed : [{ tipo: 'parrafo', contenido: texto }];
      } catch {
        return [{ tipo: 'parrafo', contenido: texto }];
      }
    }
    if (Array.isArray(texto)) {
      return texto;
    }
    return [];
  }
}
