import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { Router } from '@angular/router';
import { AlertController } from '@ionic/angular';
import { IRegistro, IUserProfile } from '../models/auth.model';
import { HabilidadesService } from '../services/habilidades.service';
import { ProfileService } from '../services/profile.service';

@Component({
  selector: 'app-tab2',
  templateUrl: 'tab2.page.html',
  styleUrls: ['tab2.page.scss'],
  standalone: false,
})
export class Tab2Page implements OnInit {
  registroForm!: FormGroup;
  submitted = false;
  showPassword = false;
  showConfirmPassword = false;

  // Focus states for input animations
  rutFocused = false;
  nombreFocused = false;
  emailFocused = false;
  passwordFocused = false;
  confirmFocused = false;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private habilidadesService: HabilidadesService,
    private profileService: ProfileService,
    private alertController: AlertController,
  ) {
    this.initializeForm();
  }

  ngOnInit(): void {
    this.initializeForm();
  }

  initializeForm(): void {
    this.registroForm = this.fb.group({
      rut: ['', [Validators.required, this.rutValidator.bind(this)]],
      nombre: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(50)]],
      email: ['', [Validators.required, Validators.email]],
      contrasena: ['', [Validators.required, Validators.minLength(6), this.passwordStrengthValidator]],
      confirmarContrasena: ['', Validators.required]
    }, { 
      validators: this.passwordMatchValidator 
    });
  }

  // Validador personalizado para RUT chileno
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

  // Validador de fortaleza de contraseña
  passwordStrengthValidator(control: AbstractControl): ValidationErrors | null {
    if (!control.value) {
      return null;
    }

    const hasUpperCase = /[A-Z]/.test(control.value);
    const hasLowerCase = /[a-z]/.test(control.value);
    const hasNumeric = /[0-9]/.test(control.value);

    const valid = hasUpperCase && hasLowerCase && hasNumeric;

    return valid ? null : { 'weakPassword': true };
  }

  // Validador para confirmar que las contraseñas coinciden
  passwordMatchValidator(group: AbstractControl): ValidationErrors | null {
    const password = group.get('contrasena');
    const confirmPassword = group.get('confirmarContrasena');

    if (!password || !confirmPassword) {
      return null;
    }

    return password.value === confirmPassword.value ? null : { 'passwordMismatch': true };
  }

  ionViewWillEnter(): void {
    this.resetForm();
  }

  get hasMinLength(): boolean {
    const val = this.registroForm?.get('contrasena')?.value || '';
    return val.length >= 6;
  }

  get hasUpperCase(): boolean {
    const val = this.registroForm?.get('contrasena')?.value || '';
    return /[A-Z]/.test(val);
  }

  get hasLowerCase(): boolean {
    const val = this.registroForm?.get('contrasena')?.value || '';
    return /[a-z]/.test(val);
  }

  get hasNumeric(): boolean {
    const val = this.registroForm?.get('contrasena')?.value || '';
    return /[0-9]/.test(val);
  }

  get confirmPasswordState(): 'empty' | 'matching' | 'mismatch' {
    const password = this.registroForm?.get('contrasena')?.value || '';
    const confirmPassword = this.registroForm?.get('confirmarContrasena')?.value || '';
    if (!confirmPassword) return 'empty';
    return password === confirmPassword ? 'matching' : 'mismatch';
  }

  getErrorMessage(fieldName: string): string {
    const control = this.registroForm.get(fieldName);

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

    if (fieldName === 'contrasena') {
      if (control.errors['minlength']) {
        return 'Mínimo 6 caracteres';
      }
      if (control.errors['weakPassword']) {
        return 'Debe incluir mayúsculas, minúsculas y números';
      }
    }

    if (fieldName === 'confirmarContrasena') {
      if (this.registroForm.errors?.['passwordMismatch']) {
        return 'Las contraseñas no coinciden';
      }
    }

    return 'Campo inválido';
  }

  togglePasswordVisibility(field: string): void {
    if (field === 'password') {
      this.showPassword = !this.showPassword;
    } else if (field === 'confirmPassword') {
      this.showConfirmPassword = !this.showConfirmPassword;
    }
  }

  onSubmit(): void {
    this.submitted = true;

    if (this.registroForm.valid) {
      const registroData: IRegistro = {
        rut: this.registroForm.value.rut,
        nombre: this.registroForm.value.nombre,
        email: this.registroForm.value.email,
        contrasena: this.registroForm.value.contrasena,
        confirmarContrasena: this.registroForm.value.confirmarContrasena
      };
      this.habilidadesService.register({
        rut: registroData.rut,
        nombre_completo: registroData.nombre,
        email: registroData.email,
        contrasena: registroData.contrasena,
      }).subscribe({
        next: async response => {
          const profile: IUserProfile = {
            rut: response.rut,
            nombre: response.nombre_completo,
            email: response.email,
            telefono: '',
            direccion: '',
          };
          this.profileService.saveProfile(profile);

          const alertPopup = await this.alertController.create({
            header: '¡Registro de usuario exitoso!',
            message: 'Tu cuenta ha sido registrada con éxito.',
            buttons: [
              {
                text: 'Aceptar',
                handler: () => {
                  this.router.navigate(['/habilidades'], { queryParams: { firstTime: true } });
                }
              }
            ]
          });
          await alertPopup.present();
        },
        error: error => {
          console.error('Error de registro:', error);
          let detailMsg = error.error?.detail || 'Revisa tus datos';
          if (detailMsg === 'El RUT ya existe') {
            detailMsg = 'Ya se encuentra un usuario registrado con ese RUT.';
          }
          alert('Registro fallido: ' + detailMsg);
        }
      });
    }
  }

  onRutInput(event: any): void {
    let input = event.target.value;
    if (!input) return;
    
    let clean = input.replace(/[^0-9kK]/g, '').toUpperCase();
    if (clean.length > 9) {
      clean = clean.slice(0, 9);
    }
    
    let formatted = clean;
    if (clean.length > 1) {
      const body = clean.slice(0, -1);
      const dv = clean.slice(-1);
      formatted = `${body}-${dv}`;
    }
    
    this.registroForm.get('rut')?.setValue(formatted, { emitEvent: false });
  }

  resetForm(): void {
    this.registroForm.reset();
    this.submitted = false;
  }
}
