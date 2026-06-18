import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AlertController, ViewWillEnter } from '@ionic/angular';
import { HabilidadesService } from '../services/habilidades.service';
import { ProfileService } from '../services/profile.service';
import { DashboardResponse, HabilidadData, Desafio } from '../models/backend.model';
import { IUserProfile } from '../models/auth.model';
import { DesafiosService } from '../services/desafios.service';

@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
  standalone: false,
})
export class HomePage implements OnInit, ViewWillEnter {
  dashboard: DashboardResponse | null = null;
  profile: IUserProfile | null = null;
  loading = false;
  errorFrecuente: any = null;
  habilidades: HabilidadData[] = [];
  desafios: Desafio[] = [];
  saldoMonedas: number = 0;
  dailyGoalClaimed = false;

  constructor(
    private router: Router,
    private habilidadesService: HabilidadesService,
    private profileService: ProfileService,
    private desafiosService: DesafiosService,
    private alertController: AlertController
  ) {}

  ngOnInit() {
    this.profileService.getProfile().subscribe((profile) => {
      this.profile = profile;
      if (profile?.rut) {
        this.loadDashboard(profile.rut);
      }
    });
    this.habilidadesService.dashboard$.subscribe(
      (data: DashboardResponse | null) => {
        if (data) {
          this.habilidades = data.habilidades;
        }
      },
    );
    // Suscripción reactiva al saldo de monedas (fuente única: DB)
    this.habilidadesService.saldoMonedas$.subscribe(saldo => {
      this.saldoMonedas = saldo;
    });
    this.desafiosService.desafiosDiarios$.subscribe(desafios => {
      this.desafios = desafios;
    });
    this.checkDailyGoalClaimed();
  }

  ionViewWillEnter() {
    // Refrescar saldo y estado de meta al volver al home
    this.checkDailyGoalClaimed();
    if (this.profile?.rut) {
      this.loadDashboard(this.profile.rut);
    }
  }

  private checkDailyGoalClaimed() {
    const todayStr = new Date().toDateString();
    this.dailyGoalClaimed = localStorage.getItem('daily_goal_claimed') === todayStr;
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

  getClass(nivel: number): string {
    if (nivel === 100) {
      return 'maestria-full';
    }
    if (nivel >= 50) {
      return 'maestria-media';
    }
    return 'maestria-baja';
  }

  onLogout() {
    this.router.navigate(['/']);
  }

  get firstName(): string {
    if (!this.profile?.nombre) return 'Estudiante';
    return this.profile.nombre.trim().split(/\s+/)[0];
  }

  getDailyGoalPct(): number {
    const todayStr = new Date().toDateString();
    const savedDate = localStorage.getItem('daily_goal_date');
    if (savedDate !== todayStr) {
      localStorage.setItem('daily_goal_date', todayStr);
      localStorage.setItem('daily_goal_count', '0');
      return 0;
    }
    const count = parseInt(localStorage.getItem('daily_goal_count') || '0', 10);
    return Math.min(100, count * 50);
  }

  getStreak(): number {
    return this.dashboard ? this.dashboard.racha_actual : 0;
  }

  getCoins(): number {
    return this.saldoMonedas;
  }

  getDailyGoalHint(): string {
    const pct = this.getDailyGoalPct();
    if (pct >= 100) return '¡Felicidades! Has alcanzado tu meta diaria hoy. 🎉';
    if (pct >= 50) return '¡Vas por la mitad! Completa 1 lección más para cumplir tu meta del día.';
    return 'Comienza a practicar para cumplir tu meta diaria (completa 2 lecciones de habilidades o sesiones de gym para llegar al 100%).';
  }

  onHabilidadesClick(): void {
    this.router.navigate(['/habilidades']);
  }

  onGymClick(): void {
    this.router.navigate(['/gym']);
  }

  onExamenClick(): void {
    this.router.navigate(['/examen']);
  }

  onRankingClick(): void {
    this.router.navigate(['/ranking']);
  }

  onAdminClick(): void {
    this.router.navigate(['/admin']);
  }

  onStatsClick(): void {
    this.router.navigate(['/stats']);
  }

  onChallengeClick(): void {
  }

  reclamarRecompensa(idDesafio: number) {
    const desafio = this.desafios.find(d => d.id === idDesafio);
    if (!desafio || !desafio.completado || desafio.reclamado) return;

    this.desafiosService.reclamarRecompensa(idDesafio);
    // El servicio llama al backend y actualiza el saldoMonedas$ reactivamente
    if (this.profile?.rut) {
      // Refresca el dashboard tras un breve delay para asegurar que el backend ya persistó
      setTimeout(() => this.loadDashboard(this.profile!.rut!), 800);
    }

    this.alertController.create({
      header: '¡Recompensa reclamada!',
      message: `Has ganado ${desafio.recompensa_monedas} monedas. ¡Sigue así!`,
      buttons: ['Genial 🎉']
    }).then(a => a.present());
  }

  async reclamarMetaDiaria() {
    if (this.dailyGoalClaimed || this.getDailyGoalPct() < 100) return;
    if (!this.profile?.rut) return;

    const todayStr = new Date().toDateString();
    localStorage.setItem('daily_goal_claimed', todayStr);
    this.dailyGoalClaimed = true;

    // Acreditar 50 monedas directamente en la DB
    this.habilidadesService.acreditarMonedas(this.profile.rut, 50).subscribe({
      next: (res) => {
        // Actualizar el BehaviorSubject con el nuevo saldo real
        this.habilidadesService.actualizarSaldoMonedas(res.saldo_nuevo);
        // También refrescar el dashboard completo
        this.loadDashboard(this.profile!.rut!);
      },
      error: (err) => {
        console.error('No se pudieron acreditar las monedas de la meta diaria:', err);
      }
    });

    const alerta = await this.alertController.create({
      header: '¡Meta diaria completada!',
      message: 'Has ganado 50 monedas por cumplir tu meta diaria. ¡Vuelve mañana para ganar más!',
      buttons: ['¡Genial! 🎉']
    });
    await alerta.present();
  }

  /** Icono según tipo de desafío */
  getChallengeIcon(tipo: string): string {
    const icons: Record<string, string> = {
      'tiempo_habilidades': 'flash',
      'diversidad_habilidades': 'compass',
      'habilidad_baja': 'trending-up',
      'gym_sin_errores': 'trophy',
      'tiempo_examen': 'document-text',
    };
    return icons[tipo] || 'star';
  }

  /** Porcentaje de progreso del desafío (0-100) */
  getDesafioPct(desafio: Desafio): number {
    return Math.min(100, Math.round((desafio.progreso / desafio.meta) * 100));
  }

  /** Etiqueta de progreso humanizada */
  getDesafioLabel(desafio: Desafio): string {
    if (desafio.completado) return '¡Completado!';
    switch (desafio.tipo) {
      case 'tiempo_habilidades':
        return `${Math.round(desafio.progreso)} / ${desafio.meta} min`;
      case 'tiempo_examen':
        return `${Math.round(desafio.progreso)} / ${desafio.meta} min`;
      case 'diversidad_habilidades':
        return `${desafio.progreso} / ${desafio.meta} habilidades`;
      case 'habilidad_baja':
        return `${desafio.progreso} / ${desafio.meta} veces`;
      case 'gym_sin_errores':
        return desafio.progreso >= 1 ? '¡Completado!' : 'Pendiente';
      default:
        return `${desafio.progreso} / ${desafio.meta}`;
    }
  }

  /** Lista de habilidades practicadas hoy (para el desafío de diversidad) */
  getHabilidadesPracticadas(): string[] {
    const data = localStorage.getItem('lexiscan_desafios_diarios');
    if (!data) return [];
    try {
      const progreso = JSON.parse(data);
      const hoy = new Date().toISOString().split('T')[0];
      if (progreso.fecha !== hoy) return [];
      return (progreso.habilidadesPracticadas || []).map((h: string) =>
        h.replace(/_/g, ' ')
      );
    } catch { return []; }
  }

  // En tu clase del componente
  getRadarPointsArray(): { x: number; y: number }[] {
    if (!this.habilidades || this.habilidades.length === 0) return [];

    const center = { x: 100, y: 100 };
    const vertices = [
      { x: 100, y: 40 }, // Interpretar
      { x: 155, y: 70 }, // Vocabulario
      { x: 155, y: 130 }, // Tipos_de_Texto
      { x: 100, y: 160 }, // Localizar
      { x: 45, y: 130 }, // Lectura_Critica
      { x: 45, y: 70 }, // Evaluar
    ];

    const order = [
      'Interpretar',
      'Vocabulario',
      'Tipos_de_Texto',
      'Localizar',
      'Lectura_Critica',
      'Evaluar',
    ];

    return order.map((skill, i) => {
      const vertex = vertices[i];
      const habilidad = this.habilidades.find(
        (h) => h.nombre_habilidad === skill,
      );
      const percent = habilidad ? habilidad.nivel_maestria / 100 : 0;
      return {
        x: center.x + (vertex.x - center.x) * percent,
        y: center.y + (vertex.y - center.y) * percent,
      };
    });
  }

  getRegionPath(index: number): string {
    const points = this.getRadarPointsArray();
    if (points.length < 6) return '';

    const p1 = points[index];
    const p2 = points[(index + 1) % 6]; // Siguiente punto (con vuelta al inicio)

    // Retorna un path que va: Centro -> Punto 1 -> Punto 2 -> Cerrar (Z)
    return `M 100,100 L ${p1.x},${p1.y} L ${p2.x},${p2.y} Z`;
  }

  getRadarPoints(): string {
    if (!this.dashboard?.habilidades) return '';

    const center = { x: 100, y: 100 };

    // Estos vértices deben ser EXACTAMENTE iguales a los del polígono de fondo del HTML
    const vertices: { [key: string]: { x: number; y: number } } = {
      Interpretar: { x: 100, y: 40 },
      Vocabulario: { x: 155, y: 70 },
      Tipos_de_Texto: { x: 155, y: 130 },
      Localizar: { x: 100, y: 160 },
      Lectura_Critica: { x: 45, y: 130 },
      Evaluar: { x: 45, y: 70 },
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

      // Si no encuentra la habilidad, el punto se queda en el centro (0%)
      const percent = habilidad ? habilidad.nivel_maestria / 100 : 0;

      // Interpolación lineal entre el centro y el vértice
      const x = center.x + (vertex.x - center.x) * percent;
      const y = center.y + (vertex.y - center.y) * percent;

      points.push(`${x.toFixed(1)},${y.toFixed(1)}`);
    }

    // Retorna algo como "100,40 127.5,85 ..."
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
