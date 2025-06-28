"use client";

import React, { useState, useEffect } from "react";
import { SlideContent, ReferenceLink, LiveUpdate } from "@/types/api";
import { ApiClient } from "@/lib/api";
import Conversation from "@/components/Conversation";

export default function Home() {
  const [currentSlide, setCurrentSlide] = useState<SlideContent | null>(null);
  const [references, setReferences] = useState<ReferenceLink[]>([]);
  const [liveUpdates, setLiveUpdates] = useState<LiveUpdate[]>([]);
  const [currentSlideNumber, setCurrentSlideNumber] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      const [slide, refs, updates] = await Promise.all([
        ApiClient.getSlide(currentSlideNumber),
        ApiClient.getReferences(),
        ApiClient.getLiveUpdates()
      ]);
      
      setCurrentSlide(slide);
      setReferences(refs);
      setLiveUpdates(updates);
    } catch (err) {
      setError("Failed to load content");
      console.error("Error loading data:", err);
    } finally {
      setLoading(false);
    }
  };

  const changeSlide = async (slideNumber: number) => {
    try {
      const slide = await ApiClient.getSlide(slideNumber);
      setCurrentSlide(slide);
      setCurrentSlideNumber(slideNumber);
    } catch (err) {
      console.error("Error loading slide:", err);
    }
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

        {/* Main Content Area */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Slides Section - Takes 2/3 of space on large screens */}
          <div className="lg:col-span-2">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-semibold text-gray-800 flex items-center">
                <span className="mr-2">📑</span>
                {currentSlide?.title || "Presentation Slides"}
              </h2>
              
              {/* Slide Navigation */}
              <div className="flex space-x-2">
                <button
                  onClick={() => changeSlide(Math.max(1, currentSlideNumber - 1))}
                  disabled={currentSlideNumber <= 1}
                  className="px-3 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 disabled:opacity-50"
                >
                  ← Prev
                </button>
                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded">
                  Slide {currentSlideNumber}
                </span>
                <button
                  onClick={() => changeSlide(currentSlideNumber + 1)}
                  className="px-3 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
                >
                  Next →
                </button>
              </div>
            </div>
            
            <div className="bg-amber-50 border-2 border-gray-300 rounded-lg p-8 min-h-[400px]">
              {currentSlide ? (
                <div className="text-center">
                  <img 
                    src={currentSlide.image_url} 
                    alt={currentSlide.title}
                    className="w-full max-w-2xl mx-auto rounded-lg shadow-md mb-4"
                  />
                  <p className="text-gray-700 text-lg">{currentSlide.content}</p>
                </div>
              ) : (
                <div className="flex items-center justify-center h-full">
                  <p className="text-gray-600 text-lg">Loading slide...</p>
                </div>
              )}
            </div>
          </div>

          {/* Video Section - Takes 1/3 of space on large screens */}
          <div className="lg:col-span-1">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
              <span className="mr-2">🎥</span>
              Live Video Stream
            </h2>
            <div className="bg-amber-50 border-2 border-gray-300 rounded-lg p-6 min-h-[400px] flex items-center justify-center">
              <div className="text-center">
                <div className="w-16 h-16 bg-red-500 rounded-full mx-auto mb-4 flex items-center justify-center">
                  <span className="text-white text-2xl">🔴</span>
                </div>
                <p className="text-gray-600">Live speaker video stream</p>
                <p className="text-sm text-gray-500 mt-2">Coming soon...</p>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Reference Links */}
          <div>
            <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
              <span className="mr-2">📚</span>
              Reference Links
            </h2>
            <div className="bg-amber-50 border-2 border-gray-300 rounded-lg p-6">
              <ul className="space-y-3">
                {references.map((ref, index) => (
                  <li key={index}>
                    <a 
                      href={ref.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 hover:underline transition-colors block"
                    >
                      <span className="font-medium">{ref.title}</span>
                      <p className="text-sm text-gray-600 mt-1">{ref.description}</p>
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Conversation Component */}
          <div>
            <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
              <span className="mr-2">💬</span>
              Live Q&A
            </h2>
            <Conversation />
          </div>
        </div>
      </div>
    </div>
  );
} 