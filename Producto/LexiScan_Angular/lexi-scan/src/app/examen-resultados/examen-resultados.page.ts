import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AlertController } from '@ionic/angular';
import { HabilidadesService } from '../services/habilidades.service';
import { ProfileService } from '../services/profile.service';

@Component({
  selector: 'app-examen-resultados',
  templateUrl: 'examen-resultados.page.html',
  styleUrls: ['examen-resultados.page.scss'],
  standalone: false,
})
export class ExamenResultadosPage implements OnInit {
  examResult: any = null;
  examData: any = null;
  profile: any = null;
  loading = false;

  constructor(
    private router: Router,
    private alertController: AlertController,
    private habilidadesService: HabilidadesService,
    private profileService: ProfileService,
  ) {}

  ngOnInit() {
    const navigation = this.router.getCurrentNavigation();
    if (navigation?.extras?.state) {
      this.examResult = navigation.extras.state['examResult'];
      this.examData = navigation.extras.state['examData'];
    }
    if (!this.examResult || !this.examData) {
      this.router.navigate(['/examen']);
    }
    this.profileService.getProfile().subscribe((profile) => {
      this.profile = profile;
    });
  }

  getRadarPoints(): string {
    if (!this.examResult?.rendimiento_habilidades) return '';

    const center = { x: 100, y: 100 };
    const vertices: { [key: string]: { x: number; y: number } } = {
      Interpretar: { x: 100, y: 30 },
      Vocabulario: { x: 150, y: 55 },
      Tipos_de_Texto: { x: 150, y: 130 },
      Localizar: { x: 100, y: 170 },
      Lectura_Critica: { x: 50, y: 130 },
      Evaluar: { x: 50, y: 55 },
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
      const hab = this.examResult.rendimiento_habilidades.find(
        (h: any) => h.nombre_habilidad === skill,
      );
      const percent = hab ? hab.porcentaje / 100 : 0;
      const x = center.x + (vertex.x - center.x) * percent;
      const y = center.y + (vertex.y - center.y) * percent;
      points.push(`${x.toFixed(1)},${y.toFixed(1)}`);
    }

    return points.join(' ');
  }

  async saveResults() {
    if (!this.profile?.rut) return;

    this.loading = true;
    this.habilidadesService
      .guardarResultadosExamen(this.profile.rut, this.examResult.id_examen)
      .subscribe({
        next: () => {
          this.loading = false;
          alert('Resultados guardados exitosamente.');
          this.router.navigate(['/home']);
        },
        error: (error) => {
          console.error('Error guardando resultados:', error);
          this.loading = false;
          alert('Error al guardar resultados.');
        },
      });
  }

  async discardExam() {
    const alert = await this.alertController.create({
      header: 'Descartar Examen',
      message:
        '¿Estás seguro de que quieres descartar este examen? Los resultados no afectarán tu progreso.',
      buttons: [
        {
          text: 'Cancelar',
          role: 'cancel',
        },
        {
          text: 'Descartar',
          handler: () => {
            this.router.navigate(['/home']);
          },
        },
      ],
    });
    await alert.present();
  }

  async downloadResultsPDF() {
    if (!this.examResult) return;

    // Importación dinámica para no afectar el bundle inicial
    const { jsPDF } = await import('jspdf');
    const autoTableModule = await import('jspdf-autotable');
    const autoTable = autoTableModule.default ? autoTableModule.default : (autoTableModule as any);

    const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
    const pageW = doc.internal.pageSize.getWidth();

    // ── Encabezado ───────────────────────────────────────────────────────────
    doc.setFillColor(58, 90, 148);
    doc.rect(0, 0, pageW, 15, 'F');
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(255, 255, 255);
    doc.text('LexiScan PAES - Reporte de Resultados', 15, 10);

    // ── Datos del Estudiante ─────────────────────────────────────────────────
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(30, 30, 30);
    doc.text('Datos del Estudiante', 15, 25);

    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    const nombre = this.profile?.nombre || 'Estudiante';
    const rut = this.profile?.rut || 'No disponible';
    doc.text(`Nombre: ${nombre}`, 15, 32);
    doc.text(`RUT: ${rut}`, 15, 38);

    // ── Resumen de Resultados ────────────────────────────────────────────────
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.text('Resumen del Examen', 15, 50);

    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.text(`Puntaje: ${this.examResult.total_correctas} / ${this.examResult.total_preguntas}`, 15, 57);
    doc.text(`Porcentaje de logro: ${this.examResult.porcentaje}%`, 15, 63);

    // ── Tabla de Habilidades ─────────────────────────────────────────────────
    if (this.examResult.rendimiento_habilidades && this.examResult.rendimiento_habilidades.length > 0) {
      const tableData = this.examResult.rendimiento_habilidades.map((hab: any) => [
        hab.nombre_habilidad,
        `${hab.correctas} / ${hab.total}`,
        `${hab.porcentaje}%`
      ]);

      autoTable(doc, {
        startY: 75,
        head: [['Habilidad', 'Puntaje', 'Porcentaje']],
        body: tableData,
        theme: 'striped',
        headStyles: { fillColor: [58, 90, 148] },
        styles: { font: 'helvetica', fontSize: 10 }
      });
    }

    doc.save(`LexiScan_Resultados_${new Date().toISOString().slice(0, 10)}.pdf`);
  }
}
