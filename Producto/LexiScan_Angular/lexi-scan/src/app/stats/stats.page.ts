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

  // Trend data (stored in localStorage)
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
      }
    });
    this.loadTrendHistory();
  }

  loadDashboard(rut: string): void {
    this.loading = true;
    this.habilidadesService.getDashboard(rut).subscribe({
      next: (dashboard) => {
        this.dashboard = dashboard;
        this.loading = false;
        this.saveCurrentScoreToHistory();
      },
      error: () => {
        this.loading = false;
      },
    });
  }

  loadErroresFrecuentes(rut: string): void {
    this.habilidadesService.getErroresFrecuentes(rut).subscribe({
      next: (errores) => {
        this.erroresFrecuentes = errores || [];
      },
      error: () => {
        this.erroresFrecuentes = [];
      },
    });
  }

  // ============================================================
  // TREND HISTORY (localStorage)
  // ============================================================
  private loadTrendHistory(): void {
    const raw = localStorage.getItem('lexiscan_score_history');
    if (raw) {
      try {
        this.trendHistory = JSON.parse(raw);
      } catch {
        this.trendHistory = [];
      }
    }
  }

  private saveCurrentScoreToHistory(): void {
    if (!this.dashboard) return;

    const score = this.getEstimatedPAES();
    const today = new Date().toISOString().slice(0, 10);

    // Avoid duplicate entries on same day
    const lastEntry = this.trendHistory[this.trendHistory.length - 1];
    if (lastEntry && lastEntry.date === today) {
      lastEntry.score = score;
    } else {
      this.trendHistory.push({ score, date: today });
    }

    // Keep last 20 entries max
    if (this.trendHistory.length > 20) {
      this.trendHistory = this.trendHistory.slice(-20);
    }

    localStorage.setItem('lexiscan_score_history', JSON.stringify(this.trendHistory));
  }

  // ============================================================
  // GAUGE CHART
  // ============================================================
  getEstimatedPAES(): number {
    if (!this.dashboard?.habilidades || this.dashboard.habilidades.length === 0) return 100;
    const avg = this.dashboard.habilidades.reduce((s, h) => s + h.nivel_maestria, 0) / this.dashboard.habilidades.length;
    // Map 0-100 mastery → 100-1000 PAES scale
    return Math.round(100 + (avg / 100) * 900);
  }

  getGaugeArcPath(): string {
    const score = this.getEstimatedPAES();
    const pct = (score - 100) / 900; // 0 to 1
    const startAngle = Math.PI; // 180 degrees (left)
    const endAngle = startAngle + pct * Math.PI; // sweep to right

    const cx = 150;
    const cy = 150;
    const r = 120;

    const x1 = cx + r * Math.cos(startAngle);
    const y1 = cy + r * Math.sin(startAngle);
    const x2 = cx + r * Math.cos(endAngle);
    const y2 = cy + r * Math.sin(endAngle);

    const largeArc = pct > 0.5 ? 1 : 0;

    return `M ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2}`;
  }

  getNeedleX(): number {
    const score = this.getEstimatedPAES();
    const pct = (score - 100) / 900;
    const angle = Math.PI + pct * Math.PI;
    return 150 + 100 * Math.cos(angle);
  }

  getNeedleY(): number {
    const score = this.getEstimatedPAES();
    const pct = (score - 100) / 900;
    const angle = Math.PI + pct * Math.PI;
    return 150 + 100 * Math.sin(angle);
  }

  // ============================================================
  // META STATS
  // ============================================================
  getXPTotal(): number {
    return this.dashboard?.xp_total ?? 0;
  }

  getStreak(): number {
    return this.dashboard?.racha_actual ?? 0;
  }

  getCoins(): number {
    return this.dashboard?.saldo_monedas ?? 0;
  }

  // ============================================================
  // TREND CHART
  // ============================================================
  getTrendPoints(): { x: number; y: number }[] {
    if (this.trendHistory.length === 0) {
      // Default: single point at current score
      const score = this.getEstimatedPAES();
      return [{ x: 185, y: this.scoreToY(score) }];
    }

    const minScore = 100;
    const maxScore = 1000;
    const xStart = 50;
    const xEnd = 320;
    const step = this.trendHistory.length > 1
      ? (xEnd - xStart) / (this.trendHistory.length - 1)
      : 0;

    return this.trendHistory.map((pt, i) => ({
      x: xStart + i * step,
      y: this.scoreToY(pt.score),
    }));
  }

  private scoreToY(score: number): number {
    // Map 100-1000 → 150-30 (top to bottom inverted)
    const pct = (score - 100) / 900;
    return 150 - pct * 120;
  }

  getTrendLinePath(): string {
    const pts = this.getTrendPoints();
    if (pts.length === 0) return '';
    if (pts.length === 1) return `M ${pts[0].x} ${pts[0].y}`;

    // Smooth curve using cardinal spline approximation
    let d = `M ${pts[0].x} ${pts[0].y}`;
    for (let i = 1; i < pts.length; i++) {
      const prev = pts[i - 1];
      const curr = pts[i];
      const cpx = (prev.x + curr.x) / 2;
      d += ` C ${cpx} ${prev.y}, ${cpx} ${curr.y}, ${curr.x} ${curr.y}`;
    }
    return d;
  }

  getTrendAreaPath(): string {
    const line = this.getTrendLinePath();
    if (!line) return '';
    const pts = this.getTrendPoints();
    if (pts.length === 0) return '';

    const lastX = pts[pts.length - 1].x;
    const firstX = pts[0].x;
    return `${line} L ${lastX} 150 L ${firstX} 150 Z`;
  }

  getGoalLineY(): number {
    return this.scoreToY(850);
  }

  getTrendLabels(): { x: number; text: string }[] {
    if (this.trendHistory.length === 0) {
      return [{ x: 185, text: 'Hoy' }];
    }

    const xStart = 50;
    const xEnd = 320;
    const step = this.trendHistory.length > 1
      ? (xEnd - xStart) / (this.trendHistory.length - 1)
      : 0;

    return this.trendHistory.map((pt, i) => ({
      x: xStart + i * step,
      text: pt.date.slice(5), // MM-DD
    }));
  }

  // ============================================================
  // SKILL BARS
  // ============================================================
  getSkills(): HabilidadData[] {
    return this.dashboard?.habilidades || [];
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
    return map[name] || name;
  }

  getSkillIcon(name: string): string {
    const map: { [key: string]: string } = {
      'Interpretar': 'reader-outline',
      'Vocabulario': 'text-outline',
      'Tipos_de_Texto': 'document-outline',
      'Localizar': 'search-outline',
      'Lectura_Critica': 'eye-outline',
      'Evaluar': 'checkmark-circle-outline',
    };
    return map[name] || 'help-circle-outline';
  }

  getSkillColor(index: number): string {
    const colors = [
      '#6366f1', // Interpretar — índigo
      '#f97316', // Vocabulario — naranja
      '#f87171', // Tipos de Texto — coral
      '#38bdf8', // Localizar — sky
      '#a78bfa', // Lectura Crítica — violeta
      '#fbbf24', // Evaluar — ámbar
    ];
    return colors[index % colors.length];
  }

  // ============================================================
  // NAVIGATION
  // ============================================================
  goToGym(): void {
    this.router.navigate(['/gym']);
  }
}
