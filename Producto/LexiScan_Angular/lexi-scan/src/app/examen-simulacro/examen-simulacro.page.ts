import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { AlertController } from '@ionic/angular';
import { HabilidadesService } from '../services/habilidades.service';
import { ExamenResponse } from '../models/backend.model';
import { DesafiosService } from '../services/desafios.service';



@Component({
  selector: 'app-examen-simulacro',
  templateUrl: 'examen-simulacro.page.html',
  styleUrls: ['examen-simulacro.page.scss'],
  standalone: false,
})
export class ExamenSimulacroPage implements OnInit, OnDestroy {
  examData: ExamenResponse | null = null;
  answers: { [key: number]: string } = {};
  loading = false;

  constructor(
    private router: Router,
    private alertController: AlertController,
    private habilidadesService: HabilidadesService,
  ) {}

  private enterTime: number = 0;

  ngOnInit() {
    this.enterTime = Date.now();
    const navigation = this.router.getCurrentNavigation();
    if (navigation?.extras?.state) {
      this.examData = navigation.extras.state['examData'];

      if (this.examData) {
        this.organizeQuestions();
      }
    }
    if (!this.examData) {
      this.router.navigate(['/examen']);
    }
  }

  getAlternativesArray(
    alternativas: any,
  ): Array<{ key: string; value: string }> {
    if (!alternativas) return [];
    return Object.entries(alternativas)
      .map(([key, value]) => ({
        key,
        value: value as string,
      }))
      .sort((a, b) => a.key.localeCompare(b.key));
  }

  async finishExam() {
    const alert = await this.alertController.create({
      header: 'Confirmar',
      message:
        '¿Realmente desea terminar el examen? Esta acción no se puede deshacer.',
      buttons: [
        {
          text: 'Cancelar',
          role: 'cancel',
        },
        {
          text: 'Terminar',
          handler: () => {
            this.submitExam();
          },
        },
      ],
    });
    await alert.present();
  }

  groupedQuestions: any[] = [];

  // Función para organizar preguntas por su texto
  organizeQuestions() {
    const groups: { [key: string]: any } = {};
    let globalCounter = 1;

    this.examData?.preguntas.forEach((pregunta: any) => {
      const texto = pregunta.texto_inedito || 'Sin texto de contexto';

      if (!groups[texto]) {
        groups[texto] = {
          texto: texto,
          preguntas: [],
        };
      }

      // Añadimos un índice global para que las preguntas sigan numeradas del 1 al 20
      groups[texto].preguntas.push({
        ...pregunta,
        globalIndex: globalCounter++,
      });
    });

    this.groupedQuestions = Object.values(groups);
  }

  submitExam() {
    if (!this.examData) return;

    this.loading = true;
    const respuestas = this.examData.preguntas.map((pregunta, index) => ({
      id_pregunta: pregunta.id_pregunta,
      respuesta_dada: this.answers[pregunta.id_pregunta] || null,
    }));

    this.habilidadesService
      .evaluarExamen(this.examData.id_examen, respuestas)
      .subscribe({
        next: (result) => {
          this.loading = false;
          this.router.navigate(['/examen-resultados'], {
            state: { examResult: result, examData: this.examData },
          });
        },
        error: (error) => {
          console.error('Error al evaluar examen:', error);
          this.loading = false;
          alert('Error al enviar el examen. Intenta nuevamente.');
        },
      });
  }

  async downloadPDF() {
    if (!this.examData) return;

    // Importación dinámica para no afectar el bundle inicial
    const { jsPDF } = await import('jspdf');

    const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });

    const pageW = doc.internal.pageSize.getWidth();
    const pageH = doc.internal.pageSize.getHeight();
    const marginL = 18;
    const marginR = 18;
    const marginT = 20;
    const marginB = 20;
    const usableW = pageW - marginL - marginR;

    let y = marginT;

    // ── Utilidades ──────────────────────────────────────────────────────────
    const checkNewPage = (neededHeight: number) => {
      if (y + neededHeight > pageH - marginB) {
        doc.addPage();
        y = marginT;
      }
    };

    const addWrappedText = (
      text: string,
      x: number,
      fontSize: number,
      fontStyle: 'normal' | 'bold',
      color: [number, number, number] = [30, 30, 30],
      lineSpacing = 1.3,
    ): void => {
      doc.setFontSize(fontSize);
      doc.setFont('helvetica', fontStyle);
      doc.setTextColor(...color);
      const lines: string[] = doc.splitTextToSize(text, usableW);
      const lineH = fontSize * 0.3528 * lineSpacing; // pt → mm
      lines.forEach((line: string) => {
        checkNewPage(lineH);
        doc.text(line, x, y);
        y += lineH;
      });
    };

    // ── Encabezado del documento ─────────────────────────────────────────────
    doc.setFillColor(58, 90, 148);
    doc.rect(0, 0, pageW, 14, 'F');
    doc.setFontSize(13);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(255, 255, 255);
    doc.text('LexiScan PAES – Simulacro de Examen', marginL, 9.5);

    y = 22;

    // Título + tiempo
    addWrappedText('Simulacro PAES', marginL, 16, 'bold', [30, 30, 30]);
    y += 1;
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(100, 100, 100);
    doc.text(
      `Tiempo estimado: ${this.examData.estimated_time} min  |  Total preguntas: ${this.examData.preguntas.length}`,
      marginL,
      y,
    );
    y += 4;

    // Línea separadora
    doc.setDrawColor(200, 200, 200);
    doc.line(marginL, y, pageW - marginR, y);
    y += 6;

    // Instrucción
    doc.setFontSize(9);
    doc.setFont('helvetica', 'italic');
    doc.setTextColor(80, 80, 80);
    doc.text(
      'Instrucciones: Lee atentamente cada texto y selecciona la alternativa correcta para cada pregunta.',
      marginL,
      y,
      { maxWidth: usableW },
    );
    y += 8;

    // ── Contenido por grupos ─────────────────────────────────────────────────
    this.groupedQuestions.forEach((grupo, grupoIdx) => {
      // — Texto contextual ——————————————————————————————————
      checkNewPage(20);

      // Fondo de etiqueta
      doc.setFillColor(240, 244, 255);
      doc.roundedRect(marginL, y - 4, usableW, 7, 1.5, 1.5, 'F');
      doc.setFontSize(8);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(58, 90, 148);
      doc.text(`LECTURA CONTEXTUAL ${grupoIdx + 1}`, marginL + 2, y);
      y += 5;

      addWrappedText(grupo.texto, marginL, 10, 'normal', [40, 40, 40], 1.45);
      y += 5;

      // Línea separadora sutil
      doc.setDrawColor(220, 220, 220);
      doc.setLineDashPattern([2, 2], 0);
      doc.line(marginL, y, pageW - marginR, y);
      doc.setLineDashPattern([], 0);
      y += 5;

      // — Preguntas del grupo ——————————————————————————————
      grupo.preguntas.forEach((pregunta: any) => {
        const alts = this.getAlternativesArray(pregunta.alternativas);
        const estimatedLines = Math.ceil(pregunta.enunciado.length / 80) + alts.length * 2 + 6;
        checkNewPage(estimatedLines * 4.5);

        // Número de pregunta
        doc.setFillColor(58, 90, 148);
        doc.circle(marginL + 3.5, y - 1.5, 3.5, 'F');
        doc.setFontSize(8.5);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(255, 255, 255);
        const numStr = String(pregunta.globalIndex);
        doc.text(numStr, marginL + 3.5, y - 0.8, { align: 'center' });

        // Enunciado
        doc.setFontSize(10.5);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(30, 30, 30);
        const enunciadoLines: string[] = doc.splitTextToSize(
          pregunta.enunciado,
          usableW - 10,
        );
        enunciadoLines.forEach((line: string, li: number) => {
          doc.text(line, marginL + 9, y);
          y += li === 0 ? 5 : 4.8;
        });
        y += 2;

        // Alternativas
        alts.forEach((alt) => {
          checkNewPage(8);

          // Círculo para marcar
          doc.setDrawColor(140, 140, 140);
          doc.setFillColor(255, 255, 255);
          doc.circle(marginL + 11, y - 1.5, 2.8, 'FD');

          // Letra
          doc.setFontSize(9.5);
          doc.setFont('helvetica', 'bold');
          doc.setTextColor(58, 90, 148);
          doc.text(alt.key, marginL + 11, y - 0.8, { align: 'center' });

          // Texto alternativa
          doc.setFontSize(10);
          doc.setFont('helvetica', 'normal');
          doc.setTextColor(50, 50, 50);
          const altLines: string[] = doc.splitTextToSize(alt.value, usableW - 20);
          altLines.forEach((line: string) => {
            checkNewPage(5);
            doc.text(line, marginL + 16, y);
            y += 4.8;
          });
          y += 0.5;
        });

        y += 5;
      });
    });

    // ── Footer en cada página ────────────────────────────────────────────────
    const totalPages = (doc.internal as any).getNumberOfPages();
    for (let p = 1; p <= totalPages; p++) {
      doc.setPage(p);
      doc.setFontSize(8);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(150, 150, 150);
      doc.text(
        `LexiScan PAES – Página ${p} de ${totalPages}`,
        pageW / 2,
        pageH - 8,
        { align: 'center' },
      );
    }

    // ── Guardar ──────────────────────────────────────────────────────────────
    doc.save(`LexiScan_Examen_${new Date().toISOString().slice(0, 10)}.pdf`);
  }
}
