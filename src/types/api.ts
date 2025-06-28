export interface ReferenceLink {
  title: string;
  url: string;
  description: string;
}

export interface SlideContent {
  title: string;
  content: string;
  image_url: string;
  slide_number: number;
}

export interface LiveUpdate {
  message: string;
  timestamp: string;
  type: "info" | "question" | "announcement";
}

export interface ConversationMessage {
  id: number;
  user: string;
  message: string;
  timestamp: string;
  type: "question" | "answer" | "comment";
} 