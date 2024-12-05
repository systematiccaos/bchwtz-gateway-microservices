import { Routes } from '@angular/router';
import { StartComponent } from './start/start.component';

export const routes: Routes = [
  {
      path: '',
      pathMatch: 'full',
      component: StartComponent
  },
];
