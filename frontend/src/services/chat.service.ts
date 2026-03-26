/**
 * Chat Service - Handles all chat API communication
 * Supports both real backend API and mock responses
 */

export interface ChatMessage {
  id?: string;
  text: string;
  isUser: boolean;
  timestamp: string;
  sessionId?: string;
}

export interface ChatResponse {
  message: string;
  isStreaming?: boolean;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const MOCK_MODE = import.meta.env.VITE_MOCK_MODE !== "false";

class ChatService {
  private sessionId: string = this.generateSessionId();

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Send a message to the chat API
   * Falls back to mock response if API is unavailable
   */
  async sendMessage(messageText: string): Promise<ChatResponse> {
    if (MOCK_MODE) {
      return this.mockBotResponse(messageText);
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/send`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: messageText,
          sessionId: this.sessionId,
          timestamp: new Date().toISOString(),
        }),
      });

      if (!response.ok) {
        console.warn(
          `Chat API error: ${response.status}. Falling back to mock response.`,
        );
        return this.mockBotResponse(messageText);
      }

      const data = await response.json();
      return {
        message: data.reply || data.message || "Unable to process your request",
        isStreaming: data.isStreaming || false,
      };
    } catch (error) {
      console.warn("Chat API request failed, using mock response:", error);
      return this.mockBotResponse(messageText);
    }
  }

  /**
   * Start a new chat session
   */
  async startSession(userId?: string): Promise<{ sessionId: string }> {
    this.sessionId = this.generateSessionId();

    if (MOCK_MODE) {
      return { sessionId: this.sessionId };
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/session`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userId: userId || "anonymous",
          timestamp: new Date().toISOString(),
        }),
      });

      if (response.ok) {
        const data = await response.json();
        this.sessionId = data.sessionId || this.sessionId;
      }
    } catch (error) {
      console.warn("Failed to start session with API:", error);
    }

    return { sessionId: this.sessionId };
  }

  /**
   * End the current chat session
   */
  async endSession(): Promise<void> {
    if (MOCK_MODE) return;

    try {
      await fetch(`${API_BASE_URL}/api/chat/session/${this.sessionId}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
      });
    } catch (error) {
      console.warn("Failed to end session:", error);
    }
  }

  /**
   * Get chat history for current session
   */
  async getChatHistory(): Promise<ChatMessage[]> {
    if (MOCK_MODE) {
      return [];
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/chat/history/${this.sessionId}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        },
      );

      if (response.ok) {
        const data = await response.json();
        return data.messages || [];
      }
    } catch (error) {
      console.warn("Failed to fetch chat history:", error);
    }

    return [];
  }

  /**
   * Submit feedback for a message
   */
  async submitFeedback(messageId: string, rating: number): Promise<void> {
    if (MOCK_MODE) return;

    try {
      await fetch(`${API_BASE_URL}/api/chat/feedback`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messageId,
          rating,
          sessionId: this.sessionId,
          timestamp: new Date().toISOString(),
        }),
      });
    } catch (error) {
      console.warn("Failed to submit feedback:", error);
    }
  }

  /**
   * Mock bot response for development/fallback
   * Generates realistic responses based on user input
   */
  private mockBotResponse(userText: string): ChatResponse {
    const lowerText = userText.toLowerCase();

    // Response templates based on keywords
    const responses: Record<string, string[]> = {
      scoring: [
        "Getmee's AI scoring system evaluates your responses based on several factors: clarity, relevance, completeness, and professionalism. Each factor is weighted to provide a comprehensive assessment.",
        "The scoring algorithm uses natural language processing to analyze your answers for quality, coherence, and relevance to the question asked.",
      ],
      interview: [
        "For interview preparation, I recommend: 1) Practice answering common questions aloud, 2) Research the company thoroughly, 3) Prepare examples of your achievements, 4) Practice active listening skills.",
        "Great interview tips: Be specific with examples, maintain good eye contact (or camera eye for video), ask thoughtful questions about the role, and follow up within 24 hours.",
      ],
      improve: [
        "To improve your answers, focus on: 1) Being more specific and detailed, 2) Using the STAR method (Situation, Task, Action, Result), 3) Practicing time management, 4) Getting feedback from peers.",
        "Here are ways to enhance your responses: Review recorded practice sessions, ask for feedback from mentors, study model answers, and practice regularly.",
      ],
      platform: [
        "Getmee is an AI-powered interview and career development platform designed to help you prepare for interviews, improve your communication skills, and get real-time feedback on your performance.",
        "On the Getmee platform, you can practice interviews, get AI-generated feedback, track your progress, and access learning resources tailored to your career goals.",
      ],
    };

    // Find matching category
    for (const [keyword, messages] of Object.entries(responses)) {
      if (lowerText.includes(keyword)) {
        return {
          message: messages[Math.floor(Math.random() * messages.length)],
          isStreaming: false,
        };
      }
    }

    // Default response
    const defaultResponses = [
      `I'd be happy to help you with "${userText}"! Could you provide more specific details so I can give you a better answer?`,
      `That's a great question about "${userText}". Based on best practices, I'd suggest exploring this further. Would you like more specific guidance?`,
      `Regarding "${userText}", here are some key points to consider: First, thoroughly understand the context. Second, practice regularly to improve your skills. Third, seek feedback from others.`,
    ];

    return {
      message:
        defaultResponses[Math.floor(Math.random() * defaultResponses.length)],
      isStreaming: false,
    };
  }

  /**
   * Get the current session ID
   */
  getSessionId(): string {
    return this.sessionId;
  }
}

// Export singleton instance
export const chatService = new ChatService();
