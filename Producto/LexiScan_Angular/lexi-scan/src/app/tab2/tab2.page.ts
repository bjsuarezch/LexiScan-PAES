import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { IRegistro } from '../models/auth.model';

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

  constructor(private fb: FormBuilder) {
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
      console.log('Datos de registro validados:', registroData);
      // Aquí enviarías los datos al backend
      alert('Registro enviado exitosamente');
      this.resetForm();
    }
  }

  resetForm(): void {
    this.registroForm.reset();
    this.submitted = false;
  }
}
