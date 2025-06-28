import { SlideContent, LiveUpdate, DocumentSummary, UploadResult } from '@/types/api';

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
    const response = await fetch(`${API_BASE_URL}/api/slides/${slideNumber}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch slide ${slideNumber}`);
    }
    return response.json();
  }

  static async getSlidesMetadata(): Promise<{ total_slides: number; available_slides: number[] }> {
    const response = await fetch(`${API_BASE_URL}/api/slides/metadata`);
    if (!response.ok) {
      throw new Error('Failed to fetch slides metadata');
    }
    return response.json();
  }

  static async getLiveUpdates(): Promise<LiveUpdate[]> {
    const response = await fetch(`${API_BASE_URL}/api/live-updates`);
    if (!response.ok) {
      throw new Error('Failed to fetch live updates');
    }
    return response.json();
  }

  static async getDocumentSummary(): Promise<DocumentSummary> {
    const response = await fetch(`${API_BASE_URL}/api/document-summary`);
    if (!response.ok) {
      throw new Error('Failed to fetch document summary');
    }
    return response.json();
  }

  static async uploadPDF(file: File): Promise<UploadResult> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to upload PDF');
    }

    return response.json();
  }

  static async generateSlides(): Promise<SlideContent[]> {
    const response = await fetch(`${API_BASE_URL}/api/generate-slides`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to generate slides');
    }

    return response.json();
  }

  static async regenerateSlides(): Promise<SlideContent[]> {
    return this.request<SlideContent[]>('/api/regenerate-slides', {
      method: 'POST',
    });
  }
} 