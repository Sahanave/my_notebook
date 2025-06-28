import { NextRequest, NextResponse } from 'next/server';

const slides = [
  {
    title: "Welcome to Claude Agents",
    content: "Building intelligent agents with Claude on Vertex AI",
    image_url: "https://via.placeholder.com/800x600/4F46E5/FFFFFF?text=Slide+1",
    image_description: "Title slide with Claude AI branding and agent illustration",
    speaker_notes: "Welcome everyone to our presentation on Claude Agents. Today we'll explore how to build intelligent agents using Claude AI on Google's Vertex AI platform.",
    slide_number: 1
  },
  {
    title: "Architecture Overview",
    content: "Understanding the MCP (Model Context Protocol) integration",
    image_url: "https://via.placeholder.com/800x600/7C3AED/FFFFFF?text=Slide+2",
    image_description: "Architecture diagram showing MCP components and data flow",
    speaker_notes: "Let's dive into the architecture. The Model Context Protocol provides a standardized way for AI agents to interact with external systems and data sources.",
    slide_number: 2
  },
  {
    title: "Implementation Guide",
    content: "Step-by-step implementation with code examples",
    image_url: "https://via.placeholder.com/800x600/DC2626/FFFFFF?text=Slide+3",
    image_description: "Code snippets and implementation steps visualization",
    speaker_notes: "Now we'll walk through the practical implementation steps. I'll show you code examples and best practices for building robust Claude agents.",
    slide_number: 3
  }
];

export async function GET(
  request: NextRequest,
  { params }: { params: { slideNumber: string } }
) {
  const slideNumber = parseInt(params.slideNumber);
  const slide = slides.find(s => s.slide_number === slideNumber);
  
  if (!slide) {
    return NextResponse.json(
      {
        title: "Slide Not Found",
        content: "The requested slide is not available",
        image_url: "https://via.placeholder.com/800x600/6B7280/FFFFFF?text=Not+Found",
        slide_number: slideNumber
      }
    );
  }
  
  return NextResponse.json(slide);
}

export async function POST(
  request: NextRequest,
  { params }: { params: { slideNumber: string } }
) {
  try {
    const { action } = await request.json();
    const slideNumber = parseInt(params.slideNumber);
    
    if (action === 'generate_voice') {
      const slide = slides.find(s => s.slide_number === slideNumber);
      
      if (!slide) {
        return NextResponse.json({ error: 'Slide not found' }, { status: 404 });
      }

      // Create narration text (title and content only)
      const narrationText = `${slide.title}. ${slide.content}`;
      
      // For now, return the text. In production, this would call the backend TTS API
      // When backend is deployed, replace this with actual API call
      return NextResponse.json({ 
        narration_text: narrationText,
        audio_url: null, // Will be populated when backend is connected
        message: 'Voice generation ready (backend needed for actual audio)'
      });
    }
    
    return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to process request' }, { status: 500 });
  }
} 