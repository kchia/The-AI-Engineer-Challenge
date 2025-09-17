"use client";

import React, { useState, useRef, useEffect } from "react";
import { Message, apiClient } from "@/lib/api";
import { MessageBubble } from "./MessageBubble";
import { MessageInput } from "./MessageInput";
import { ApiKeyInput } from "./ApiKeyInput";
import { ThemeSelector } from "./ThemeSelector";
import { Settings, X, AlertCircle } from "lucide-react";

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [apiKey, setApiKey] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [isUploadingPDF, setIsUploadingPDF] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load API key from localStorage on mount
  useEffect(() => {
    const savedApiKey = localStorage.getItem("openai-api-key");
    if (savedApiKey) {
      setApiKey(savedApiKey);
    }
  }, []);

  // Save API key to localStorage when it changes
  useEffect(() => {
    if (apiKey) {
      localStorage.setItem("openai-api-key", apiKey);
    }
  }, [apiKey]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleTestConnection = async (): Promise<boolean> => {
    try {
      const isHealthy = await apiClient.healthCheck();
      setIsConnected(isHealthy);
      return isHealthy;
    } catch {
      setIsConnected(false);
      return false;
    }
  };

  const handleSendMessage = async (userMessage: string) => {
    if (!apiKey.trim()) {
      setError("Please enter your OpenAI API key in settings");
      setShowSettings(true);
      return;
    }

    if (!isConnected) {
      setError(
        "Cannot connect to the API. Please check your connection and try again."
      );
      return;
    }

    // Add user message
    const userMsg: Message = {
      id: Date.now().toString(),
      content: userMessage,
      role: "user",
      timestamp: new Date()
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);
    setError(null);

    // Create assistant message placeholder
    const assistantMsg: Message = {
      id: (Date.now() + 1).toString(),
      content: "",
      role: "assistant",
      timestamp: new Date()
    };
    setMessages((prev) => [...prev, assistantMsg]);

    try {
      await apiClient.sendMessage(
        {
          developer_message:
            "You are a helpful AI assistant. Provide clear, concise, and accurate responses.",
          user_message: userMessage,
          model: "gpt-4.1-mini",
          api_key: apiKey
        },
        (chunk: string) => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMsg.id
                ? { ...msg, content: msg.content + chunk }
                : msg
            )
          );
        }
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "An error occurred while sending the message"
      );
      // Remove the assistant message if there was an error
      setMessages((prev) => prev.filter((msg) => msg.id !== assistantMsg.id));
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  const handlePDFUpload = async (file: File) => {
    if (!apiKey.trim()) {
      setError("Please enter your OpenAI API key first");
      return;
    }

    setIsUploadingPDF(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("api_key", apiKey);

      // Use the same API base URL logic as the API client
      const API_BASE_URL = process.env.NODE_ENV === 'production' 
        ? '' 
        : (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000");
      
      console.log('PDF upload API_BASE_URL:', API_BASE_URL); // Debug log
      
      const response = await fetch(`${API_BASE_URL}/api/upload-pdf`, {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Upload failed: ${errorText}`);
      }

      const result = await response.json();
      if (result.success) {
        setPdfFile(file);
        setError(null);
      } else {
        throw new Error("Upload failed");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setIsUploadingPDF(false);
    }
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Settings Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-80 bg-surface border-r border-border transform transition-transform duration-300 ease-in-out ${
          showSettings ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h2 className="text-lg font-semibold text-text-primary">Settings</h2>
          <button
            onClick={() => setShowSettings(false)}
            className="p-1 text-text-secondary hover:text-primary transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <div className="p-4 space-y-6">
          <ApiKeyInput
            apiKey={apiKey}
            onApiKeyChange={setApiKey}
            onTestConnection={handleTestConnection}
          />

          <div className="space-y-2">
            <label className="text-sm font-medium text-text-primary">PDF Document (Optional)</label>
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => e.target.files?.[0] && handlePDFUpload(e.target.files[0])}
              disabled={isUploadingPDF}
              className="w-full p-2 border border-border rounded bg-background text-text-primary"
            />
            {pdfFile && (
              <p className="text-xs text-text-secondary">Loaded: {pdfFile.name}</p>
            )}
            {isUploadingPDF && (
              <p className="text-xs text-text-secondary">Processing PDF...</p>
            )}
          </div>

          <ThemeSelector />

          <div className="pt-4 border-t border-border">
            <button onClick={clearChat} className="btn-secondary w-full">
              Clear Chat
            </button>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border bg-surface">
          <div>
            <h1 className="text-xl font-semibold text-text-primary">
              AI Chat Assistant
            </h1>
            <div className="text-sm text-text-secondary">
              <p>{isConnected ? "Connected" : "Disconnected"}</p>
              {pdfFile && (
                <p className="text-xs mt-1">📄 {pdfFile.name}</p>
              )}
            </div>
          </div>
          <button
            onClick={() => setShowSettings(true)}
            className="btn-secondary p-2"
          >
            <Settings size={20} />
          </button>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🤖</span>
                </div>
                <h3 className="text-lg font-medium text-text-primary mb-2">
                  {pdfFile ? `Chat with ${pdfFile.name}` : "Welcome to AI Chat"}
                </h3>
                <p className="text-text-secondary mb-4">
                  {pdfFile 
                    ? "Ask questions about the uploaded PDF document."
                    : "Start a conversation by typing a message below."
                  }
                </p>
                {!apiKey && (
                  <p className="text-sm text-warning">
                    Don&apos;t forget to add your OpenAI API key in settings!
                  </p>
                )}
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))
          )}

          {isLoading && (
            <div className="flex justify-start">
              <div className="message-bubble message-assistant">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                  <div
                    className="w-2 h-2 bg-primary rounded-full animate-pulse"
                    style={{ animationDelay: "0.2s" }}
                  />
                  <div
                    className="w-2 h-2 bg-primary rounded-full animate-pulse"
                    style={{ animationDelay: "0.4s" }}
                  />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Error Display */}
        {error && (
          <div className="mx-4 mb-2 p-3 bg-error/10 border border-error/20 rounded-lg flex items-start space-x-2">
            <AlertCircle
              size={16}
              className="text-error flex-shrink-0 mt-0.5"
            />
            <p className="text-sm text-error">{error}</p>
            <button
              onClick={() => setError(null)}
              className="text-error hover:text-red-600 ml-auto"
            >
              <X size={16} />
            </button>
          </div>
        )}

        {/* Input Area */}
        <MessageInput
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          disabled={!apiKey.trim() || !isConnected}
        />
      </div>

      {/* Overlay for mobile */}
      {showSettings && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setShowSettings(false)}
        />
      )}
    </div>
  );
}
