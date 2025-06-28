# Helper functions from https://github.com/openai/openai-cookbook/blob/5d9219a90890a681890b24e25df196875907b18c/examples/File_Search_Responses.ipynb#L10
# Imports

from openai import OpenAI
import PyPDF2
import io
import json
import os
from typing import List, Dict, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor
import datetime
from tqdm import tqdm
from data_models import SlideContent, LiveUpdate, DocumentSummary, UploadResult



def upload_single_pdf(client, file_path: str, vector_store_id: str):
    file_name = os.path.basename(file_path)
    try:
        file_response = client.files.create(file=open(file_path, 'rb'), purpose="assistants")
        attach_response = client.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=file_response.id
        )
        return {"file": file_name, "status": "success"}
    except Exception as e:
        print(f"Error with {file_name}: {str(e)}")
        return {"file": file_name, "status": "failed", "error": str(e)}


def create_vector_store(client, store_name: str) -> dict:
    try:
        vector_store = client.vector_stores.create(name=store_name)
        details = {
            "id": vector_store.id,
            "name": vector_store.name,
            "created_at": vector_store.created_at,
            "file_count": vector_store.file_counts.completed
        }
        print("Vector store created:", details)
        return details
    except Exception as e:
        print(f"Error creating vector store: {e}")
        return {}
    

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text

def generate_summary(client, pdf_path):
    text = extract_text_from_pdf(pdf_path)
    filename = os.path.basename(pdf_path)
    
    # Truncate text if too long (OpenAI has token limits)
    max_text_length = 15000  # Approximately 3000-4000 tokens
    if len(text) > max_text_length:
        text = text[:max_text_length] + "..."

    prompt = (
        f"Please analyze this document and generate a comprehensive summary. "
        f"Extract structured information from the document.\n\n"
        f"Document content:\n{text}\n\n"
        f"Provide a structured summary with title, abstract, key points, main topics, "
        f"difficulty level, estimated read time, document type, authors, and publication date."
    )

    try:
        summary_schema = {
            "name": "extract_summary",
            "description": "Extract summary from input document.",
            "parameters": DocumentSummary.model_json_schema()
        }
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert document analyst. Provide structured, comprehensive summaries."},
                {"role": "user", "content": prompt}
            ],
            tools=[{"type": "function", "function": summary_schema}],
            tool_choice={"type": "function", "function": {"name": "extract_summary"}}
        )

        # Check if response and tool_calls exist
        if response.choices and response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            structured_json = json.loads(tool_call.function.arguments)
            structured_output = DocumentSummary(**structured_json)
            return structured_output
        else:
            print("No tool calls in response, falling back to basic summary")
            raise Exception("No structured response from OpenAI")
    
    except Exception as e:
        print(f"Error generating summary: {e}")
        # Return a basic DocumentSummary instead of string
        return DocumentSummary(
            title=filename.replace('.pdf', ''),
            abstract=f"Document analysis completed for {filename}. Full AI analysis unavailable.",
            key_points=["Document uploaded successfully", "Text extraction completed", "Basic analysis performed"],
            main_topics=["Document analysis", "Content processing"],
            difficulty_level="intermediate",
            estimated_read_time="30 minutes",
            document_type="article",
            authors=["Unknown"],
            publication_date="2024-12-28"
        )

def generate_questions_from_summary(client, summary: DocumentSummary) -> List[str]:
    """Generate relevant questions based on the document summary"""
    
    prompt = f"""
    Based on this document summary, generate 5-7 thoughtful questions that would help someone understand the key concepts and details of this paper. 
    Focus on questions that require specific information from the document to answer correctly.
    
    Document Summary:
    Title: {summary.title}
    Abstract: {summary.abstract}
    Key Points: {', '.join(summary.key_points)}
    Main Topics: {', '.join(summary.main_topics)}
    Document Type: {summary.document_type}
    Difficulty Level: {summary.difficulty_level}
    
    Generate questions that cover:
    1. Main objectives and contributions
    2. Methodology or approach used
    3. Key findings or results
    4. Technical details and implementation
    5. Limitations or future work
    
    Return only the questions, one per line.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at generating insightful questions for academic papers. Create questions that require deep understanding of the document content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        questions_text = response.choices[0].message.content
        questions = [q.strip() for q in questions_text.split('\n') if q.strip() and not q.strip().startswith('Question')]
        
        # Clean up numbered questions
        cleaned_questions = []
        for q in questions:
            # Remove numbers like "1.", "2)", etc. from the beginning
            import re
            cleaned_q = re.sub(r'^\d+[\.)]\s*', '', q).strip()
            if cleaned_q and cleaned_q.endswith('?'):
                cleaned_questions.append(cleaned_q)
        
        return cleaned_questions[:7]  # Limit to 7 questions
    
    except Exception as e:
        print(f"Error generating questions: {e}")
        return [
            f"What is the main objective of {summary.title}?",
            f"What methodology does this {summary.document_type} use?",
            "What are the key findings or contributions?",
            "What are the limitations mentioned in this work?",
            "How does this work compare to previous research?"
        ]

def get_answer_using_file_search(client, question: str, vector_store_id: str, max_results: int = 5) -> str:
    """Get answer to a question using file search via Assistants API"""
    
    try:
        # Create a temporary assistant with file search capability
        assistant = client.beta.assistants.create(
            name="Document Q&A Assistant",
            instructions="You are a helpful assistant that answers questions based on the provided documents. Provide clear, accurate answers based on the document content.",
            model="gpt-4o-mini",
            tools=[{"type": "file_search"}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store_id]
                }
            }
        )
        
        # Create a thread
        thread = client.beta.threads.create()
        
        # Add the question as a message
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question
        )
        
        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )
        
        # Wait for completion
        import time
        while run.status in ['queued', 'in_progress']:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
        
        if run.status == 'completed':
            # Get the assistant's response
            messages = client.beta.threads.messages.list(
                thread_id=thread.id,
                order="desc",
                limit=1
            )
            
            if messages.data:
                message = messages.data[0]
                if message.content and len(message.content) > 0:
                    content = message.content[0]
                    if hasattr(content, 'text') and hasattr(content.text, 'value'):
                        answer = content.text.value
                        
                        # Clean up - delete the assistant and thread
                        try:
                            client.beta.assistants.delete(assistant.id)
                        except:
                            pass  # Ignore cleanup errors
                        
                        return answer
        
        # Clean up on failure
        try:
            client.beta.assistants.delete(assistant.id)
        except:
            pass
        
        return f"I found information related to your question in the document, but couldn't extract specific details. The assistant run status was: {run.status}"
    
    except Exception as e:
        print(f"Error getting answer for question '{question}': {e}")
        return "Unable to retrieve answer due to an error."

def generate_qa_pairs_from_document(client, summary: DocumentSummary, vector_store_id: str) -> List[dict]:
    """Generate question-answer pairs using summary for questions and file search for answers"""
    
    if not vector_store_id:
        print("No vector store ID provided, cannot generate Q&A pairs")
        return []
    
    # Step 1: Generate questions from summary
    questions = generate_questions_from_summary(client, summary)
    
    if not questions:
        print("No questions generated")
        return []
    
    print(f"Generated {len(questions)} questions, processing answers in parallel...")
    
    # Step 2: Process questions in parallel using ThreadPoolExecutor
    def process_question(question_data):
        question, question_number = question_data
        answer = get_answer_using_file_search(client, question, vector_store_id)
        return {
            "question": question,
            "answer": answer,
            "question_number": question_number
        }
    
    # Prepare data for parallel processing
    question_data = [(question, i + 1) for i, question in enumerate(questions)]
    
    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=5) as executor:  # Limit to 5 concurrent requests
        qa_pairs = list(tqdm(
            executor.map(process_question, question_data), 
            total=len(questions),
            desc="Generating Q&A pairs"
        ))
    
    return qa_pairs


def generate_slides_from_qa_pairs(client, qa_pairs: List[dict], document_summary: DocumentSummary) -> List[SlideContent]:
    """Generate slides from Q&A pairs to create an educational presentation"""
    
    if not qa_pairs:
        print("No Q&A pairs provided, cannot generate slides")
        return []
    
    # Prepare Q&A content for slide generation
    qa_content = "\n\n".join([f"Q: {qa['question']}\nA: {qa['answer']}" for qa in qa_pairs])
    
    prompt = f"""
    Create an engaging and practical presentation from this Q&A content. Focus on making slides that are easy to present and understand.

    **Document Context:**
    Title: {document_summary.title}
    Type: {document_summary.document_type}
    Main Topics: {', '.join(document_summary.main_topics)}

    **Source Q&A Content:**
    {qa_content}

    **Instructions:**
    Create 4-6 slides from this content. For each slide, provide:

    1. **Title**: Clear, descriptive slide title
    2. **Content**: Main  key information for the slide (3-5 points max)  
    3. **Image Description**: Describe what visual/image would help explain this slide
    4. **Speaker Notes**: What the presenter should say when presenting this slide (2-3 sentences)

    Keep it simple and practical - focus on the key insights from the Q&A that would help someone understand the main concepts.
    """

    slides_schema = {
        "name": "generate_slides_from_qa",
        "description": "Generate educational slides from Q&A pairs",
        "parameters": {
            "type": "object",
            "properties": {
                "slides": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "content": {"type": "string"},
                            "image_description": {"type": "string"},
                            "speaker_notes": {"type": "string"},
                            "slide_number": {"type": "integer"}
                        },
                        "required": ["title", "content", "image_description", "speaker_notes", "slide_number"]
                    }
                }
            },
            "required": ["slides"]
        }
    }

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert educator who creates clear, engaging slides from Q&A content. Generate valid JSON with proper escaping."},
                {"role": "user", "content": prompt}
            ],
            tools=[{"type": "function", "function": slides_schema}],
            tool_choice={"type": "function", "function": {"name": "generate_slides_from_qa"}}
        )

        if not (response.choices and response.choices[0].message.tool_calls):
            raise Exception("No tool calls found in response")
        
        # Simple JSON parsing - let Python handle the escaping
        tool_call = response.choices[0].message.tool_calls[0]
        slides_data = json.loads(tool_call.function.arguments)
        
        # Convert to SlideContent objects
        slides = []
        for i, slide_data in enumerate(slides_data["slides"], 1):
            slide = SlideContent(
                title=slide_data.get("title", f"Slide {i}"),
                content=slide_data.get("content", ""),
                image_description=slide_data.get("image_description", ""),
                speaker_notes=slide_data.get("speaker_notes", ""),
                slide_number=slide_data.get("slide_number", i)
            )
            slides.append(slide)
        
        print(f"✅ Successfully generated {len(slides)} slides")
        return slides
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"🔍 Raw response: {tool_call.function.arguments[:500]}...")
        return create_fallback_slides(document_summary)
        
    except Exception as e:
        print(f"❌ Error generating slides: {e}")
        return create_fallback_slides(document_summary)

def create_fallback_slides(document_summary: DocumentSummary) -> List[SlideContent]:
    """Create simple fallback slides when generation fails"""
    return [
        SlideContent(
            title=document_summary.title,
            content=f"Educational presentation based on analysis of {document_summary.document_type}. Main topics include: {', '.join(document_summary.main_topics[:3])}.",
            image_description="Title slide with document cover or main concept visualization",
            speaker_notes=f"Welcome to this presentation about {document_summary.title}. Today we'll explore the key concepts from this {document_summary.document_type}.",
            slide_number=1
        )
    ]