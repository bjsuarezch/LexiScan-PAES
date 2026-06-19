import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';
import {
  DashboardResponse,
  HabilidadDetail,
  ExamenResponse,
  GeneratedHabilidadDetail,
  EvaluarRespuestasResponse,
  ConfiguracionItem,
  ConfiguracionUpdate,
  GroqModelsResponse,
} from '../models/backend.model';
import { ILogin } from '../models/auth.model';

@Injectable({
  providedIn: 'root',
})
export class HabilidadesService {
  private readonly baseUrl = environment.apiUrl;
  private dashboardSubject = new BehaviorSubject<DashboardResponse | null>(
    null,
  );
  dashboard$ = this.dashboardSubject.asObservable();

  /** Fuente única de verdad para el saldo de monedas. Se actualiza tras cada llamada al dashboard. */
  private saldoMonedasSubject = new BehaviorSubject<number>(0);
  saldoMonedas$ = this.saldoMonedasSubject.asObservable();

  constructor(private http: HttpClient) {}

  login(data: Pick<ILogin, 'rut' | 'contrasena'>): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/login`, data);
  }

  register(registro: {
    rut: string;
    nombre_completo: string;
    email: string;
    contrasena: string;
  }): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/register`, registro);
  }

  getDashboard(rut: string): Observable<DashboardResponse> {
    return this.http
      .get<DashboardResponse>(`${this.baseUrl}/dashboard/${rut}`)
      .pipe(tap((data) => {
        this.dashboardSubject.next(data);
        this.saldoMonedasSubject.next(data.saldo_monedas ?? 0);
      }));
  }

  /** Actualiza el saldo de monedas en el BehaviorSubject sin refrescar todo el dashboard. */
  actualizarSaldoMonedas(nuevoSaldo: number): void {
    this.saldoMonedasSubject.next(nuevoSaldo);
  }

  checkBackendHealth(): Observable<{status: string, version: string}> {
    return this.http.get<{status: string, version: string}>(`${this.baseUrl}/health`);
  }

  getHabilidadDetail(
    rut: string,
    habilidad: string,
  ): Observable<HabilidadDetail> {
    return this.http.get<HabilidadDetail>(
      `${this.baseUrl}/habilidades/${encodeURIComponent(habilidad)}?rut=${encodeURIComponent(rut)}`,
    );
  }

  generarPreguntas(rut: string, habilidad: string, tema: string | null = null, es_fijo: boolean = false): Observable<GeneratedHabilidadDetail> {
    return this.http.post<GeneratedHabilidadDetail>(
      `${this.baseUrl}/generar-preguntas`,
      { rut, habilidad, tema, es_fijo },
    );
  }

  getTemas(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/temas`);
  }

  seleccionarTema(rut: string, tema_id: number | null, tema_custom: string | null): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/seleccionar-tema`, {
      rut,
      tema_id,
      tema_custom
    });
  }

  evaluarRespuestas(payload: {
    rut: string;
    tipo_habilidad: string;
    preguntas: Array<{
      id_pregunta: number;
      enunciado: string;
      alternativas: Record<string, string>;
      respuesta_usuario: string;
      respuesta_correcta: string;
      texto_inedito?: string | any[];
      justificacion?: string;
    }>;
    tiempo_segundos?: number;
  }): Observable<EvaluarRespuestasResponse> {
    return this.http.post<EvaluarRespuestasResponse>(
      `${this.baseUrl}/evaluar-preguntas`,
      payload,
    );
  }

  crearExamen(
    rut: string,
    cantidad_preguntas: number,
  ): Observable<ExamenResponse> {
    return this.http.post<ExamenResponse>(`${this.baseUrl}/examen`, {
      rut,
      cantidad_preguntas,
    });
  }

  evaluarExamen(idExamen: number, respuestas: any[], tiempo_segundos?: number): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/evaluar-examen`, {
      id_examen: idExamen,
      respuestas,
      tiempo_segundos
    });
  }

  guardarResultadosExamen(rut: string, idExamen: number): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/guardar-resultados-examen`, {
      rut,
      id_examen: idExamen,
    });
  }

  getErrorFrecuente(rut: string): Observable<any> {
    return this.http.get<any>(
      `${this.baseUrl}/error-frecuente/${encodeURIComponent(rut)}`,
    );
  }

  getErroresFrecuentes(rut: string): Observable<any[]> {
    return this.http.get<any[]>(
      `${this.baseUrl}/errores-frecuentes/${encodeURIComponent(rut)}`,
    );
  }

  resolveError(errorId: number): Observable<any> {
    return this.http.put<any>(
      `${this.baseUrl}/errores-frecuentes/${errorId}/resolver`,
      {},
    );
  }

  getConfiguracion(): Observable<ConfiguracionItem[]> {
    return this.http.get<ConfiguracionItem[]>(`${this.baseUrl}/configuracion`);
  }

  setConfiguracion(config: ConfiguracionUpdate): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/configuracion`, config);
  }

  getGroqModels(): Observable<GroqModelsResponse> {
    return this.http.get<GroqModelsResponse>(`${this.baseUrl}/groq-models`);
  }

  /** Persiste monedas ganadas por desafíos/meta diaria en la DB del usuario. */
  acreditarMonedas(rut: string, cantidad: number): Observable<{ saldo_nuevo: number; cantidad_acreditada: number }> {
    return this.http.post<{ saldo_nuevo: number; cantidad_acreditada: number }>(
      `${this.baseUrl}/acreditar-monedas`,
      { rut, cantidad }
    );
  }
}
