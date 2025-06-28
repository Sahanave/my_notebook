"use client";

import React, { useState, useEffect, useRef } from "react";
import { SlideContent, LiveUpdate } from "@/types/api";
import { ApiClient } from "@/lib/api";
import DocumentSummaryComponent, { DocumentSummaryRef } from "@/components/DocumentSummary";
import DocumentUpload from "@/components/DocumentUpload";

export default function Home() {
  const [currentSlide, setCurrentSlide] = useState<SlideContent | null>(null);
  const [liveUpdates, setLiveUpdates] = useState<LiveUpdate[]>([]);
  const [currentSlideNumber, setCurrentSlideNumber] = useState(1);
  const [totalSlides, setTotalSlides] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [summaryRefreshing, setSummaryRefreshing] = useState(false);
  const [slideGenerating, setSlideGenerating] = useState(false);
  const [isNarrating, setIsNarrating] = useState(false);
  
  // Ref to access DocumentSummary refresh function
  const documentSummaryRef = useRef<DocumentSummaryRef>(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      const [metadata, updates] = await Promise.all([
        ApiClient.getSlidesMetadata(),
        ApiClient.getLiveUpdates()
      ]);
      
      setTotalSlides(metadata.total_slides);
      
      // Only load first slide if slides are available
      if (metadata.total_slides > 0) {
        const slide = await ApiClient.getSlide(1);
        setCurrentSlide(slide);
      }
      
      setLiveUpdates(updates);
    } catch (err) {
      setError("Failed to load content");
      console.error("Error loading data:", err);
    } finally {
      setLoading(false);
    }
  };

  const generateSlides = async () => {
    try {
      setSlideGenerating(true);
      console.log('🔄 Generating slides (including Q&A processing)...');
      
      const newSlides = await ApiClient.generateSlides();
      console.log('✅ Slides generated successfully:', newSlides);
      
      // Wait a moment for backend to update, then refresh slides metadata
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Get updated slides metadata from backend
      const metadata = await ApiClient.getSlidesMetadata();
      console.log('📊 Updated slides metadata:', metadata);
      
      // Update total slides count and load first slide from backend
      setTotalSlides(metadata.total_slides);
      
      if (metadata.total_slides > 0) {
        // Fetch the first slide from the updated backend
        const firstSlide = await ApiClient.getSlide(1);
        setCurrentSlide(firstSlide);
        setCurrentSlideNumber(1);
        console.log('📄 Loaded first slide:', firstSlide);
      }
      
      // Show success message
      setLiveUpdates(prev => [{
        message: `Generated ${metadata.total_slides} slides from your document content!`,
        timestamp: new Date().toISOString(),
        type: "info"
      }, ...prev]);
      
    } catch (err) {
      console.error('❌ Error generating slides:', err);
      setError("Failed to generate slides. Please try again.");
    } finally {
      setSlideGenerating(false);
    }
  };

  const changeSlide = async (slideNumber: number) => {
    // Check bounds before attempting to load
    if (slideNumber < 1 || slideNumber > totalSlides) {
      return;
    }
    
    try {
      const slide = await ApiClient.getSlide(slideNumber);
      setCurrentSlide(slide);
      setCurrentSlideNumber(slideNumber);
    } catch (err) {
      console.error("Error loading slide:", err);
      // If slide doesn't exist, stay on current slide
    }
  };

  const playSlideNarration = async (slideNumber: number) => {
    setIsNarrating(true);
    try {
      const response = await fetch(`/api/slides/${slideNumber}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'generate_voice' })
      });
      
      const data = await response.json();
      
      if (data.narration_text) {
        // For now, just speak the text using browser's speech synthesis
        // When backend is connected, this will play the actual audio file
        if ('speechSynthesis' in window) {
          const utterance = new SpeechSynthesisUtterance(data.narration_text);
          utterance.rate = 0.9;
          utterance.pitch = 1.0;
          utterance.volume = 0.8;
          utterance.onend = () => setIsNarrating(false);
          utterance.onerror = () => setIsNarrating(false);
          speechSynthesis.speak(utterance);
        } else {
          console.log('Narration text:', data.narration_text);
          setIsNarrating(false);
        }
      }
    } catch (error) {
      console.error('Failed to generate narration:', error);
      setIsNarrating(false);
    }
  };

  const stopNarration = () => {
    if ('speechSynthesis' in window) {
      speechSynthesis.cancel();
    }
    setIsNarrating(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-4 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading presentation...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-4 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button 
            onClick={loadInitialData}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Are you taking Notes
          </h1>
          
          {/* Live Updates */}
          {liveUpdates.length > 0 && (
            <div className="mt-4 space-y-2">
              {liveUpdates.map((update, index) => (
                <div 
                  key={index}
                  className={`p-3 rounded-lg text-sm ${
                    update.type === 'announcement' ? 'bg-blue-100 text-blue-800' :
                    update.type === 'info' ? 'bg-green-100 text-green-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}
                >
                  <span className="font-medium">📢 {update.message}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Document Upload Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
            <span className="mr-2">📤</span>
            Upload Document
          </h2>
          <DocumentUpload onUploadComplete={async (result) => {
            console.log('Upload completed:', result);
            
            // Refresh the document summary immediately after upload
            try {
              setSummaryRefreshing(true);
              await documentSummaryRef.current?.refreshSummary();
              console.log('✅ Document summary refreshed successfully');
              
              // Show success notification briefly
              setTimeout(() => {
                setSummaryRefreshing(false);
              }, 1000);
            } catch (error) {
              console.error('❌ Failed to refresh document summary:', error);
              setSummaryRefreshing(false);
            }
          }} />
        </div>

        {/* Document Summary Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
            <span className="mr-2">📄</span>
            Document Summary
            {summaryRefreshing && (
              <span className="ml-2 text-sm text-blue-600 flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-1"></div>
                Updating...
              </span>
            )}
          </h2>
          <DocumentSummaryComponent ref={documentSummaryRef} />
        </div>

        {/* Main Content Area */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Slides Section - Takes 2/3 of space on large screens */}
          <div className="lg:col-span-2">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-semibold text-gray-800 flex items-center">
                <span className="mr-2">📑</span>
                {currentSlide?.title || "Presentation Slides"}
              </h2>
              
              {/* Slide Controls */}
              <div className="flex items-center space-x-2">
                {/* Slide Generation Buttons */}
                <button
                  onClick={generateSlides}
                  disabled={slideGenerating}
                  className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center text-sm"
                >
                  {slideGenerating ? (
                    <>
                      <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-1"></div>
                      Generating...
                    </>
                  ) : (
                    <>
                      <span className="mr-1">🎯</span>
                      Generate Slides
                    </>
                  )}
                </button>
                
                {/* Slide Navigation */}
                <div className="border-l border-gray-300 pl-2 ml-2">
                  <button
                    onClick={() => changeSlide(Math.max(1, currentSlideNumber - 1))}
                    disabled={currentSlideNumber <= 1 || totalSlides === 0}
                    className="px-3 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    ← Prev
                  </button>
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded mx-1">
                    {totalSlides > 0 ? `Slide ${currentSlideNumber} of ${totalSlides}` : 'No slides'}
                  </span>
                  <button
                    onClick={() => changeSlide(currentSlideNumber + 1)}
                    disabled={currentSlideNumber >= totalSlides || totalSlides === 0}
                    className="px-3 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next →
                  </button>
                </div>
              </div>
            </div>
            
            <div className="bg-amber-50 border-2 border-gray-300 rounded-lg p-8 min-h-[400px]">
              {currentSlide ? (
                <div className="space-y-6">
                  {/* Slide Title */}
                  <h3 className="text-2xl font-semibold text-gray-900 text-center border-b border-gray-300 pb-3">{currentSlide.title}</h3>
                  
                  {/* Main Content */}
                  <div className="text-gray-700 text-lg leading-relaxed">
                    <div className="whitespace-pre-line">{currentSlide.content}</div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center h-full text-gray-500">
                  <div className="text-center">
                    <p className="text-xl mb-2">📖</p>
                    <p>No slides available. Upload a document and generate slides to get started!</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Live Stream Section - Takes 1/3 of space on large screens */}
          <div className="lg:col-span-1">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
              <span className="mr-2">🎙️</span>
              Live Audio Stream
            </h2>
            <div className="bg-amber-50 border-2 border-gray-300 rounded-lg p-6 min-h-[400px]">
              <div className="space-y-6">
                {/* Live Status */}
                <div className="text-center">
                  <div className={`w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center transition-all ${
                    isNarrating ? 'bg-red-500 animate-pulse' : 'bg-gray-400'
                  }`}>
                    <span className="text-white text-2xl">
                      {isNarrating ? '🎙️' : '⏸️'}
                    </span>
                  </div>
                  <p className={`font-medium ${isNarrating ? 'text-red-600' : 'text-gray-600'}`}>
                    {isNarrating ? 'LIVE - Narrating Slide' : 'Audio Stream Ready'}
                  </p>
                </div>

                {/* Current Slide Info */}
                {currentSlide && (
                  <div className="bg-white rounded-lg p-4 border">
                    <h4 className="font-semibold text-gray-800 mb-2">Now Playing:</h4>
                    <p className="text-sm text-gray-600 mb-1">Slide {currentSlideNumber}: {currentSlide.title}</p>
                    <p className="text-xs text-gray-500 line-clamp-2">{currentSlide.content}</p>
                  </div>
                )}

                {/* Voice Controls */}
                <div className="space-y-3">
                  <button
                    onClick={() => isNarrating ? stopNarration() : playSlideNarration(currentSlideNumber)}
                    disabled={!currentSlide}
                    className={`w-full py-3 px-4 rounded-lg font-medium transition-all ${
                      isNarrating 
                        ? 'bg-red-500 text-white hover:bg-red-600' 
                        : 'bg-blue-500 text-white hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed'
                    }`}
                  >
                    {isNarrating ? (
                      <>
                        <svg className="w-5 h-5 inline mr-2" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                        Stop Narration
                      </>
                    ) : (
                      <>
                        <svg className="w-5 h-5 inline mr-2" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                        </svg>
                        Start Narration
                      </>
                    )}
                  </button>

                  {/* Quick Actions */}
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={async () => {
                        if (currentSlideNumber > 1) {
                          await changeSlide(currentSlideNumber - 1);
                          setTimeout(() => playSlideNarration(currentSlideNumber - 1), 100);
                        }
                      }}
                      disabled={currentSlideNumber <= 1 || totalSlides === 0 || isNarrating}
                      className="px-3 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                    >
                      ← Prev & Play
                    </button>
                    <button
                      onClick={async () => {
                        if (currentSlideNumber < totalSlides) {
                          await changeSlide(currentSlideNumber + 1);
                          setTimeout(() => playSlideNarration(currentSlideNumber + 1), 100);
                        }
                      }}
                      disabled={currentSlideNumber >= totalSlides || totalSlides === 0 || isNarrating}
                      className="px-3 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                    >
                      Next & Play →
                    </button>
                  </div>
                </div>

                {/* Audio Status */}
                <div className="text-center pt-4 border-t">
                  <p className="text-xs text-gray-500">
                    {isNarrating ? 'Audio streaming...' : 'Ready to stream audio'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 