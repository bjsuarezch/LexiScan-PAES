import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { DashboardResponse, HabilidadDetail, ExamenResponse } from '../models/backend.model';
import { ILogin } from '../models/auth.model';

@Injectable({
  providedIn: 'root',
})
export class HabilidadesService {
  private readonly baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  login(data: Pick<ILogin, 'rut' | 'contrasena'>): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/login`, data);
  }

  register(registro: { rut: string; nombre_completo: string; email: string; contrasena: string }): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/register`, registro);
  }

  getDashboard(rut: string): Observable<DashboardResponse> {
    return this.http.get<DashboardResponse>(`${this.baseUrl}/dashboard/${rut}`);
  }

  getHabilidadDetail(rut: string, habilidad: string): Observable<HabilidadDetail> {
    return this.http.get<HabilidadDetail>(`${this.baseUrl}/habilidades/${encodeURIComponent(habilidad)}?rut=${encodeURIComponent(rut)}`);
  }

  crearExamen(rut: string, cantidad_preguntas: number): Observable<ExamenResponse> {
    return this.http.post<ExamenResponse>(`${this.baseUrl}/examen`, { rut, cantidad_preguntas });
  }
}
