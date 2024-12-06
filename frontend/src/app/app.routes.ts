import { Routes } from '@angular/router';
import { StartComponent } from './start/start.component';
import { TagComponent } from './tag/tag.component';

export const routes: Routes = [
  {
      path: '',
      pathMatch: 'full',
      component: StartComponent
  },
  {
      path: 'tag/:address',
      pathMatch: 'full',
      component: TagComponent
  },
];
