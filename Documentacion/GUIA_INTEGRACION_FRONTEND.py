"""
GUÍA DE INTEGRACIÓN FRONTEND: CU10 + CU8

Este archivo contiene ejemplos de cómo el frontend Angular/Ionic debe
integrar los nuevos endpoints en los componentes.
"""

# ============================================================================
# 1. MÓDULO GYM: Mostrar Recomendaciones (CU10)
# ============================================================================

"""
// gym.component.ts

import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-gym',
  templateUrl: './gym.component.html',
  styleUrls: ['./gym.component.scss']
})
export class GymComponent implements OnInit {
  
  recomendaciones: any = null;
  cargando = false;
  error = '';
  
  constructor(private http: HttpClient) {}
  
  ngOnInit() {
    this.cargarRecomendaciones();
  }
  
  cargarRecomendaciones() {
    const rut = localStorage.getItem('rut_usuario'); // O desde auth service
    
    if (!rut) {
      this.error = 'Usuario no autenticado';
      return;
    }
    
    this.cargando = true;
    this.error = '';
    
    // Llamar endpoint CU10
    this.http.get(`/api/usuarios/${rut}/recomendaciones`)
      .subscribe(
        (response: any) => {
          this.recomendaciones = response;
          console.log('Recomendaciones cargadas:', response);
          this.cargando = false;
        },
        (error) => {
          console.error('Error al cargar recomendaciones:', error);
          this.error = 'No se pudieron cargar las recomendaciones';
          this.cargando = false;
        }
      );
  }
  
  practicarHabilidad(habilidad: string) {
    // Navegar al módulo de práctica de esa habilidad
    console.log('Iniciando práctica de:', habilidad);
    // Ejemplo: this.router.navigate(['/practica', { skill: habilidad }]);
  }
}
"""

# Template: gym.component.html
"""
<ion-content class="ion-padding">
  
  <!-- Cargando -->
  <ion-spinner *ngIf="cargando"></ion-spinner>
  
  <!-- Error -->
  <ion-card *ngIf="error" color="danger">
    <ion-card-content>{{ error }}</ion-card-content>
  </ion-card>
  
  <!-- Recomendaciones -->
  <div *ngIf="recomendaciones && !cargando">
    
    <!-- Sugerencia Principal -->
    <ion-card>
      <ion-card-header>
        <ion-card-title>Próxima Práctica Recomendada</ion-card-title>
      </ion-card-header>
      <ion-card-content>
        <p>{{ recomendaciones.proxima_practica_sugerida }}</p>
      </ion-card-content>
    </ion-card>
    
    <!-- Habilidades Débiles -->
    <ion-card>
      <ion-card-header>
        <ion-card-title>Habilidades con Menor Dominio</ion-card-title>
      </ion-card-header>
      <ion-card-content>
        <ion-list>
          <ion-item *ngFor="let hab of recomendaciones.habilidades_debiles">
            <ion-label>
              <h2>{{ hab.nombre }}</h2>
              <p>{{ hab.sugerencia }}</p>
              <!-- Barra de progreso -->
              <ion-progress-bar 
                value="{{ hab.nivel_maestria / 100 }}"
                color="warning">
              </ion-progress-bar>
              <p>{{ hab.nivel_maestria }}%</p>
            </ion-label>
            <ion-button 
              slot="end" 
              (click)="practicarHabilidad(hab.nombre)">
              Practicar
            </ion-button>
          </ion-item>
        </ion-list>
      </ion-card-content>
    </ion-card>
    
    <!-- Errores Frecuentes -->
    <ion-card *ngIf="recomendaciones.errores_frecuentes.length > 0">
      <ion-card-header>
        <ion-card-title>Preguntas Que Falla Frecuentemente</ion-card-title>
      </ion-card-header>
      <ion-card-content>
        <ion-list>
          <ion-item-divider>
            <ion-label>Falló {{ item.veces_fallada }} veces</ion-label>
          </ion-item-divider>
          <ion-item *ngFor="let item of recomendaciones.errores_frecuentes">
            <ion-label>
              <p>{{ item.enunciado | slice:0:80 }}...</p>
              <small>ID Pregunta: {{ item.id_pregunta }}</small>
            </ion-label>
          </ion-item>
        </ion-list>
      </ion-card-content>
    </ion-card>
    
  </div>
  
</ion-content>
"""

# ============================================================================
# 2. COMPONENTE DE PREGUNTA: Bloquear Respuesta por Impulsividad (CU8)
# ============================================================================

"""
// pregunta.component.ts

import { HttpClient } from '@angular/common/http';
import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-pregunta',
  templateUrl: './pregunta.component.html',
  styleUrls: ['./pregunta.component.scss']
})
export class PreguntaComponent implements OnInit {
  
  @Input() idPregunta: number;
  
  umbral: any = null;
  tiempoRestante = 0;
  puedeResponder = false;
  cargando = false;
  error = '';
  respuestaSeleccionada = '';
  
  private timerInterval: any;
  
  constructor(private http: HttpClient) {}
  
  ngOnInit() {
    this.cargarUmbralImpulsividad();
  }
  
  cargarUmbralImpulsividad() {
    this.cargando = true;
    
    // Llamar endpoint CU8
    this.http.get(`/api/preguntas/${this.idPregunta}/umbral-impulsividad`)
      .subscribe(
        (response: any) => {
          this.umbral = response;
          this.tiempoRestante = Math.ceil(response.umbral_segundos);
          this.iniciarContador();
          this.cargando = false;
          console.log('Umbral cargado:', response);
        },
        (error) => {
          console.error('Error al cargar umbral:', error);
          this.error = 'Error al procesar la pregunta';
          this.cargando = false;
          // Fallback: permitir responder después de 5 segundos
          setTimeout(() => {
            this.puedeResponder = true;
          }, 5000);
        }
      );
  }
  
  iniciarContador() {
    this.puedeResponder = false;
    
    // Mostrar el umbral inicial
    console.log(`Espera ${this.tiempoRestante}s antes de responder`);
    
    // Iniciar countdown
    this.timerInterval = setInterval(() => {
      this.tiempoRestante--;
      
      if (this.tiempoRestante <= 0) {
        clearInterval(this.timerInterval);
        this.puedeResponder = true;
        console.log('Ahora puedes responder');
      }
    }, 1000);
  }
  
  enviarRespuesta() {
    if (!this.puedeResponder) {
      alert(`Debes esperar ${this.tiempoRestante} segundos más`);
      return;
    }
    
    if (!this.respuestaSeleccionada) {
      alert('Selecciona una respuesta');
      return;
    }
    
    // Evaluar respuesta (endpoint POST /evaluar-examen u otro)
    console.log('Enviando respuesta:', this.respuestaSeleccionada);
    
    // Limpiar timer
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
    }
  }
  
  ngOnDestroy() {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
    }
  }
}
"""

# Template: pregunta.component.html
"""
<ion-card>
  
  <!-- Encabezado -->
  <ion-card-header>
    <ion-card-title>Pregunta</ion-card-title>
    <ion-card-subtitle *ngIf="umbral">
      {{ umbral.num_palabras }} palabras • Tiempo mínimo de lectura: {{ umbral.umbral_segundos }}s
    </ion-card-subtitle>
  </ion-card-header>
  
  <ion-card-content>
    
    <!-- Mensaje de alerta de impulsividad -->
    <ion-alert 
      *ngIf="umbral && !puedeResponder"
      color="warning"
      [isOpen]="true">
      <ion-icon slot="start" name="timer"></ion-icon>
      <p>{{ umbral.mensaje_usuario }}</p>
      <p><strong>Tiempo restante: {{ tiempoRestante }}s</strong></p>
    </ion-alert>
    
    <!-- Contenido de la pregunta -->
    <div *ngIf="!cargando">
      
      <!-- Texto inédito (si aplica) -->
      <div class="texto-inedito" [ngStyle]="{'opacity': puedeResponder ? 1 : 0.5}">
        <!-- Aquí va el texto a leer -->
        <p>{{ preguntaTexto }}</p>
      </div>
      
      <!-- Enunciado -->
      <h3>{{ enunciado }}</h3>
      
      <!-- Alternativas -->
      <ion-list>
        <ion-radio-group [(ngModel)]="respuestaSeleccionada">
          <ion-item>
            <ion-label>A) {{ alternativaA }}</ion-label>
            <ion-radio slot="start" value="A" [disabled]="!puedeResponder"></ion-radio>
          </ion-item>
          <ion-item>
            <ion-label>B) {{ alternativaB }}</ion-label>
            <ion-radio slot="start" value="B" [disabled]="!puedeResponder"></ion-radio>
          </ion-item>
          <ion-item>
            <ion-label>C) {{ alternativaC }}</ion-label>
            <ion-radio slot="start" value="C" [disabled]="!puedeResponder"></ion-radio>
          </ion-item>
          <ion-item>
            <ion-label>D) {{ alternativaD }}</ion-label>
            <ion-radio slot="start" value="D" [disabled]="!puedeResponder"></ion-radio>
          </ion-item>
        </ion-radio-group>
      </ion-list>
      
      <!-- Botón Responder -->
      <ion-button 
        expand="block" 
        color="primary"
        (click)="enviarRespuesta()"
        [disabled]="!puedeResponder">
        <span *ngIf="puedeResponder">Responder</span>
        <span *ngIf="!puedeResponder">
          Espera {{ tiempoRestante }}s...
        </span>
      </ion-button>
      
    </div>
    
    <!-- Loading -->
    <ion-spinner *ngIf="cargando"></ion-spinner>
    
  </ion-card-content>
  
</ion-card>
"""

# ============================================================================
# 3. SERVICIO CENTRALIZADO (APIService)
# ============================================================================

"""
// api.service.ts

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  
  private baseUrl = 'http://127.0.0.1:8001'; // Ajustar según entorno
  
  constructor(private http: HttpClient) {}
  
  // CU10: Obtener recomendaciones personalizadas
  getRecomendaciones(rut: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/usuarios/${rut}/recomendaciones`);
  }
  
  // CU8: Obtener umbral de impulsividad
  getUmbralImpulsividad(idPregunta: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/preguntas/${idPregunta}/umbral-impulsividad`);
  }
  
}
"""

# Usar en componente:
"""
// Inyectar ApiService
constructor(private api: ApiService) {}

// Llamar métodos
this.api.getRecomendaciones(rut).subscribe(
  (response) => console.log('Recomendaciones:', response),
  (error) => console.error('Error:', error)
);

this.api.getUmbralImpulsividad(idPregunta).subscribe(
  (response) => console.log('Umbral:', response),
  (error) => console.error('Error:', error)
);
"""

# ============================================================================
# 4. EJEMPLO DE FLUJO COMPLETO EN UNA SESIÓN DE EXAMEN
# ============================================================================

"""
FLUJO DE USUARIO:

1. Usuario abre el Módulo GYM
   ↓
2. Frontend llama: GET /usuarios/{rut}/recomendaciones
   ↓
3. Backend retorna:
   {
     "habilidades_debiles": [{"nombre": "Evaluar", "nivel_maestria": 25.5}, ...],
     "errores_frecuentes": [{"id_pregunta": 42, "enunciado": "...", ...}, ...],
     "proxima_practica_sugerida": "Enfócate en 'Evaluar'..."
   }
   ↓
4. UI muestra recomendaciones y botones "Practicar"
   ↓
5. Usuario hace clic en "Practicar Evaluar"
   ↓
6. Se carga una pregunta (id_pregunta = 42, por ej)
   ↓
7. Frontend llama: GET /preguntas/42/umbral-impulsividad
   ↓
8. Backend retorna:
   {
     "id_pregunta": 42,
     "num_palabras": 87,
     "umbral_segundos": 5.8,
     "mensaje_usuario": "Lee detenidamente. Espera 5.8 segundos antes de responder."
   }
   ↓
9. Frontend:
   - Muestra el texto a leer
   - Inicia contador de 5.8 segundos
   - Bloquea botón "Responder" durante el countdown
   - Muestra: "Espera 5.8s..." con contador visual
   ↓
10. Usuario lee el texto (mientras pasa el tiempo)
   ↓
11. Cuando llega a 0 segundos:
    - Botón "Responder" se habilita
    - Se puede seleccionar alternativa
    - Se envía respuesta al backend
   ↓
12. Endpoint POST /evaluar-preguntas procesa respuesta
    ↓
13. Se registra en errores_favoritos si falla
    ↓
14. Siguiente pregunta → volver al paso 7
"""

# ============================================================================
# 5. CONFIGURACIÓN EN environment.ts
# ============================================================================

"""
// environment.ts (desarrollo)
export const environment = {
  production: false,
  apiUrl: 'http://127.0.0.1:8001'
};

// environment.prod.ts (producción)
export const environment = {
  production: true,
  apiUrl: 'https://api.lexiscan.cl'  // O tu dominio
};
"""

# ============================================================================
# 6. CASOS DE ERROR Y MANEJO
# ============================================================================

"""
CASO 1: Usuario no existe
  Request: GET /usuarios/99999999-9/recomendaciones
  Response: 404 {"detail": "Usuario con RUT '99999999-9' no encontrado"}
  Acción Frontend: Mostrar error, pedir que se registre o valide su RUT

CASO 2: Usuario sin errores registrados
  Request: GET /usuarios/12345678-9/recomendaciones
  Response: 200 {
    "habilidades_debiles": [...],
    "errores_frecuentes": [],  ← Vacío
    "proxima_practica_sugerida": "¡Excelente! Has dominado todas las habilidades."
  }
  Acción Frontend: Mostrar mensaje motivacional, sugerir exámenes de simulacro

CASO 3: Pregunta no existe
  Request: GET /preguntas/99999/umbral-impulsividad
  Response: 404 {"detail": "Pregunta con ID 99999 no existe"}
  Acción Frontend: Mostrar error, permitir responder sin umbral

CASO 4: Pregunta inactiva
  Request: GET /preguntas/42/umbral-impulsividad
  Response: 404 {"detail": "Pregunta con ID 42 no está activa"}
  Acción Frontend: Idem caso 3

CASO 5: Error de base de datos
  Request: GET /usuarios/{rut}/recomendaciones
  Response: 500 {"detail": "Error al obtener recomendaciones: ..."}
  Acción Frontend: Mostrar error genérico, sugerir reintentar más tarde
"""

# ============================================================================
# 7. TESTING FRONTEND (ejemplo con Jasmine/Karma)
# ============================================================================

"""
// gym.component.spec.ts

import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { GymComponent } from './gym.component';

describe('GymComponent', () => {
  let component: GymComponent;
  let fixture: ComponentFixture<GymComponent>;
  let httpMock: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [GymComponent],
      imports: [HttpClientTestingModule]
    }).compileComponents();

    fixture = TestBed.createComponent(GymComponent);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
  });

  it('debe cargar recomendaciones correctamente', () => {
    const mockResponse = {
      rut: '12345678-9',
      habilidades_debiles: [
        { nombre: 'Evaluar', nivel_maestria: 25.5, sugerencia: '...' }
      ],
      errores_frecuentes: [],
      proxima_practica_sugerida: '...'
    };

    localStorage.setItem('rut_usuario', '12345678-9');
    component.ngOnInit();

    const req = httpMock.expectOne('/api/usuarios/12345678-9/recomendaciones');
    expect(req.request.method).toBe('GET');
    req.flush(mockResponse);

    expect(component.recomendaciones).toEqual(mockResponse);
    expect(component.cargando).toBeFalse();
  });

  afterEach(() => {
    httpMock.verify();
  });
});
"""
