import { Component, OnInit } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';


@Component({
  imports: [CommonModule], 
  
  selector: 'app-landing',
  templateUrl: './landing.html',
  styleUrls: ['./landing.css']
})
export class LandingComponent implements OnInit {

  typingText: string = '';
  texts: string[] = [
    'Analyzing report...',
    'Detecting abnormalities...',
    'Generating AI health insights...',
    'Almost ready...'
  ];

  steps: string[] = [
    'Upload your medical reports securely',
    'AI analyzes your lab reports instantly',
    'Important health values are extracted',
    'You receive smart AI-based insights'
  ];

  index = 0;
  charIndex = 0;

  ngOnInit() {
    this.typeEffect();
  }

  typeEffect() {
    if (this.charIndex < this.texts[this.index].length) {
      this.typingText += this.texts[this.index].charAt(this.charIndex);
      this.charIndex++;
      setTimeout(() => this.typeEffect(), 80);
    } else {
      setTimeout(() => {
        this.typingText = '';
        this.charIndex = 0;
        this.index = (this.index + 1) % this.texts.length;
        this.typeEffect();
      }, 1500);
    }
  }

  constructor(private router: Router) {} 

  startInterview() {
    this.router.navigate(['/chatbot']);
  }
  test(){
    alert("button click");
  }
}
