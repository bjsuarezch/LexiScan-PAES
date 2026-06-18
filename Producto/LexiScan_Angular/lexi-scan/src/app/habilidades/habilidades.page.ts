import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { AlertController, ModalController, IonicSafeString, ViewWillEnter } from '@ionic/angular';
import { ProfileService } from '../services/profile.service';
import { HabilidadesService } from '../services/habilidades.service';
import { ConfigModalComponent } from '../config-modal/config-modal.component';
import {
  DashboardResponse,
  HabilidadData,
  GeneratedHabilidadDetail,
} from '../models/backend.model';
import { IUserProfile } from '../models/auth.model';
import { DesafiosService } from '../services/desafios.service';
import { BehaviorSubject, Observable, interval, Subscription } from 'rxjs';


interface EvaluacionResultado {
  index: number;
  enunciado: string;
  respuesta_usuario: string;
  respuesta_correcta: string;
  correcta: boolean;
  feedback: string;
}

@Component({
  selector: 'app-habilidades',
  templateUrl: 'habilidades.page.html',
  styleUrls: ['habilidades.page.scss'],
  standalone: false,
})
export class HabilidadesPage implements OnInit, OnDestroy, ViewWillEnter {
  habilidades: HabilidadData[] = [];
  selectedHabilidad: GeneratedHabilidadDetail | null = null;
  profile: IUserProfile | null = null;
  selectedAnswers: Record<number, string> = {};
  evaluationResults: EvaluacionResultado[] = [];
  totalCorrect = 0;
  totalQuestions = 0;
  xpGanada = 0;
  submitting = false;
  isSubmitted = false;
  evaluationError: string | null = null;
  textosRestantes: number = 0;
  temaActualId: number | null = null;
  
  private enterTime: number = 0;
  
  // Temporizador de preguntas
  elapsedSeconds: number = 0;
  private timerSubscription: Subscription | null = null;

  constructor(
    private router: Router,
    private profileService: ProfileService,
    private habilidadesService: HabilidadesService,
    private alertController: AlertController,
    private modalController: ModalController,
    private desafiosService: DesafiosService,
    private route: ActivatedRoute,
  ) {}

  ngOnInit() {
    this.enterTime = Date.now();
    this.profileService.getProfile().subscribe((profile) => {
      this.profile = profile;
      if (profile?.rut) {
        this.loadHabilidades(profile.rut);
        this.checkFirstTime();
      }
    });
  }

  /**
   * ionViewWillEnter se ejecuta cada vez que la página aparece en pantalla,
   * incluso cuando Angular reutiliza la instancia (ej: volver desde selección de tema).
   * Refresca el contador de textos y el dashboard sin mostrar alertas.
   */
  ionViewWillEnter() {
    if (this.profile?.rut) {
      this.refreshTextosRestantes();
    } else {
      // Si el perfil aun no cargó, esperar al suscriptor de ngOnInit
      this.profileService.getProfile().subscribe((profile) => {
        if (profile?.rut) {
          this.profile = profile;
          this.refreshTextosRestantes();
        }
      });
    }
  }

  checkFirstTime(): void {
    this.route.queryParams.subscribe(async (params) => {
      if (params['firstTime'] === 'true') {
        const alertPopup = await this.alertController.create({
          header: '¡Veamos cómo son tus habilidades de comprensión lectora!',
          message: 'Elige un tema para ser evaluado:',
          buttons: [
            {
              text: 'Comenzar',
              handler: () => {
                this.router.navigate(['/seleccion-tema']);
              }
            }
          ]
        });
        await alertPopup.present();
      }
    });
  }

  ngOnDestroy() {
    this.stopTimer();
    if (this.enterTime > 0) {
      const timeSpentMinutes = (Date.now() - this.enterTime) / 60000;
      this.desafiosService.reportarTiempoHabilidades(timeSpentMinutes);
    }
  }

  loadHabilidades(rut: string) {
    this.habilidadesService.getDashboard(rut).subscribe({
      next: (data) => {
        this.habilidades = data.habilidades;
        this.textosRestantes = data.textos_restantes ?? 0;
        this.temaActualId = data.tema_actual_id ?? null;
        // El popup de textos agotados NO va aquí — solo se muestra al hacer click en una habilidad.
      },
      error: (error) => {
        console.error('Error al cargar habilidades:', error);
      },
    });
  }

  /** Refresca solo el contador de textos restantes sin mostrar ninguna alerta. */
  private refreshTextosRestantes() {
    if (!this.profile?.rut) return;
    this.habilidadesService.getDashboard(this.profile.rut).subscribe({
      next: (data) => {
        this.textosRestantes = data.textos_restantes ?? 0;
        this.temaActualId = data.tema_actual_id ?? null;
        this.habilidades = data.habilidades;
      },
      error: () => { /* silencioso */ }
    });
  }

  getClass(nivel: number): string {
    if (nivel === 0) return 'maestria-0';
    if (nivel <= 10) return 'maestria-10';
    if (nivel <= 20) return 'maestria-20';
    if (nivel <= 30) return 'maestria-30';
    if (nivel <= 40) return 'maestria-40';
    if (nivel <= 50) return 'maestria-50';
    if (nivel <= 60) return 'maestria-60';
    if (nivel <= 70) return 'maestria-70';
    if (nivel <= 80) return 'maestria-80';
    if (nivel <= 90) return 'maestria-90';
    return 'maestria-100';
  }

  getSkillDisplayName(name: string): string {
    const map: { [key: string]: string } = {
      'Interpretar': 'Interpretar',
      'Vocabulario': 'Vocabulario',
      'Tipos_de_Texto': 'Tipos de Texto',
      'Localizar': 'Localizar',
      'Lectura_Critica': 'Lectura Crítica',
      'Evaluar': 'Evaluar',
    };
    return map[name] || name.replace(/_/g, ' ');
  }

  selectSkill(skill: string): void {
    // --- PROBLEMA 3: El popup de textos agotados SOLO se muestra aquí ---
    if (this.textosRestantes <= 0) {
      this.alertController.create({
        header: '¡Se acabaron tus textos!',
        message: 'Se te han acabado los 3 textos personalizados. Supera los desafíos del día para ganar oportunidades de escoger nuevos temas.',
        buttons: [
          { text: 'Cancelar', role: 'cancel' },
          {
            text: 'Elegir nuevo tema',
            handler: () => this.router.navigate(['/seleccion-tema'])
          }
        ]
      }).then(a => a.present());
      return; // No llamar a la API
    }

    this.selectedHabilidad = null;
    this.selectedAnswers = {};
    this.evaluationResults = [];
    this.totalCorrect = 0;
    this.totalQuestions = 0;
    this.xpGanada = 0;
    this.evaluationError = null;
    this.isSubmitted = false;

    if (!this.profile?.rut) return;

    this.habilidadesService.generarPreguntas(this.profile.rut, skill, null, false).subscribe({
      next: (data) => {
        this.selectedHabilidad = data;
        this.totalQuestions = data.preguntas.length;
        this.startTimer();
        // --- PROBLEMA 1: Refrescar el contador DESPUÉS de generar preguntas ---
        this.refreshTextosRestantes();
      },
      error: (error) => {
        console.error('Error al generar preguntas:', error);
        const detail = error.error?.detail || '';
        if (detail.toLowerCase().includes('groq')) {
          this.handleGroqError();
        } else if (detail.toLowerCase().includes('textos')) {
          // El backend confirmó que no quedan textos: refrescar y mostrar popup
          this.refreshTextosRestantes();
          this.alertController.create({
            header: '¡Se acabaron tus textos!',
            message: detail,
            buttons: [
              { text: 'Cancelar', role: 'cancel' },
              {
                text: 'Elegir nuevo tema',
                handler: () => this.router.navigate(['/seleccion-tema'])
              }
            ]
          }).then(a => a.present());
        } else {
          alert(detail || 'No se pudo generar las preguntas. Inténtalo de nuevo.');
        }
      },
    });
  }

  get minSecondsRequired(): number {
    return this.totalQuestions * 15; // 15 segundos por pregunta
  }

  get isSubmitLocked(): boolean {
    return this.elapsedSeconds < this.minSecondsRequired;
  }

  get submitButtonText(): string {
    if (!this.isSubmitLocked) return 'Enviar Respuestas';
    const remaining = this.minSecondsRequired - this.elapsedSeconds;
    const m = Math.floor(remaining / 60).toString().padStart(2, '0');
    const s = (remaining % 60).toString().padStart(2, '0');
    return `Espera ${m}:${s} para enviar`;
  }

  startTimer() {
    this.stopTimer();
    this.elapsedSeconds = 0;
    this.timerSubscription = interval(1000).subscribe(() => {
      this.elapsedSeconds++;
    });
  }

  stopTimer() {
    if (this.timerSubscription) {
      this.timerSubscription.unsubscribe();
      this.timerSubscription = null;
    }
  }

  canSubmit(): boolean {
    return (
      !this.isSubmitLocked &&
      !this.isSubmitted &&
      Boolean(this.selectedHabilidad) &&
      (this.selectedHabilidad?.preguntas.every(
        (_, index) => !!this.selectedAnswers[index],
      ) ??
        false)
    );
  }

  submitAnswers(): void {
    if (this.isSubmitted || this.isSubmitLocked) return;

    if (!this.selectedHabilidad || !this.profile?.rut) {
      return;
    }

    this.stopTimer();
    this.submitting = true;
    this.evaluationError = null;
    this.evaluationResults = [];

    const payload = {
      rut: this.profile.rut,
      tipo_habilidad: this.selectedHabilidad!.tipo_habilidad,
      preguntas: this.selectedHabilidad!.preguntas.map((pregunta, index) => ({
        id_pregunta: pregunta.id_pregunta,
        enunciado: pregunta.enunciado,
        alternativas: pregunta.alternativas,
        respuesta_usuario: this.selectedAnswers[index] || '',
        respuesta_correcta: pregunta.respuesta_correcta,
        justificacion: pregunta.justificacion_cot,
        texto_inedito:
          pregunta.texto_inedito || this.selectedHabilidad?.texto_inedito,
      })),
      tiempo_segundos: this.elapsedSeconds
    };

    this.habilidadesService.evaluarRespuestas(payload).subscribe({
      next: (result) => {
        this.evaluationResults = result.resultados;
        this.totalCorrect = result.total_correct;
        this.totalQuestions = result.total_preguntas;
        this.xpGanada = result.xp_ganada;
        this.submitting = false;
        this.isSubmitted = true;

        // Refrescar habilidades y contador silenciosamente tras entregar respuestas
        if (this.profile?.rut) {
          this.loadHabilidades(this.profile.rut);
        }

        // Increment daily goal count
        const todayStr = new Date().toDateString();
        const savedDate = localStorage.getItem('daily_goal_date');
        let count = 0;
        if (savedDate === todayStr) {
          count = parseInt(localStorage.getItem('daily_goal_count') || '0', 10);
        } else {
          localStorage.setItem('daily_goal_date', todayStr);
        }
        localStorage.setItem('daily_goal_count', (count + 1).toString());

        // --- Alerta de Rendimiento ---
        if (result.rendimiento_cambio !== undefined) {
           const cambio = result.rendimiento_cambio;
           const isPositive = cambio > 0;
           const isNegative = cambio < 0;
           const prefix = isPositive ? 'Subió' : isNegative ? 'Bajó' : 'Se mantuvo';
           const symbol = isPositive ? '+' : '';
           // We use css styles directly or ion-text-color classes if they exist, but standard CSS works in message.
           const colorHtml = isPositive ? 'color: var(--ion-color-success);' : isNegative ? 'color: var(--ion-color-danger);' : 'color: var(--ion-color-medium);';
           
           this.alertController.create({
             header: 'Rendimiento de Habilidad',
             subHeader: 'Resultados de tu práctica',
             message: new IonicSafeString(`Tu rendimiento en la habilidad ${this.selectedHabilidad?.tipo_habilidad} <strong style="${colorHtml}">${prefix} ${symbol}${cambio.toFixed(2)}%</strong>.`),
             buttons: ['Entendido']
           }).then(alert => alert.present());
        }

        // --- Desafios Report ---
        if (this.selectedHabilidad) {
          const habilidadPracticada = this.selectedHabilidad.tipo_habilidad;
          // Determine if it's the lowest skill
          let esLaMasBaja = false;
          if (this.habilidades && this.habilidades.length > 0) {
            const lowestScore = Math.min(...this.habilidades.map(h => h.nivel_maestria));
            const currentHabilidad = this.habilidades.find(h => h.nombre_habilidad === habilidadPracticada);
            if (currentHabilidad && currentHabilidad.nivel_maestria === lowestScore) {
              esLaMasBaja = true;
            }
          }
          this.desafiosService.reportarHabilidadPracticada(habilidadPracticada, esLaMasBaja);
        }
        // -----------------------
      },
      error: (error) => {
        console.error('Error al evaluar respuestas:', error);
        const detail = error.error?.detail || '';
        if (detail.toLowerCase().includes('groq')) {
          this.handleGroqError();
          this.evaluationError = 'Error en la comunicación con Groq. Configura la API para resolverlo.';
        } else {
          this.evaluationError =
            detail || 'No se pudo evaluar tus respuestas. Intenta de nuevo más tarde.';
        }
        this.submitting = false;
      },
    });
  }

  getRadarPoints(): string {
    if (!this.habilidades) return '';

    const center = { x: 100, y: 100 };
    const vertices: { [key: string]: { x: number; y: number } } = {
      Interpretar: { x: 100, y: 30 },
      Vocabulario: { x: 160, y: 65 },
      Tipos_de_Texto: { x: 160, y: 135 },
      Localizar: { x: 100, y: 170 },
      Lectura_Critica: { x: 40, y: 135 },
      Evaluar: { x: 40, y: 65 },
    };

    const order = [
      'Interpretar',
      'Vocabulario',
      'Tipos_de_Texto',
      'Localizar',
      'Lectura_Critica',
      'Evaluar',
    ];
    const points: string[] = [];

    for (const skill of order) {
      const vertex = vertices[skill];
      const habilidad = this.habilidades.find(
        (h) => h.nombre_habilidad === skill,
      );
      const percent = habilidad ? habilidad.nivel_maestria / 100 : 0;
      const x = center.x + (vertex.x - center.x) * percent;
      const y = center.y + (vertex.y - center.y) * percent;
      points.push(`${x.toFixed(1)},${y.toFixed(1)}`);
    }

    return points.join(' ');
  }

  getTextoBlocks(): any[] {
    if (!this.selectedHabilidad) return [];
    const texto = this.selectedHabilidad.texto_inedito;
    if (typeof texto === 'string') {
      try {
        const parsed = JSON.parse(texto);
        return Array.isArray(parsed) ? parsed : [{ tipo: 'parrafo', contenido: texto }];
      } catch {
        return [{ tipo: 'parrafo', contenido: texto }];
      }
    }
    if (Array.isArray(texto)) {
      return texto;
    }
    return [];
  }

  async handleGroqError() {
    const alert = await this.alertController.create({
      header: 'Error de Comunicación',
      message: 'Error en la comunicación con Groq. ¿Desea ir a la configuración de la IA para resolverlo?',
      buttons: [
        {
          text: 'No',
          role: 'cancel'
        },
        {
          text: 'Sí',
          handler: async () => {
            const modal = await this.modalController.create({
              component: ConfigModalComponent,
              componentProps: {}
            });
            await modal.present();
          }
        }
      ]
    });
    await alert.present();
  }
}
