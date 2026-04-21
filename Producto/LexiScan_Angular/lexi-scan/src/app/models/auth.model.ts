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

export interface IUserProfile {
  id?: string;
  rut: string;
  nombre: string;
  email: string;
  telefono: string;
  direccion: string;
  ciudad?: string;
  codigoPostal?: string;
  createdAt?: Date;
  updatedAt?: Date;
}

export interface IValidationErrors {
  [key: string]: string | null;
}
