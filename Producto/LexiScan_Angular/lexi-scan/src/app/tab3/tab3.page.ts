import { Component, OnInit, OnDestroy } from '@angular/core';
import { FormBuilder, FormGroup, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { AlertController, ToastController } from '@ionic/angular';
import { ProfileService } from '../services/profile.service';
import { IUserProfile } from '../models/auth.model';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-tab3',
  templateUrl: 'tab3.page.html',
  styleUrls: ['tab3.page.scss'],
  standalone: false,
})
export class Tab3Page implements OnInit, OnDestroy {
  profileForm!: FormGroup;
  submitted = false;
  isEditing = false;
  isLoading = false;
  profileExists = false;
  private destroy$ = new Subject<void>();

  constructor(
    private fb: FormBuilder,
    private profileService: ProfileService,
    private alertController: AlertController,
    private toastController: ToastController
  ) {
    this.initializeForm();
  }

  ngOnInit(): void {
    this.loadProfile();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  initializeForm(): void {
    this.profileForm = this.fb.group({
      rut: ['', [Validators.required, this.rutValidator.bind(this)]],
      nombre: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(50)]],
      email: ['', [Validators.required, Validators.email]],
      telefono: ['', [Validators.required, this.phoneValidator.bind(this)]],
      direccion: ['', [Validators.required, Validators.minLength(5), Validators.maxLength(100)]],
      ciudad: ['', [Validators.minLength(3), Validators.maxLength(50)]],
      codigoPostal: ['', [Validators.pattern(/^\d{1,10}$/)]]
    });
  }

  /**
   * Cargar perfil del servicio
   */
  loadProfile(): void {
    this.isLoading = true;
    this.profileService.profile$
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (profile) => {
          this.profileExists = profile !== null;
          if (profile) {
            this.profileForm.patchValue(profile);
            this.profileForm.markAsPristine();
            this.isEditing = false;
          } else {
            this.profileForm.reset();
            this.isEditing = true;
          }
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error cargando perfil:', error);
          this.isLoading = false;
          this.showToast('Error cargando perfil');
        }
      });
  }

  /**
   * Validador personalizado para RUT chileno
   */
  rutValidator(control: any): { [key: string]: any } | null {
    if (!control.value) {
      return null;
    }

    const rut = control.value.replace(/[^0-9kK]/g, '').toUpperCase();
    
    if (rut.length < 8) {
      return { 'rutInvalid': true };
    }

    const body = rut.slice(0, -1);
    const dv = rut.slice(-1);
    let sum = 0;
    let multiplier = 2;

    for (let i = body.length - 1; i >= 0; i--) {
      sum += parseInt(body[i]) * multiplier;
      multiplier++;
      if (multiplier > 7) {
        multiplier = 2;
      }
    }

    const calculatedDv = (11 - (sum % 11)) % 11;
    const calculatedDvStr = calculatedDv === 10 ? 'K' : calculatedDv.toString();

    return dv === calculatedDvStr ? null : { 'rutInvalid': true };
  }

  /**
   * Validador para teléfono chileno
   */
  phoneValidator(control: any): { [key: string]: any } | null {
    if (!control.value) {
      return null;
    }

    const phone = control.value.replace(/[^0-9]/g, '');
    
    // Teléfono chileno: 9 dígitos o comenzar con +56
    if (phone.length < 9 || phone.length > 12) {
      return { 'phoneInvalid': true };
    }

    return null;
  }

  getErrorMessage(fieldName: string): string {
    const control = this.profileForm.get(fieldName);

    if (!control || !control.errors || !this.submitted) {
      return '';
    }

    if (control.errors['required']) {
      return `${fieldName} es requerido`;
    }

    if (fieldName === 'rut' && control.errors['rutInvalid']) {
      return 'RUT inválido';
    }

    if (fieldName === 'nombre') {
      if (control.errors['minlength']) {
        return 'Mínimo 3 caracteres';
      }
      if (control.errors['maxlength']) {
        return 'Máximo 50 caracteres';
      }
    }

    if (fieldName === 'email' && control.errors['email']) {
      return 'Email inválido';
    }

    if (fieldName === 'telefono' && control.errors['phoneInvalid']) {
      return 'Teléfono inválido (mínimo 9 dígitos)';
    }

    if (fieldName === 'direccion') {
      if (control.errors['minlength']) {
        return 'Mínimo 5 caracteres';
      }
      if (control.errors['maxlength']) {
        return 'Máximo 100 caracteres';
      }
    }

    if (fieldName === 'ciudad') {
      if (control.errors['minlength']) {
        return 'Mínimo 3 caracteres';
      }
      if (control.errors['maxlength']) {
        return 'Máximo 50 caracteres';
      }
    }

    if (fieldName === 'codigoPostal' && control.errors['pattern']) {
      return 'Código postal inválido';
    }

    return 'Campo inválido';
  }

  /**
   * Alternar modo edición
   */
  toggleEdit(): void {
    this.isEditing = !this.isEditing;
    this.submitted = false;

    if (!this.isEditing) {
      this.profileForm.markAsPristine();
    }
  }

  /**
   * Guardar o actualizar perfil
   */
  onSubmit(): void {
    this.submitted = true;

    if (!this.profileForm.valid) {
      this.showToast('Por favor corrija los errores en el formulario');
      return;
    }

    this.isLoading = true;
    const profileData: IUserProfile = this.profileForm.value;

    const operation$ = this.profileExists 
      ? this.profileService.updateProfile(profileData)
      : this.profileService.createProfile(profileData);

    operation$
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (result) => {
          this.isLoading = false;
          this.profileExists = true;
          this.isEditing = false;
          this.submitted = false;
          this.profileForm.markAsPristine();
          
          const message = this.profileExists ? 'Perfil actualizado exitosamente' : 'Perfil creado exitosamente';
          this.showToast(message, 'success');
        },
        error: (error) => {
          this.isLoading = false;
          console.error('Error guardando perfil:', error);
          this.showToast('Error al guardar perfil');
        }
      });
  }

  /**
   * Eliminar perfil
   */
  async deleteProfile(): Promise<void> {
    const alert = await this.alertController.create({
      header: 'Eliminar Perfil',
      message: '¿Está seguro que desea eliminar su perfil? Esta acción no se puede deshacer.',
      buttons: [
        {
          text: 'Cancelar',
          role: 'cancel',
          cssClass: 'secondary'
        },
        {
          text: 'Eliminar',
          role: 'destructive',
          handler: () => {
            this.confirmDelete();
          }
        }
      ]
    });

    await alert.present();
  }

  /**
   * Confirmar eliminación de perfil
   */
  private confirmDelete(): void {
    this.isLoading = true;
    const profile = this.profileForm.value;

    this.profileService.deleteProfile(profile.id)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (result) => {
          this.isLoading = false;
          if (result) {
            this.profileForm.reset();
            this.profileExists = false;
            this.isEditing = true;
            this.submitted = false;
            this.showToast('Perfil eliminado exitosamente', 'success');
          }
        },
        error: (error) => {
          this.isLoading = false;
          console.error('Error eliminando perfil:', error);
          this.showToast('Error al eliminar perfil');
        }
      });
  }

  /**
   * Cancelar edición
   */
  cancelEdit(): void {
    this.submitted = false;
    this.isEditing = false;
    this.profileForm.markAsPristine();
    this.loadProfile();
  }

  /**
   * Resetear formulario
   */
  resetForm(): void {
    this.profileForm.reset();
    this.submitted = false;
  }

  /**
   * Mostrar toast
   */
  private async showToast(message: string, color: string = 'danger'): Promise<void> {
    const toast = await this.toastController.create({
      message,
      duration: 2000,
      position: 'bottom',
      color
    });

    await toast.present();
  }
}
