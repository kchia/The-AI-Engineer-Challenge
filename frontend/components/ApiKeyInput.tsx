"use client";

import React, { useState } from "react";
import { Key, Eye, EyeOff, Check } from "lucide-react";

interface ApiKeyInputProps {
  apiKey: string;
  onApiKeyChange: (key: string) => void;
  onTestConnection: () => Promise<boolean>;
}

export function ApiKeyInput({
  apiKey,
  onApiKeyChange,
  onTestConnection
}: ApiKeyInputProps) {
  const [showKey, setShowKey] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<
    "idle" | "success" | "error"
  >("idle");

  const handleTestConnection = async () => {
    setIsTesting(true);
    setConnectionStatus("idle");

    try {
      const isConnected = await onTestConnection();
      setConnectionStatus(isConnected ? "success" : "error");
    } catch {
      setConnectionStatus("error");
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <label
          htmlFor="api-key"
          className="block text-sm font-medium text-text-primary mb-2"
        >
          OpenAI API Key
        </label>
        <div className="relative">
          <input
            id="api-key"
            type={showKey ? "text" : "password"}
            value={apiKey}
            onChange={(e) => onApiKeyChange(e.target.value)}
            placeholder="Enter your OpenAI API key"
            className="input-field pr-20"
          />
          <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex space-x-1">
            <button
              type="button"
              onClick={() => setShowKey(!showKey)}
              className="p-1 text-text-secondary hover:text-primary transition-colors"
            >
              {showKey ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
            <button
              type="button"
              onClick={handleTestConnection}
              disabled={!apiKey.trim() || isTesting}
              className="p-1 text-text-secondary hover:text-primary transition-colors disabled:opacity-50"
            >
              {isTesting ? (
                <div className="w-4 h-4 border-2 border-secondary border-t-primary rounded-full animate-spin" />
              ) : connectionStatus === "success" ? (
                <Check size={16} className="text-success" />
              ) : (
                <Key size={16} />
              )}
            </button>
          </div>
        </div>
        {connectionStatus === "success" && (
          <p className="text-xs text-success mt-1">✓ Connection successful</p>
        )}
        {connectionStatus === "error" && (
          <p className="text-xs text-error mt-1">
            ✗ Connection failed. Please check your API key.
          </p>
        )}
      </div>

      <div className="text-xs text-text-secondary">
        <p>Your API key is stored locally and never sent to our servers.</p>
        <p>
          Get your API key from{" "}
          <a
            href="https://platform.openai.com/api-keys"
            target="_blank"
            rel="noopener noreferrer"
            className="text-accent hover:underline"
          >
            OpenAI Platform
          </a>
        </p>
      </div>
    </div>
  );
}
