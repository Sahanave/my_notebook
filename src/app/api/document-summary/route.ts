import { NextResponse } from 'next/server';

// Fallback sample summary for when no document has been uploaded
const sampleDocumentSummary = {
  title: "Building Intelligent Agents with Claude on Vertex AI",
  abstract: "This comprehensive guide explores the integration of Anthropic's Claude language model with Google Cloud's Vertex AI platform to create powerful, context-aware intelligent agents. The document covers the Model Context Protocol (MCP), implementation strategies, and best practices for deploying Claude-based agents in production environments.",
  key_points: [
    "Integration of Claude with Vertex AI infrastructure",
    "Implementation of Model Context Protocol (MCP) for enhanced context management",
    "Authentication and security considerations for production deployments",
    "Scalability patterns and performance optimization techniques",
    "Real-world use cases and deployment scenarios"
  ],
  main_topics: [
    "Claude API Integration",
    "Vertex AI Platform",
    "Model Context Protocol",
    "Authentication & Security",
    "Performance Optimization",
    "Production Deployment"
  ],
  difficulty_level: "intermediate",
  estimated_read_time: "45 minutes",
  document_type: "tutorial",
  authors: ["Google Cloud Team", "Anthropic Documentation"],
  publication_date: "2024-12-28"
};

export async function GET() {
  // Return sample data - real document summary now comes directly from upload results
  return NextResponse.json(sampleDocumentSummary);
} 