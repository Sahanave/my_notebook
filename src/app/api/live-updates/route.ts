import { NextResponse } from 'next/server';

export async function GET() {
  const liveUpdates = [
    {
      message: "Welcome everyone! We'll start in 2 minutes.",
      timestamp: "2024-12-28T10:28:00Z",
      type: "announcement"
    },
    {
      message: "Demo environment is now live and ready for testing",
      timestamp: "2024-12-28T10:35:00Z",
      type: "info"
    }
  ];

  return NextResponse.json(liveUpdates);
} 