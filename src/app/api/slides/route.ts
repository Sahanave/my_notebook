import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Proxy to FastAPI backend instead of returning hardcoded data
    const backendUrl = process.env.FASTAPI_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/slides`);
    
    if (!response.ok) {
      // If backend is not available, return empty array instead of Claude Agents data
      console.warn('FastAPI backend not available, returning empty slides');
      return NextResponse.json([]);
    }
    
    const slides = await response.json();
    return NextResponse.json(slides);
  } catch (error) {
    console.error('Error fetching slides from backend:', error);
    // Return empty array instead of sample data
    return NextResponse.json([]);
  }
} 