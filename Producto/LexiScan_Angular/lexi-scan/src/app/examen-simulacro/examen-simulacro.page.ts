import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AlertController } from '@ionic/angular';
import { HabilidadesService } from '../services/habilidades.service';
import { ExamenResponse } from '../models/backend.model';

@Component({
  selector: 'app-examen-simulacro',
  templateUrl: 'examen-simulacro.page.html',
  styleUrls: ['examen-simulacro.page.scss'],
  standalone: false,
})
export class ExamenSimulacroPage implements OnInit {
  examData: ExamenResponse | null = null;
  answers: { [key: number]: string } = {};
  loading = false;

  constructor(
    private router: Router,
    private alertController: AlertController,
    private habilidadesService: HabilidadesService,
  ) {}

  ngOnInit() {
    const navigation = this.router.getCurrentNavigation();
    if (navigation?.extras?.state) {
      this.examData = navigation.extras.state['examData'];
    }
    if (!this.examData) {
      this.router.navigate(['/examen']);
    }
  }

  getAlternativesArray(
    alternativas: any,
  ): Array<{ key: string; value: string }> {
    if (!alternativas) return [];
    return Object.entries(alternativas)
      .map(([key, value]) => ({
        key,
        value: value as string,
      }))
      .sort((a, b) => a.key.localeCompare(b.key));
  }

  async finishExam() {
    const alert = await this.alertController.create({
      header: 'Confirmar',
      message:
        '¿Realmente desea terminar el examen? Esta acción no se puede deshacer.',
      buttons: [
        {
          text: 'Cancelar',
          role: 'cancel',
        },
        {
          text: 'Terminar',
          handler: () => {
            this.submitExam();
          },
        },
      ],
    });
    await alert.present();
  }

  submitExam() {
    if (!this.examData) return;

    this.loading = true;
    const respuestas = this.examData.preguntas.map((pregunta, index) => ({
      id_pregunta: pregunta.id_pregunta,
      respuesta_dada: this.answers[pregunta.id_pregunta] || null,
    }));

    this.habilidadesService
      .evaluarExamen(this.examData.id_examen, respuestas)
      .subscribe({
        next: (result) => {
          this.loading = false;
          this.router.navigate(['/examen-resultados'], {
            state: { examResult: result, examData: this.examData },
          });
        },
        error: (error) => {
          console.error('Error al evaluar examen:', error);
          this.loading = false;
          alert('Error al enviar el examen. Intenta nuevamente.');
        },
      });
  }
}
