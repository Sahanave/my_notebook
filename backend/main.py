from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn
import PyPDF2
import io
import time
import os
import tempfile
from datetime import datetime
from openai import OpenAI
from data_models import SlideContent, ReferenceLink, ConversationMessage, LiveUpdate, DocumentSummary, UploadResult
from parsing_info_from_pdfs import upload_single_pdf, generate_summary, create_vector_store, generate_slides_from_content, generate_qa_pairs_from_document, generate_slides_from_qa_pairs
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Are You Taking Notes API", version="1.0.0")

# Initialize OpenAI client
# You'll need to set OPENAI_API_KEY environment variable
openai_client = None
vector_store_id = None
current_document_summary = None  # Store the latest generated summary
current_qa_pairs = []  # Store the latest generated Q&A pairs

try:
    openai_client = OpenAI()  # Will use OPENAI_API_KEY from environment
    print("✅ OpenAI client initialized successfully")
except Exception as e:
    print(f"⚠️  OpenAI client not initialized: {e}")
    print("Set OPENAI_API_KEY environment variable to enable AI features")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



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
    if current_document_summary:
        return current_document_summary
    return sample_document_summary

@app.post("/api/generate-qa", response_model=List[dict])
async def generate_qa_pairs(use_current_document: bool = True):
    """Generate Q&A pairs from the currently uploaded document"""
    global current_document_summary, vector_store_id, current_qa_pairs
    
    if not openai_client:
        raise HTTPException(status_code=500, detail="OpenAI client not configured")
    
    if not current_document_summary:
        raise HTTPException(status_code=400, detail="No document summary available. Please upload a document first.")
    
    if not vector_store_id:
        raise HTTPException(status_code=400, detail="No vector store available. Please upload a document first.")
    
    try:
        # Generate Q&A pairs using the document summary and vector store
        qa_pairs = generate_qa_pairs_from_document(
            client=openai_client,
            summary=current_document_summary,
            vector_store_id=vector_store_id
        )
        
        # Store for future use
        current_qa_pairs = qa_pairs
        
        return qa_pairs
        
    except Exception as e:
        print(f"Error generating Q&A pairs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate Q&A pairs: {str(e)}")

@app.get("/api/qa-pairs", response_model=List[dict])
async def get_qa_pairs():
    """Get the current Q&A pairs for the uploaded document"""
    global current_qa_pairs
    
    if not current_qa_pairs:
        return []
    
    return current_qa_pairs

@app.post("/api/generate-slides", response_model=List[SlideContent])
async def generate_slides_from_qa():
    """Generate slides based on Q&A pairs from the uploaded document (auto-generates Q&A if needed)"""
    global openai_client, current_document_summary, current_qa_pairs, vector_store_id
    
    print(f"🔄 Generate slides request received")
    print(f"📊 Current state:")
    print(f"   - OpenAI client: {'✅ Available' if openai_client else '❌ Not configured'}")
    print(f"   - Document summary: {'✅ Available' if current_document_summary else '❌ None'}")
    print(f"   - Q&A pairs: {'✅ Available' if current_qa_pairs else '❌ None'} ({len(current_qa_pairs) if current_qa_pairs else 0} pairs)")
    print(f"   - Vector store: {'✅ Available' if vector_store_id else '❌ None'}")
    
    if not openai_client:
        error_msg = "OpenAI client not configured. Please check OPENAI_API_KEY environment variable."
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
    
    if not current_document_summary:
        error_msg = "No document summary available. Please upload a PDF document first."
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    
    if not vector_store_id:
        error_msg = "No vector store available. Please upload a PDF document first."
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    
    try:
        # Step 1: Generate Q&A pairs if they don't exist
        if not current_qa_pairs:
            print(f"🔄 No Q&A pairs found, generating them first...")
            current_qa_pairs = generate_qa_pairs_from_document(
                client=openai_client,
                summary=current_document_summary,
                vector_store_id=vector_store_id
            )
            print(f"✅ Generated {len(current_qa_pairs)} Q&A pairs")
        else:
            print(f"✅ Using existing {len(current_qa_pairs)} Q&A pairs")
        
        # Step 2: Generate slides using Q&A pairs
        print(f"🎯 Generating slides from {len(current_qa_pairs)} Q&A pairs...")
        print(f"📄 Document: {current_document_summary.title}")
        
        slides = generate_slides_from_qa_pairs(
            client=openai_client,
            qa_pairs=current_qa_pairs,
            document_summary=current_document_summary
        )
        
        print(f"✅ Generated {len(slides)} slides successfully")
        
        # Update the global sample_slides with generated content
        global sample_slides
        sample_slides = slides
        
        return slides
        
    except Exception as e:
        error_msg = f"Failed to generate slides: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"🔍 Error details: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/generate-andrew-ng-slides", response_model=List[SlideContent])
async def generate_andrew_ng_slides():
    """Generate slides based on Andrew Ng's research paper reading methodology"""
    global openai_client
    
    if not openai_client:
        raise HTTPException(status_code=500, detail="OpenAI client not configured")
    
    try:
        # Generate slides using Andrew Ng's methodology
        slides = generate_slides_from_content(
            client=openai_client,
            content="",  # The content is already embedded in the function
            title="How to Read Research Papers"
        )
        
        # Update the global sample_slides with generated content
        global sample_slides
        sample_slides = slides
        
        return slides
        
    except Exception as e:
        print(f"Error generating Andrew Ng slides: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate slides: {str(e)}")

# Helper function to parse AI summary into DocumentSummary structure
def parse_ai_summary_to_document_summary(ai_summary: str, filename: str) -> DocumentSummary:
    """Parse AI-generated summary text into DocumentSummary structure"""
    try:
        # Simple parsing - in production you might want more sophisticated parsing
        lines = ai_summary.split('\n')
        
        title = filename.replace('.pdf', '')
        abstract = ""
        key_points = []
        main_topics = []
        difficulty_level = "intermediate"
        document_type = "article"
        
        # Extract information from AI summary
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if "title:" in line.lower() or "document title:" in line.lower():
                title = line.split(':', 1)[1].strip()
            elif "abstract:" in line.lower() or "overview:" in line.lower():
                abstract = line.split(':', 1)[1].strip()
            elif "key points:" in line.lower():
                current_section = "key_points"
            elif "main topics:" in line.lower() or "topics:" in line.lower():
                current_section = "main_topics"
            elif "difficulty:" in line.lower():
                level = line.split(':', 1)[1].strip().lower()
                if level in ["beginner", "intermediate", "advanced"]:
                    difficulty_level = level
            elif "document type:" in line.lower() or "type:" in line.lower():
                doc_type = line.split(':', 1)[1].strip().lower()
                if doc_type in ["research_paper", "tutorial", "book_chapter", "article"]:
                    document_type = doc_type
            elif line.startswith('-') or line.startswith('•'):
                content = line[1:].strip()
                if current_section == "key_points":
                    key_points.append(content)
                elif current_section == "main_topics":
                    main_topics.append(content)
            elif not abstract and len(line) > 50:  # Likely the abstract if it's a long line
                abstract = line
        
        # Fallback values if parsing didn't extract everything
        if not abstract:
            abstract = "Document summary generated from PDF content."
        if not key_points:
            key_points = ["Document analysis completed", "Content extracted and processed"]
        if not main_topics:
            main_topics = ["General content", "Document analysis"]
            
        return DocumentSummary(
            title=title,
            abstract=abstract,
            key_points=key_points,
            main_topics=main_topics,
            difficulty_level=difficulty_level,
            estimated_read_time="30 minutes",  # Could be calculated from word count
            document_type=document_type,
            authors=["Extracted from PDF"],
            publication_date=datetime.now().strftime("%Y-%m-%d")
        )
        
    except Exception as e:
        print(f"Error parsing AI summary: {e}")
        # Return a basic summary if parsing fails
        return DocumentSummary(
            title=filename.replace('.pdf', ''),
            abstract="AI-generated summary of the uploaded document.",
            key_points=["Document processed successfully", "Content analysis completed"],
            main_topics=["Document content", "Analysis results"],
            difficulty_level="intermediate",
            estimated_read_time="30 minutes",
            document_type="article",
            authors=["Extracted from PDF"],
            publication_date=datetime.now().strftime("%Y-%m-%d")
        )

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
    global current_document_summary, vector_store_id
    
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
        # Save PDF file locally
        temp_dir = tempfile.mkdtemp()
        temp_pdf_path = os.path.join(temp_dir, file.filename)
        
        with open(temp_pdf_path, 'wb') as temp_file:
            temp_file.write(file_contents)
        
        # Create vector store and upload PDF for Q&A functionality
        if openai_client:
            print(f"🔄 Creating vector store for: {file.filename}")
            
            # Create a new vector store for this document
            store_name = f"document_store_{file.filename.replace('.pdf', '')}_{int(time.time())}"
            vector_store_details = create_vector_store(openai_client, store_name)
            
            if vector_store_details and 'id' in vector_store_details:
                vector_store_id = vector_store_details['id']
                print(f"✅ Vector store created: {vector_store_id}")
                
                # Upload PDF to vector store
                print(f"🔄 Uploading PDF to vector store...")
                upload_result = upload_single_pdf(openai_client, temp_pdf_path, vector_store_id)
                
                if upload_result['status'] == 'success':
                    print(f"✅ PDF uploaded to vector store successfully")
                else:
                    print(f"⚠️ PDF upload to vector store failed: {upload_result.get('error', 'Unknown error')}")
            else:
                print(f"⚠️ Failed to create vector store")
                vector_store_id = None
            
            # Generate AI summary
            current_document_summary = generate_summary(openai_client, temp_pdf_path)
            print(f"✅ AI summary generated for: {file.filename}")
        else:
            print(f"⚠️ OpenAI client not available, skipping vector store creation")
            vector_store_id = None
        
        # Basic analysis for response
        extracted_text, page_count = extract_text_from_pdf(file_contents)
        analysis = analyze_document_content(extracted_text, file.filename)
        processing_time = round(time.time() - start_time, 2)
        
        # Clean up temporary file
        os.remove(temp_pdf_path)
        os.rmdir(temp_dir)
        
        # Return simple result
        result = UploadResult(
            success=True,
            message=f"Successfully processed '{file.filename}' with AI analysis and vector store creation",
            filename=file.filename,
            fileSize=f"{file_size_mb:.2f} MB",
            pages=page_count,
            readingTime=analysis["reading_time"],
            topics=len(analysis["detected_topics"]),
            processingTime=f"{processing_time} seconds",
            keyTopics=analysis["detected_topics"],
            extractedSections=analysis["sections"],
            generatedSlides=analysis["estimated_slides"],
            detectedLanguage="English",
            complexity=analysis["complexity"],
            extractedText=extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text
        )
        
        print(f"📄 PDF Processed: {file.filename} ({file_size_mb:.2f}MB) in {processing_time}s")
        if vector_store_id:
            print(f"🗃️ Vector store ready for Q&A: {vector_store_id}")
        
        return result
        
    except Exception as e:
        print(f"❌ PDF Processing Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 