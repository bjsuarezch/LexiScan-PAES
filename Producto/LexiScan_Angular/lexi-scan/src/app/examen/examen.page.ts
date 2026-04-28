import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-examen',
  templateUrl: 'examen.page.html',
  styleUrls: ['examen.page.scss'],
  standalone: false,
})
export class ExamenPage implements OnInit {
  questionCount: number = 25;
  estimatedTime: number = 55;

  constructor(private router: Router) {}

  ngOnInit() {
    this.calculateTime();
  }

  onQuestionCountChange(event: any): void {
    this.questionCount = parseInt(event.target.value, 10);
    this.calculateTime();
  }

  calculateTime(): void {
    // Aproximadamente 2.2 minutos por pregunta
    this.estimatedTime = Math.round(this.questionCount * 2.2);
  }

  startExam(): void {
    console.log('Starting exam with', this.questionCount, 'questions');
    // Aquí se puede navegar a la página del examen
  }
}
