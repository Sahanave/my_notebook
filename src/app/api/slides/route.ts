import { NextResponse } from 'next/server';

export async function GET() {
  const slides = [
    {
      title: "Welcome to Claude Agents",
      content: "Building intelligent agents with Claude on Vertex AI",
      image_url: "https://via.placeholder.com/800x600/4F46E5/FFFFFF?text=Slide+1",
      slide_number: 1
    },
    {
      title: "Architecture Overview",
      content: "Understanding the MCP (Model Context Protocol) integration",
      image_url: "https://via.placeholder.com/800x600/7C3AED/FFFFFF?text=Slide+2",
      slide_number: 2
    },
    {
      title: "Implementation Guide",
      content: "Step-by-step implementation with code examples",
      image_url: "https://via.placeholder.com/800x600/DC2626/FFFFFF?text=Slide+3",
      slide_number: 3
    }
  ];

  return NextResponse.json(slides);
} 