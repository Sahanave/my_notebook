#!/usr/bin/env python3
"""
Simple test script for the PDF processing backend
"""

import requests
import os
import sys

def test_backend_health():
    """Test if the backend is running"""
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ Backend is running!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on http://localhost:8000")
        return False

def test_pdf_upload(pdf_path):
    """Test PDF upload functionality"""
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return False
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
            response = requests.post("http://localhost:8000/api/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ PDF upload successful!")
            print(f"📄 File: {result['filename']}")
            print(f"📊 Pages: {result['pages']}")
            print(f"⏱️  Processing time: {result['processingTime']}")
            print(f"🎯 Topics detected: {result['topics']}")
            print(f"📚 Key topics: {', '.join(result['keyTopics'][:3])}...")
            print(f"🧩 Complexity: {result['complexity']}")
            print(f"📖 Reading time: {result['readingTime']}")
            return True
        else:
            print(f"❌ PDF upload failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing PDF upload: {str(e)}")
        return False

def main():
    print("🧪 Testing PDF Processing Backend\n")
    
    # Test backend health
    if not test_backend_health():
        print("\n💡 To start the backend, run:")
        print("   cd backend")
        print("   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    print()
    
    # Test PDF upload if file provided
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        test_pdf_upload(pdf_path)
    else:
        print("💡 To test PDF upload, provide a PDF file path:")
        print(f"   python {sys.argv[0]} path/to/your/document.pdf")
    
    print("\n🌐 Backend endpoints available at:")
    print("   - Health check: http://localhost:8000/")
    print("   - API docs: http://localhost:8000/docs")
    print("   - PDF upload: POST http://localhost:8000/api/upload")

if __name__ == "__main__":
    main() 