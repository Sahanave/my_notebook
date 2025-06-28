# Are You Taking Notes? 📝

An interactive presentation platform for "Building Agents with Claude on Vertex AI" featuring a modern Next.js frontend with a Python FastAPI backend.

## 🚀 Quick Start

This application has both a **Next.js frontend** and a **Python FastAPI backend** for PDF processing.

### Frontend Setup (Next.js)
```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

### Backend Setup (Python FastAPI)
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the Python backend
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🔧 Development Workflow

1. **Start Backend First**:
   ```bash
   cd backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   Backend will run on: http://localhost:8000

2. **Start Frontend**:
   ```bash
   npm run dev
   ```
   Frontend will run on: http://localhost:3000

3. **Test PDF Upload**:
   - Upload a PDF through the frontend
   - The frontend will send the PDF to the Python backend
   - Backend will extract text and analyze content
   - Results will be displayed in the frontend

## 📄 PDF Processing Features

The Python backend provides:

- **Text Extraction**: Uses PyPDF2 to extract text from PDF files
- **Content Analysis**: Analyzes extracted text for key topics and complexity
- **Section Detection**: Identifies document sections (Introduction, Methodology, etc.)
- **Slide Generation**: Estimates optimal number of slides based on content
- **Reading Time**: Calculates estimated reading time
- **Topic Detection**: Identifies key technical topics in the document

## 🛠️ Architecture

- **Frontend**: Next.js 14 with TypeScript & Tailwind CSS
- **Backend**: Python FastAPI with async endpoints
- **Deployment**: Vercel (Frontend) + GitLab CI/CD
- **Database**: Supabase (available for future features)

## ✨ Features

- 📑 **Dynamic Slide Presentation** - Navigate through slides with real-time content
- 💬 **Live Q&A Chat** - Interactive conversation with message history
- 📚 **Dynamic Reference Links** - API-driven resource links
- 📢 **Live Updates** - Real-time announcements and notifications
- 🎥 **Video Stream Placeholder** - Ready for live video integration
- 📱 **Responsive Design** - Mobile-first Tailwind CSS styling

## 🛠️ Local Development

### Prerequisites

- Node.js 18+ 
- Python 3.8+
- npm or yarn

## 🛠 API Endpoints

### Frontend APIs (Next.js - Vercel deployment)
- `GET /api/slides` - Get presentation slides
- `GET /api/references` - Get reference links
- `GET /api/conversation` - Get Q&A messages
- `GET /api/live-updates` - Get live announcements
- `GET /api/document-summary` - Get document overview

### Backend APIs (Python FastAPI - PDF processing)
- `POST /api/upload` - Upload and process PDF files
- `GET /api/slides` - Get slides (with processed content)
- `GET /api/references` - Get references
- `GET /api/conversation` - Get/post conversation messages
- `GET /api/live-updates` - Get live updates
- `GET /api/document-summary` - Get document summary

## 🔄 Deployment Options

### Option 1: Frontend Only (Current Vercel Deployment)
- Only Next.js frontend deployed
- Uses placeholder API routes
- PDF upload uses Next.js API route (limited processing)

### Option 2: Full Stack (Frontend + Python Backend)
- Deploy Next.js frontend to Vercel
- Deploy Python backend to a service like Railway, Heroku, or Google Cloud Run
- Set `NEXT_PUBLIC_API_URL` environment variable to point to Python backend

## 🎯 Technology Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: Python FastAPI, PyPDF2, Pydantic
- **Deployment**: Vercel (Frontend), Python backend can be deployed anywhere
- **Styling**: Tailwind CSS with custom components

## 📊 Environment Variables

```bash
# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000  # Point to Python backend

# Backend
# No specific environment variables required for basic setup
```

## 🧪 Testing

To test PDF processing:

1. Start both frontend and backend
2. Go to http://localhost:3000
3. Upload a PDF file using the upload interface
4. Check the console logs in the Python backend for processing details
5. View the analysis results in the frontend

## 📚 Dependencies

### Frontend
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS

### Backend
- FastAPI
- PyPDF2 (PDF text extraction)
- Pydantic (data validation)
- Uvicorn (ASGI server)
- Python-multipart (file uploads)

Ready to process your documents! 🚀

## 🚢 Deployment

The application is automatically deployed via GitLab CI/CD:

1. **Push to GitLab main branch**
2. **Vercel automatically deploys** the Next.js frontend
3. **Backend can be deployed** to any Python hosting service

### Environment Variables for Production

- `NEXT_PUBLIC_API_URL` - Backend API URL for production

## 🔮 Future Enhancements

- [ ] Live video streaming integration
- [ ] Real-time WebSocket connections
- [ ] User authentication with Supabase
- [ ] Slide deck upload functionality
- [ ] Chat moderation features
- [ ] Analytics and engagement tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test both frontend and backend
5. Submit a pull request

## 📄 License

This project is part of the Claude Agents on Vertex AI presentation series.
Build a Multi-Agent system meant to help visual learners understand complex academic papers and books in a very engaging way. Inspired by Notebook LLM 
