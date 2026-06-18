import { Component, OnInit } from '@angular/core';
import { ProfileService } from '../services/profile.service';
import { AdminUsuarioItem } from '../models/backend.model';
import { NavController, AlertController } from '@ionic/angular';
import { IUserProfile } from '../models/auth.model';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.page.html',
  styleUrls: ['./admin.page.scss'],
  standalone: false
})
export class AdminPage implements OnInit {
  usuarios: AdminUsuarioItem[] = [];
  usuariosFiltrados: AdminUsuarioItem[] = [];
  adminProfile: IUserProfile | null = null;
  loading = true;
  searchTerm: string = '';

  constructor(
    private profileService: ProfileService,
    private navCtrl: NavController,
    private alertController: AlertController
  ) { }

  ngOnInit() {
    this.profileService.getProfile().subscribe(profile => {
      this.adminProfile = profile;
      if (this.adminProfile?.rut && this.adminProfile.es_admin) {
        this.loadUsers();
      } else {
        // Redirigir si no es admin
        this.navCtrl.navigateRoot('/home');
      }
    });
  }

  loadUsers() {
    this.loading = true;
    if (!this.adminProfile?.rut) return;
    
    this.profileService.getAdminUsuarios(this.adminProfile.rut).subscribe({
      next: (users) => {
        this.usuarios = users;
        this.usuariosFiltrados = users;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error al cargar usuarios:', err);
        this.loading = false;
      }
    });
  }

  getActivosCount(): number {
    return this.usuarios.filter(u => u.activo).length;
  }

  filterUsers(event: any) {
    const term = event.target.value.toLowerCase();
    this.searchTerm = term;
    if (!term) {
      this.usuariosFiltrados = this.usuarios;
      return;
    }
    
    this.usuariosFiltrados = this.usuarios.filter(u => 
      u.nombre_completo.toLowerCase().includes(term) || 
      u.rut.toLowerCase().includes(term) ||
      u.email.toLowerCase().includes(term)
    );
  }

  async toggleStatus(user: AdminUsuarioItem) {
    if (user.rut === this.adminProfile?.rut) {
      const alert = await this.alertController.create({
        header: 'Acción no permitida',
        message: 'No puedes desactivar tu propia cuenta.',
        buttons: ['OK']
      });
      await alert.present();
      return;
    }

    if (!this.adminProfile?.rut) return;

    this.profileService.toggleUserStatus(user.rut, this.adminProfile.rut).subscribe({
      next: () => {
        user.activo = !user.activo;
      },
      error: (err) => {
        console.error('Error:', err);
      }
    });
  }

  async confirmDelete(user: AdminUsuarioItem) {
    if (user.rut === this.adminProfile?.rut) {
      const alert = await this.alertController.create({
        header: 'Acción no permitida',
        message: 'No puedes eliminar tu propia cuenta.',
        buttons: ['OK']
      });
      await alert.present();
      return;
    }

    const alert = await this.alertController.create({
      header: 'Confirmar Eliminación',
      message: `¿Estás seguro que deseas eliminar al usuario ${user.nombre_completo}? Esta acción es irreversible.`,
      buttons: [
        { text: 'Cancelar', role: 'cancel' },
        { 
          text: 'Eliminar', 
          role: 'destructive',
          handler: () => {
            this.deleteUser(user.rut);
          }
        }
      ]
    });
    await alert.present();
  }

  deleteUser(rut: string) {
    if (!this.adminProfile?.rut) return;
    this.profileService.deleteUser(rut, this.adminProfile.rut).subscribe({
      next: () => {
        this.usuarios = this.usuarios.filter(u => u.rut !== rut);
        this.filterUsers({ target: { value: this.searchTerm } });
      },
      error: (err) => console.error('Error al eliminar:', err)
    });
  }
}
