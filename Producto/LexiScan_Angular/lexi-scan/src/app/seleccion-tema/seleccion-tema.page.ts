import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AlertController } from '@ionic/angular';
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
    private profileService: ProfileService,
    private alertController: AlertController
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

  async seleccionarTemaCustom() {
    if (!this.profile?.rut || !this.temaCustom.trim()) return;
    
    const esPrimeroGratis = this.temaActualId === null;

    // First custom theme selection is free (temaActualId is null)
    if (!esPrimeroGratis && this.saldoMonedas < 50) {
      const alerta = await this.alertController.create({
        header: 'Monedas insuficientes',
        message: `Necesitas 50 monedas para un tema personalizado. Tienes ${this.saldoMonedas} monedas. ¡Completa desafíos diarios para ganar más!`,
        buttons: [{ text: 'Entendido', role: 'cancel' }]
      });
      await alerta.present();
      return;
    }

    // Popup de confirmación si cuesta monedas
    if (!esPrimeroGratis) {
      const confirmar = await this.alertController.create({
        header: 'Confirmar tema personalizado',
        message: `Se descontarán <strong>50 monedas</strong> de tu saldo (tienes ${this.saldoMonedas}) para usar el tema "<strong>${this.temaCustom.trim()}</strong>". ¿Continuar?`,
        buttons: [
          { text: 'Cancelar', role: 'cancel' },
          {
            text: 'Confirmar (−50 🪙)',
            role: 'confirm',
            handler: () => true
          }
        ]
      });
      await confirmar.present();
      const { role } = await confirmar.onDidDismiss();
      if (role !== 'confirm') return;
    }

    this.loading = true;
    this.habilidadesService.seleccionarTema(this.profile.rut, null, this.temaCustom.trim()).subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate(['/habilidades']);
      },
      error: async (err) => {
        this.loading = false;
        const errAlert = await this.alertController.create({
          header: 'Error',
          message: err.error?.detail || 'Error al seleccionar tema personalizado',
          buttons: ['Aceptar']
        });
        await errAlert.present();
      }
    });
  }
}
