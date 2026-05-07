import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { IonicModule } from '@ionic/angular';
import { ModalController } from '@ionic/angular';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HabilidadesService } from '../services/habilidades.service';

@Component({
  selector: 'app-config-modal',
  templateUrl: './config-modal.component.html',
  styleUrls: ['./config-modal.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    IonicModule
  ]
})
export class ConfigModalComponent implements OnInit {
  configForm!: FormGroup;
  availableModels: string[] = [];
  loading = false;

  constructor(
    private modalController: ModalController,
    private fb: FormBuilder,
    private habilidadesService: HabilidadesService
  ) {}

  ngOnInit() {
    this.initializeForm();
    this.loadConfig();
    this.loadModels();
  }

  initializeForm(): void {
    this.configForm = this.fb.group({
      apiKey: ['', [Validators.required]],
      model: ['llama-3.1-8b-instant', [Validators.required]]
    });
  }

  async loadConfig(): Promise<void> {
    try {
      const config = await this.habilidadesService.getConfiguracion().toPromise();
      if (config) {
        const apiKeyConfig = config.find((c: any) => c.clave === 'GROQ_API_KEY');
        const modelConfig = config.find((c: any) => c.clave === 'GROQ_MODEL');

        this.configForm.patchValue({
          apiKey: apiKeyConfig?.valor || '',
          model: modelConfig?.valor || 'llama-3.1-8b-instant'
        });
      }
    } catch (error) {
      console.error('Error loading config:', error);
    }
  }

  async loadModels(): Promise<void> {
    try {
      const response = await this.habilidadesService.getGroqModels().toPromise();
      if (response && response.data) {
        this.availableModels = response.data.map((model: any) => model.id);
      } else {
        // Modelos por defecto si falla la carga
        this.availableModels = [
          'llama-3.1-8b-instant',
          'llama3-8b-8192',
          'mixtral-8x7b-32768',
          'gemma-7b-it'
        ];
      }
    } catch (error) {
      console.error('Error loading models:', error);
      // Modelos por defecto si falla la carga
      this.availableModels = [
        'llama-3.1-8b-instant',
        'llama3-8b-8192',
        'mixtral-8x7b-32768',
        'gemma-7b-it'
      ];
    }
  }

  async onSubmit(): Promise<void> {
    if (this.configForm.valid) {
      this.loading = true;
      try {
        const { apiKey, model } = this.configForm.value;

        await this.habilidadesService.setConfiguracion({
          clave: 'GROQ_API_KEY',
          valor: apiKey,
          descripcion: 'API Key para Groq'
        }).toPromise();

        await this.habilidadesService.setConfiguracion({
          clave: 'GROQ_MODEL',
          valor: model,
          descripcion: 'Modelo de Groq a utilizar'
        }).toPromise();

        this.closeModal();
      } catch (error) {
        console.error('Error saving config:', error);
      } finally {
        this.loading = false;
      }
    }
  }

  closeModal(): void {
    this.modalController.dismiss();
  }
}
