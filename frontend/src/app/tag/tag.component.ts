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
  private readonly state: Array<any>= [];
  public stateJSON: any = "";
  public params: any;

  ngOnInit() {
    this.messageSubscription = this.tagService.onMessage().subscribe({
      next: (message: any) => {
        console.log(message);
        this.setState(message);
      },
      error: (err: any) => console.error('Error:', err)
    });

    this.errorSubscription = this.tagService.onConnectError().subscribe(
      (err: any) => console.error('Connection error:', err)
    );

    this.getState();
  }

  public getState() {
    this.tagService.getState().subscribe(response => {
      this.setState(response);
      console.log(response);
    });
  }

  private setState(state: any) {
    this.state.push(state[this.params.address]);
    this.stateJSON = JSON.stringify(state[this.params.address], null, "    ")
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
  public setSamplerate(rate: number) {
    this.tagService.setSamplerate(this.params.address, rate).subscribe(result => console.log(result));
  }
  public setHeartbeat(heartbeat: number) {
    this.tagService.setHeartbeat(this.params.address, heartbeat).subscribe(result => console.log(result));
  }
  public startStreaming() {
    this.tagService.startStreaming(this.params.address).subscribe(result => console.log(result));
  }
  public stopStreaming() {
    this.tagService.stopStreaming(this.params.address).subscribe(result => console.log(result));
  }
}
