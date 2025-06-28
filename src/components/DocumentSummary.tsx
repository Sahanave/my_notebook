"use client";

import React, { useState, useEffect, forwardRef, useImperativeHandle } from 'react';
import { DocumentSummary } from '@/types/api';
import { ApiClient } from '@/lib/api';

export interface DocumentSummaryRef {
  refreshSummary: () => Promise<void>;
}

const DocumentSummaryComponent = forwardRef<DocumentSummaryRef>((props, ref) => {
  const [summary, setSummary] = useState<DocumentSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedSection, setExpandedSection] = useState<string | null>(null);

  useEffect(() => {
    loadSummary();
  }, []);

  // Expose refresh function to parent component
  useImperativeHandle(ref, () => ({
    refreshSummary: loadSummary
  }));

  const loadSummary = async () => {
    try {
      setLoading(true);
      const documentSummary = await ApiClient.getDocumentSummary();
      setSummary(documentSummary);
    } catch (err) {
      setError('Failed to load document summary');
      console.error('Error loading document summary:', err);
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (level: string) => {
    switch (level) {
      case 'beginner':
        return 'bg-green-100 text-green-800';
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800';
      case 'advanced':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getDocumentTypeIcon = (type: string) => {
    switch (type) {
      case 'research_paper':
        return '📄';
      case 'tutorial':
        return '📚';
      case 'book_chapter':
        return '📖';
      case 'article':
        return '📰';
      default:
        return '📝';
    }
  };

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  if (loading) {
    return (
      <div className="bg-amber-50 border-2 border-gray-300 rounded-lg p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-full"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6"></div>
        </div>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="bg-amber-50 border-2 border-gray-300 rounded-lg p-6">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'No summary available'}</p>
          <button 
            onClick={loadSummary}
            className="text-sm text-blue-600 hover:text-blue-800 underline"
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-amber-50 border-2 border-gray-300 rounded-lg p-6 space-y-6">
      {/* Header */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{getDocumentTypeIcon(summary.document_type)}</span>
          <h3 className="text-xl font-bold text-gray-900">{summary.title}</h3>
        </div>
        
        <div className="flex flex-wrap gap-2">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getDifficultyColor(summary.difficulty_level)}`}>
            {summary.difficulty_level}
          </span>
          <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
            ⏱️ {summary.estimated_read_time}
          </span>
          <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">
            {summary.document_type.replace('_', ' ')}
          </span>
        </div>
      </div>

      {/* Abstract */}
      <div className="space-y-2">
        <h4 className="font-semibold text-gray-800">Abstract</h4>
        <p className="text-gray-700 text-sm leading-relaxed">{summary.abstract}</p>
      </div>

      {/* Key Points */}
      <div className="space-y-2">
        <button 
          onClick={() => toggleSection('keyPoints')}
          className="flex items-center justify-between w-full font-semibold text-gray-800 hover:text-gray-600"
        >
          <span>Key Points ({summary.key_points.length})</span>
          <span className="text-lg">
            {expandedSection === 'keyPoints' ? '▼' : '▶'}
          </span>
        </button>
        {expandedSection === 'keyPoints' && (
          <ul className="space-y-2 ml-4">
            {summary.key_points.map((point, index) => (
              <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                <span className="text-blue-600 font-bold">•</span>
                <span>{point}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Main Topics */}
      <div className="space-y-2">
        <button 
          onClick={() => toggleSection('mainTopics')}
          className="flex items-center justify-between w-full font-semibold text-gray-800 hover:text-gray-600"
        >
          <span>Main Topics ({summary.main_topics.length})</span>
          <span className="text-lg">
            {expandedSection === 'mainTopics' ? '▼' : '▶'}
          </span>
        </button>
        {expandedSection === 'mainTopics' && (
          <div className="flex flex-wrap gap-2 mt-2">
            {summary.main_topics.map((topic, index) => (
              <span 
                key={index}
                className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm border border-gray-200"
              >
                {topic}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Metadata */}
      <div className="border-t border-gray-200 pt-4 space-y-2">
        <div className="text-sm text-gray-600">
          <span className="font-medium">Authors:</span> {summary.authors.join(', ')}
        </div>
        <div className="text-sm text-gray-600">
          <span className="font-medium">Published:</span> {summary.publication_date}
        </div>
      </div>
    </div>
  );
});

DocumentSummaryComponent.displayName = 'DocumentSummaryComponent';

export default DocumentSummaryComponent; 