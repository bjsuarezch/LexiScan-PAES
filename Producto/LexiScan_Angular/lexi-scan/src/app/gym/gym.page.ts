import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-gym',
  templateUrl: 'gym.page.html',
  styleUrls: ['gym.page.scss'],
  standalone: false,
})
export class GymPage implements OnInit {
  constructor(private router: Router) {}

  ngOnInit() {}

  startTraining(): void {
    console.log('Starting training');
    // Aquí se puede navegar a una página de entrenamiento
  }
}
