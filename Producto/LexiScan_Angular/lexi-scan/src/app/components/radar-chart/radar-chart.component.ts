import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { HabilidadData } from '../../models/backend.model';

@Component({
  selector: 'app-radar-chart',
  templateUrl: './radar-chart.component.html',
  styleUrls: ['./radar-chart.component.scss'],
  standalone: false,
})
export class RadarChartComponent implements OnChanges {
  @Input() habilidades: HabilidadData[] = [];
  @Input() oldHabilidades: HabilidadData[] | null = null;
  @Input() animateFeedback: boolean = false;

  public displayHabilidades: HabilidadData[] = [];
  public displayOldHabilidades: HabilidadData[] = [];
  private animationTimeout: any;
  private animationTimeout2: any;

  regiones = [
    { color: 'rgba(119, 157, 79, 0.75)', nombre: 'Verde Claro' },
    { color: 'rgba(201, 144, 48, 0.75)', nombre: 'Naranja' },
    { color: 'rgba(168, 54, 55, 0.75)', nombre: 'Rojo' },
    { color: 'rgba(60, 66, 122, 0.75)', nombre: 'Púrpura' },
    { color: 'rgba(37, 105, 128, 0.75)', nombre: 'Turquesa' },
    { color: 'rgba(63, 116, 101, 0.75)', nombre: 'Verde Oscuro' },
  ];

  ngOnChanges(changes: SimpleChanges) {
    if (this.animateFeedback && this.oldHabilidades && this.oldHabilidades.length > 0) {
      if (changes['habilidades']) {
         this.playAnimation();
      }
    } else {
      this.displayHabilidades = [...this.habilidades];
      this.displayOldHabilidades = [...(this.oldHabilidades || [])];
    }
  }

  playAnimation() {
    if (!this.animateFeedback || !this.oldHabilidades) return;
    
    clearTimeout(this.animationTimeout);
    clearTimeout(this.animationTimeout2);

    // Phase 0: Big bang (start at 0 for all)
    const zeroHabilidades = this.habilidades.map(h => ({ ...h, nivel_maestria: 0 }));
    this.displayOldHabilidades = zeroHabilidades;
    this.displayHabilidades = zeroHabilidades;

    // Phase 1: Expand to old state
    this.animationTimeout = setTimeout(() => {
      this.displayOldHabilidades = [...this.oldHabilidades!];
      this.displayHabilidades = [...this.oldHabilidades!];
      
      // Phase 2: Pause and expand to new state
      this.animationTimeout2 = setTimeout(() => {
        this.displayHabilidades = [...this.habilidades];
      }, 1500); // Wait for the 1.2s animation to finish + 0.3s pause
    }, 50);
  }

  getOldRadarPointsArray(): { x: number; y: number }[] {
    return this.calculatePoints(this.displayOldHabilidades);
  }

  getOldRadarPolygon(): string {
    const points = this.getOldRadarPointsArray();
    if (points.length < 6) return '';
    return points.map(p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ');
  }

  getOldRegionPath(index: number): string {
    const points = this.getOldRadarPointsArray();
    if (points.length < 6) return '';
    const p1 = points[index];
    const p2 = points[(index + 1) % 6];
    return `M 125,100 L ${p1.x},${p1.y} L ${p2.x},${p2.y} Z`;
  }

  getRadarPointsArray(): { x: number; y: number }[] {
    return this.calculatePoints(this.displayHabilidades);
  }

  getRegionPath(index: number): string {
    const points = this.getRadarPointsArray();
    if (points.length < 6) return '';
    const p1 = points[index];
    const p2 = points[(index + 1) % 6];
    return `M 125,100 L ${p1.x},${p1.y} L ${p2.x},${p2.y} Z`;
  }

  private calculatePoints(data: HabilidadData[]): { x: number; y: number }[] {
    if (!data || data.length === 0) return [];

    const center = { x: 125, y: 100 };
    const vertices = [
      { x: 125, y: 40 },
      { x: 180, y: 70 },
      { x: 180, y: 130 },
      { x: 125, y: 160 },
      { x: 70, y: 130 },
      { x: 70, y: 70 },
    ];

    const order = [
      'Interpretar',
      'Vocabulario',
      'Tipos_de_Texto',
      'Localizar',
      'Lectura_Critica',
      'Evaluar',
    ];

    return order.map((skill, i) => {
      const vertex = vertices[i];
      const hab = data.find((h) => h.nombre_habilidad === skill);
      const percent = hab ? hab.nivel_maestria / 100 : 0;
      return {
        x: center.x + (vertex.x - center.x) * percent,
        y: center.y + (vertex.y - center.y) * percent,
      };
    });
  }
}
