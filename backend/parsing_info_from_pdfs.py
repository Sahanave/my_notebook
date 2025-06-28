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
    
    # Truncate text if too long (OpenAI has token limits)
    max_text_length = 15000  # Approximately 3000-4000 tokens
    if len(text) > max_text_length:
        text = text[:max_text_length] + "..."

    prompt = (
        "Please analyze this document and generate a comprehensive summary. "
        "Extract structured information from the document."
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
            tool_choice="auto"
        )

        tool_call = response.choices[0].message.tool_calls[0]
        structured_json = json.loads(tool_call.function.arguments)
        structured_output = DocumentSummary(**structured_json)
        return structured_output
    
    except Exception as e:
        print(f"Error generating summary: {e}")
        return f"Error generating summary: {str(e)}"

