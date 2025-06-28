import { NextRequest, NextResponse } from 'next/server';

// In-memory storage for demo (in real app, this would be a database)
let messages = [
  {
    id: 1,
    user: "Alice",
    message: "How do we handle authentication with Claude on Vertex AI?",
    timestamp: "2024-12-28T10:30:00Z",
    type: "question"
  },
  {
    id: 2,
    user: "Presenter",
    message: "Great question! Authentication is handled through Google Cloud IAM. You'll need to set up service accounts with the appropriate permissions.",
    timestamp: "2024-12-28T10:31:00Z",
    type: "answer"
  },
  {
    id: 3,
    user: "Bob",
    message: "What about rate limiting? Are there any constraints we should be aware of?",
    timestamp: "2024-12-28T10:33:00Z",
    type: "question"
  }
];

export async function GET() {
  return NextResponse.json(messages);
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, user = "Anonymous" } = body;

    if (!message) {
      return NextResponse.json(
        { detail: "Message is required" },
        { status: 400 }
      );
    }

    const newMessage = {
      id: messages.length + 1,
      user,
      message,
      timestamp: new Date().toISOString(),
      type: "question" as const
    };

    messages.push(newMessage);
    return NextResponse.json(newMessage, { status: 201 });
  } catch (error) {
    return NextResponse.json(
      { detail: "Invalid JSON" },
      { status: 400 }
    );
  }
} 