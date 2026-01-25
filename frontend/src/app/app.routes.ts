import { Routes } from '@angular/router';
import { LandingComponent } from './landing/landing';
import { ChatbotComponent } from './chatbot/chatbot';

export const routes: Routes = [
  { path: '', component: LandingComponent },
  { path: 'chatbot', component: ChatbotComponent }
];
