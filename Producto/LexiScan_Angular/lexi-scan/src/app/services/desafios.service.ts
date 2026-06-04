import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { Desafio, DesafioProgresoLocal } from '../models/backend.model';
import { HabilidadesService } from './habilidades.service';
import { ProfileService } from './profile.service';

@Injectable({
  providedIn: 'root'
})
export class DesafiosService {
  private readonly STORAGE_KEY = 'lexiscan_desafios_diarios';
  
  private desafiosDiariosSubject = new BehaviorSubject<Desafio[]>([]);
  public desafiosDiarios$ = this.desafiosDiariosSubject.asObservable();

  private desafiosPool: Desafio[] = [
    {
      id: 1,
      titulo: 'Constancia en Habilidades',
      descripcion: 'Usar y trabajar en el módulo habilidades por 15 minutos en total durante el día.',
      recompensa_monedas: 50,
      progreso: 0,
      meta: 15,
      completado: false,
      reclamado: false,
      tipo: 'tiempo_habilidades'
    },
    {
      id: 2,
      titulo: 'Explorador de Habilidades',
      descripcion: 'Trabajar 4 habilidades diferentes durante el día al menos una vez cada una.',
      recompensa_monedas: 60,
      progreso: 0,
      meta: 4,
      completado: false,
      reclamado: false,
      tipo: 'diversidad_habilidades'
    },
    {
      id: 3,
      titulo: 'Superando Debilidades',
      descripcion: 'Trabajar la habilidad con desempeño más bajo al menos 3 veces.',
      recompensa_monedas: 75,
      progreso: 0,
      meta: 3,
      completado: false,
      reclamado: false,
      tipo: 'habilidad_baja'
    },
    {
      id: 4,
      titulo: 'Gym Impecable',
      descripcion: 'Utilizar el módulo gym hasta quedar sin errores pendientes.',
      recompensa_monedas: 100,
      progreso: 0,
      meta: 1, // 1 significa completado cuando se llega a 0 errores
      completado: false,
      reclamado: false,
      tipo: 'gym_sin_errores'
    },
    {
      id: 5,
      titulo: 'Práctica Intensiva',
      descripcion: 'Usar el módulo examen al menos 10 minutos hoy.',
      recompensa_monedas: 80,
      progreso: 0,
      meta: 10,
      completado: false,
      reclamado: false,
      tipo: 'tiempo_examen'
    }
  ];

  constructor(
    private habilidadesService: HabilidadesService,
    private profileService: ProfileService
  ) {
    this.inicializarDesafios();
  }

  private inicializarDesafios() {
    const hoy = new Date().toISOString().split('T')[0];
    const dataGuardada = localStorage.getItem(this.STORAGE_KEY);
    
    if (dataGuardada) {
      const progreso: DesafioProgresoLocal = JSON.parse(dataGuardada);
      if (progreso.fecha === hoy) {
        this.desafiosDiariosSubject.next(progreso.desafiosActivos);
        return;
      }
    }

    // Nuevo día o sin datos, generar nuevos desafíos
    this.generarNuevosDesafios(hoy);
  }

  private generarNuevosDesafios(fecha: string) {
    // Mezclar el array y tomar 3
    const mezclados = [...this.desafiosPool].sort(() => 0.5 - Math.random());
    const seleccionados = mezclados.slice(0, 3).map(d => ({...d})); // Clon profundo
    
    const nuevoProgreso: DesafioProgresoLocal = {
      fecha: fecha,
      desafiosActivos: seleccionados,
      habilidadesPracticadas: [],
      vecesHabilidadBajaPracticada: 0
    };

    this.guardarProgreso(nuevoProgreso);
    this.desafiosDiariosSubject.next(seleccionados);
  }

  private obtenerProgresoActual(): DesafioProgresoLocal | null {
    const data = localStorage.getItem(this.STORAGE_KEY);
    return data ? JSON.parse(data) : null;
  }

  private guardarProgreso(progreso: DesafioProgresoLocal) {
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(progreso));
  }

  private updateDesafio(tipo: string, act: (desafio: Desafio, progresoLocal: DesafioProgresoLocal) => void) {
    const progresoLocal = this.obtenerProgresoActual();
    if (!progresoLocal) return;

    const hoy = new Date().toISOString().split('T')[0];
    if (progresoLocal.fecha !== hoy) {
      this.generarNuevosDesafios(hoy);
      return;
    }

    let cambiado = false;
    progresoLocal.desafiosActivos = progresoLocal.desafiosActivos.map(d => {
      if (d.tipo === tipo && !d.completado) {
        act(d, progresoLocal);
        if (d.progreso >= d.meta) {
          d.progreso = d.meta;
          d.completado = true;
        }
        cambiado = true;
      }
      return d;
    });

    if (cambiado) {
      this.guardarProgreso(progresoLocal);
      this.desafiosDiariosSubject.next(progresoLocal.desafiosActivos);
    }
  }

  // Métodos para reportar progreso desde los componentes

  reportarTiempoHabilidades(minutos: number) {
    this.updateDesafio('tiempo_habilidades', (d) => {
      d.progreso += minutos;
    });
  }

  reportarHabilidadPracticada(habilidad: string, esLaMasBaja: boolean) {
    const progresoLocal = this.obtenerProgresoActual();
    if (!progresoLocal) return;
    const hoy = new Date().toISOString().split('T')[0];
    if (progresoLocal.fecha !== hoy) {
      this.generarNuevosDesafios(hoy);
      return;
    }

    let cambiado = false;

    // Actualizar diversidad
    if (!progresoLocal.habilidadesPracticadas.includes(habilidad)) {
      progresoLocal.habilidadesPracticadas.push(habilidad);
      progresoLocal.desafiosActivos = progresoLocal.desafiosActivos.map(d => {
        if (d.tipo === 'diversidad_habilidades' && !d.completado) {
          d.progreso = progresoLocal.habilidadesPracticadas.length;
          if (d.progreso >= d.meta) d.completado = true;
          cambiado = true;
        }
        return d;
      });
    }

    // Actualizar habilidad baja
    if (esLaMasBaja) {
      progresoLocal.vecesHabilidadBajaPracticada += 1;
      progresoLocal.desafiosActivos = progresoLocal.desafiosActivos.map(d => {
        if (d.tipo === 'habilidad_baja' && !d.completado) {
          d.progreso = progresoLocal.vecesHabilidadBajaPracticada;
          if (d.progreso >= d.meta) d.completado = true;
          cambiado = true;
        }
        return d;
      });
    }

    if (cambiado) {
      this.guardarProgreso(progresoLocal);
      this.desafiosDiariosSubject.next(progresoLocal.desafiosActivos);
    }
  }

  reportarGymSinErrores() {
    this.updateDesafio('gym_sin_errores', (d) => {
      d.progreso = 1;
    });
  }

  reportarTiempoExamen(minutos: number) {
    this.updateDesafio('tiempo_examen', (d) => {
      d.progreso += minutos;
    });
  }

  reclamarRecompensa(idDesafio: number) {
    const progresoLocal = this.obtenerProgresoActual();
    if (!progresoLocal) return;

    let monedasGanadas = 0;

    progresoLocal.desafiosActivos = progresoLocal.desafiosActivos.map(d => {
      if (d.id === idDesafio && d.completado && !d.reclamado) {
        d.reclamado = true;
        monedasGanadas = d.recompensa_monedas;
      }
      return d;
    });

    if (monedasGanadas > 0) {
      this.guardarProgreso(progresoLocal);
      this.desafiosDiariosSubject.next(progresoLocal.desafiosActivos);
      
      // Sumar monedas al saldo local para que la UI lo refleje temporalmente.
      // Ya que el saldo real viene de getDashboard, guardaremos las monedas reclamadas
      // localmente y las sumaremos al saldo mostrado en la app.
      const monedasGuardadas = parseInt(localStorage.getItem('monedas_extra') || '0', 10);
      localStorage.setItem('monedas_extra', (monedasGuardadas + monedasGanadas).toString());
    }
  }
}
