import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { SeleccionTemaPage } from './seleccion-tema.page';

const routes: Routes = [
  {
    path: '',
    component: SeleccionTemaPage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class SeleccionTemaPageRoutingModule {}
