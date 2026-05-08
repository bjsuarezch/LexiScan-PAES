import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { ExamenResultadosPage } from './examen-resultados.page';

const routes: Routes = [
  {
    path: '',
    component: ExamenResultadosPage,
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class ExamenResultadosPageRoutingModule {}
