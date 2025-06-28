# API Contract Documentation

This document defines the contract between the **Next.js Frontend** and **FastAPI Backend** for the "Are You Taking Notes" presentation platform.

## 🏗️ Architecture Overview

```
┌─────────────────┐    HTTP/REST     ┌─────────────────┐
│   Next.js       │ ◄──────────────► │   FastAPI       │
│   Frontend      │    JSON API      │   Backend       │
│   (TypeScript)  │                  │   (Python)      │
└─────────────────┘                  └─────────────────┘
```

## 📋 Frontend Expectations from Backend

### 🌐 Base Configuration

- **Base URL**: Configurable via `NEXT_PUBLIC_API_URL` environment variable
- **Default**: `http://localhost:8000` (development)
- **Protocol**: HTTP/HTTPS REST API
- **Content-Type**: `application/json`
- **CORS**: Must allow frontend domain origins

### 🔗 Required API Endpoints

#### 1. Health Check
```http
GET /
```
**Purpose**: Verify backend is running  
**Response**: `{ "message": "Are You Taking Notes API is running!" }`

#### 2. Slides Management
```http
GET /api/slides
```
**Purpose**: Get all available slides  
**Response**: Array of `SlideContent` objects

```http
GET /api/slides/{slide_number}
```
**Purpose**: Get specific slide by number  
**Parameters**: `slide_number` (integer, path parameter)  
**Response**: Single `SlideContent` object

#### 3. Reference Links
```http
GET /api/references
```
**Purpose**: Get all reference links  
**Response**: Array of `ReferenceLink` objects

#### 4. Live Conversation
```http
GET /api/conversation
```
**Purpose**: Get current conversation messages  
**Response**: Array of `ConversationMessage` objects

```http
POST /api/conversation
```
**Purpose**: Add new message to conversation  
**Body**: `{ "message": string, "user": string }`  
**Response**: Single `ConversationMessage` object

#### 5. Live Updates
```http
GET /api/live-updates
```
**Purpose**: Get live announcements and updates  
**Response**: Array of `LiveUpdate` objects

---

## 📊 Data Models & Interfaces

### SlideContent
```typescript
interface SlideContent {
  title: string;           // Slide title/heading
  content: string;         // Descriptive text content
  image_url: string;       // URL to slide image/visual
  slide_number: number;    // Slide position (1-based)
}
```

**Frontend Usage**:
- Displays `title` in slide header
- Shows `image_url` as main slide visual
- Renders `content` as description text
- Uses `slide_number` for navigation

**Backend Requirements**:
- `image_url` must be accessible URL (placeholder or real image)
- `slide_number` should be unique and sequential
- All fields are required (no null/undefined values)

### ReferenceLink
```typescript
interface ReferenceLink {
  title: string;           // Link display name
  url: string;            // Target URL (full HTTP/HTTPS)
  description: string;     // Link description/context
}
```

**Frontend Usage**:
- Creates clickable links with `url`
- Displays `title` as link text
- Shows `description` as subtitle

**Backend Requirements**:
- `url` must be valid HTTP/HTTPS URL
- Links open in new tab (`target="_blank"`)
- All fields required for proper display

### ConversationMessage
```typescript
interface ConversationMessage {
  id: number;             // Unique message identifier
  user: string;           // User/sender name
  message: string;        // Message content
  timestamp: string;      // ISO 8601 datetime string
  type: "question" | "answer" | "comment";  // Message category
}
```

**Frontend Usage**:
- Renders messages in chronological order
- Color-codes by `type` (blue=question, green=answer, gray=comment)
- Formats `timestamp` for display
- Uses `id` for React keys

**Backend Requirements**:
- `id` must be unique across all messages
- `timestamp` in ISO 8601 format (e.g., "2024-12-28T10:30:00Z")
- `type` must be one of: "question", "answer", "comment"
- Auto-increment `id` for new messages

### LiveUpdate
```typescript
interface LiveUpdate {
  message: string;        // Update/announcement text
  timestamp: string;      // ISO 8601 datetime string
  type: "info" | "question" | "announcement";  // Update category
}
```

**Frontend Usage**:
- Displays as notification banners
- Color-codes by `type` (blue=announcement, green=info, yellow=question)
- Shows most recent updates prominently

**Backend Requirements**:
- `type` must be one of: "info", "question", "announcement"
- `timestamp` for chronological ordering
- Keep recent updates (last 5-10 items)

---

## 🔄 API Response Formats

### Success Responses
```json
// Single object
{
  "title": "Welcome to Claude Agents",
  "content": "Building intelligent agents...",
  "image_url": "https://example.com/slide1.jpg",
  "slide_number": 1
}

// Array response
[
  { "id": 1, "user": "Alice", "message": "Hello!", ... },
  { "id": 2, "user": "Bob", "message": "Hi there!", ... }
]
```

### Error Responses
```json
// 4xx/5xx status codes with JSON body
{
  "detail": "Slide number 99 not found"
}
```

---

## 🛡️ Error Handling Expectations

### Frontend Error Handling
- **Network Errors**: Shows "Failed to load content" with retry button
- **API Errors**: Displays specific error message from `detail` field
- **Timeouts**: Falls back to placeholder content
- **Invalid Data**: Graceful degradation with default values

### Backend Error Requirements
- **404 Not Found**: For non-existent slides (`GET /api/slides/{invalid_number}`)
- **400 Bad Request**: For invalid POST data
- **500 Internal Server Error**: For server-side issues
- **Consistent Format**: Always return JSON with `detail` field

### Required HTTP Status Codes
- `200 OK`: Successful data retrieval
- `201 Created`: Successful message creation
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Backend errors

---

## ⚡ Performance Expectations

### Response Times
- **Slide Loading**: < 500ms
- **Message Posting**: < 300ms
- **Reference Loading**: < 200ms
- **Health Check**: < 100ms

### Data Size Limits
- **Message Content**: Max 1000 characters
- **User Names**: Max 50 characters
- **Image URLs**: Valid HTTP/HTTPS only
- **API Responses**: Max 1MB per request

---

## 🔧 Development & Testing

### Backend Development Checklist
- [ ] Implement all 5 required endpoints
- [ ] Return data in exact TypeScript interface format
- [ ] Enable CORS for frontend domain
- [ ] Validate input data on POST requests
- [ ] Return appropriate HTTP status codes
- [ ] Handle errors with JSON responses
- [ ] Test with frontend API client

### Frontend Development Checklist
- [ ] Configure `NEXT_PUBLIC_API_URL` environment variable
- [ ] Handle loading states for all API calls
- [ ] Implement error boundaries and fallbacks
- [ ] Test with backend offline (graceful degradation)
- [ ] Validate TypeScript interfaces match API responses
- [ ] Test responsive design on mobile devices

---

## 🚀 Deployment Considerations

### Environment Variables
```bash
# Frontend (.env.local)
NEXT_PUBLIC_API_URL=https://your-backend-domain.com

# Backend
PORT=8000
CORS_ORIGINS=https://your-frontend-domain.com
```

### Production Requirements
- **Backend**: Must be accessible from frontend domain
- **HTTPS**: Required for production deployments
- **CORS**: Configure specific frontend origins (not *)
- **Health Checks**: Implement for deployment monitoring
- **Rate Limiting**: Consider implementing for production

---

## 📝 Example Integration

### Frontend API Call
```typescript
// Using the ApiClient utility
const slides = await ApiClient.getSlides();
const newMessage = await ApiClient.addMessage("Hello!", "Alice");
```

### Backend Response
```python
# FastAPI endpoint implementation
@app.get("/api/slides", response_model=List[SlideContent])
async def get_slides():
    return [
        SlideContent(
            title="Welcome",
            content="Introduction to the presentation",
            image_url="https://example.com/slide1.jpg",
            slide_number=1
        )
    ]
```

---

## 🔍 Testing & Validation

### API Testing Commands
```bash
# Test health check
curl http://localhost:8000/

# Test slides endpoint
curl http://localhost:8000/api/slides

# Test message posting
curl -X POST http://localhost:8000/api/conversation \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message", "user": "Tester"}'
```

### Frontend Testing
- Test with backend running: Full functionality
- Test with backend offline: Graceful fallbacks
- Test with slow network: Loading states
- Test with invalid data: Error handling

---

This contract ensures seamless integration between your Next.js frontend and FastAPI backend. Both teams can develop independently while maintaining compatibility. 🤝 