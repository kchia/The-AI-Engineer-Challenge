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

export interface UploadDocumentRequest {
  api_key: string;
  file: File;
}

export interface UploadDocumentResponse {
  success: boolean;
  filename: string;
  file_type: string;
  chunks: number;
  text_length: number;
  subject_category: string;
  category_confidence: number;
  category_scores: Record<string, number>;
}

export interface CategorizeContentRequest {
  text: string;
  confidence_threshold?: number;
}

export interface CategorizeContentResponse {
  success: boolean;
  category: string;
  confidence: number;
  scores: Record<string, number>;
  keywords_found: string[];
  total_keywords: number;
  text_length: number;
  available_categories: string[];
}

export interface GenerateQuizRequest {
  content: string;
  api_key: string;
  num_questions?: number;
  question_types?: string[];
}

export interface QuizQuestion {
  id: number;
  type: string;
  question: string;
  options?: string[];
  correct_answer: string | boolean;
  explanation: string;
  difficulty: string;
}

export interface Quiz {
  title: string;
  description: string;
  questions: QuizQuestion[];
  total_questions: number;
  estimated_time: string;
}

export interface GenerateQuizResponse {
  success: boolean;
  quiz: Quiz;
}

export interface GenerateStudyGuideRequest {
  content: string;
  api_key: string;
  subject_category?: string;
}

export interface StudyGuide {
  title: string;
  subject: string;
  key_concepts: string[];
  important_points: string[];
  study_tips: string[];
  practice_questions: string[];
  summary: string;
  estimated_study_time: string;
}

export interface GenerateStudyGuideResponse {
  success: boolean;
  study_guide: StudyGuide;
}

export interface SupportedFileTypesResponse {
  supported_types: Record<string, string>;
  extensions: string[];
}

export interface SubjectCategoriesResponse {
  categories: string[];
  total_categories: number;
}

export interface QuestionTypesResponse {
  question_types: string[];
  descriptions: Record<string, string>;
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

  // Document upload with multiple file types
  async uploadDocument(request: UploadDocumentRequest): Promise<UploadDocumentResponse> {
    try {
      const formData = new FormData();
      formData.append("file", request.file);
      formData.append("api_key", request.api_key);

      const response = await fetch(`${this.baseUrl}/api/upload-document`, {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Upload failed: ${errorText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Document upload failed:", error);
      throw error;
    }
  }

  // Content categorization
  async categorizeContent(request: CategorizeContentRequest): Promise<CategorizeContentResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/categorize-content`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Categorization failed: ${errorText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Content categorization failed:", error);
      throw error;
    }
  }

  // Quiz generation
  async generateQuiz(request: GenerateQuizRequest): Promise<GenerateQuizResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/generate-quiz`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Quiz generation failed: ${errorText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Quiz generation failed:", error);
      throw error;
    }
  }

  // Study guide generation
  async generateStudyGuide(request: GenerateStudyGuideRequest): Promise<GenerateStudyGuideResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/generate-study-guide`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Study guide generation failed: ${errorText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Study guide generation failed:", error);
      throw error;
    }
  }

  // Get supported file types
  async getSupportedFileTypes(): Promise<SupportedFileTypesResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/supported-file-types`);
      if (!response.ok) {
        throw new Error(`Failed to get supported file types: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error("Failed to get supported file types:", error);
      throw error;
    }
  }

  // Get subject categories
  async getSubjectCategories(): Promise<SubjectCategoriesResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/subject-categories`);
      if (!response.ok) {
        throw new Error(`Failed to get subject categories: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error("Failed to get subject categories:", error);
      throw error;
    }
  }

  // Get question types
  async getQuestionTypes(): Promise<QuestionTypesResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/quiz-question-types`);
      if (!response.ok) {
        throw new Error(`Failed to get question types: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error("Failed to get question types:", error);
      throw error;
    }
  }
}

export const apiClient = new ApiClient();
