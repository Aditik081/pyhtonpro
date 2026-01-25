import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class Health {

  constructor(private http: HttpClient) {}

  checkHealth(): Observable<{ status: string }> {
    return this.http.get<{ status: string }>(
      'http://127.0.0.1:5000/health'
    );
  }
}

  
//service file hai backend se data laati hai
