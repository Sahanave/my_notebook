"use client";

import React, { useState, useEffect } from "react";
import { SlideContent, ReferenceLink, LiveUpdate, DocumentSummary } from "@/types/api";
import { ApiClient } from "@/lib/api";
import Conversation from "@/components/Conversation";
import DocumentSummaryComponent from "@/components/DocumentSummary";
import DocumentUpload from "@/components/DocumentUpload";

export default function Home() {
  const [currentSlide, setCurrentSlide] = useState<SlideContent | null>(null);
  const [references, setReferences] = useState<ReferenceLink[]>([]);
  const [liveUpdates, setLiveUpdates] = useState<LiveUpdate[]>([]);
  const [currentSlideNumber, setCurrentSlideNumber] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Document summary state - comes from upload results
  const [documentSummary, setDocumentSummary] = useState<DocumentSummary | null>(null);
  const [summaryLoading, setSummaryLoading] = useState(false);

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

  const handleUploadComplete = (result: any) => {
    console.log('Upload completed:', result);
    
    // Set the document summary directly from upload results
    if (result.documentSummary) {
      setDocumentSummary(result.documentSummary);
      console.log('✅ Document summary updated from upload results');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-4 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading content...</p>
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
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
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
          <DocumentUpload onUploadComplete={handleUploadComplete} />
        </div>

        {/* Document Summary Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
            <span className="mr-2">📄</span>
            Document Summary
          </h2>
          <DocumentSummaryComponent 
            summary={documentSummary} 
            loading={summaryLoading}
          />
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

            {/* Slide Content */}
            {currentSlide && (
              <div className="bg-white rounded-lg shadow-md overflow-hidden">
                <img 
                  src={currentSlide.image_url} 
                  alt={currentSlide.title}
                  className="w-full h-64 object-cover"
                />
                <div className="p-6">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {currentSlide.title}
                  </h3>
                  <p className="text-gray-700 leading-relaxed">
                    {currentSlide.content}
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* References Sidebar */}
          <div className="space-y-6">
            {/* References */}
            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
                <span className="mr-2">🔗</span>
                References
              </h3>
              <div className="space-y-3">
                {references.map((ref, index) => (
                  <div key={index} className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                    <a 
                      href={ref.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 font-medium"
                    >
                      {ref.title}
                    </a>
                    <p className="text-gray-600 text-sm mt-1">{ref.description}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Live Q&A */}
            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
                <span className="mr-2">💬</span>
                Live Q&A
              </h3>
              <Conversation />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 