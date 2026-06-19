import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HabilidadesService } from '../services/habilidades.service';
import { ProfileService } from '../services/profile.service';
import { DashboardResponse } from '../models/backend.model';
import { IUserProfile } from '../models/auth.model';
import { DesafiosService } from '../services/desafios.service';

@Component({
  selector: 'app-gym',
  templateUrl: 'gym.page.html',
  styleUrls: ['gym.page.scss'],
  standalone: false,
})
export class GymPage implements OnInit {
  dashboard: DashboardResponse | null = null;
  profile: IUserProfile | null = null;
  loading = false;
  errorFrecuente: any = null;
  erroresFrecuentes: any[] = [];
  errorActual: any = null;
  selectedAnswer: string = '';
  evaluationSubmitted = false;
  isCorrect = false;
  feedback = '';
  trainingStarted = false;

  erroresTotalesSesion = 0;
  erroresResueltosSesion = 0;
  showFeedbackBlock = false;
  isSubmitLocked = false;


  constructor(
    private router: Router,
    private habilidadesService: HabilidadesService,
    private profileService: ProfileService,
    private desafiosService: DesafiosService
  ) {}

  ngOnInit() {
    this.profileService.getProfile().subscribe((profile) => {
      this.profile = profile;
      if (profile?.rut) {
        this.loadDashboard(profile.rut);
        this.loadErrorFrecuente(profile.rut);
        // Removed loadErroresFrecuentes here
        this.errorActual = null;
      }
    });
  }

  loadDashboard(rut: string): void {
    this.loading = true;
    this.habilidadesService.getDashboard(rut).subscribe({
      next: (dashboard) => {
        this.dashboard = dashboard;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error al cargar dashboard:', error);
        this.loading = false;
      },
    });
  }

  loadErrorFrecuente(rut: string): void {
    this.habilidadesService.getErrorFrecuente(rut).subscribe({
      next: (error) => {
        this.errorFrecuente = error;
      },
      error: (error) => {
        console.error('Error al cargar error frecuente:', error);
        this.errorFrecuente = null;
      },
    });
  }

  loadErroresFrecuentes(rut: string): void {
    this.habilidadesService.getErroresFrecuentes(rut).subscribe({
      next: (errores) => {
        this.erroresFrecuentes = errores;
        this.erroresTotalesSesion = errores.length;
        this.erroresResueltosSesion = 0;
        if (errores.length > 0) {
          this.errorActual = errores[0];
          this.resetErrorState();
        }
      },
      error: (error) => {
        console.error('Error al cargar errores frecuentes:', error);
        this.erroresFrecuentes = [];
      },
    });
  }

  startTraining(): void {
    this.trainingStarted = true;
    if (this.profile?.rut) {
      this.loadErroresFrecuentes(this.profile.rut);
    }
  }

  submitErrorAnswer(): void {
    if (!this.selectedAnswer || !this.errorActual || this.isSubmitLocked) return;

    this.evaluationSubmitted = true;
    this.isSubmitLocked = true;
    this.isCorrect =
      this.selectedAnswer === this.errorActual.pregunta.respuesta_correcta;

    if (this.isCorrect) {
      this.feedback = '¡Excelente! ¡Resolviste este error! 🎉';
      this.showFeedbackBlock = true;
      this.erroresResueltosSesion++;

      this.habilidadesService
        .resolveError(this.errorActual.id_error)
        .subscribe({
          next: () => {
            if (this.profile?.rut) {
              const rut = this.profile.rut;
              const todayStr = new Date().toDateString();
              const savedDate = localStorage.getItem(`daily_goal_date_${rut}`);
              let count = 0;
              if (savedDate === todayStr) {
                count = parseInt(localStorage.getItem(`daily_goal_count_${rut}`) || '0', 10);
              } else {
                localStorage.setItem(`daily_goal_date_${rut}`, todayStr);
              }
              localStorage.setItem(`daily_goal_count_${rut}`, (count + 1).toString());
            }
          },
          error: (err) => {
            console.error('Error resolving error:', err);
          },
        });
    } else {
      this.feedback = `Respuesta incorrecta. La respuesta correcta es: ${this.errorActual.pregunta.respuesta_correcta}. ${this.errorActual.pregunta.justificacion_cot}`;
      this.showFeedbackBlock = true;

      this.habilidadesService.fallarError(this.errorActual.id_error).subscribe({
          next: () => console.log('Error fallado registrado'),
          error: (err) => console.error('Error fallando error:', err)
      });
    }
  }

  avanzarSiguiente(): void {
    if (this.isCorrect) {
      this.erroresFrecuentes = this.erroresFrecuentes.filter(
        (e) => e.id_error !== this.errorActual.id_error,
      );
    } else {
      this.erroresFrecuentes = this.erroresFrecuentes.filter(
        (e) => e.id_error !== this.errorActual.id_error,
      );
      this.erroresFrecuentes.push(this.errorActual);
    }

    if (this.erroresFrecuentes.length > 0) {
      this.errorActual = this.erroresFrecuentes[0];
    } else {
      this.errorActual = null;
      this.desafiosService.reportarGymSinErrores();
    }
    this.resetErrorState();
  }

  resetErrorState(): void {
    this.selectedAnswer = '';
    this.evaluationSubmitted = false;
    this.isSubmitLocked = false;
    this.showFeedbackBlock = false;
    this.feedback = '';
  }

  getAlternativesArray(): Array<{ key: string; value: string }> {
    if (!this.errorActual?.pregunta?.alternativas) return [];

    return Object.entries(this.errorActual.pregunta.alternativas)
      .map(([key, value]) => ({
        key,
        value: value as string,
      }))
      .sort((a, b) => a.key.localeCompare(b.key));
  }

  getRadarPoints(): string {
    if (!this.dashboard?.habilidades) return '';

    const center = { x: 100, y: 100 };
    const vertices: { [key: string]: { x: number; y: number } } = {
      Interpretar: { x: 100, y: 30 },
      Vocabulario: { x: 150, y: 55 },
      Tipos_de_Texto: { x: 150, y: 130 },
      Localizar: { x: 100, y: 170 },
      Lectura_Critica: { x: 50, y: 130 },
      Evaluar: { x: 50, y: 55 },
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
      const habilidad = this.dashboard.habilidades.find(
        (h) => h.nombre_habilidad === skill,
      );
      const percent = habilidad ? habilidad.nivel_maestria / 100 : 0;
      const x = center.x + (vertex.x - center.x) * percent;
      const y = center.y + (vertex.y - center.y) * percent;
      points.push(`${x.toFixed(1)},${y.toFixed(1)}`);
    }

    return points.join(' ');
  }

  getSkillDisplayName(name: string): string {
    const map: { [key: string]: string } = {
      'Interpretar': 'Interpretar',
      'Vocabulario': 'Vocabulario',
      'Tipos_de_Texto': 'Tipos de Texto',
      'Localizar': 'Localizar',
      'Lectura_Critica': 'Lectura Crítica',
      'Evaluar': 'Evaluar',
    };
    return map[name] || name.replace(/_/g, ' ');
  }
}
