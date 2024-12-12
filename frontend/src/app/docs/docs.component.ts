import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { MarkdownModule } from 'ngx-markdown';

@Component({
  selector: 'app-docs',
  imports: [MarkdownModule],
  templateUrl: './docs.component.html',
  styleUrl: './docs.component.scss'
})
export class DocsComponent {

  public params: any;

  constructor(private readonly route: ActivatedRoute) {
    this.route.params.subscribe(params => this.params = params);
    console.log(this.params);
  }
}
