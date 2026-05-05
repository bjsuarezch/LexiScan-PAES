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

  getClass(nivel: number): string {
    if (nivel === 100) {
      return 'maestria-full';
    }
    if (nivel >= 50) {
      return 'maestria-media';
    }
    return 'maestria-baja';
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
}
