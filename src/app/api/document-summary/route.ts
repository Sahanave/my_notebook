import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Proxy to FastAPI backend instead of returning hardcoded data
    const backendUrl = process.env.FASTAPI_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/document-summary`);
    
    if (!response.ok) {
      console.warn('FastAPI backend not available for document summary');
      // Return a minimal fallback instead of Claude Agents data
      return NextResponse.json({
        title: "No Document Uploaded",
        abstract: "Upload a PDF document to see its summary here.",
        key_points: ["Upload a document to get started"],
        main_topics: ["Document Analysis"],
        difficulty_level: "beginner",
        estimated_read_time: "0 minutes",
        document_type: "unknown",
        authors: ["Unknown"],
        publication_date: new Date().toISOString().split('T')[0]
      });
    }
    
    const summary = await response.json();
    return NextResponse.json(summary);
  } catch (error) {
    console.error('Error fetching document summary from backend:', error);
    // Return minimal fallback
    return NextResponse.json({
      title: "Document Summary Unavailable",
      abstract: "Unable to connect to backend service.",
      key_points: ["Backend service unavailable"],
      main_topics: ["Error"],
      difficulty_level: "beginner",
      estimated_read_time: "0 minutes",
      document_type: "error",
      authors: ["System"],
      publication_date: new Date().toISOString().split('T')[0]
    });
  }
} 