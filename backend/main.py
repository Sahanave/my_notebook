from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI(title="Are You Taking Notes API", version="1.0.0")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
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

# Sample data (placeholder content)
sample_slides = [
    SlideContent(
        title="Welcome to Claude Agents",
        content="Building intelligent agents with Claude on Vertex AI",
        image_url="https://via.placeholder.com/800x600/4F46E5/FFFFFF?text=Slide+1",
        slide_number=1
    ),
    SlideContent(
        title="Architecture Overview",
        content="Understanding the MCP (Model Context Protocol) integration",
        image_url="https://via.placeholder.com/800x600/7C3AED/FFFFFF?text=Slide+2",
        slide_number=2
    ),
    SlideContent(
        title="Implementation Guide",
        content="Step-by-step implementation with code examples",
        image_url="https://via.placeholder.com/800x600/DC2626/FFFFFF?text=Slide+3",
        slide_number=3
    )
]

sample_references = [
    ReferenceLink(
        title="Configure Claude Code on Vertex",
        url="https://cloud.google.com/vertex-ai/docs/generative-ai/models/claude",
        description="Official Google Cloud documentation for Claude on Vertex AI"
    ),
    ReferenceLink(
        title="Learn more about MCP",
        url="https://docs.anthropic.com/claude/docs/mcp",
        description="Model Context Protocol documentation"
    ),
    ReferenceLink(
        title="Get started with Claude on Vertex AI",
        url="https://console.cloud.google.com/vertex-ai",
        description="Google Cloud Vertex AI Console"
    )
]

sample_conversation = [
    ConversationMessage(
        id=1,
        user="Alice",
        message="How do we handle authentication with Claude on Vertex AI?",
        timestamp="2024-12-28T10:30:00Z",
        type="question"
    ),
    ConversationMessage(
        id=2,
        user="Presenter",
        message="Great question! Authentication is handled through Google Cloud IAM. You'll need to set up service accounts with the appropriate permissions.",
        timestamp="2024-12-28T10:31:00Z",
        type="answer"
    ),
    ConversationMessage(
        id=3,
        user="Bob",
        message="What about rate limiting? Are there any constraints we should be aware of?",
        timestamp="2024-12-28T10:33:00Z",
        type="question"
    )
]

sample_live_updates = [
    LiveUpdate(
        message="Welcome everyone! We'll start in 2 minutes.",
        timestamp="2024-12-28T10:28:00Z",
        type="announcement"
    ),
    LiveUpdate(
        message="Demo environment is now live and ready for testing",
        timestamp="2024-12-28T10:35:00Z",
        type="info"
    )
]

sample_document_summary = DocumentSummary(
    title="Building Intelligent Agents with Claude on Vertex AI",
    abstract="This comprehensive guide explores the integration of Anthropic's Claude language model with Google Cloud's Vertex AI platform to create powerful, context-aware intelligent agents. The document covers the Model Context Protocol (MCP), implementation strategies, and best practices for deploying Claude-based agents in production environments.",
    key_points=[
        "Integration of Claude with Vertex AI infrastructure",
        "Implementation of Model Context Protocol (MCP) for enhanced context management",
        "Authentication and security considerations for production deployments",
        "Scalability patterns and performance optimization techniques",
        "Real-world use cases and deployment scenarios"
    ],
    main_topics=[
        "Claude API Integration",
        "Vertex AI Platform",
        "Model Context Protocol",
        "Authentication & Security",
        "Performance Optimization",
        "Production Deployment"
    ],
    difficulty_level="intermediate",
    estimated_read_time="45 minutes",
    document_type="tutorial",
    authors=["Google Cloud Team", "Anthropic Documentation"],
    publication_date="2024-12-28"
)

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Are You Taking Notes API is running!"}

@app.get("/api/slides", response_model=List[SlideContent])
async def get_slides():
    """Get all presentation slides"""
    return sample_slides

@app.get("/api/slides/{slide_number}", response_model=SlideContent)
async def get_slide(slide_number: int):
    """Get a specific slide by number"""
    for slide in sample_slides:
        if slide.slide_number == slide_number:
            return slide
    return SlideContent(
        title="Slide Not Found",
        content="The requested slide is not available",
        image_url="https://via.placeholder.com/800x600/6B7280/FFFFFF?text=Not+Found",
        slide_number=slide_number
    )

@app.get("/api/references", response_model=List[ReferenceLink])
async def get_references():
    """Get all reference links"""
    return sample_references

@app.get("/api/conversation", response_model=List[ConversationMessage])
async def get_conversation():
    """Get the current conversation/Q&A"""
    return sample_conversation

@app.post("/api/conversation", response_model=ConversationMessage)
async def add_message(message: str, user: str = "Anonymous"):
    """Add a new message to the conversation"""
    new_message = ConversationMessage(
        id=len(sample_conversation) + 1,
        user=user,
        message=message,
        timestamp="2024-12-28T10:40:00Z",  # In real app, use current timestamp
        type="question"
    )
    sample_conversation.append(new_message)
    return new_message

@app.get("/api/live-updates", response_model=List[LiveUpdate])
async def get_live_updates():
    """Get live updates and announcements"""
    return sample_live_updates

@app.get("/api/document-summary", response_model=DocumentSummary)
async def get_document_summary():
    """Get summary of the document being discussed"""
    return sample_document_summary

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 