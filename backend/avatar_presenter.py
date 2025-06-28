#!/usr/bin/env python3
"""
Avatar Presenter for Slide Presentations

This script creates a visual avatar that can present your slides with voice interaction.
The avatar will use your real slides and document content from the backend.

Usage:
    python avatar_presenter.py                    # Use default avatar
    python avatar_presenter.py --avatar-id 123   # Use specific avatar ID
"""

import argparse
import sys
from typing import Optional
from dotenv import load_dotenv

def main():
    """Main function to run the avatar presenter"""
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Run a slide presentation with Bey avatar",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python avatar_presenter.py                    # Default avatar
    python avatar_presenter.py --avatar-id 123   # Specific avatar
    
Prerequisites:
    1. Upload a PDF document via the web interface
    2. Generate slides using the generate slides button
    3. Make sure LiveKit and Bey are installed:
       pip install livekit-agents[bey]
        """
    )
    
    parser.add_argument(
        "--avatar-id", 
        type=str, 
        help="Avatar ID to use (optional, will use default if not specified)"
    )
    
    parser.add_argument(
        "--voice", 
        type=str, 
        choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        default="alloy",
        help="Voice to use for the avatar (default: alloy)"
    )
    
    parser.add_argument(
        "--check-status", 
        action="store_true",
        help="Check if slides are available and avatar is ready"
    )
    
    args = parser.parse_args()
    
    # Check status if requested
    if args.check_status:
        check_presentation_status()
        return
    
    # Try to import and run the avatar presenter
    try:
        from voice_agent import run_avatar_presenter, SlidePresenterAvatar
        
        if SlidePresenterAvatar is None:
            print("❌ Bey avatar not available!")
            print("📦 Install required packages:")
            print("   pip install livekit-agents[bey]")
            print("   pip install livekit-plugins-bey")
            return
            
        print("🎭 Starting Avatar Presenter...")
        print(f"🎤 Voice: {args.voice}")
        if args.avatar_id:
            print(f"👤 Avatar ID: {args.avatar_id}")
        else:
            print("👤 Using default avatar")
            
        print("\n🚀 Starting presentation room...")
        print("💡 Connect to the LiveKit room to see your avatar presenter!")
        
        # Run the avatar presenter
        run_avatar_presenter(avatar_id=args.avatar_id)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("📦 Make sure you have installed:")
        print("   pip install livekit-agents[bey]")
        print("   pip install livekit-plugins-bey")
    except Exception as e:
        print(f"❌ Error starting avatar presenter: {e}")
        print("💡 Make sure your .env file has OPENAI_API_KEY configured")

def check_presentation_status():
    """Check if slides and avatar system are ready"""
    print("🔍 Checking Avatar Presenter Status...")
    print("=" * 50)
    
    try:
        # Check voice agent and slides
        from voice_agent import create_voice_agent_for_backend, SlidePresenterAvatar
        
        if SlidePresenterAvatar is None:
            print("❌ Bey avatar not available")
            print("📦 Install: pip install livekit-agents[bey]")
            return
            
        print("✅ Avatar system available")
        
        # Check slides status
        voice_agent = create_voice_agent_for_backend()
        slides_info = voice_agent.get_slides_info()
        
        print(f"\n📊 Slides Status:")
        print(f"   - Total slides: {slides_info['total_slides']}")
        print(f"   - Document: {slides_info['document_title']}")
        print(f"   - Ready: {'✅' if slides_info['slides_available'] else '❌'}")
        
        if slides_info['slides_available']:
            print(f"\n🎯 Available Slides:")
            for slide in slides_info['slides'][:3]:  # Show first 3
                print(f"   - Slide {slide['number']}: {slide['title']}")
            if len(slides_info['slides']) > 3:
                print(f"   ... and {len(slides_info['slides']) - 3} more")
                
            print(f"\n🎭 Avatar Presenter Ready!")
            print(f"   Run: python avatar_presenter.py")
        else:
            print(f"\n⚠️ No slides available!")
            print(f"   1. Upload a PDF via the web interface")
            print(f"   2. Click 'Generate Slides'")
            print(f"   3. Then run the avatar presenter")
            
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        print("💡 Make sure the backend is running and configured")

def show_usage_guide():
    """Show detailed usage guide"""
    guide = """
🎭 Avatar Presenter Setup Guide
===============================

1. 📋 Prerequisites:
   • Upload PDF document via web interface
   • Generate slides using "Generate Slides" button
   • Install LiveKit and Bey: pip install livekit-agents[bey]

2. 🚀 Running the Avatar:
   python avatar_presenter.py                    # Default avatar
   python avatar_presenter.py --avatar-id 123   # Specific avatar
   python avatar_presenter.py --voice nova      # Different voice

3. 🎯 During Presentation:
   • Avatar will introduce the presentation
   • Say "next slide" to advance
   • Say "previous slide" to go back
   • Say "go to slide 3" to jump to specific slide
   • Ask questions about the content

4. 🔧 Troubleshooting:
   python avatar_presenter.py --check-status    # Check readiness
   
5. 🎥 Connecting:
   • The avatar runs in a LiveKit room
   • Connect using LiveKit client or web interface
   • You'll see and hear your avatar presenter!
"""
    print(guide)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments, show usage guide
        show_usage_guide()
    
    main() 