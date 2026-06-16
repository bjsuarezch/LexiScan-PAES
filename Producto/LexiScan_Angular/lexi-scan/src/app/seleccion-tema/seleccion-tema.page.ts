import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HabilidadesService } from '../services/habilidades.service';
import { ProfileService } from '../services/profile.service';
import { IUserProfile } from '../models/auth.model';

@Component({
  selector: 'app-seleccion-tema',
  templateUrl: './seleccion-tema.page.html',
  styleUrls: ['./seleccion-tema.page.scss'],
  standalone: false,
})
export class SeleccionTemaPage implements OnInit {
  temas: any[] = [];
  temaCustom: string = '';
  profile: IUserProfile | null = null;
  saldoMonedas: number = 0;
  temaActualId: number | null = null;
  loading: boolean = false;

  constructor(
    private router: Router,
    private habilidadesService: HabilidadesService,
    private profileService: ProfileService
  ) {}

  ngOnInit() {
    this.cargarDatos();
  }

  cargarDatos() {
    this.profileService.getProfile().subscribe((profile) => {
      this.profile = profile;
      if (this.profile?.rut) {
        this.habilidadesService.getDashboard(this.profile.rut).subscribe(dash => {
          this.saldoMonedas = dash.saldo_monedas;
          this.temaActualId = dash.tema_actual_id ?? null;
        });
      }
    });

    this.habilidadesService.getTemas().subscribe(temas => {
      this.temas = temas.filter((t: any) => !t.es_custom); // Mostrar solo fijos en la piscina principal
    });
  }

  seleccionarTemaFijo(id_tema: number) {
    if (!this.profile?.rut) return;
    this.loading = true;
    this.habilidadesService.seleccionarTema(this.profile.rut, id_tema, null).subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate(['/habilidades']);
      },
      error: (err) => {
        this.loading = false;
        alert(err.error?.detail || 'Error al seleccionar tema');
      }
    });
  }

  seleccionarTemaCustom() {
    if (!this.profile?.rut || !this.temaCustom.trim()) return;
    
    // First custom theme selection is free (temaActualId is null)
    if (this.temaActualId !== null && this.saldoMonedas < 50) {
      alert('No tienes suficientes monedas para un tema personalizado. ¡Completa habilidades para ganar más!');
      return;
    }

    this.loading = true;
    this.habilidadesService.seleccionarTema(this.profile.rut, null, this.temaCustom.trim()).subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate(['/habilidades']);
      },
      error: (err) => {
        this.loading = false;
        alert(err.error?.detail || 'Error al seleccionar tema personalizado');
      }
    });
  }
}
