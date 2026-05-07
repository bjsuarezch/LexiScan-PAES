import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HabilidadesService } from '../services/habilidades.service';
import { ProfileService } from '../services/profile.service';
import { DashboardResponse } from '../models/backend.model';
import { IUserProfile } from '../models/auth.model';

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

  constructor(
    private router: Router,
    private habilidadesService: HabilidadesService,
    private profileService: ProfileService,
  ) {}

  ngOnInit() {
    this.profileService.getProfile().subscribe(profile => {
      this.profile = profile;
      if (profile?.rut) {
        this.loadDashboard(profile.rut);
        this.loadErrorFrecuente(profile.rut);
      }
    });
  }

  loadDashboard(rut: string): void {
    this.loading = true;
    this.habilidadesService.getDashboard(rut).subscribe({
      next: dashboard => {
        this.dashboard = dashboard;
        this.loading = false;
      },
      error: error => {
        console.error('Error al cargar dashboard:', error);
        this.loading = false;
      }
    });
  }

  loadErrorFrecuente(rut: string): void {
    this.habilidadesService.getErrorFrecuente(rut).subscribe({
      next: error => {
        this.errorFrecuente = error;
      },
      error: error => {
        console.error('Error al cargar error frecuente:', error);
        this.errorFrecuente = null;
      }
    });
  }

  startTraining(): void {
    console.log('Starting training');
    // Aquí se puede navegar a una página de entrenamiento
  }

  getRadarPoints(): string {
    if (!this.dashboard?.habilidades) return '';

    const center = { x: 100, y: 100 };
    const vertices: { [key: string]: { x: number; y: number } } = {
      'Interpretar': { x: 100, y: 30 },
      'Vocabulario': { x: 150, y: 55 },
      'Tipos_de_Texto': { x: 150, y: 130 },
      'Localizar': { x: 100, y: 170 },
      'Lectura_Critica': { x: 50, y: 130 },
      'Evaluar': { x: 50, y: 55 },
    };

    const order = ['Interpretar', 'Vocabulario', 'Tipos_de_Texto', 'Localizar', 'Lectura_Critica', 'Evaluar'];
    const points: string[] = [];

    for (const skill of order) {
      const vertex = vertices[skill];
      const habilidad = this.dashboard.habilidades.find(h => h.nombre_habilidad === skill);
      const percent = habilidad ? habilidad.nivel_maestria / 100 : 0;
      const x = center.x + (vertex.x - center.x) * percent;
      const y = center.y + (vertex.y - center.y) * percent;
      points.push(`${x.toFixed(1)},${y.toFixed(1)}`);
    }

    return points.join(' ');
  }
}
