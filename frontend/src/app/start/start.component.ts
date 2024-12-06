import { Component, OnInit } from '@angular/core';
import { TagService } from '../tag.service';
import { Subscription } from 'rxjs';
import { NgFor } from '@angular/common';
import { MapToArrayPipe } from '../maptoarray.pipe';
import { MatButtonModule } from '@angular/material/button'

@Component({
  selector: 'app-start',
  imports: [NgFor, MapToArrayPipe, MatButtonModule],
  templateUrl: './start.component.html',
  styleUrl: './start.component.scss'
})
export class StartComponent implements OnInit {
  constructor(private readonly tagService: TagService) {}

  private messageSubscription!: Subscription;
  private errorSubscription!: Subscription;
  public state: any;

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

  ngOnDestroy() {
    this.messageSubscription.unsubscribe();
    this.errorSubscription.unsubscribe();
  }

  public getState() {
    this.tagService.getState().subscribe(response => {
      this.state = response;
      console.log(response);
    });
  }
  public getTags() {
    this.tagService.getTags().subscribe(response => {
      console.log(response);
    });
  }
}
