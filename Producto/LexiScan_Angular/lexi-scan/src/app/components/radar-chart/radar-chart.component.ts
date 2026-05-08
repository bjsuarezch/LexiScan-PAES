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
    { color: 'rgba(119, 157, 79, 0.75)', nombre: 'Verde Claro' }, // Interpretar - Vocabulario
    { color: 'rgba(201, 144, 48, 0.75)', nombre: 'Naranja' }, // Vocabulario - Tipos de Texto
    { color: 'rgba(168, 54, 55, 0.75)', nombre: 'Rojo' }, // Tipos de Texto - Localizar
    { color: 'rgba(60, 66, 122, 0.75)', nombre: 'Púrpura' }, // Localizar - Lectura Crítica
    { color: 'rgba(37, 105, 128, 0.75)', nombre: 'Turquesa' }, // Lectura Crítica - Evaluar
    { color: 'rgba(63, 116, 101, 0.75)', nombre: 'Verde Oscuro' }, // Evaluar - Interpretar
  ];

  getRadarPointsArray(): { x: number; y: number }[] {
    if (!this.habilidades || this.habilidades.length === 0) return [];

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
    return `M 125,100 L ${p1.x},${p1.y} L ${p2.x},${p2.y} Z`;
  }
}
