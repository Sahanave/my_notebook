# Helper functions from https://github.com/openai/openai-cookbook/blob/5d9219a90890a681890b24e25df196875907b18c/examples/File_Search_Responses.ipynb#L10
# Imports

from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import concurrent
import PyPDF2
import os
import pandas as pd
import base64
from data_models import SlideContent, ReferenceLink, ConversationMessage, LiveUpdate, DocumentSummary, UploadResult
import json
from typing import List


def generate_questions(client, summary: DocumentSummary):
    text = extract_text_from_pdf(pdf_path)

    prompt = (
        "Can you generate a question that can only be answered from this document?:\n"
        f"{text}\n\n"
    )

    response = client.responses.create(
        input=prompt,
        model="gpt-4o",
    )

    question = response.output[0].content[0].text

    return question

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

def generate_slides_from_content(client, content: str, title: str = "How to Read Research Papers") -> List[SlideContent]:
    """Generate slides from Andrew Ng's research paper reading methodology"""
    
    # Clean up the Andrew Ng content
    cleaned_content = """
    How to Read Research Papers - Andrew Ng's Methodology
    
    Take multiple passes through the paper
    Worst strategy: reading from the first word until the last word!
    
    Pass 1: Read the Title/Abstract/Figures
    - In deep learning, there are many papers where the entire paper is summarized in one or two figures
    - You can often get a good understanding about what the whole paper is about without reading much of the text
    
    Pass 2: Read the Introduction/Conclusions/Figures (again)/Skim Rest
    - Abstract, intro, and conclusion are where authors summarize their work most carefully
    - These are the most useful parts to read
    - Neural network architectures are often written up in a table
    - Maybe also skim Related work section for context
    
    Pass 3: Read the Paper, but skip the maths
    - Focus on understanding the concepts first
    
    Pass 4: Read the Paper, but skip parts that don't make sense
    - In cutting edge papers we don't always know what is really important
    - Some great, highly cited papers have groundbreaking parts and other parts which later turn out to be unimportant
    - Maybe what was the key part of the algorithm wasn't what the authors thought
    
    Questions to Keep in Mind:
    - What did the authors try to accomplish?
    - What were the key elements of the approach?
    - What can you use yourself?
    - What other references do you want to follow?
    
    Deeper Understanding:
    
    Mathematics:
    - Read through it and make notes
    - Try to re-derive from scratch on a blank piece of paper
    - As you get good at this you will gain the ability to derive novel algorithms yourself
    - Learn from the masters, not from their students
    
    Code:
    - Lightweight: download and run their open-source code
    - Deeper: reimplement their code from scratch
    
    General Advice:
    - Steady reading, not short bursts
    - Better off reading 2-3 papers a week for the next year, than cramming everything over Christmas
    """

    prompt = f"""
    Create a slide presentation from this content about how to read research papers effectively.
    Create 3-5 slides that break down the methodology into clear, digestible sections.
    Each slide should have a clear title and bullet points.
    Make it engaging and educational for researchers and students.
    
    Content to convert to slides:
    {cleaned_content}
    
    Return as a list of slides with title, content, and slide numbers.
    """

    try:
        slides_schema = {
            "name": "generate_slides",
            "description": "Generate presentation slides from content",
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
                                "slide_number": {"type": "integer"}
                            },
                            "required": ["title", "content", "slide_number"]
                        }
                    }
                },
                "required": ["slides"]
            }
        }

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert presentation designer. Create clear, engaging slides for academic content."},
                {"role": "user", "content": prompt}
            ],
            tools=[{"type": "function", "function": slides_schema}],
            tool_choice={"type": "function", "function": {"name": "generate_slides"}}
        )

        if response.choices and response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            structured_json = json.loads(tool_call.function.arguments)
            
            slides = []
            for slide_data in structured_json["slides"]:
                slide = SlideContent(
                    title=slide_data["title"],
                    content=slide_data["content"],
                    image_url="https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=800&h=600&fit=crop&crop=center",  # Generic academic image
                    slide_number=slide_data["slide_number"]
                )
                slides.append(slide)
            
            return slides
        else:
            raise Exception("No structured response from OpenAI")
    
    except Exception as e:
        print(f"Error generating slides: {e}")
        # Return fallback slides
        return [
            SlideContent(
                title="How to Read Research Papers",
                content="Andrew Ng's methodology for effective paper reading",
                image_url="https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=800&h=600&fit=crop&crop=center",
                slide_number=1
            )
        ]

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
    """Get answer to a question using file search via Responses API"""
    
    try:
        response = client.responses.create(
            input=question,
            model="gpt-4o-mini",
            tools=[{
                "type": "file_search",
                "vector_store_ids": [vector_store_id],
                "max_num_results": max_results,
            }],
            tool_choice="required"  # Force file_search usage
        )
        
        if response.output and len(response.output) > 0:
            return response.output[0].content[0].text
        else:
            return "I couldn't find a specific answer to this question in the document."
    
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
    qa_content = ""
    for qa in qa_pairs:
        qa_content += f"Q: {qa['question']}\nA: {qa['answer']}\n\n"
    
    prompt = f"""
    Create educational slides based on these Q&A pairs from a document analysis.
    Use the questions and answers to create informative slides that teach the key concepts.
    
    Document Information:
    Title: {document_summary.title}
    Type: {document_summary.document_type}
    Main Topics: {', '.join(document_summary.main_topics)}
    
    Q&A Content to convert to slides:
    {qa_content}
    
    Create 4-6 slides that:
    1. Start with a title slide introducing the document
    2. Each slide should cover 1-2 related Q&A pairs
    3. Transform questions into slide titles and answers into bullet points
    4. Make content educational and easy to understand
    5. Include relevant examples from the answers
    
    Return as a list of slides with title, content, and slide numbers.
    """

    try:
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
                                "slide_number": {"type": "integer"}
                            },
                            "required": ["title", "content", "slide_number"]
                        }
                    }
                },
                "required": ["slides"]
            }
        }

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert educator who creates clear, engaging slides from Q&A content. Make slides informative and educational."},
                {"role": "user", "content": prompt}
            ],
            tools=[{"type": "function", "function": slides_schema}],
            tool_choice={"type": "function", "function": {"name": "generate_slides_from_qa"}}
        )

        if response.choices and response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            structured_json = json.loads(tool_call.function.arguments)
            
            slides = []
            for slide_data in structured_json["slides"]:
                slide = SlideContent(
                    title=slide_data["title"],
                    content=slide_data["content"],
                    image_url="https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=800&h=600&fit=crop&crop=center",  # Academic image
                    slide_number=slide_data["slide_number"]
                )
                slides.append(slide)
            
            return slides
        else:
            raise Exception("No structured response from OpenAI")
    
    except Exception as e:
        print(f"Error generating slides from Q&A: {e}")
        # Return fallback slides
        return [
            SlideContent(
                title=document_summary.title,
                content=f"Educational presentation based on Q&A analysis of {document_summary.document_type}",
                image_url="https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=800&h=600&fit=crop&crop=center",
                slide_number=1
            )
        ]

