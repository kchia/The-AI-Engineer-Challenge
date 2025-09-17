export interface ChatRequest {
  developer_message: string;
  user_message: string;
  model: string;
  api_key: string;
}

export interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
  timestamp: Date;
}

export interface ApiError {
  message: string;
  status: number;
}

// In production, API calls should be relative to the same domain
// In development, use localhost:8000
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '' 
  : (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000");

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async sendMessage(
    request: ChatRequest,
    onChunk?: (chunk: string) => void
  ): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API Error: ${response.status} - ${errorText}`);
      }

      if (!response.body) {
        throw new Error("No response body received");
      }

      // Handle streaming response
      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      try {
        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            break;
          }

          const chunk = decoder.decode(value, { stream: true });
          if (onChunk) {
            onChunk(chunk);
          }
        }
      } finally {
        reader.releaseLock();
      }
    } catch (error) {
      console.error("API Error:", error);
      throw error;
    }
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/health`);
      return response.ok;
    } catch (error) {
      console.error("Health check failed:", error);
      return false;
    }
  }
}

export const apiClient = new ApiClient();
