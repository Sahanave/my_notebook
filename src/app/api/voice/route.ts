import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { text, voice = 'alloy' } = await request.json();
    
    if (!text) {
      return NextResponse.json({ error: 'Text is required' }, { status: 400 });
    }
    
    if (text.length > 4000) {
      return NextResponse.json({ error: 'Text too long (max 4000 characters)' }, { status: 400 });
    }
    
    // For now, return mock response. When backend is deployed, this will call the actual TTS API
    // TODO: Replace with actual backend call to /api/voice/custom
    return NextResponse.json({ 
      message: 'Voice generation ready (backend needed for actual audio)',
      text: text,
      voice: voice,
      audio_url: null // Will be populated when backend is connected
    });
    
  } catch (error) {
    return NextResponse.json({ error: 'Failed to process voice request' }, { status: 500 });
  }
} 