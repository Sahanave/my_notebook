"use client";

import React, { useState } from "react";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (question.trim()) {
      setSubmitted(true);
      // Reset after 3 seconds
      setTimeout(() => {
        setSubmitted(false);
        setQuestion("");
      }, 3000);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Are you taking Notes
          </h1>
        </div>

        {/* Main Content Area */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Slides Section - Takes 2/3 of space on large screens */}
          <div className="lg:col-span-2">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
              <span className="mr-2">📑</span>
              Slide Placeholder
            </h2>
            <div className="bg-amber-50 border-2 border-gray-300 rounded-lg p-8 min-h-[400px] flex items-center justify-center">
              <p className="text-gray-600 text-lg">Add your slides or visuals here.</p>
            </div>
          </div>

          {/* Video Section - Takes 1/3 of space on large screens */}
          <div className="lg:col-span-1">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
              <span className="mr-2">🎥</span>
              Live Video Placeholder
            </h2>
            <div className="bg-amber-50 border-2 border-gray-300 rounded-lg p-6 min-h-[400px] flex items-center justify-center">
              <p className="text-gray-600 text-center">Live speaker video stream here.</p>
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
                <li>
                  <a 
                    href="#" 
                    className="text-blue-600 hover:text-blue-800 hover:underline transition-colors"
                  >
                    Configure Claude Code on Vertex
                  </a>
                </li>
                <li>
                  <a 
                    href="#" 
                    className="text-blue-600 hover:text-blue-800 hover:underline transition-colors"
                  >
                    Learn more about MCP
                  </a>
                </li>
                <li>
                  <a 
                    href="#" 
                    className="text-blue-600 hover:text-blue-800 hover:underline transition-colors"
                  >
                    Get started with Claude on Vertex AI
                  </a>
                </li>
              </ul>
            </div>
          </div>

          {/* Question Form */}
          <div>
            <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
              <span className="mr-2">❓</span>
              Ask a Question
            </h2>
            <div className="bg-amber-50 border-2 border-gray-300 rounded-lg p-6">
              <p className="text-gray-600 mb-4">Form for live Q&A interaction.</p>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Enter your question:"
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                  />
                </div>
                <button
                  type="submit"
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
                >
                  Submit
                </button>
              </form>
              {submitted && (
                <div className="mt-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded-md">
                  Your question has been submitted!
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 