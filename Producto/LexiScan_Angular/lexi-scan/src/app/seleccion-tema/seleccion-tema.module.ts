import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { SeleccionTemaPageRoutingModule } from './seleccion-tema-routing.module';

import { SeleccionTemaPage } from './seleccion-tema.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    SeleccionTemaPageRoutingModule
  ],
  declarations: [SeleccionTemaPage]
})
export class SeleccionTemaPageModule {}
