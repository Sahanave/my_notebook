from dotenv import load_dotenv
import asyncio
from openai import OpenAI
from typing import List, Optional
import json
import os
from data_models import SlideContent, DocumentSummary

load_dotenv()

class SimpleVoiceAgent:
    """Simplified voice agent for slide narration using real backend data"""
    
    def __init__(self, openai_client: OpenAI = None):
        self.openai_client = openai_client or OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.current_slide = 0
        
    def get_real_slides(self) -> List[SlideContent]:
        """Get real slides from the main backend"""
        try:
            # Import the global slides from main.py
            from main import sample_slides
            return sample_slides
        except ImportError:
            print("Warning: Could not import slides from main.py, using empty list")
            return []
    
    def get_real_document_summary(self) -> Optional[DocumentSummary]:
        """Get real document summary from the main backend"""
        try:
            # Import the global document summary from main.py
            from main import current_document_summary
            return current_document_summary
        except ImportError:
            print("Warning: Could not import document summary from main.py")
            return None
        
    def get_current_slide_narration(self) -> str:
        """Get narration text for current slide"""
        slides = self.get_real_slides()
        if not slides or self.current_slide >= len(slides):
            return "No slides available for narration."
            
        slide = slides[self.current_slide]
        return f"{slide.title}. {slide.content}"
    
    def get_slide_narration(self, slide_number: int) -> str:
        """Get narration text for specific slide"""
        slides = self.get_real_slides()
        slide = next((s for s in slides if s.slide_number == slide_number), None)
        if not slide:
            return "Slide not found."
        return f"{slide.title}. {slide.content}"
    
    def get_all_slides_count(self) -> int:
        """Get total number of real slides"""
        slides = self.get_real_slides()
        return len(slides)
    
    def get_slides_info(self) -> dict:
        """Get information about current slides and document"""
        slides = self.get_real_slides()
        document_summary = self.get_real_document_summary()
        
        return {
            "total_slides": len(slides),
            "current_slide": self.current_slide + 1 if slides else 0,
            "document_title": document_summary.title if document_summary else "No document",
            "slides_available": len(slides) > 0,
            "slides": [{"number": s.slide_number, "title": s.title} for s in slides]
        }
    
    async def generate_audio(self, text: str, voice: str = "alloy") -> bytes:
        """Generate audio from text using OpenAI TTS"""
        try:
            response = self.openai_client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            return response.content
        except Exception as e:
            print(f"Error generating audio: {e}")
            return b""
    
    def navigate_slides(self, direction: str) -> str:
        """Handle slide navigation"""
        slides = self.get_real_slides()
        if not slides:
            return "No slides available for navigation."
            
        if direction == "next" and self.current_slide < len(slides) - 1:
            self.current_slide += 1
            slide = slides[self.current_slide]
            return f"Moving to slide {slide.slide_number}: {slide.title}"
            
        elif direction == "previous" and self.current_slide > 0:
            self.current_slide -= 1
            slide = slides[self.current_slide]
            return f"Going back to slide {slide.slide_number}: {slide.title}"
            
        elif direction.isdigit():
            slide_num = int(direction) - 1
            if 0 <= slide_num < len(slides):
                self.current_slide = slide_num
                slide = slides[self.current_slide]
                return f"Jumping to slide {slide.slide_number}: {slide.title}"
        
        return f"Currently on slide {self.current_slide + 1} of {len(slides)}"


# Integration function to work with main backend
def create_voice_agent_for_backend() -> SimpleVoiceAgent:
    """Create a voice agent that integrates with the main backend"""
    try:
        from main import openai_client
        return SimpleVoiceAgent(openai_client)
    except ImportError:
        print("Warning: Could not import openai_client from main.py, creating new client")
        return SimpleVoiceAgent()


# LiveKit compatible version (if you want to use LiveKit later)
try:
    from livekit import agents
    from livekit.agents import AgentSession, JobContext
    
    # Updated imports for current LiveKit versions
    try:
        from livekit.plugins.openai import LLM as OpenAILLM
        from livekit.plugins.deepgram import STT as DeepgramSTT
        from livekit.plugins.cartesia import TTS as CartesiaTTS
        from livekit.plugins.silero import VAD as SileroVAD
    except ImportError:
        print("Warning: Some LiveKit plugins not available. Using simplified version.")
        OpenAILLM = None
        DeepgramSTT = None
        CartesiaTTS = None
        SileroVAD = None
    
    class LiveKitSlideAgent:
        """LiveKit compatible slide presentation agent"""
        
        def __init__(self):
            self.voice_agent = create_voice_agent_for_backend()
            
        async def entrypoint(self, ctx: JobContext):
            """LiveKit entry point"""
            if not all([OpenAILLM, DeepgramSTT, CartesiaTTS, SileroVAD]):
                print("Required LiveKit plugins not available. Please install:")
                print("pip install livekit-agents[openai,deepgram,cartesia,silero]")
                return
                
            # Create agent session with proper imports
            session = AgentSession(
                stt=DeepgramSTT(model="nova-2"),
                llm=OpenAILLM(model="gpt-4o-mini"),
                tts=CartesiaTTS(voice="f9836c6e-a0bd-460e-9d3c-f7299fa60f94"),
                vad=SileroVAD.load(),
            )
            
            await session.start(ctx.room)
            await ctx.connect()
            
            # Get real document info
            slides_info = self.voice_agent.get_slides_info()
            
            # Start presentation
            await session.generate_reply(
                content=f"Welcome to the presentation on {slides_info['document_title']}. We have {slides_info['total_slides']} slides to cover today."
            )

except ImportError:
    print("LiveKit not available. Using simplified voice agent only.")
    LiveKitSlideAgent = None


# Bey Avatar Integration
try:
    from livekit.agents import (
        AutoSubscribe,
        JobContext,
        RoomOutputOptions,
        WorkerOptions,
        WorkerType,
        cli,
    )
    from livekit.agents.voice import Agent, AgentSession
    from livekit.plugins import bey, openai as livekit_openai
    import argparse
    import sys
    from functools import partial
    
    class SlidePresenterAvatar:
        """Visual avatar presenter that works with real slides"""
        
        def __init__(self, avatar_id: Optional[str] = None):
            self.avatar_id = avatar_id
            self.voice_agent = create_voice_agent_for_backend()
            
        async def entrypoint(self, ctx: JobContext) -> None:
            """Main entry point for the avatar presenter"""
            await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
            
            # Get real slides and document info
            slides_info = self.voice_agent.get_slides_info()
            
            # Create agent with slide presentation instructions
            presentation_instructions = self.create_presentation_instructions(slides_info)
            
            # Create local agent session with OpenAI Realtime
            local_agent_session = AgentSession(
                llm=livekit_openai.realtime.RealtimeModel(voice="alloy")
            )
            
            # Create Bey avatar session
            if self.avatar_id is not None:
                bey_avatar_session = bey.AvatarSession(avatar_id=self.avatar_id)
            else:
                bey_avatar_session = bey.AvatarSession()
                
            # Start avatar session
            await bey_avatar_session.start(local_agent_session, room=ctx.room)
            
            # Start the agent with presentation instructions
            await local_agent_session.start(
                agent=Agent(instructions=presentation_instructions),
                room=ctx.room,
            )
            
        def create_presentation_instructions(self, slides_info: dict) -> str:
            """Create instructions for the avatar based on real slide content"""
            
            if not slides_info['slides_available']:
                return """You are a presentation assistant. Currently no slides are loaded. 
                Please ask the user to upload a document and generate slides first."""
            
            slides_list = "\n".join([
                f"Slide {slide['number']}: {slide['title']}" 
                for slide in slides_info['slides']
            ])
            
            instructions = f"""You are an expert presenter giving a live presentation about "{slides_info['document_title']}".

PRESENTATION OVERVIEW:
- Document: {slides_info['document_title']}
- Total slides: {slides_info['total_slides']}
- Current slide: {slides_info['current_slide']}

SLIDE OUTLINE:
{slides_list}

PRESENTATION BEHAVIOR:
- You are presenting slide-by-slide content to a live audience
- Speak naturally and conversationally
- Reference slide numbers when moving between slides
- Handle audience questions by relating back to the slide content
- Keep responses focused on the presentation topic
- Use gestures and body language appropriate for presentation

VOICE COMMANDS YOU UNDERSTAND:
- "next slide" / "go to next slide" - Move to next slide
- "previous slide" / "go back" - Move to previous slide  
- "go to slide [number]" - Jump to specific slide
- "what slide are we on?" - Current slide info
- "overview" / "summary" - Brief presentation overview

Start by introducing yourself and the presentation topic, then begin with the first slide."""

            return instructions
            
        def get_slide_content_for_narration(self, slide_number: int) -> str:
            """Get detailed slide content for avatar narration"""
            narration = self.voice_agent.get_slide_narration(slide_number)
            if narration == "Slide not found.":
                return "I don't have that slide available."
            return narration

    # Function to create and run the avatar presenter
    async def create_avatar_presenter(avatar_id: Optional[str] = None):
        """Create an avatar presenter for the slide presentation"""
        presenter = SlidePresenterAvatar(avatar_id)
        return presenter
        
    def run_avatar_presenter(avatar_id: Optional[str] = None):
        """Run the avatar presenter with CLI"""
        from dotenv import load_dotenv
        load_dotenv()
        
        # Create the presenter
        presenter = SlidePresenterAvatar(avatar_id)
        
        # Override CLI args
        sys.argv = [sys.argv[0], "dev"]
        
        # Run with LiveKit CLI
        cli.run_app(
            WorkerOptions(
                entrypoint_fnc=presenter.entrypoint,
                worker_type=WorkerType.ROOM,
            )
        )

except ImportError as e:
    print(f"Bey avatar not available: {e}")
    print("To use avatar features, install: pip install livekit-agents[bey]")
    
    SlidePresenterAvatar = None
    create_avatar_presenter = None
    run_avatar_presenter = None


# Test function using real backend data
async def test_voice_agent_with_real_data():
    """Test the voice agent with real backend data"""
    
    print("Testing Voice Agent with Real Backend Data:")
    print("=" * 50)
    
    # Create agent that uses real backend data
    agent = create_voice_agent_for_backend()
    
    # Get slides info
    slides_info = agent.get_slides_info()
    print(f"📊 Slides Status:")
    print(f"   - Total slides: {slides_info['total_slides']}")
    print(f"   - Document: {slides_info['document_title']}")
    print(f"   - Slides available: {slides_info['slides_available']}")
    
    if slides_info['slides_available']:
        print(f"\n🎯 Slide List:")
        for slide_info in slides_info['slides'][:5]:  # Show first 5 slides
            print(f"   - Slide {slide_info['number']}: {slide_info['title']}")
        
        if len(slides_info['slides']) > 5:
            print(f"   ... and {len(slides_info['slides']) - 5} more slides")
        
        print(f"\n🎙️ Testing Narration:")
        print("Current slide narration:", agent.get_current_slide_narration())
        
        if slides_info['total_slides'] > 1:
            print("Navigation:", agent.navigate_slides("next"))
            print("Current slide narration:", agent.get_current_slide_narration())
        
        # Test audio generation with real content
        print("\nGenerating audio for current slide...")
        narration_text = agent.get_current_slide_narration()
        audio_data = await agent.generate_audio(narration_text)
        print(f"Generated {len(audio_data)} bytes of audio")
        
    else:
        print("\n⚠️ No slides found. Make sure to:")
        print("   1. Upload a PDF document")
        print("   2. Generate slides using the /api/generate-slides endpoint")
        print("   3. Then test the voice agent")


# Simple fallback test with mock data (for when no real slides exist)
async def test_voice_agent_fallback():
    """Test the voice agent functionality with mock data as fallback"""
    
    # Sample data
    slides = [
        SlideContent(
            title="Introduction to AI",
            content="Artificial Intelligence is transforming how we work and live",
            image_description="AI brain illustration",
            speaker_notes="Welcome to our AI presentation",
            slide_number=1
        )
    ]
    
    document_summary = DocumentSummary(
        title="AI Fundamentals",
        abstract="A comprehensive introduction to artificial intelligence and machine learning concepts",
        key_points=["AI basics", "ML algorithms", "Real-world applications"],
        main_topics=["AI", "Machine Learning"],
        difficulty_level="Beginner",
        estimated_read_time="15 minutes",
        document_type="Presentation",
        authors=["AI Research Team"],
        publication_date="2024-01-15"
    )
    
    # Test simple agent with mock data
    agent = SimpleVoiceAgent()
    
    print("Testing Voice Agent (Fallback Mode):")
    print("Current slide narration:", "Mock data - upload documents to get real slides")
    
    # Test audio generation
    print("Generating audio...")
    audio_data = await agent.generate_audio("Hello, this is a test of the voice agent with real backend integration.")
    print(f"Generated {len(audio_data)} bytes of audio")


if __name__ == "__main__":
    print("🎙️ Voice Agent Backend Integration Test")
    print("=" * 50)
    
    # Test if we can run the voice agent with real data
    try:
        asyncio.run(test_voice_agent_with_real_data())
        print("✅ Voice agent integration test completed!")
    except Exception as e:
        print(f"❌ Voice agent error: {e}")
        print("\n🔄 Trying fallback test...")
        try:
            asyncio.run(test_voice_agent_fallback())
            print("✅ Fallback test completed!")
        except Exception as e2:
            print(f"❌ Fallback test error: {e2}")
        print("💡 Make sure you have OPENAI_API_KEY set in your .env file")