export interface SlideContent {
  title: string;
  content: string;
  image_description: string;
  slide_number: number;
}

export interface LiveUpdate {
  message: string;
  timestamp: string;
  type: "info" | "question" | "announcement";
}

export interface DocumentSummary {
  title: string;
  abstract: string;
  key_points: string[];
  main_topics: string[];
  difficulty_level: "beginner" | "intermediate" | "advanced";
  estimated_read_time: string;
  document_type: "research_paper" | "tutorial" | "book_chapter" | "article";
  authors: string[];
  publication_date: string;
  // sections are handled on backend only - frontend doesn't need detailed structure
}

export interface UploadResult {
  success: boolean;
  message: string;
  filename: string;
  fileSize: string;
  pages: number;
  readingTime: string;
  topics: number;
  processingTime: string;
  keyTopics: string[];
  extractedSections: {
    title: string;
    pages: string;
  }[];
  generatedSlides: number;
  detectedLanguage: string;
  complexity: string;
  extractedText: string; // Full text content from Python backend
} 