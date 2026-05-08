import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { IonicModule } from '@ionic/angular';
import { ExamenResultadosPageRoutingModule } from './examen-resultados-routing.module';
import { ExamenResultadosPage } from './examen-resultados.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    ExamenResultadosPageRoutingModule,
  ],
  declarations: [ExamenResultadosPage],
})
export class ExamenResultadosPageModule {}
