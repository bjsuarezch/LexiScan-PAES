import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
  standalone: false,
})
export class HomePage implements OnInit {
  constructor(private router: Router) {}

  ngOnInit() {}

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
