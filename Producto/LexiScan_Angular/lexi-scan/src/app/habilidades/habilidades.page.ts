import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ProfileService } from '../services/profile.service';
import { HabilidadesService } from '../services/habilidades.service';
import { DashboardResponse, HabilidadData, HabilidadDetail } from '../models/backend.model';
import { IUserProfile } from '../models/auth.model';

@Component({
  selector: 'app-habilidades',
  templateUrl: 'habilidades.page.html',
  styleUrls: ['habilidades.page.scss'],
  standalone: false,
})
export class HabilidadesPage implements OnInit {
  habilidades: HabilidadData[] = [];
  selectedHabilidad: HabilidadDetail | null = null;
  profile: IUserProfile | null = null;

  constructor(
    private router: Router,
    private profileService: ProfileService,
    private habilidadesService: HabilidadesService,
  ) {}

  ngOnInit() {
    this.profileService.getProfile().subscribe(profile => {
      this.profile = profile;
      if (profile?.rut) {
        this.loadHabilidades(profile.rut);
      }
    });
  }

  loadHabilidades(rut: string) {
    this.habilidadesService.getDashboard(rut).subscribe({
      next: data => {
        this.habilidades = data.habilidades;
      },
      error: error => {
        console.error('Error al cargar habilidades:', error);
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

  selectSkill(skill: string): void {
    if (!this.profile?.rut) {
      return;
    }

    this.selectedHabilidad = null;
    this.habilidadesService.getHabilidadDetail(this.profile.rut, skill).subscribe({
      next: data => {
        this.selectedHabilidad = data;
      },
      error: error => {
        console.error('Error al cargar detalle de habilidad:', error);
        alert('No se pudo cargar los detalles de la habilidad.');
      }
    });
  }
}
