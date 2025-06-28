import { ReferenceLink, SlideContent, LiveUpdate, ConversationMessage } from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiClient {
  private static async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  static async getSlides(): Promise<SlideContent[]> {
    return this.request<SlideContent[]>('/api/slides');
  }

  static async getSlide(slideNumber: number): Promise<SlideContent> {
    return this.request<SlideContent>(`/api/slides/${slideNumber}`);
  }

  static async getReferences(): Promise<ReferenceLink[]> {
    return this.request<ReferenceLink[]>('/api/references');
  }

  static async getConversation(): Promise<ConversationMessage[]> {
    return this.request<ConversationMessage[]>('/api/conversation');
  }

  static async addMessage(message: string, user: string = 'Anonymous'): Promise<ConversationMessage> {
    return this.request<ConversationMessage>('/api/conversation', {
      method: 'POST',
      body: JSON.stringify({ message, user }),
    });
  }

  static async getLiveUpdates(): Promise<LiveUpdate[]> {
    return this.request<LiveUpdate[]>('/api/live-updates');
  }
} 