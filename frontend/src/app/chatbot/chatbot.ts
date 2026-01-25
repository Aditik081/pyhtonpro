import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { Router } from '@angular/router';

@Component({
  selector: 'app-chatbot',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './chatbot.html',
  styleUrls: ['./chatbot.css']
})
export class ChatbotComponent {

  userInput = '';
  selectedFile!: File;
  analysisData: any = null;
  reportUploaded = false;

  messages: { sender: string, text: string }[] = [
    { sender: 'bot', text: 'Hello! Please upload your medical report.' }
  ];

  constructor(private http: HttpClient, private router: Router) {}

  goHome(){
    this.router.navigate(['/']);
  }

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
    this.messages.push({
      sender: 'user',
      text: '📄 ' + this.selectedFile.name
    });
  }

  uploadReport() {
    if (!this.selectedFile) {
      alert('Please select a file first');
      return;
    }

    const formData = new FormData();
    formData.append('file', this.selectedFile);

    this.messages.push({
      sender: 'bot',
      text: '⏳ Analyzing your report...'
    });

    this.http.post<any>('http://localhost:5000/extract', formData)
      .subscribe({
        next: (res) => {
          this.analysisData = res.analysis;
          this.reportUploaded = true;

          this.messages.push({
            sender: 'bot',
            text: this.formatResult(res)
          });

          this.messages.push({
            sender: 'bot',
            text: '✅ You can now ask questions about your report.'
          });
        },
        error: () => {
          this.messages.push({
            sender: 'bot',
            text: '❌ Server error. Please try again.'
          });
        }
      });
  }

  sendMessage() {
    if (!this.userInput.trim()) return;

    const question = this.userInput;
    this.messages.push({ sender: 'user', text: question });
    this.userInput = '';

    if (!this.reportUploaded) {
      this.messages.push({
        sender: 'bot',
        text: 'Please upload your report first.'
      });
      return;
    }

    this.http.post<any>('http://localhost:5000/ask', {
      question: question,
      analysis: this.analysisData
    }).subscribe({
      next: (res) => {
        let answer = res.answer;
        answer = answer.replace(/\t/g, '   ').replace(/\n/g, '<br>');

        this.messages.push({
          sender: 'bot',
          text: answer
        });
      },
      error: () => {
        this.messages.push({
          sender: 'bot',
          text: 'Unable to answer right now.'
        });
      }
    });
  }

 formatResult(res: any): string {
  let msg = `📊 Report analyzed<br><br>`;

  if (res.analysis.observations.length) {
    msg += '🔎 Observations:<br>';
    res.analysis.observations.forEach((o: string) => {
      msg += `• ${o}<br><br>`; // double <br> for spacing
    });
  }

  if (res.analysis.possible_conditions.length) {
    msg += '⚠ Possible Conditions:<br>';
    res.analysis.possible_conditions.forEach((d: string) => {
      msg += `• ${d}<br><br>`;
    });
  } else {
    msg += '✅ No major abnormalities detected.<br>';
  }

  return msg;
}

}
