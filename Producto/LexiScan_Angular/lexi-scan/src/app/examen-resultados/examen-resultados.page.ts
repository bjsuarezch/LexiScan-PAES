import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AlertController, IonicSafeString } from '@ionic/angular';
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

  // ============================================================
  // RADAR CHART
  // ============================================================
  getRadarPoints(): string {
    if (!this.examResult?.rendimiento_habilidades) return '';

    const center = { x: 100, y: 100 };
    const vertices: { [key: string]: { x: number; y: number } } = {
      Interpretar:     { x: 100, y: 30 },
      Vocabulario:     { x: 150, y: 55 },
      Tipos_de_Texto:  { x: 150, y: 130 },
      Localizar:       { x: 100, y: 170 },
      Lectura_Critica: { x: 50,  y: 130 },
      Evaluar:         { x: 50,  y: 55 },
    };

    const order = ['Interpretar','Vocabulario','Tipos_de_Texto','Localizar','Lectura_Critica','Evaluar'];
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

  getRadarPointsArray(): { x: number; y: number }[] {
    if (!this.examResult?.rendimiento_habilidades) return [];

    const center = { x: 100, y: 100 };
    const vertices: { [key: string]: { x: number; y: number } } = {
      Interpretar:     { x: 100, y: 30 },
      Vocabulario:     { x: 150, y: 55 },
      Tipos_de_Texto:  { x: 150, y: 130 },
      Localizar:       { x: 100, y: 170 },
      Lectura_Critica: { x: 50,  y: 130 },
      Evaluar:         { x: 50,  y: 55 },
    };

    const order = ['Interpretar','Vocabulario','Tipos_de_Texto','Localizar','Lectura_Critica','Evaluar'];
    const points: { x: number; y: number }[] = [];

    for (const skill of order) {
      const vertex = vertices[skill];
      const hab = this.examResult.rendimiento_habilidades.find(
        (h: any) => h.nombre_habilidad === skill,
      );
      const percent = hab ? hab.porcentaje / 100 : 0;
      const x = center.x + (vertex.x - center.x) * percent;
      const y = center.y + (vertex.y - center.y) * percent;
      points.push({ x, y });
    }
    return points;
  }

  // ============================================================
  // SAVE RESULTS — con popup de cambios por habilidad
  // ============================================================
  async saveResults() {
    if (!this.profile?.rut) return;

    this.loading = true;
    this.habilidadesService
      .guardarResultadosExamen(this.profile.rut, this.examResult.id_examen)
      .subscribe({
        next: async (res: any) => {
          this.loading = false;

          // Construir mensaje HTML con cambios por habilidad
          const cambios: any[] = res.cambios_habilidades ?? [];

          let msgHtml = '';
          if (cambios.length === 0) {
            msgHtml = '<p>No hubo cambios en el nivel de maestría.</p>';
          } else {
            msgHtml = '<div style="font-size:13px;line-height:1.6">';
            for (const c of cambios) {
              const nombre = this.getSkillDisplayName(c.nombre_habilidad);
              const flecha = c.cambio > 0 ? '▲' : c.cambio < 0 ? '▼' : '—';
              const color  = c.cambio > 0 ? '#22c55e' : c.cambio < 0 ? '#ef4444' : '#94a3b8';
              const signo  = c.cambio > 0 ? '+' : '';
              msgHtml += `
                <div style="display:flex;justify-content:space-between;
                            border-bottom:1px solid #e2e8f0;padding:4px 0;">
                  <span style="font-weight:600">${nombre}</span>
                  <span style="color:${color};font-weight:700">
                    ${c.nivel_antes}% → ${c.nivel_despues}%
                    &nbsp;(${flecha} ${signo}${c.cambio}%)
                  </span>
                </div>`;
            }
            msgHtml += '</div>';
          }

          const popup = await this.alertController.create({
            header: '📊 Progreso actualizado',
            subHeader: 'Cambios en nivel de maestría',
            message: new IonicSafeString(msgHtml),
            buttons: [{
              text: 'Ir al inicio',
              handler: () => {
                // Refrescar dashboard para que saldoMonedas$ se actualice
                if (this.profile?.rut) {
                  this.habilidadesService.getDashboard(this.profile.rut).subscribe();
                }
                this.router.navigate(['/home']);
              }
            }],
            cssClass: 'skill-progress-alert'
          });
          await popup.present();
        },
        error: (error: any) => {
          console.error('Error guardando resultados:', error);
          this.loading = false;
          this.alertController.create({
            header: 'Error',
            message: 'No se pudieron guardar los resultados. Inténtalo de nuevo.',
            buttons: ['Aceptar']
          }).then(a => a.present());
        },
      });
  }

  // ============================================================
  // DISCARD
  // ============================================================
  async discardExam() {
    const alert = await this.alertController.create({
      header: 'Descartar Examen',
      message: '¿Estás seguro de que quieres descartar este examen? Los resultados no afectarán tu progreso.',
      buttons: [
        { text: 'Cancelar', role: 'cancel' },
        { text: 'Descartar', handler: () => { this.router.navigate(['/home']); } },
      ],
    });
    await alert.present();
  }

  // ============================================================
  // HELPERS
  // ============================================================
  getSkillDisplayName(name: string): string {
    const map: { [key: string]: string } = {
      'Interpretar':     'Interpretar',
      'Vocabulario':     'Vocabulario',
      'Tipos_de_Texto':  'Tipos de Texto',
      'Localizar':       'Localizar',
      'Lectura_Critica': 'Lectura Crítica',
      'Evaluar':         'Evaluar',
    };
    return map[name] || name.replace(/_/g, ' ');
  }

  /** Extrae texto plano desde texto_inedito (string o array de bloques JSON). */
  extractTextoPlano(textoInedito: any): string {
    if (!textoInedito) return 'Sin texto de contexto';
    if (typeof textoInedito === 'string') {
      try {
        const parsed = JSON.parse(textoInedito);
        if (Array.isArray(parsed)) return this.extractTextoPlano(parsed);
      } catch { /* string puro */ }
      return textoInedito;
    }
    if (Array.isArray(textoInedito)) {
      return textoInedito
        .filter((b: any) => b.tipo === 'parrafo' || b.tipo === 'dato_clave')
        .map((b: any) => b.contenido || '')
        .join('\n\n');
    }
    return String(textoInedito);
  }

  /** Agrupa las preguntas del examen por texto contextual único (igual que simulacro). */
  private buildGroupedForPDF(): any[] {
    if (!this.examData?.preguntas) return [];
    const groups: { [key: string]: any } = {};
    let globalCounter = 1;

    this.examData.preguntas.forEach((pregunta: any) => {
      const textoPlano = this.extractTextoPlano(pregunta.texto_inedito);
      const textoKey = textoPlano.substring(0, 120);

      if (!groups[textoKey]) {
        groups[textoKey] = { textoPlano, preguntas: [] };
      }
      groups[textoKey].preguntas.push({ ...pregunta, globalIndex: globalCounter++ });
    });

    return Object.values(groups);
  }

  private getAlternativesArray(alternativas: any): Array<{ key: string; value: string }> {
    if (!alternativas) return [];
    return Object.entries(alternativas)
      .map(([key, value]) => ({ key, value: value as string }))
      .sort((a, b) => a.key.localeCompare(b.key));
  }

  // ============================================================
  // PDF — Examen completo + Informe de resultados
  // ============================================================
  async downloadResultsPDF() {
    if (!this.examResult || !this.examData) return;

    const { jsPDF } = await import('jspdf');
    const autoTableModule = await import('jspdf-autotable');
    const autoTable = autoTableModule.default ? autoTableModule.default : (autoTableModule as any);

    const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
    const pageW = doc.internal.pageSize.getWidth();
    const pageH = doc.internal.pageSize.getHeight();
    const marginL = 18;
    const marginR = 18;
    const marginT = 20;
    const marginB = 20;
    const usableW = pageW - marginL - marginR;
    let y = marginT;

    const checkNewPage = (neededH: number) => {
      if (y + neededH > pageH - marginB) { doc.addPage(); y = marginT; }
    };

    const sanitizeText = (str: string) => {
      if (!str) return '';
      // Remove soft hyphens (\u00AD) and other zero-width characters completely
      let clean = str.replace(/[\u00AD\u200B-\u200D\uFEFF]/g, '');
      // Replace non-breaking spaces (\u00A0) with normal spaces
      clean = clean.replace(/\u00A0/g, ' ');
      // Normalize multiple spaces
      return clean.replace(/\s+/g, ' ').trim();
    };

    const addWrappedText = (
      text: string, x: number, fontSize: number,
      fontStyle: 'normal' | 'bold',
      color: [number, number, number] = [30, 30, 30],
      lineSpacing = 1.3
    ) => {
      doc.setFontSize(fontSize);
      doc.setFont('helvetica', fontStyle);
      doc.setTextColor(...color);
      const lines: string[] = doc.splitTextToSize(sanitizeText(text), usableW);
      const lineH = fontSize * 0.3528 * lineSpacing;
      lines.forEach((line: string) => {
        checkNewPage(lineH);
        doc.text(line, x, y);
        y += lineH;
      });
    };

    // ── Portada / Encabezado ─────────────────────────────────────────────────
    doc.setFillColor(99, 102, 241);
    doc.rect(0, 0, pageW, 14, 'F');
    doc.setFontSize(13);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(255, 255, 255);
    doc.text('LexiScan PAES — Examen y Resultados', marginL, 9.5);

    y = 22;
    addWrappedText('Simulacro PAES', marginL, 16, 'bold', [30, 30, 30]);
    y += 1;

    const nombre = this.profile?.nombre_completo || this.profile?.nombre || 'Estudiante';
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(100, 100, 100);
    doc.text(`Estudiante: ${sanitizeText(nombre)}  |  Fecha: ${new Date().toLocaleDateString('es-CL')}`, marginL, y);
    y += 4;
    doc.text(`Puntaje: ${this.examResult.total_correctas}/${this.examResult.total_preguntas}  (${this.examResult.porcentaje}%)`, marginL, y);
    y += 5;
    doc.setDrawColor(200, 200, 200);
    doc.line(marginL, y, pageW - marginR, y);
    y += 5;
    doc.setFontSize(9);
    doc.setFont('helvetica', 'italic');
    doc.setTextColor(80, 80, 80);
    doc.text('Instrucciones: Lee atentamente cada texto y selecciona la alternativa correcta.', marginL, y, { maxWidth: usableW });
    y += 9;

    // ── PARTE 1: Textos + Preguntas completas ────────────────────────────────
    const grouped = this.buildGroupedForPDF();
    grouped.forEach((grupo, grupoIdx) => {
      checkNewPage(20);

      // Encabezado de lectura contextual
      doc.setFillColor(240, 244, 255);
      doc.roundedRect(marginL, y - 4, usableW, 7, 1.5, 1.5, 'F');
      doc.setFontSize(8);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(99, 102, 241);
      doc.text(`LECTURA CONTEXTUAL ${grupoIdx + 1}`, marginL + 2, y);
      y += 5;

      // Texto contextual
      addWrappedText(grupo.textoPlano || 'Sin texto disponible', marginL, 10, 'normal', [40, 40, 40], 1.45);
      y += 5;

      doc.setDrawColor(220, 220, 220);
      doc.setLineDashPattern([2, 2], 0);
      doc.line(marginL, y, pageW - marginR, y);
      doc.setLineDashPattern([], 0);
      y += 5;

      // Preguntas
      grupo.preguntas.forEach((pregunta: any) => {
        const alts = this.getAlternativesArray(pregunta.alternativas);
        checkNewPage(Math.ceil(pregunta.enunciado.length / 80) * 5 + alts.length * 6 + 10);

        // Número de pregunta
        doc.setFillColor(99, 102, 241);
        doc.circle(marginL + 3.5, y - 1.5, 3.5, 'F');
        doc.setFontSize(8.5);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(255, 255, 255);
        doc.text(String(pregunta.globalIndex), marginL + 3.5, y - 0.8, { align: 'center' });

        // Enunciado
        doc.setFontSize(10.5);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(30, 30, 30);
        const enunciadoLines: string[] = doc.splitTextToSize(sanitizeText(pregunta.enunciado), usableW - 10);
        enunciadoLines.forEach((line: string, li: number) => {
          doc.text(line, marginL + 9, y);
          y += li === 0 ? 5 : 4.8;
        });
        y += 2;

        // Alternativas
        alts.forEach((alt) => {
          checkNewPage(8);
          doc.setDrawColor(140, 140, 140);
          doc.setFillColor(255, 255, 255);
          doc.circle(marginL + 11, y - 1.5, 2.8, 'FD');
          doc.setFontSize(9.5);
          doc.setFont('helvetica', 'bold');
          doc.setTextColor(99, 102, 241);
          doc.text(alt.key, marginL + 11, y - 0.8, { align: 'center' });

          doc.setFontSize(10);
          doc.setFont('helvetica', 'normal');
          doc.setTextColor(50, 50, 50);
          const altLines: string[] = doc.splitTextToSize(sanitizeText(alt.value), usableW - 20);
          altLines.forEach((line: string) => {
            checkNewPage(5);
            doc.text(line, marginL + 16, y);
            y += 4.8;
          });
          y += 0.5;
        });
        y += 5;
      });

      y += 4; // Espacio entre grupos
    });

    // ── PARTE 2: Informe de Resultados ───────────────────────────────────────
    doc.addPage();
    y = marginT;

    doc.setFillColor(58, 90, 148);
    doc.rect(0, 0, pageW, 14, 'F');
    doc.setFontSize(13);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(255, 255, 255);
    doc.text('Informe de Resultados', marginL, 9.5);

    y = 22;
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(30, 30, 30);
    doc.text('Datos del Estudiante', marginL, y);
    y += 8;

    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.text(`Nombre: ${sanitizeText(nombre)}`, marginL, y); y += 6;
    doc.text(`RUT: ${this.profile?.rut || 'No disponible'}`, marginL, y); y += 6;
    doc.text(`Fecha: ${new Date().toLocaleDateString('es-CL')}`, marginL, y); y += 10;

    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.text('Resumen del Examen', marginL, y); y += 8;

    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.text(`Puntaje: ${this.examResult.total_correctas} / ${this.examResult.total_preguntas}`, marginL, y); y += 6;
    doc.text(`Porcentaje de logro: ${this.examResult.porcentaje}%`, marginL, y); y += 10;

    if (this.examResult.rendimiento_habilidades?.length > 0) {
      const tableData = this.examResult.rendimiento_habilidades.map((hab: any) => [
        this.getSkillDisplayName(hab.nombre_habilidad),
        `${hab.correctas} / ${hab.total}`,
        `${hab.porcentaje}%`
      ]);

      autoTable(doc, {
        startY: y,
        head: [['Habilidad', 'Puntaje', 'Porcentaje']],
        body: tableData,
        theme: 'striped',
        headStyles: { fillColor: [99, 102, 241] },
        styles: { font: 'helvetica', fontSize: 10 }
      });
      
      y = (doc as any).lastAutoTable.finalY + 15;
      
      // -- GRÁFICO DE BARRAS DE RENDIMIENTO --
      checkNewPage(80); // Ensure space for the chart
      doc.setFontSize(12);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(30, 30, 30);
      doc.text('Gráfico de Rendimiento por Habilidad', marginL, y);
      y += 10;
      
      const maxBarW = usableW - 55;
      this.examResult.rendimiento_habilidades.forEach((hab: any) => {
         const label = this.getSkillDisplayName(hab.nombre_habilidad);
         const pct = hab.porcentaje;
         doc.setFontSize(9);
         doc.setFont('helvetica', 'normal');
         doc.setTextColor(50, 50, 50);
         doc.text(label, marginL, y + 4);
         
         // background bar
         doc.setFillColor(235, 235, 235);
         doc.rect(marginL + 45, y, maxBarW, 6, 'F');
         
         // filled bar
         doc.setFillColor(99, 102, 241);
         doc.rect(marginL + 45, y, (pct / 100) * maxBarW, 6, 'F');
         
         // text pct
         doc.setFontSize(8);
         doc.setFont('helvetica', 'bold');
         doc.text(`${pct}%`, marginL + 45 + ((pct / 100) * maxBarW) + 2, y + 4.5);
         
         y += 10;
      });
    }

    // ── PARTE 3: Advertencia de Solucionario ─────────────────────────────────
    doc.addPage();
    doc.setFillColor(239, 68, 68); // Tailwind red-500
    doc.rect(0, 0, pageW, pageH, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(32);
    doc.setFont('helvetica', 'bold');
    doc.text('¡ALTO AHÍ!', pageW / 2, pageH / 2 - 20, { align: 'center' });
    
    doc.setFontSize(16);
    doc.setFont('helvetica', 'normal');
    const warningText = 'Las siguientes páginas contienen las respuestas correctas y sus justificaciones.\n\nPor favor, procede solo si ya has intentado resolver el examen por tu propia cuenta.';
    const warningLines = doc.splitTextToSize(warningText, usableW - 20);
    doc.text(warningLines, pageW / 2, pageH / 2 + 10, { align: 'center' });

    // ── PARTE 4: Solucionario y Justificaciones ──────────────────────────────
    doc.addPage();
    y = marginT;
    doc.setFillColor(34, 197, 94); // Tailwind green-500
    doc.rect(0, 0, pageW, 14, 'F');
    doc.setFontSize(13);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(255, 255, 255);
    doc.text('Solucionario y Justificaciones', marginL, 9.5);
    y = 25;

    grouped.forEach((grupo, grupoIdx) => {
      checkNewPage(15);
      doc.setFontSize(11);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(30, 30, 30);
      doc.text(`Lectura Contextual ${grupoIdx + 1}`, marginL, y);
      y += 8;

      grupo.preguntas.forEach((pregunta: any) => {
         checkNewPage(40);
         doc.setFontSize(10);
         doc.setFont('helvetica', 'bold');
         doc.setTextColor(99, 102, 241);
         doc.text(`Pregunta ${pregunta.globalIndex}`, marginL, y);
         y += 6;
         
         const correctKey = pregunta.respuesta_correcta;
         const alts = this.getAlternativesArray(pregunta.alternativas);
         const correctAlt = alts.find(a => a.key === correctKey);
         
         addWrappedText(`Respuesta Correcta: ${correctKey} - ${correctAlt ? correctAlt.value : ''}`, marginL, 9.5, 'bold', [21, 128, 61]);
         y += 3;
         
         addWrappedText(`Justificación:`, marginL, 9, 'bold', [50, 50, 50]);
         y += 1.5;
         const justificacion = pregunta.justificacion_cot || pregunta.justificacion || 'No se proporcionó justificación detallada para esta pregunta.';
         addWrappedText(justificacion, marginL, 9, 'normal', [80, 80, 80], 1.4);
         y += 8;
      });
      y += 5;
    });

    // ── Paginación ───────────────────────────────────────────────────────────
    const totalPages = (doc.internal as any).getNumberOfPages();
    // Start pagination ignoring the warning page, or just paginate all pages
    for (let p = 1; p <= totalPages; p++) {
      doc.setPage(p);
      doc.setFontSize(8);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(150, 150, 150);
      doc.text(
        `LexiScan PAES — Página ${p} de ${totalPages}`,
        pageW / 2, pageH - 8, { align: 'center' }
      );
    }

    doc.save(`LexiScan_Examen_Resultados_${new Date().toISOString().slice(0, 10)}.pdf`);
  }
}
