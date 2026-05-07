import { Component, Input } from '@angular/core';
import { HabilidadData } from '../../models/backend.model';

@Component({
  selector: 'app-radar-chart',
  templateUrl: './radar-chart.component.html',
  styleUrls: ['./radar-chart.component.scss'],
  standalone: false,
})
export class RadarChartComponent {
  @Input() habilidades: HabilidadData[] = [];

  // Definición de colores por región según pediste
  regiones = [
    { color: 'rgba(144, 238, 144, 0.5)', nombre: 'Verde Claro' }, // Interpretar - Vocabulario
    { color: 'rgba(255, 165, 0, 0.5)', nombre: 'Naranja' }, // Vocabulario - Tipos de Texto
    { color: 'rgba(255, 69, 0, 0.5)', nombre: 'Rojo' }, // Tipos de Texto - Localizar
    { color: 'rgba(147, 112, 219, 0.5)', nombre: 'Púrpura' }, // Localizar - Lectura Crítica
    { color: 'rgba(64, 224, 208, 0.5)', nombre: 'Turquesa' }, // Lectura Crítica - Evaluar
    { color: 'rgba(0, 100, 0, 0.5)', nombre: 'Verde Oscuro' }, // Evaluar - Interpretar
  ];

  getRadarPointsArray(): { x: number; y: number }[] {
    if (!this.habilidades || this.habilidades.length === 0) return [];

    const center = { x: 100, y: 100 };
    const vertices = [
      { x: 100, y: 40 },
      { x: 155, y: 70 },
      { x: 155, y: 130 },
      { x: 100, y: 160 },
      { x: 45, y: 130 },
      { x: 45, y: 70 },
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
      const hab = this.habilidades.find((h) => h.nombre_habilidad === skill);
      const percent = hab ? hab.nivel_maestria / 100 : 0;
      return {
        x: center.x + (vertex.x - center.x) * percent,
        y: center.y + (vertex.y - center.y) * percent,
      };
    });
  }

  getRegionPath(index: number): string {
    const points = this.getRadarPointsArray();
    if (points.length < 6) return '';
    const p1 = points[index];
    const p2 = points[(index + 1) % 6];
    return `M 100,100 L ${p1.x},${p1.y} L ${p2.x},${p2.y} Z`;
  }
}
