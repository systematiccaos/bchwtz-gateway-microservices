import { Component } from '@angular/core';
import { TagService } from '../tag.service';
import { Subscription } from 'rxjs';
import { ActivatedRoute } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-tag',
  imports: [MatButtonModule],
  templateUrl: './tag.component.html',
  styleUrl: './tag.component.scss'
})
export class TagComponent {
  constructor(private readonly tagService: TagService, private readonly route: ActivatedRoute) {
    this.route.params.subscribe( params => this.params = params );
  }

  private messageSubscription!: Subscription;
  private errorSubscription!: Subscription;
  private state: any;
  private params: any;

  ngOnInit() {
    this.messageSubscription = this.tagService.onMessage().subscribe({
      next: (message: any) => {
        console.log(message);
        this.state = message;
      },
      error: (err: any) => console.error('Error:', err)
    });

    this.errorSubscription = this.tagService.onConnectError().subscribe(
      (err: any) => console.error('Connection error:', err)
    );

    this.state = this.getState();
  }

  public getState() {
    this.tagService.getState().subscribe(response => {
      this.state = response;
      console.log(response);
    });
  }

  public getConfig() {
    this.tagService.getConfig(this.params.address).subscribe(result => console.log(result));
  }
  public getTime() {
    this.tagService.getTime(this.params.address).subscribe(result => console.log(result));
  }
  public getHeartbeat() {
    this.tagService.getHeartbeat(this.params.address).subscribe(result => console.log(result));
  }
  public setTime() {
    this.tagService.setTime(this.params.address).subscribe(result => console.log(result));
  }
}
