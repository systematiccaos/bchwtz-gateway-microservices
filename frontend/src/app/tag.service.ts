import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { io, Socket } from 'socket.io-client';

@Injectable({
  providedIn: 'root'
})
export class TagService {
  private readonly apibase = "http://localhost:8000";
  private readonly socket: Socket
  public state: Object = {};
  constructor(private readonly httpClient: HttpClient) {
    this.socket = io("http://localhost:8000");
  }

  // Listen to events from the server
  onMessage(): Observable<any> {
    return new Observable<any>((observer) => {
      this.socket.on('state', (message: any) => {
        this.state = message;
        observer.next(message);
      });

      // Clean up connection when observable completes
      return () => {
        this.socket.disconnect();
      };
    });
  }

  onConnectError(): Observable<any> {
    return new Observable<any>((observer) => {
      this.socket.on('connect_error', (error: any) => {
        observer.error(error);
      });

      return () => {
        this.socket.off('connect_error');
      };
    });
  }

  public getState(): Observable<any> {
    return this.httpClient.get(`${this.apibase}/get-state`);
  }

  public getTags(): Observable<any> {
    return this.httpClient.get(`${this.apibase}/get-tags`);
  }

  public getConfig(addr: string): Observable<any> {
    return this.httpClient.get(`${this.apibase}/tag/${addr}/get-config`);
  }

  public getTime(addr: string): Observable<any> {
    return this.httpClient.get(`${this.apibase}/tag/${addr}/get-time`);
  }
}
