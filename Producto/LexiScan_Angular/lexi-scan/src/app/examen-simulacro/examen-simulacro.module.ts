import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { IonicModule } from '@ionic/angular';
import { ExamenSimulacroPageRoutingModule } from './examen-simulacro-routing.module';
import { ExamenSimulacroPage } from './examen-simulacro.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    ExamenSimulacroPageRoutingModule,
  ],
  declarations: [ExamenSimulacroPage],
})
export class ExamenSimulacroPageModule {}
