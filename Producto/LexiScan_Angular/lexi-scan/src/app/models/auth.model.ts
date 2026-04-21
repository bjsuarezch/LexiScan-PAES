export interface ILogin {
  rut: string;
  email: string;
  contrasena: string;
}

export interface IRegistro {
  rut: string;
  nombre: string;
  email: string;
  contrasena: string;
  confirmarContrasena: string;
}

export interface IValidationErrors {
  [key: string]: string | null;
}
