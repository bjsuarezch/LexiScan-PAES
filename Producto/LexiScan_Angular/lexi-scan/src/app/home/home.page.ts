import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HabilidadesService } from '../services/habilidades.service';
import { ProfileService } from '../services/profile.service';
import { DashboardResponse } from '../models/backend.model';
import { IUserProfile } from '../models/auth.model';

@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
  standalone: false,
})
export class HomePage implements OnInit {
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
    // navigateRoot resetea el historial para que no se pueda volver atrás
    // Usamos la ruta vacía porque tus Tabs están definidos en el path: ''
    this.router.navigate(['/']); 
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

  onChallengeClick(): void {
    console.log('Challenge clicked');
  }

  getRadarPoints(): string {
    if (!this.dashboard?.habilidades) return '';

    const center = { x: 100, y: 100 };
    
    // Estos vértices deben ser EXACTAMENTE iguales a los del polígono de fondo del HTML
    const vertices: { [key: string]: { x: number; y: number } } = {
      'Interpretar':     { x: 100, y: 40 },
      'Vocabulario':     { x: 155, y: 70 },
      'Tipos_de_Texto':  { x: 155, y: 130 },
      'Localizar':       { x: 100, y: 160 },
      'Lectura_Critica': { x: 45,  y: 130 },
      'Evaluar':         { x: 45,  y: 70 },
    };

    const order = ['Interpretar', 'Vocabulario', 'Tipos_de_Texto', 'Localizar', 'Lectura_Critica', 'Evaluar'];
    const points: string[] = [];

    for (const skill of order) {
      const vertex = vertices[skill];
      const habilidad = this.dashboard.habilidades.find(h => h.nombre_habilidad === skill);
      
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
}
