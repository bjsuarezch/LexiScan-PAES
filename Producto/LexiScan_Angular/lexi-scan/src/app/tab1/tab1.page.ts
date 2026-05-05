import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { ILogin, IUserProfile } from '../models/auth.model';
import { HabilidadesService } from '../services/habilidades.service';
import { ProfileService } from '../services/profile.service';

@Component({
  selector: 'app-tab1',
  templateUrl: 'tab1.page.html',
  styleUrls: ['tab1.page.scss'],
  standalone: false,
})
export class Tab1Page implements OnInit {
  loginForm!: FormGroup;
  submitted = false;
  showPassword = false;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private habilidadesService: HabilidadesService,
    private profileService: ProfileService,
  ) {
    this.initializeForm();
  }

  ngOnInit(): void {
    this.initializeForm();
  }

  initializeForm(): void {
    this.loginForm = this.fb.group({
      rut: ['', [Validators.required, this.rutValidator.bind(this)]],
      email: ['', [Validators.required, Validators.email]],
      contrasena: ['', [Validators.required, Validators.minLength(6)]]
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

  getErrorMessage(fieldName: string): string {
    const control = this.loginForm.get(fieldName);

    if (!control || !control.errors || !this.submitted) {
      return '';
    }

    if (control.errors['required']) {
      return `${fieldName} es requerido`;
    }

    if (fieldName === 'rut' && control.errors['rutInvalid']) {
      return 'RUT inválido';
    }

    if (fieldName === 'email' && control.errors['email']) {
      return 'Email inválido';
    }

    if (fieldName === 'contrasena' && control.errors['minlength']) {
      return 'Mínimo 6 caracteres';
    }

    return 'Campo inválido';
  }

  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
  }

  onSubmit(): void {
    this.submitted = true;

    if (this.loginForm.valid) {
      const loginData: ILogin = this.loginForm.value;
      this.habilidadesService.login({ rut: loginData.rut, contrasena: loginData.contrasena }).subscribe({
        next: response => {
          const profile: IUserProfile = {
            rut: response.rut,
            nombre: response.nombre_completo,
            email: response.email,
            telefono: '',
            direccion: '',
          };
          this.profileService.saveProfile(profile);
          this.router.navigate(['/home']);
        },
        error: error => {
          console.error('Error de login:', error);
          alert('Login fallido: ' + (error.error?.detail || 'Revisa tus credenciales'));
        }
      });
    }
  }

  resetForm(): void {
    this.loginForm.reset();
    this.submitted = false;
  }

  goToCreateAccount(): void {
    this.router.navigate(['/tabs/tab2']);
  }
}
