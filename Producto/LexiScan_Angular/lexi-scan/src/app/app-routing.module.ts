import { NgModule } from '@angular/core';
import { PreloadAllModules, RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  {
    path: 'home',
    loadChildren: () => import('./home/home.module').then(m => m.HomePageModule)
  },
  {
    path: 'habilidades',
    loadChildren: () => import('./habilidades/habilidades.module').then(m => m.HabilidadesPageModule)
  },
  {
    path: 'gym',
    loadChildren: () => import('./gym/gym.module').then(m => m.GymPageModule)
  },
  {
    path: 'examen',
    loadChildren: () => import('./examen/examen.module').then(m => m.ExamenPageModule)
  },
  {
    path: '',
    loadChildren: () => import('./tabs/tabs.module').then(m => m.TabsPageModule)
  }
];
@NgModule({
  imports: [
    RouterModule.forRoot(routes, { preloadingStrategy: PreloadAllModules })
  ],
  exports: [RouterModule]
})
export class AppRoutingModule {}
