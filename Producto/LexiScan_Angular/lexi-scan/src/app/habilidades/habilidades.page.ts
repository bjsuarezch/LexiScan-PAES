import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-habilidades',
  templateUrl: 'habilidades.page.html',
  styleUrls: ['habilidades.page.scss'],
  standalone: false,
})
export class HabilidadesPage implements OnInit {
  constructor(private router: Router) {}

  ngOnInit() {}

  selectSkill(skill: string): void {
    console.log('Skill selected:', skill);
    // Aquí se puede agregar lógica para guardar la habilidad seleccionada
    // y navegar a una página de práctica si es necesario
  }
}
