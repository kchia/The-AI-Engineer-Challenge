"use client";

import React, { useState } from "react";
import { apiClient, GenerateQuizRequest, Quiz, QuizQuestion } from "@/lib/api";
import { Loader2, Play, CheckCircle, XCircle, RotateCcw } from "lucide-react";

interface QuizGeneratorProps {
  content: string;
  apiKey: string;
  subjectCategory?: string;
  onClose: () => void;
}

export function QuizGenerator({ content, apiKey, subjectCategory, onClose }: QuizGeneratorProps) {
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string | boolean>>({});
  const [showResults, setShowResults] = useState(false);
  const [score, setScore] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const generateQuiz = async () => {
    console.log("QuizGenerator - Content received:", content);
    console.log("QuizGenerator - Content length:", content.length);
    console.log("QuizGenerator - Content trimmed:", content.trim().length);
    
    if (!content.trim()) {
      setError("No content available to generate quiz from");
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const request: GenerateQuizRequest = {
        content,
        api_key: apiKey,
        num_questions: 5,
        question_types: ["multiple_choice", "true_false"]
      };

      const response = await apiClient.generateQuiz(request);
      
      if (response.success) {
        setQuiz(response.quiz);
        setCurrentQuestion(0);
        setAnswers({});
        setShowResults(false);
      } else {
        setError("Failed to generate quiz");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate quiz");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleAnswerSelect = (questionId: number, answer: string | boolean) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const nextQuestion = () => {
    if (quiz && currentQuestion < quiz.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const previousQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const submitQuiz = () => {
    if (!quiz) return;

    let correctAnswers = 0;
    quiz.questions.forEach(question => {
      const userAnswer = answers[question.id];
      if (userAnswer === question.correct_answer) {
        correctAnswers++;
      }
    });

    setScore(correctAnswers);
    setShowResults(true);
  };

  const resetQuiz = () => {
    setQuiz(null);
    setCurrentQuestion(0);
    setAnswers({});
    setShowResults(false);
    setScore(0);
    setError(null);
  };

  const getQuestionIcon = (question: QuizQuestion) => {
    if (!showResults) return null;
    
    const userAnswer = answers[question.id];
    const isCorrect = userAnswer === question.correct_answer;
    
    return isCorrect ? (
      <CheckCircle className="w-5 h-5 text-green-500" />
    ) : (
      <XCircle className="w-5 h-5 text-red-500" />
    );
  };

  if (isGenerating) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-surface border border-border rounded-lg p-6 max-w-md w-full mx-4">
          <div className="flex items-center justify-center space-x-2">
            <Loader2 className="w-5 h-5 animate-spin text-primary" />
            <span className="text-text-primary">Generating quiz...</span>
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
                onClick={resetQuiz}
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

  if (!quiz) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-surface border border-border rounded-lg p-6 max-w-md w-full mx-4">
          <div className="text-center">
            <Play className="w-12 h-12 text-primary mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">Generate Quiz</h3>
            <p className="text-text-secondary mb-4">
              Create a quiz from the uploaded content to test your knowledge.
            </p>
            {subjectCategory && (
              <p className="text-sm text-text-secondary mb-4">
                Subject: <span className="font-medium text-primary">{subjectCategory}</span>
              </p>
            )}
            <div className="flex space-x-2">
              <button
                onClick={generateQuiz}
                className="btn-primary flex-1"
              >
                Generate Quiz
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

  if (showResults) {
    const percentage = Math.round((score / quiz.questions.length) * 100);
    
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-surface border border-border rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
          <div className="text-center mb-6">
            <h3 className="text-2xl font-semibold text-text-primary mb-2">Quiz Results</h3>
            <div className="text-4xl font-bold text-primary mb-2">{percentage}%</div>
            <p className="text-text-secondary">
              You got {score} out of {quiz.questions.length} questions correct
            </p>
          </div>

          <div className="space-y-4 mb-6">
            {quiz.questions.map((question, index) => (
              <div key={question.id} className="border border-border rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-medium text-text-primary">
                    Question {index + 1}: {question.question}
                  </h4>
                  {getQuestionIcon(question)}
                </div>
                
                <div className="text-sm text-text-secondary mb-2">
                  <p><strong>Your answer:</strong> {answers[question.id]?.toString() || "Not answered"}</p>
                  <p><strong>Correct answer:</strong> {question.correct_answer.toString()}</p>
                </div>
                
                <div className="text-sm text-text-secondary">
                  <p><strong>Explanation:</strong> {question.explanation}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="flex space-x-2">
            <button
              onClick={resetQuiz}
              className="btn-secondary flex-1"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              New Quiz
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
    );
  }

  const question = quiz.questions[currentQuestion];
  const isLastQuestion = currentQuestion === quiz.questions.length - 1;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-surface border border-border rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-semibold text-text-primary">{quiz.title}</h3>
            <span className="text-sm text-text-secondary">
              Question {currentQuestion + 1} of {quiz.questions.length}
            </span>
          </div>
          <p className="text-text-secondary text-sm">{quiz.description}</p>
        </div>

        <div className="mb-6">
          <h4 className="font-medium text-text-primary mb-4">
            {question.question}
          </h4>

          {question.type === "multiple_choice" && question.options && (
            <div className="space-y-2">
              {question.options.map((option, index) => (
                <label
                  key={index}
                  className="flex items-center space-x-2 p-3 border border-border rounded-lg cursor-pointer hover:bg-background/50"
                >
                  <input
                    type="radio"
                    name={`question-${question.id}`}
                    value={option}
                    checked={answers[question.id] === option}
                    onChange={() => handleAnswerSelect(question.id, option)}
                    className="text-primary"
                  />
                  <span className="text-text-primary">{option}</span>
                </label>
              ))}
            </div>
          )}

          {question.type === "true_false" && (
            <div className="space-y-2">
              <label className="flex items-center space-x-2 p-3 border border-border rounded-lg cursor-pointer hover:bg-background/50">
                <input
                  type="radio"
                  name={`question-${question.id}`}
                  checked={answers[question.id] === true}
                  onChange={() => handleAnswerSelect(question.id, true)}
                  className="text-primary"
                />
                <span className="text-text-primary">True</span>
              </label>
              <label className="flex items-center space-x-2 p-3 border border-border rounded-lg cursor-pointer hover:bg-background/50">
                <input
                  type="radio"
                  name={`question-${question.id}`}
                  checked={answers[question.id] === false}
                  onChange={() => handleAnswerSelect(question.id, false)}
                  className="text-primary"
                />
                <span className="text-text-primary">False</span>
              </label>
            </div>
          )}
        </div>

        <div className="flex justify-between">
          <button
            onClick={previousQuestion}
            disabled={currentQuestion === 0}
            className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>

          {isLastQuestion ? (
            <button
              onClick={submitQuiz}
              className="btn-primary"
            >
              Submit Quiz
            </button>
          ) : (
            <button
              onClick={nextQuestion}
              className="btn-primary"
            >
              Next
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
