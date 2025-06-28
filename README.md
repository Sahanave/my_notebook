# Are You Taking Notes? 📝

An interactive presentation platform for "Building Agents with Claude on Vertex AI" featuring a modern Next.js frontend with a Python FastAPI backend.

## 🚀 Live Demo

**Production URL**: [https://815d4da6-1541-4f0d-ab14-b583f9dab9f.vercel.app](https://815d4da6-1541-4f0d-ab14-b583f9dab9f.vercel.app)

## 🏗️ Architecture

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

### Backend Setup (FastAPI)

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the FastAPI backend:**
   ```bash
   cd backend
   python main.py
   ```

   The API will be available at `http://localhost:8000`
   - API docs: `http://localhost:8000/docs`
   - Alternative docs: `http://localhost:8000/redoc`

### Frontend Setup (Next.js)

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set environment variables** (optional):
   ```bash
   # Create .env.local file
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Run development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

### Building for Production

```bash
npm run build
npm start
```

## 🔌 API Endpoints

### Slides
- `GET /api/slides` - Get all slides
- `GET /api/slides/{slide_number}` - Get specific slide

### References  
- `GET /api/references` - Get reference links

### Conversation
- `GET /api/conversation` - Get chat messages
- `POST /api/conversation` - Add new message

### Live Updates
- `GET /api/live-updates` - Get announcements

## 📁 Project Structure

```
├── src/
│   ├── app/              # Next.js app router
│   ├── components/       # React components
│   ├── lib/             # API client utilities
│   └── types/           # TypeScript interfaces
├── backend/
│   └── main.py          # FastAPI application
├── requirements.txt     # Python dependencies
└── package.json        # Node.js dependencies
```

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
