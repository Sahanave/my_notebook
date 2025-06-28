from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
import PyPDF2
import io
import time
from datetime import datetime

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

# PDF Processing Functions
def extract_text_from_pdf(file_contents: bytes) -> tuple[str, int]:
    """Extract text from PDF and return text + page count"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_contents))
        text = ""
        page_count = len(pdf_reader.pages)
        
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text, page_count
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract PDF text: {str(e)}")

def analyze_document_content(text: str, filename: str) -> dict:
    """Analyze extracted text and generate insights"""
    # Simple analysis - in production you'd use AI/ML here
    words = text.split()
    word_count = len(words)
    
    # Estimate reading time (average 200 words per minute)
    reading_minutes = max(1, word_count // 200)
    reading_time = f"{reading_minutes} minutes" if reading_minutes < 60 else f"{reading_minutes // 60}h {reading_minutes % 60}m"
    
    # Extract potential key topics (basic keyword extraction)
    # In production, you'd use NLP libraries like spaCy, NLTK, or AI APIs
    common_tech_terms = [
        "machine learning", "artificial intelligence", "neural network", "deep learning",
        "algorithm", "data science", "python", "tensorflow", "pytorch", "model",
        "training", "prediction", "classification", "regression", "clustering"
    ]
    
    text_lower = text.lower()
    detected_topics = [term for term in common_tech_terms if term in text_lower]
    
    # Generate sections based on common document patterns
    sections = []
    if "introduction" in text_lower:
        sections.append({"title": "Introduction", "pages": "1-2"})
    if "method" in text_lower or "approach" in text_lower:
        sections.append({"title": "Methodology", "pages": "3-5"})
    if "result" in text_lower or "finding" in text_lower:
        sections.append({"title": "Results", "pages": "6-8"})
    if "conclusion" in text_lower:
        sections.append({"title": "Conclusion", "pages": "9-10"})
    
    # Default sections if none detected
    if not sections:
        sections = [
            {"title": "Content Overview", "pages": "1-3"},
            {"title": "Main Discussion", "pages": "4-7"},
            {"title": "Summary", "pages": "8-10"}
        ]
    
    # Determine complexity based on vocabulary and length
    complexity = "beginner"
    if word_count > 5000:
        complexity = "intermediate"
    if word_count > 10000 or len(detected_topics) > 5:
        complexity = "advanced"
    
    return {
        "word_count": word_count,
        "reading_time": reading_time,
        "detected_topics": detected_topics[:8],  # Limit to 8 topics
        "sections": sections,
        "complexity": complexity,
        "estimated_slides": min(12, max(4, len(sections) * 2))
    }

# PDF Upload Endpoint
@app.post("/api/upload", response_model=UploadResult)
async def upload_pdf(file: UploadFile = File(...)):
    """Process uploaded PDF and extract content for presentation generation"""
    
    # Validate file type
    if not file.content_type == "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Read file contents
    file_contents = await file.read()
    file_size_mb = len(file_contents) / (1024 * 1024)
    
    # Validate file size (10MB limit)
    if file_size_mb > 10:
        raise HTTPException(status_code=400, detail="File size must be less than 10MB")
    
    start_time = time.time()
    
    try:
        # Extract text from PDF
        extracted_text, page_count = extract_text_from_pdf(file_contents)
        
        # Analyze content
        analysis = analyze_document_content(extracted_text, file.filename)
        
        processing_time = round(time.time() - start_time, 2)
        
        # Create result
        result = UploadResult(
            success=True,
            message=f"Successfully processed '{file.filename}'",
            filename=file.filename,
            fileSize=f"{file_size_mb:.2f} MB",
            pages=page_count,
            readingTime=analysis["reading_time"],
            topics=len(analysis["detected_topics"]),
            processingTime=f"{processing_time} seconds",
            keyTopics=analysis["detected_topics"],
            extractedSections=analysis["sections"],
            generatedSlides=analysis["estimated_slides"],
            detectedLanguage="English",  # Could add language detection
            complexity=analysis["complexity"],
            extractedText=extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text
        )
        
        print(f"📄 PDF Processed: {file.filename} ({file_size_mb:.2f}MB)")
        print(f"📊 Analysis: {page_count} pages, {len(analysis['detected_topics'])} topics")
        print(f"⏱️  Processing time: {processing_time}s")
        
        return result
        
    except Exception as e:
        print(f"❌ PDF Processing Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 