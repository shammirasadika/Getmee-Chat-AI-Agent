import { useState, useRef, useEffect } from "react";
import { X, Minimize2, Maximize2, Send, Share2, Mail, Loader2 } from "lucide-react";
import logo from "@/assets/getmee-logo.svg.png";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8001";

const quickQuestions = [
  "How does AI scoring work?",
  "Interview preparation tips",
  "How do i improve my answers?",
];

type Message = {
  text: string;
  isUser: boolean;
  time: string;
};

const getTime = () =>
  new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  });

const generateSessionId = () =>
  `session_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;

const ChatWidget = () => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [chatStarted, setChatStarted] = useState(false);
  const [isFullScreen, setIsFullScreen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(generateSessionId);

  // Email collection state
  const [showEmailInput, setShowEmailInput] = useState(false);
  const [emailAddress, setEmailAddress] = useState("");
  const [lastFallbackMessage, setLastFallbackMessage] = useState("");
  const [isSubmittingEmail, setIsSubmittingEmail] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendToApi = async (userText: string) => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userText,
          session_id: sessionId,
        }),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data = await res.json();

      const botMsg: Message = {
        text: data.answer,
        isUser: false,
        time: getTime(),
      };
      setMessages((prev) => [...prev, botMsg]);

      // If fallback triggered, show email input
      if (data.requires_email) {
        setShowEmailInput(true);
        setLastFallbackMessage(userText);
      }
    } catch (err) {
      console.error("Chat API error:", err);
      setMessages((prev) => [
        ...prev,
        {
          text: "Sorry, something went wrong. Please try again.",
          isUser: false,
          time: getTime(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitEmail = async () => {
    if (!emailAddress.trim()) return;

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(emailAddress)) {
      setMessages((prev) => [
        ...prev,
        {
          text: "Please enter a valid email address.",
          isUser: false,
          time: getTime(),
        },
      ]);
      return;
    }

    setIsSubmittingEmail(true);
    try {
      const res = await fetch(`${API_BASE}/api/support`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          user_email: emailAddress,
          user_message: lastFallbackMessage,
        }),
      });
      if (!res.ok) throw new Error(`Support API error: ${res.status}`);
      const data = await res.json();

      setShowEmailInput(false);
      setEmailAddress("");
      setMessages((prev) => [
        ...prev,
        {
          text: data.message || "Thank you! A team member will contact you soon.",
          isUser: false,
          time: getTime(),
        },
      ]);
    } catch (err) {
      console.error("Support API error:", err);
      setMessages((prev) => [
        ...prev,
        {
          text: "Failed to submit your request. Please try again.",
          isUser: false,
          time: getTime(),
        },
      ]);
    } finally {
      setIsSubmittingEmail(false);
    }
  };

  const handleQuickQuestion = (question: string) => {
    const userMsg: Message = { text: question, isUser: true, time: getTime() };
    const botGreeting: Message = {
      text: "Hello! I'm GetMee AI Assistant. How can I help you today?",
      isUser: false,
      time: getTime(),
    };
    setMessages([botGreeting, userMsg]);
    setChatStarted(true);
    sendToApi(question);
  };

  const handleSend = () => {
    if (!message.trim() || isLoading) return;
    const userMsg: Message = { text: message, isUser: true, time: getTime() };
    setMessages((prev) => [...prev, userMsg]);
    const text = message;
    setMessage("");
    sendToApi(text);
  };

  return (
    <div
      className={`flex items-center justify-center min-h-screen bg-muted ${isFullScreen ? "p-0" : "p-4"}`}
    >
      <div
        className={`bg-background flex flex-col overflow-hidden transition-all duration-300 ${
          isFullScreen
            ? "w-full h-screen max-h-screen rounded-none border-0"
            : "w-full max-w-lg rounded-2xl shadow-xl border border-border h-[85vh] max-h-[700px]"
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 shrink-0">
          <div className="flex items-center gap-3">
            <img src={logo} alt="GetMee" className="w-12 h-12 object-contain" />
            <div>
              <h2 className="text-xl font-semibold text-foreground">
                GetMee AI Assistant
              </h2>
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-online" />
                <span className="text-sm text-muted-foreground">Online</span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsFullScreen(!isFullScreen)}
              className="p-1.5 text-primary hover:bg-secondary rounded-md transition-colors"
            >
              {isFullScreen ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
            </button>
            <button
              onClick={() => {
                setChatStarted(false);
                setMessages([]);
                setShowEmailInput(false);
                setEmailAddress("");
              }}
              className="p-1.5 text-destructive hover:bg-secondary rounded-md transition-colors"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        <div className="h-px bg-border mx-4 shrink-0" />

        {isExpanded && !chatStarted && (
          <div className="flex-1 overflow-y-auto px-5 py-6 flex flex-col items-center gap-6">
            {/* Greeting */}
            <div className="text-center">
              <h3 className="text-2xl font-semibold text-foreground">
                Hello 👋
              </h3>
              <p className="text-muted-foreground mt-1">
                I'm the GetMee AI Assistant
              </p>
            </div>

            {/* Info Card */}
            <div className="w-full bg-chat-bubble rounded-2xl p-6">
              <h4 className="text-lg font-semibold text-chat-bubble-foreground mb-3">
                Ask me anything about:
              </h4>
              <ul className="space-y-2">
                {[
                  "Interview preparation",
                  "Resume tips",
                  "Using the GetMee platform",
                ].map((item) => (
                  <li
                    key={item}
                    className="flex items-center gap-2 text-chat-bubble-foreground"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-primary" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            {/* Quick Questions */}
            <div className="w-full">
              <h4 className="text-center font-semibold text-foreground mb-4">
                Quick Question:
              </h4>
              <div className="flex flex-col gap-3">
                {quickQuestions.map((q) => (
                  <button
                    key={q}
                    onClick={() => handleQuickQuestion(q)}
                    className="w-full text-left px-4 py-3 border border-border rounded-lg text-foreground hover:bg-secondary transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Chat conversation view */}
        {isExpanded && chatStarted && (
          <div className="flex-1 overflow-y-auto px-5 py-6 flex flex-col gap-6">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.isUser ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`flex flex-col ${msg.isUser ? "items-end" : "items-start"} max-w-[80%]`}
                >
                  <div
                    className={`flex items-start gap-2.5 ${msg.isUser ? "flex-row-reverse" : ""}`}
                  >
                    {!msg.isUser && (
                      <img
                        src={logo}
                        alt="GetMee"
                        className="w-9 h-9 rounded-full object-contain shrink-0 mt-0.5"
                      />
                    )}
                    <div
                      className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                        msg.isUser
                          ? "bg-chat-bubble text-chat-bubble-foreground"
                          : "bg-chat-bubble text-chat-bubble-foreground"
                      }`}
                    >
                      {msg.text}
                    </div>
                  </div>
                  <span
                    className={`text-xs text-muted-foreground mt-1.5 ${msg.isUser ? "mr-1" : "ml-12"}`}
                  >
                    {msg.time}
                  </span>
                </div>
              </div>
            ))}

            {/* Loading indicator */}
            {isLoading && (
              <div className="flex justify-start">
                <div className="flex items-start gap-2.5 max-w-[80%]">
                  <img
                    src={logo}
                    alt="GetMee"
                    className="w-9 h-9 rounded-full object-contain shrink-0 mt-0.5"
                  />
                  <div className="rounded-2xl px-4 py-3 bg-chat-bubble">
                    <Loader2 size={18} className="animate-spin text-muted-foreground" />
                  </div>
                </div>
              </div>
            )}

            {/* Email input form (shown after fallback) */}
            {showEmailInput && (
              <div className="mx-auto w-full max-w-sm bg-secondary rounded-2xl p-4 flex flex-col gap-3">
                <div className="flex items-center gap-2 text-sm font-medium text-foreground">
                  <Mail size={16} />
                  <span>Enter your email to connect with support</span>
                </div>
                <input
                  type="email"
                  value={emailAddress}
                  onChange={(e) => setEmailAddress(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSubmitEmail()}
                  placeholder="your.email@example.com"
                  className="bg-background rounded-lg px-4 py-2.5 text-foreground placeholder:text-muted-foreground outline-none focus:ring-2 focus:ring-ring text-sm"
                />
                <div className="flex gap-2">
                  <button
                    onClick={handleSubmitEmail}
                    disabled={isSubmittingEmail}
                    className="flex-1 bg-primary text-primary-foreground rounded-lg px-4 py-2 text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {isSubmittingEmail ? (
                      <Loader2 size={16} className="animate-spin" />
                    ) : (
                      <Send size={16} />
                    )}
                    Submit
                  </button>
                  <button
                    onClick={() => {
                      setShowEmailInput(false);
                      setEmailAddress("");
                    }}
                    className="px-4 py-2 text-sm text-muted-foreground hover:bg-background rounded-lg transition-colors"
                  >
                    Skip
                  </button>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Input bar */}
        {isExpanded && chatStarted && (
          <>
            <div className="h-px bg-border mx-4 shrink-0" />
            <div className="px-4 py-3 flex items-center gap-3 shrink-0">
              <button className="p-2 text-primary hover:bg-secondary rounded-md transition-colors shrink-0">
                <Share2 size={20} />
              </button>
              <input
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                placeholder="Type your message..."
                disabled={isLoading}
                className="flex-1 bg-secondary rounded-lg px-4 py-2.5 text-foreground placeholder:text-muted-foreground outline-none focus:ring-2 focus:ring-ring text-sm disabled:opacity-50"
              />
              <button
                onClick={handleSend}
                disabled={isLoading}
                className="p-2 text-primary hover:bg-secondary rounded-md transition-colors shrink-0 disabled:opacity-50"
              >
                <Send size={20} />
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ChatWidget;
