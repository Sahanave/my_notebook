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
  try {
    const backendUrl = process.env.FASTAPI_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/slides/${params.slideNumber}`);
    
    if (!response.ok) {
      return NextResponse.json(
        { error: `Slide ${params.slideNumber} not found` }, 
        { status: 404 }
      );
    }
    
    const slide = await response.json();
    return NextResponse.json(slide);
  } catch (error) {
    console.error('Error fetching slide from backend:', error);
    return NextResponse.json(
      { error: 'Failed to fetch slide' }, 
      { status: 500 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: { slideNumber: string } }
) {
  try {
    const body = await request.json();
    const backendUrl = process.env.FASTAPI_URL || 'http://localhost:8000';
    
    if (body.action === 'generate_voice') {
      // Generate audio for this slide
      const response = await fetch(`${backendUrl}/api/slides/${params.slideNumber}/voice`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate audio');
      }
      
      // Check if response is audio file or JSON
      const contentType = response.headers.get('content-type');
      if (contentType?.includes('audio/')) {
        // Return audio file directly
        const audioBuffer = await response.arrayBuffer();
        return new NextResponse(audioBuffer, {
          headers: {
            'Content-Type': 'audio/mpeg',
            'Content-Disposition': `inline; filename="slide-${params.slideNumber}.mp3"`,
          },
        });
      } else {
        // Return JSON response
        const data = await response.json();
        return NextResponse.json(data);
      }
    }
    
    return NextResponse.json({ error: 'Unknown action' }, { status: 400 });
  } catch (error) {
    console.error('Error processing slide request:', error);
    return NextResponse.json(
      { error: 'Failed to process request' }, 
      { status: 500 }
    );
  }
} 