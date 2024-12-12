import { Routes } from '@angular/router';
import { StartComponent } from './start/start.component';
import { TagComponent } from './tag/tag.component';
import { DocsComponent } from './docs/docs.component';

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
  {
      path: 'docs/:part',
      pathMatch: 'full',
      component: DocsComponent
  },
];
