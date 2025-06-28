# Data models
from pydantic import BaseModel
from typing import List

class ReferenceLink(BaseModel):
    title: str
    url: str
    description: str

class SlideContent(BaseModel):
    title: str
    content: str
    image_url: str
    slide_number: int

class LiveUpdate(BaseModel):
    message: str
    timestamp: str
    type: str  # "info", "question", "announcement"

class ConversationMessage(BaseModel):
    id: int
    user: str
    message: str
    timestamp: str
    type: str  # "question", "answer", "comment"

class DocumentSummary(BaseModel):
    title: str
    abstract: str
    key_points: List[str]
    main_topics: List[str]
    difficulty_level: str  # "beginner", "intermediate", "advanced"
    estimated_read_time: str
    document_type: str  # "research_paper", "tutorial", "book_chapter", "article"
    authors: List[str]
    publication_date: str

class UploadResult(BaseModel):
    success: bool
    message: str
    filename: str
    fileSize: str
    pages: int
    readingTime: str
    topics: int
    processingTime: str
    keyTopics: List[str]
    extractedSections: List[dict]
    generatedSlides: int
    detectedLanguage: str
    complexity: str
    extractedText: str  # Full text content