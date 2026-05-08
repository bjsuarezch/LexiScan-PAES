import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { ExamenSimulacroPage } from './examen-simulacro.page';

const routes: Routes = [
  {
    path: '',
    component: ExamenSimulacroPage,
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class ExamenSimulacroPageRoutingModule {}
