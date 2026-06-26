import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HabilidadesService } from '../services/habilidades.service';
import { ProfileService } from '../services/profile.service';
import { DashboardResponse, HabilidadData } from '../models/backend.model';
import { IUserProfile } from '../models/auth.model';

interface TrendPoint {
  score: number;
  date: string;
}

@Component({
  selector: 'app-stats',
  templateUrl: 'stats.page.html',
  styleUrls: ['stats.page.scss'],
  standalone: false,
})
export class StatsPage implements OnInit {
  dashboard: DashboardResponse | null = null;
  profile: IUserProfile | null = null;
  loading = false;
  erroresFrecuentes: any[] = [];
  trendHistory: TrendPoint[] = [];

  constructor(
    private router: Router,
    private habilidadesService: HabilidadesService,
    private profileService: ProfileService
  ) {}

  ngOnInit() {
    this.profileService.getProfile().subscribe((profile) => {
      this.profile = profile;
      if (profile?.rut) {
        this.loadDashboard(profile.rut);
        this.loadErroresFrecuentes(profile.rut);
        this.loadTrendHistory(profile.rut);
      }
    });
  }

  loadDashboard(rut: string): void {
    this.loading = true;
    this.habilidadesService.getDashboard(rut).subscribe({
      next: (dashboard) => {
        this.dashboard = dashboard;
        this.loading = false;
        this.saveCurrentScoreToHistory(rut);
      },
      error: () => { this.loading = false; },
    });
  }

  loadErroresFrecuentes(rut: string): void {
    this.habilidadesService.getErroresFrecuentes(rut).subscribe({
      next: (errores) => { this.erroresFrecuentes = errores || []; },
      error: () => { this.erroresFrecuentes = []; },
    });
  }

  // ============================================================
  // TREND HISTORY (localStorage)
  // ============================================================
  private loadTrendHistory(rut: string): void {
    const raw = localStorage.getItem(`lexiscan_score_history_${rut}`);
    if (raw) {
      try { this.trendHistory = JSON.parse(raw); }
      catch { this.trendHistory = []; }
    }
  }

  private saveCurrentScoreToHistory(rut: string): void {
    if (!this.dashboard) return;
    const score = this.getEstimatedPAES();
    const today = new Date().toISOString().slice(0, 10);
    const lastEntry = this.trendHistory[this.trendHistory.length - 1];
    if (lastEntry && lastEntry.date === today) {
      lastEntry.score = score;
    } else {
      this.trendHistory.push({ score, date: today });
    }
    if (this.trendHistory.length > 20) {
      this.trendHistory = this.trendHistory.slice(-20);
    }
    localStorage.setItem(`lexiscan_score_history_${rut}`, JSON.stringify(this.trendHistory));
  }

  // ============================================================
  // GAUGE CHART — media luna con arco correcto
  // ============================================================
  getEstimatedPAES(): number {
    if (!this.dashboard?.habilidades || this.dashboard.habilidades.length === 0) return 100;
    const avg = this.dashboard.habilidades.reduce((s, h) => s + h.nivel_maestria, 0) / this.dashboard.habilidades.length;
    return Math.round(100 + (avg / 100) * 900);
  }

  /**
   * Arco de gaugeque va de izquierda (180°) a derecha (0°) pasando por ARRIBA.
   * En SVG: y crece hacia abajo, por eso se niega el seno.
   * sweep-flag=0 → sentido antihorario en SVG = pasar por arriba.
   */
  getGaugeArcPath(): string {
    const score = this.getEstimatedPAES();
    const pct = (score - 100) / 900; // 0→1
    if (pct <= 0) return '';

    const cx = 160, cy = 155, r = 115;
    // Ángulo: va de π (izquierda) bajando hacia 0 (derecha), pasando por π/2 (arriba)
    const startAngle = Math.PI;
    const endAngle   = Math.PI - pct * Math.PI; // π→0 a medida que pct sube

    const x1 = cx + r * Math.cos(startAngle);      // punto de inicio (izquierda)
    const y1 = cy - r * Math.sin(startAngle);       // sin negado por eje Y invertido
    const x2 = cx + r * Math.cos(endAngle);
    const y2 = cy - r * Math.sin(endAngle);

    const largeArc = pct > 0.5 ? 1 : 0;
    // sweep=0 = antihorario en SVG = visualmente pasa por ARRIBA
    return `M ${x1.toFixed(1)} ${y1.toFixed(1)} A ${r} ${r} 0 ${largeArc} 0 ${x2.toFixed(1)} ${y2.toFixed(1)}`;
  }

  getNeedleTransform(): string {
    const score = this.getEstimatedPAES();
    const pct = (score - 100) / 900;
    // Ángulo de la aguja: 180° (izquierda) → 0° (derecha), pasando por arriba
    // En CSS rotate, 0° = derecha, negativo = antihorario
    // Convertimos pct a grados: 0%→-180° / 100%→0° → rotate(-180 + pct*180)
    const deg = -180 + pct * 180;
    return `rotate(${deg.toFixed(1)}, 160, 155)`;
  }

  // ============================================================
  // META STATS
  // ============================================================
  getXPTotal(): number  { return this.dashboard?.xp_total ?? 0; }
  getStreak(): number   { return this.dashboard?.racha_actual ?? 0; }
  getCoins(): number    { return this.dashboard?.saldo_monedas ?? 0; }

  // ============================================================
  // TREND CHART — curva de aprendizaje
  // ============================================================
  // ViewBox del trend: "0 0 340 170", datos entre x=45..325, y=20..150
  private readonly TREND_X_START = 45;
  private readonly TREND_X_END   = 325;
  private readonly TREND_Y_TOP   = 20;   // y para score=1000
  private readonly TREND_Y_BOT   = 148;  // y para score=100

  private scoreToY(score: number): number {
    const pct = (score - 100) / 900;
    return this.TREND_Y_BOT - pct * (this.TREND_Y_BOT - this.TREND_Y_TOP);
  }

  getTrendPoints(): { x: number; y: number }[] {
    const history = this.trendHistory.length > 0 ? this.trendHistory
      : [{ score: this.getEstimatedPAES(), date: 'Hoy' }];

    if (history.length === 1) {
      return [{ x: (this.TREND_X_START + this.TREND_X_END) / 2, y: this.scoreToY(history[0].score) }];
    }
    const step = (this.TREND_X_END - this.TREND_X_START) / (history.length - 1);
    return history.map((pt, i) => ({
      x: this.TREND_X_START + i * step,
      y: this.scoreToY(pt.score),
    }));
  }

  getTrendLinePath(): string {
    const pts = this.getTrendPoints();
    if (pts.length === 0) return '';
    if (pts.length === 1) return `M ${pts[0].x} ${pts[0].y}`;
    let d = `M ${pts[0].x} ${pts[0].y}`;
    for (let i = 1; i < pts.length; i++) {
      const prev = pts[i - 1], curr = pts[i];
      const cpx = (prev.x + curr.x) / 2;
      d += ` C ${cpx} ${prev.y}, ${cpx} ${curr.y}, ${curr.x} ${curr.y}`;
    }
    return d;
  }

  getTrendAreaPath(): string {
    const pts = this.getTrendPoints();
    if (pts.length === 0) return '';
    const line = this.getTrendLinePath();
    const lastX = pts[pts.length - 1].x;
    const firstX = pts[0].x;
    return `${line} L ${lastX} ${this.TREND_Y_BOT} L ${firstX} ${this.TREND_Y_BOT} Z`;
  }

  getGoalLineY(): number { return this.scoreToY(850); }

  /** Posición X del label de meta: a la derecha de donde termina la línea punteada */
  getGoalLabelX(): number { return this.TREND_X_START + 4; }

  getTrendLabels(): { x: number; text: string }[] {
    const history = this.trendHistory.length > 0 ? this.trendHistory
      : [{ score: 0, date: 'Hoy' }];
    if (history.length === 1) {
      return [{ x: (this.TREND_X_START + this.TREND_X_END) / 2, text: 'Hoy' }];
    }
    const step = (this.TREND_X_END - this.TREND_X_START) / (history.length - 1);
    // Solo mostrar hasta 7 etiquetas para no saturar
    const stride = Math.ceil(history.length / 7);
    return history
      .map((pt, i) => ({ x: this.TREND_X_START + i * step, text: pt.date.slice(5) }))
      .filter((_, i) => i % stride === 0 || i === history.length - 1);
  }

  // Etiquetas del eje Y con posiciones calculadas correctamente
  getYAxisLabels(): { y: number; text: string }[] {
    return [
      { y: this.scoreToY(1000), text: '1000' },
      { y: this.scoreToY(750),  text: '750' },
      { y: this.scoreToY(500),  text: '500' },
      { y: this.scoreToY(250),  text: '250' },
    ];
  }

  // Posiciones Y de las gridlines (iguales que las etiquetas)
  getGridLineYs(): number[] {
    return [1000, 750, 500, 250].map(s => this.scoreToY(s));
  }

  // ============================================================
  // SKILL BARS
  // ============================================================
  getSkills(): HabilidadData[] { return this.dashboard?.habilidades || []; }

  getSkillDisplayName(name: string): string {
    const map: { [key: string]: string } = {
      'Interpretar': 'Interpretar', 'Vocabulario': 'Vocabulario',
      'Tipos_de_Texto': 'Tipos de Texto', 'Localizar': 'Localizar',
      'Lectura_Critica': 'Lectura Crítica', 'Evaluar': 'Evaluar',
    };
    return map[name] || name.replace(/_/g, ' ');
  }

  getSkillIcon(name: string): string {
    const map: { [key: string]: string } = {
      'Interpretar': 'reader-outline', 'Vocabulario': 'text-outline',
      'Tipos_de_Texto': 'document-outline', 'Localizar': 'search-outline',
      'Lectura_Critica': 'eye-outline', 'Evaluar': 'checkmark-circle-outline',
    };
    return map[name] || 'help-circle-outline';
  }

  getSkillColor(index: number): string {
    const colors = ['#6366f1','#f97316','#f87171','#38bdf8','#a78bfa','#fbbf24'];
    return colors[index % colors.length];
  }

  // ============================================================
  // ERRORES FRECUENTES — helpers para la vista
  // ============================================================
  /** Extrae el nombre de la habilidad del objeto habilidad del error. */
  getErrorHabilidad(error: any): string {
    if (!error.habilidad) return 'Sin habilidad';
    const nombre = error.habilidad.nombre || error.habilidad.nombre_habilidad || '';
    return this.getSkillDisplayName(nombre);
  }

  /** Extrae el enunciado de la pregunta del error, truncado a 120 chars. */
  getErrorEnunciado(error: any): string {
    const enunciado = error.pregunta?.enunciado || error.enunciado || 'Sin descripción';
    return enunciado.length > 120 ? enunciado.substring(0, 117) + '…' : enunciado;
  }

  /** Nivel de maestría actual de la habilidad relacionada. */
  getErrorNivelMaestria(error: any): number {
    return Math.round(error.habilidad?.nivel_maestria ?? 0);
  }

  // ============================================================
  // NAVIGATION
  // ============================================================
  goToGym(): void { this.router.navigate(['/gym']); }
}
