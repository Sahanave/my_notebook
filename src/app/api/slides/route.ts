import { NextResponse } from 'next/server';

export async function GET() {
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

  return NextResponse.json(slides);
} 