import { NextResponse } from 'next/server';

export async function GET() {
  const references = [
    {
      title: "Configure Claude Code on Vertex",
      url: "https://cloud.google.com/vertex-ai/docs/generative-ai/models/claude",
      description: "Official Google Cloud documentation for Claude on Vertex AI"
    },
    {
      title: "Learn more about MCP",
      url: "https://docs.anthropic.com/claude/docs/mcp",
      description: "Model Context Protocol documentation"
    },
    {
      title: "Get started with Claude on Vertex AI",
      url: "https://console.cloud.google.com/vertex-ai",
      description: "Google Cloud Vertex AI Console"
    }
  ];

  return NextResponse.json(references);
} 