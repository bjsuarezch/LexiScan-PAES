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

  // ============================================================
  // RADAR CHART — Professional redesign
  // ============================================================
  readonly skillOrder = [
    'Interpretar', 'Vocabulario', 'Tipos_de_Texto',
    'Localizar', 'Lectura_Critica', 'Evaluar',
  ];

  readonly vertices: { [key: string]: { x: number; y: number } } = {
    Interpretar:      { x: 100, y: 35 },
    Vocabulario:      { x: 155, y: 62 },
    Tipos_de_Texto:   { x: 155, y: 138 },
    Localizar:        { x: 100, y: 165 },
    Lectura_Critica:  { x: 45,  y: 138 },
    Evaluar:          { x: 45,  y: 62 },
  };

  readonly sectorColors = [
    'rgba(99, 102, 241, 0.55)',
    'rgba(249, 115, 22, 0.55)',
    'rgba(239, 68, 68, 0.55)',
    'rgba(14, 165, 233, 0.55)',
    'rgba(168, 85, 247, 0.55)',
    'rgba(234, 179, 8, 0.55)',
  ];

  readonly sectorStrokes = [
    '#6366f1', '#f97316', '#ef4444', '#0ea5e9', '#a855f7', '#eab308',
  ];

  getRadarPointsArray(): { x: number; y: number }[] {
    const center = { x: 100, y: 100 };
    return this.skillOrder.map(skill => {
      const vertex = this.vertices[skill];
      const h = this.dashboard?.habilidades.find(
        hp => hp.nombre_habilidad === skill
      );
      const pct = h ? Math.min(h.nivel_maestria / 100, 1) : 0;
      return {
        x: center.x + (vertex.x - center.x) * pct,
        y: center.y + (vertex.y - center.y) * pct,
      };
    });
  }

  getRegionPath(index: number): string {
    const center = { x: 100, y: 100 };
    const pts = this.getRadarPointsArray();
    const curr = pts[index];
    const next = pts[(index + 1) % 6];
    return `M ${center.x} ${center.y} L ${curr.x.toFixed(1)} ${curr.y.toFixed(1)} L ${next.x.toFixed(1)} ${next.y.toFixed(1)} Z`;
  }

  getGuideHexagonPath(level: number): string {
    const center = { x: 100, y: 100 };
    const maxR = 65;
    const r = maxR * level;
    const points = this.skillOrder.map(skill => {
      const v = this.vertices[skill];
      const dx = v.x - center.x;
      const dy = v.y - center.y;
      const len = Math.sqrt(dx * dx + dy * dy);
      return `${(center.x + dx / len * r).toFixed(1)},${(center.y + dy / len * r).toFixed(1)}`;
    });
    return points.join(' ');
  }

  getErrorCountForSkill(skillName: string): number {
    return this.erroresFrecuentes
      .filter(e => e.habilidad?.nombre === skillName)
      .reduce((sum, e) => sum + (e.veces_fallada || 0), 0);
  }

  hasErrorsForSkill(skillName: string): boolean {
    return this.getErrorCountForSkill(skillName) > 0;
  }

  getRadarPoints(): string {
    return this.getRadarPointsArray()
      .map(p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`)
      .join(' ');
  }
}
