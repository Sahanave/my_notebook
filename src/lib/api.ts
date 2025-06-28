import { ReferenceLink, SlideContent, LiveUpdate, ConversationMessage, DocumentSummary, UploadResult } from '@/types/api';

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

  static async getDocumentSummary(): Promise<DocumentSummary> {
    return this.request<DocumentSummary>('/api/document-summary');
  }

  static async uploadPDF(file: File): Promise<UploadResult> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/upload`, {
      method: 'POST',
      body: formData,
      // Don't set Content-Type header for FormData, let browser set it
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(errorData.detail || `Upload Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  static async generateSlides(): Promise<SlideContent[]> {
    return this.request<SlideContent[]>('/api/generate-slides', {
      method: 'POST',
    });
  }

  static async regenerateSlides(): Promise<SlideContent[]> {
    return this.request<SlideContent[]>('/api/regenerate-slides', {
      method: 'POST',
    });
  }


} 