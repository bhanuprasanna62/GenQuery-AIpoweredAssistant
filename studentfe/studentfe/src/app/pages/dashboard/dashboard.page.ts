import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Api } from 'src/app/services/api';
import { Router } from '@angular/router';
import { Auth } from 'src/app/services/auth';

import {
  IonContent,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonButton,
  IonButtons,
  IonTitle,
  IonToolbar,
  IonHeader,
  IonInput
} from '@ionic/angular/standalone';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.page.html',
  styleUrls: ['./dashboard.page.scss'],
  standalone: true,
  imports: [
    IonContent,
    IonCard,
    IonButton,
    IonButtons,
    IonTitle,
    IonToolbar,
    IonHeader,
    IonCardHeader,
    IonCardTitle,
    IonCardContent,
    CommonModule,
    FormsModule,
    IonInput
  ]
})
export class DashboardPage implements OnInit {

  profile: any;

  conversationId: number | null = null;

  chatInput = '';

  chatLoading = false;

  messages: {
    role: 'user' | 'assistant';
    content: string;
    sources?: {
      document_id: number;
      source: string;
      chunk_index: number;
    }[];
    confidence?: string;
  }[] = [];

  constructor(
    private api: Api,
    private auth: Auth,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadProfile();
    this.createNewConversation();
  }

  loadProfile() {
    this.api.getProfile().subscribe({
      next: (res: any) => {
        console.log('PROFILE API RESPONSE:', res);

        this.profile = res[0];
      },

      error: (error) => {
        console.error('PROFILE ERROR:', error);
        this.router.navigateByUrl('/login');
      }
    });
  }

  logout() {
    this.auth.logout();
    this.router.navigateByUrl('/login');
  }

  goUpload() {
    console.log('🟢 Upload button clicked');

    this.router.navigate(['/upload-documents'])
      .then(success => {
        console.log('Navigation success:', success);
      })
      .catch(error => {
        console.error('Navigation error:', error);
      });
  }

  createNewConversation() {

    console.log('Creating conversation...');

    this.api.createConversation().subscribe({

      next: (res: any) => {

        console.log('CONVERSATION CREATED:', res);

        this.conversationId = res.conversation_id;

        this.messages = [];
      },

      error: (error) => {

        console.error(
          'CONVERSATION CREATE ERROR:',
          error
        );

      }

    });
  }

  sendMessage() {

    console.log('SEND BUTTON CLICKED');

    if (!this.chatInput.trim()) {
      console.log('Question is empty');
      return;
    }

    if (!this.conversationId) {
      console.error('Conversation ID is missing');
      return;
    }
    const question = this.chatInput.trim();

    this.messages.push({
      role: 'user',
      content: question
    });

    this.chatInput = '';

    this.chatLoading = true;

    console.log(
      'Sending question:',
      question,
      'Conversation ID:',
      this.conversationId
    );

    this.api.askConversation(
      this.conversationId,
      question
    ).subscribe({

      next: (res: any) => {

        console.log('AI RESPONSE:', res);

        this.messages.push({
          role: 'assistant',
          content: res.answer,
          sources: res.sources || [],
          confidence: res.confidence || ''
        });

        this.chatLoading = false;
      },

      error: (error) => {

        console.error(
          'CONVERSATION ERROR:',
          error
        );

        this.messages.push({
          role: 'assistant',
          content: 'Unable to get an answer. Please try again.'
        });

        this.chatLoading = false;
      }

    });
  }
}