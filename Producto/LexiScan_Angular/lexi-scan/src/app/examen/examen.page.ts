import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HabilidadesService } from '../services/habilidades.service';
import { ProfileService } from '../services/profile.service';
import { ExamenResponse } from '../models/backend.model';
import { IUserProfile } from '../models/auth.model';

@Component({
  selector: 'app-examen',
  templateUrl: 'examen.page.html',
  styleUrls: ['examen.page.scss'],
  standalone: false,
})
export class ExamenPage implements OnInit {
  questionCount: number = 25;
  estimatedTime: number = 55;
  examResult: ExamenResponse | null = null;
  profile: IUserProfile | null = null;
  loading = false;

  constructor(
    private router: Router,
    private habilidadesService: HabilidadesService,
    private profileService: ProfileService,
  ) {}

  ngOnInit() {
    this.calculateTime();
    this.profileService.getProfile().subscribe(profile => {
      this.profile = profile;
    });
  }

  onQuestionCountChange(event: any): void {
    this.questionCount = parseInt(event.target.value, 10);
    this.calculateTime();
  }

  calculateTime(): void {
    this.estimatedTime = Math.round(this.questionCount * 2.2);
  }

  startExam(): void {
    if (!this.profile?.rut) {
      alert('Debes iniciar sesión antes de comenzar un examen.');
      return;
    }

    this.loading = true;
    this.habilidadesService.crearExamen(this.profile.rut, this.questionCount).subscribe({
      next: response => {
        this.examResult = response;
        this.estimatedTime = response.estimated_time;
        this.loading = false;
      },
      error: error => {
        console.error('Error al crear examen:', error);
        this.loading = false;
        alert('No se pudo iniciar el examen. Intenta nuevamente.');
      }
    });
  }
}
