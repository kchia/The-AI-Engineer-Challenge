"use client";

import React, { useState } from "react";
import { apiClient, GenerateStudyGuideRequest, StudyGuide } from "@/lib/api";
import { Loader2, BookOpen, CheckCircle, XCircle, Download, Clock, Lightbulb, Target } from "lucide-react";

interface StudyGuideProps {
  content: string;
  apiKey: string;
  subjectCategory?: string;
  onClose: () => void;
}

export function StudyGuide({ content, apiKey, subjectCategory, onClose }: StudyGuideProps) {
  const [studyGuide, setStudyGuide] = useState<StudyGuide | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateStudyGuide = async () => {
    if (!content.trim()) {
      setError("No content available to generate study guide from");
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const request: GenerateStudyGuideRequest = {
        content,
        api_key: apiKey,
        subject_category: subjectCategory
      };

      const response = await apiClient.generateStudyGuide(request);
      
      if (response.success) {
        setStudyGuide(response.study_guide);
      } else {
        setError("Failed to generate study guide");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate study guide");
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadStudyGuide = () => {
    if (!studyGuide) return;

    const content = `
# ${studyGuide.title}

**Subject:** ${studyGuide.subject}
**Estimated Study Time:** ${studyGuide.estimated_study_time}

## Key Concepts
${studyGuide.key_concepts.map(concept => `- ${concept}`).join('\n')}

## Important Points
${studyGuide.important_points.map(point => `- ${point}`).join('\n')}

## Study Tips
${studyGuide.study_tips.map(tip => `- ${tip}`).join('\n')}

## Practice Questions
${studyGuide.practice_questions.map((question, index) => `${index + 1}. ${question}`).join('\n')}

## Summary
${studyGuide.summary}
    `.trim();

    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${studyGuide.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (isGenerating) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-surface border border-border rounded-lg p-6 max-w-md w-full mx-4">
          <div className="flex items-center justify-center space-x-2">
            <Loader2 className="w-5 h-5 animate-spin text-primary" />
            <span className="text-text-primary">Generating study guide...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-surface border border-border rounded-lg p-6 max-w-md w-full mx-4">
          <div className="text-center">
            <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">Error</h3>
            <p className="text-text-secondary mb-4">{error}</p>
            <div className="flex space-x-2">
              <button
                onClick={() => {
                  setError(null);
                  generateStudyGuide();
                }}
                className="btn-secondary flex-1"
              >
                Try Again
              </button>
              <button
                onClick={onClose}
                className="btn-primary flex-1"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!studyGuide) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-surface border border-border rounded-lg p-6 max-w-md w-full mx-4">
          <div className="text-center">
            <BookOpen className="w-12 h-12 text-primary mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">Generate Study Guide</h3>
            <p className="text-text-secondary mb-4">
              Create a comprehensive study guide from the uploaded content to help you learn effectively.
            </p>
            {subjectCategory && (
              <p className="text-sm text-text-secondary mb-4">
                Subject: <span className="font-medium text-primary">{subjectCategory}</span>
              </p>
            )}
            <div className="flex space-x-2">
              <button
                onClick={generateStudyGuide}
                className="btn-primary flex-1"
              >
                Generate Study Guide
              </button>
              <button
                onClick={onClose}
                className="btn-secondary flex-1"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-surface border border-border rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-2xl font-semibold text-text-primary mb-2">{studyGuide.title}</h3>
            <div className="flex items-center space-x-4 text-sm text-text-secondary">
              <span className="flex items-center">
                <BookOpen className="w-4 h-4 mr-1" />
                {studyGuide.subject}
              </span>
              <span className="flex items-center">
                <Clock className="w-4 h-4 mr-1" />
                {studyGuide.estimated_study_time}
              </span>
            </div>
          </div>
          <button
            onClick={downloadStudyGuide}
            className="btn-secondary flex items-center"
          >
            <Download className="w-4 h-4 mr-2" />
            Download
          </button>
        </div>

        <div className="space-y-6">
          {/* Key Concepts */}
          <div>
            <h4 className="text-lg font-semibold text-text-primary mb-3 flex items-center">
              <Target className="w-5 h-5 mr-2 text-primary" />
              Key Concepts
            </h4>
            <ul className="space-y-2">
              {studyGuide.key_concepts.map((concept, index) => (
                <li key={index} className="flex items-start">
                  <CheckCircle className="w-4 h-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span className="text-text-primary">{concept}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Important Points */}
          <div>
            <h4 className="text-lg font-semibold text-text-primary mb-3 flex items-center">
              <CheckCircle className="w-5 h-5 mr-2 text-primary" />
              Important Points
            </h4>
            <ul className="space-y-2">
              {studyGuide.important_points.map((point, index) => (
                <li key={index} className="flex items-start">
                  <div className="w-2 h-2 bg-primary rounded-full mr-3 mt-2 flex-shrink-0" />
                  <span className="text-text-primary">{point}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Study Tips */}
          <div>
            <h4 className="text-lg font-semibold text-text-primary mb-3 flex items-center">
              <Lightbulb className="w-5 h-5 mr-2 text-primary" />
              Study Tips
            </h4>
            <ul className="space-y-2">
              {studyGuide.study_tips.map((tip, index) => (
                <li key={index} className="flex items-start">
                  <Lightbulb className="w-4 h-4 text-yellow-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span className="text-text-primary">{tip}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Practice Questions */}
          <div>
            <h4 className="text-lg font-semibold text-text-primary mb-3 flex items-center">
              <BookOpen className="w-5 h-5 mr-2 text-primary" />
              Practice Questions
            </h4>
            <ol className="space-y-2">
              {studyGuide.practice_questions.map((question, index) => (
                <li key={index} className="flex items-start">
                  <span className="font-medium text-primary mr-2">{index + 1}.</span>
                  <span className="text-text-primary">{question}</span>
                </li>
              ))}
            </ol>
          </div>

          {/* Summary */}
          <div>
            <h4 className="text-lg font-semibold text-text-primary mb-3">Summary</h4>
            <div className="bg-background/50 border border-border rounded-lg p-4">
              <p className="text-text-primary leading-relaxed">{studyGuide.summary}</p>
            </div>
          </div>
        </div>

        <div className="flex justify-end mt-6">
          <button
            onClick={onClose}
            className="btn-primary"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
