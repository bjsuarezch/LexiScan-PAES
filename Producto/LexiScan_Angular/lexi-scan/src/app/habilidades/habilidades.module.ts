import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { HabilidadesPageRoutingModule } from './habilidades-routing.module';

import { HabilidadesPage } from './habilidades.page';
import { RadarChartComponent } from '../components/radar-chart/radar-chart.component';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    HabilidadesPageRoutingModule,
  ],
  declarations: [HabilidadesPage, RadarChartComponent],
})
export class HabilidadesPageModule {}
