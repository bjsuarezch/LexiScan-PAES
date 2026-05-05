import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { IUserProfile } from '../models/auth.model';
import { Habilidad } from '../models/habilidad.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ProfileService {
  private readonly STORAGE_KEY = 'user_profile';
  private profileSubject = new BehaviorSubject<IUserProfile | null>(null);
  public profile$ = this.profileSubject.asObservable();

  constructor(private http: HttpClient) {
    this.loadProfile();
  }

  /**
   * Cargar perfil del almacenamiento local
   */
  private loadProfile(): void {
    const profile = this.getProfileFromStorage();
    if (profile) {
      this.profileSubject.next(profile);
    }
  }

  /**
   * Obtener perfil actual
   */
  getProfile(): Observable<IUserProfile | null> {
    return this.profile$;
  }

  /**
   * Obtener perfil del almacenamiento local
   */
  private getProfileFromStorage(): IUserProfile | null {
    const data = localStorage.getItem(this.STORAGE_KEY);
    return data ? JSON.parse(data) : null;
  }

  /**
   * Crear nuevo perfil (CREATE)
   */
  createProfile(profile: IUserProfile): Observable<IUserProfile> {
    const newProfile: IUserProfile = {
      ...profile,
      id: this.generateId(),
      createdAt: new Date(),
      updatedAt: new Date()
    };
    
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(newProfile));
    this.profileSubject.next(newProfile);
    
    return of(newProfile);
  }

  /**
   * Actualizar perfil existente (UPDATE)
   */
  updateProfile(profile: IUserProfile): Observable<IUserProfile> {
    const existingProfile = this.getProfileFromStorage();
    
    if (!existingProfile) {
      throw new Error('Perfil no encontrado');
    }

    const updatedProfile: IUserProfile = {
      ...existingProfile,
      ...profile,
      id: existingProfile.id,
      createdAt: existingProfile.createdAt,
      updatedAt: new Date()
    };

    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(updatedProfile));
    this.profileSubject.next(updatedProfile);
    
    return of(updatedProfile);
  }

  /**
   * Obtener perfil por ID (READ)
   */
  getProfileById(id: string): Observable<IUserProfile | null> {
    const profile = this.getProfileFromStorage();
    return of(profile && profile.id === id ? profile : null);
  }

  /**
   * Guardar perfil recibido desde backend
   */
  saveProfile(profile: IUserProfile): void {
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(profile));
    this.profileSubject.next(profile);
  }

  /**
   * Eliminar perfil (DELETE)
   */
  deleteProfile(id: string): Observable<boolean> {
    const profile = this.getProfileFromStorage();
    
    if (profile && profile.id === id) {
      localStorage.removeItem(this.STORAGE_KEY);
      this.profileSubject.next(null);
      return of(true);
    }
    
    return of(false);
  }

  /**
   * Verificar si existe un perfil
   */
  hasProfile(): boolean {
    return this.getProfileFromStorage() !== null;
  }

  /**
   * Limpiar perfil
   */
  clearProfile(): void {
    localStorage.removeItem(this.STORAGE_KEY);
    this.profileSubject.next(null);
  }

  /**
   * Generar ID único
   */
  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Obtener habilidades del usuario
   */
  getHabilidades(rut: string): Observable<Habilidad[]> {
    return this.http.get<Habilidad[]>(`${environment.apiUrl}/habilidades/${rut}`);
  }
}
