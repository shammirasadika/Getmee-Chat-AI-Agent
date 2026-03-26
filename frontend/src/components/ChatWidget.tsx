import { useState, useRef, useEffect } from "react";
import {
  X,
  Send,
  Share2,
  AlertCircle,
  Smile,
  Frown,
  ChevronDown,
  Minimize2,
  Maximize2,
} from "lucide-react";
import { chatService, type ChatResponse } from "@/services/chat.service";
import logo from "@/assets/getmee-logo.svg.png";

type Language = "en" | "es";

const localizedText: Record<
  Language,
  {
    assistantName: string;
    online: string;
    hello: string;
    intro: string;
    askAnything: string;
    topics: string[];
    quickQuestion: string;
    quickQuestions: string[];
    initChat: string;
    inputPlaceholder: string;
    closeChatLabel: string;
    minimizeChatLabel: string;
    openChatLabel: string;
    clearChatTitle: string;
    shareLabel: string;
    sendLabel: string;
    feedbackPrompt: string;
    satisfiedLabel: string;
    notSatisfiedLabel: string;
    greetingMessage: string;
    fallbackErrorReply: string;
    responseError: string;
  }
> = {
  en: {
    assistantName: "Getmee AI Assistant",
    online: "Online",
    hello: "Hello 👋",
    intro: "I'm the Getmee AI Assistant",
    askAnything: "Ask me anything about:",
    topics: [
      "Interview preparation",
      "Resume tips",
      "Using the Getmee platform",
    ],
    quickQuestion: "Quick Question:",
    quickQuestions: [
      "How does AI scoring work?",
      "Interview preparation tips",
      "How do i improve my answers?",
    ],
    initChat: "Initializing chat...",
    inputPlaceholder: "Type your message...",
    closeChatLabel: "Close chat",
    minimizeChatLabel: "Minimize chat",
    openChatLabel: "Open chat",
    clearChatTitle: "Clear chat",
    shareLabel: "Share",
    sendLabel: "Send",
    feedbackPrompt: "Was this response helpful?",
    satisfiedLabel: "Satisfied",
    notSatisfiedLabel: "Not Satisfied",
    greetingMessage:
      "Hello! I'm Getmee AI Assistant. How can I help you today?",
    fallbackErrorReply:
      "I apologize, but I encountered an error processing your request. Please try again.",
    responseError: "Failed to get response",
  },
  es: {
    assistantName: "Asistente IA de Getmee",
    online: "En linea",
    hello: "Hola 👋",
    intro: "Soy el asistente IA de Getmee",
    askAnything: "Preguntame lo que quieras sobre:",
    topics: [
      "Preparacion de entrevistas",
      "Consejos para curriculums",
      "Uso de la plataforma Getmee",
    ],
    quickQuestion: "Pregunta rapida:",
    quickQuestions: [
      "Como funciona la puntuacion de IA?",
      "Consejos para preparar entrevistas",
      "Como puedo mejorar mis respuestas?",
    ],
    initChat: "Iniciando chat...",
    inputPlaceholder: "Escribe tu mensaje...",
    closeChatLabel: "Cerrar chat",
    minimizeChatLabel: "Minimizar chat",
    openChatLabel: "Abrir chat",
    clearChatTitle: "Limpiar chat",
    shareLabel: "Compartir",
    sendLabel: "Enviar",
    feedbackPrompt: "Te fue util esta respuesta?",
    satisfiedLabel: "Satisfecho",
    notSatisfiedLabel: "No satisfecho",
    greetingMessage:
      "Hola! Soy el asistente IA de Getmee. Como puedo ayudarte hoy?",
    fallbackErrorReply:
      "Lo siento, hubo un error al procesar tu solicitud. Intentalo de nuevo.",
    responseError: "No se pudo obtener respuesta",
  },
};

type Message = {
  text: string;
  isUser: boolean;
  time: string;
  id?: string;
};

type FeedbackChoice = "satisfied" | "not_satisfied";

const getTime = () =>
  new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  });

const ChatWidget = () => {
  const [language, setLanguage] = useState<Language>("en");
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [chatStarted, setChatStarted] = useState(false);
  const [isBotTyping, setIsBotTyping] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);
  const [isStartingChat, setIsStartingChat] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isLanguageMenuOpen, setIsLanguageMenuOpen] = useState(false);
  const [feedbackChoice, setFeedbackChoice] = useState<FeedbackChoice | null>(
    null,
  );
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const languageMenuRef = useRef<HTMLDivElement>(null);
  const welcomeScrollRef = useRef<HTMLDivElement>(null);
  const chatScrollRef = useRef<HTMLDivElement>(null);
  const t = localizedText[language];
  const lastBotMessage = [...messages].reverse().find((msg) => !msg.isUser);

  const withLanguageHint = (text: string): string => {
    if (language === "es") {
      return `Please reply in Spanish. User message: ${text}`;
    }
    return text;
  };

  // Initialize chat session on mount
  useEffect(() => {
    const initializeSession = async () => {
      try {
        await chatService.startSession();
        setIsInitializing(false);
      } catch (err) {
        console.error("Failed to initialize chat session:", err);
        setIsInitializing(false);
      }
    };

    initializeSession();

    // Cleanup on unmount
    return () => {
      chatService.endSession().catch(console.error);
    };
  }, []);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isBotTyping]);

  useEffect(() => {
    const handleOutsideClick = (event: MouseEvent) => {
      if (
        languageMenuRef.current &&
        !languageMenuRef.current.contains(event.target as Node)
      ) {
        setIsLanguageMenuOpen(false);
      }
    };

    document.addEventListener("mousedown", handleOutsideClick);
    return () => {
      document.removeEventListener("mousedown", handleOutsideClick);
    };
  }, []);

  useEffect(() => {
    if (chatStarted) {
      requestAnimationFrame(() => {
        chatScrollRef.current?.scrollTo({ top: 0, behavior: "auto" });
      });
      return;
    }

    requestAnimationFrame(() => {
      welcomeScrollRef.current?.scrollTo({ top: 0, behavior: "auto" });
    });
  }, [isMinimized, chatStarted, isInitializing]);

  const addBotReply = async (userText: string) => {
    setIsBotTyping(true);
    setError(null);

    try {
      const response: ChatResponse = await chatService.sendMessage(
        withLanguageHint(userText),
      );

      // Simulate typing delay for better UX
      await new Promise((resolve) => setTimeout(resolve, 600));

      setMessages((prev) => [
        ...prev,
        {
          text: response.message,
          isUser: false,
          time: getTime(),
          id: `bot_${Date.now()}`,
        },
      ]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : t.responseError;
      setError(errorMessage);
      console.error("Error getting bot response:", err);

      // Show error message to user
      setMessages((prev) => [
        ...prev,
        {
          text: t.fallbackErrorReply,
          isUser: false,
          time: getTime(),
          id: `error_${Date.now()}`,
        },
      ]);
    } finally {
      setIsBotTyping(false);
    }
  };

  const handleQuickQuestion = async (question: string) => {
    const userMsg: Message = {
      text: question,
      isUser: true,
      time: getTime(),
      id: `user_${Date.now()}`,
    };
    const botGreeting: Message = {
      text: t.greetingMessage,
      isUser: false,
      time: getTime(),
      id: `greeting_${Date.now()}`,
    };
    setMessages([botGreeting, userMsg]);
    setError(null);
    setFeedbackChoice(null);
    setIsStartingChat(true);

    // Let the welcome screen fade out before switching to the chat view.
    await new Promise((resolve) => setTimeout(resolve, 320));
    setChatStarted(true);
    setIsStartingChat(false);

    await addBotReply(question);
  };

  const handleSend = async () => {
    const text = message.trim();
    if (!text || isBotTyping) return;

    const userMsg: Message = {
      text,
      isUser: true,
      time: getTime(),
      id: `user_${Date.now()}`,
    };

    if (!chatStarted) {
      const botGreeting: Message = {
        text: t.greetingMessage,
        isUser: false,
        time: getTime(),
        id: `greeting_${Date.now()}`,
      };
      setMessages([botGreeting, userMsg]);
      setChatStarted(true);
    } else {
      setMessages((prev) => [...prev, userMsg]);
    }

    setError(null);
    setFeedbackChoice(null);
    setMessage("");
    await addBotReply(text);
  };

  const handleFeedback = async (choice: FeedbackChoice) => {
    setFeedbackChoice(choice);

    if (!lastBotMessage?.id) {
      return;
    }

    const rating = choice === "satisfied" ? 1 : 0;
    await chatService.submitFeedback(lastBotMessage.id, rating);
  };

  return (
    <div
      className={`bg-background flex flex-col ${
        isMinimized
          ? "fixed bottom-4 right-4 z-[2147483000] w-[min(420px,calc(100vw-24px))] h-[min(560px,calc(100vh-32px))] rounded-2xl border border-border bg-white shadow-2xl overflow-hidden"
          : "w-full h-screen"
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-3 sm:px-5 sm:py-4 shrink-0 border-b border-border bg-white">
        <div className="flex items-center gap-2 sm:gap-3 min-w-0">
          <img
            src={logo}
            alt="Getmee"
            className="w-10 h-10 sm:w-12 sm:h-12 object-contain flex-shrink-0"
          />
          <div className="min-w-0">
            <h2 className="text-base sm:text-lg font-semibold text-foreground truncate">
              {t.assistantName}
            </h2>
            <div className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-green-500 flex-shrink-0" />
              <span className="text-xs sm:text-sm text-muted-foreground">
                {t.online}
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative" ref={languageMenuRef}>
            <button
              type="button"
              onClick={() => setIsLanguageMenuOpen((prev) => !prev)}
              className="h-6 sm:h-6 md:h-7 min-w-[56px] sm:min-w-[64px] md:min-w-[92px] inline-flex items-center justify-between gap-1 rounded-lg border border-primary bg-primary px-2 text-[10px] sm:text-[11px] md:text-sm text-white outline-none focus:ring-2 focus:ring-primary"
              aria-label="Language"
              title="Language"
              aria-expanded={isLanguageMenuOpen}
            >
              <span className="md:hidden">
                {language === "en" ? "EN" : "ES"}
              </span>
              <span className="hidden md:inline">
                {language === "en" ? "English" : "Espanol"}
              </span>
              <ChevronDown className="w-3 h-3" />
            </button>

            {isLanguageMenuOpen && (
              <div className="absolute right-0 mt-2 w-20 sm:w-24 md:w-32 rounded-lg border border-border bg-white p-1 shadow-lg z-20">
                <button
                  type="button"
                  onClick={() => {
                    setLanguage("en");
                    setIsLanguageMenuOpen(false);
                  }}
                  className={`w-full rounded-md px-2 py-1.5 text-left text-xs md:text-sm transition-colors ${
                    language === "en"
                      ? "bg-secondary text-foreground"
                      : "text-foreground hover:bg-secondary"
                  }`}
                >
                  <span className="md:hidden">EN</span>
                  <span className="hidden md:inline">English</span>
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setLanguage("es");
                    setIsLanguageMenuOpen(false);
                  }}
                  className={`w-full rounded-md px-2 py-1.5 text-left text-xs md:text-sm transition-colors ${
                    language === "es"
                      ? "bg-secondary text-foreground"
                      : "text-foreground hover:bg-secondary"
                  }`}
                >
                  <span className="md:hidden">ES</span>
                  <span className="hidden md:inline">Espanol</span>
                </button>
              </div>
            )}
          </div>
          <button
            type="button"
            onClick={() => {
              setIsMinimized((prev) => !prev);
              setIsLanguageMenuOpen(false);
              requestAnimationFrame(() => {
                if (chatStarted) {
                  chatScrollRef.current?.scrollTo({ top: 0, behavior: "auto" });
                } else {
                  welcomeScrollRef.current?.scrollTo({
                    top: 0,
                    behavior: "auto",
                  });
                }
              });
            }}
            className="p-1.5 text-muted-foreground hover:bg-secondary rounded-md transition-colors flex-shrink-0"
            aria-label={isMinimized ? t.openChatLabel : t.minimizeChatLabel}
            title={isMinimized ? t.openChatLabel : t.minimizeChatLabel}
          >
            {isMinimized ? <Maximize2 size={16} /> : <Minimize2 size={16} />}
          </button>
          <button
            onClick={() => {
              setIsBotTyping(false);
              setChatStarted(false);
              setMessages([]);
              setMessage("");
              setError(null);
              setIsMinimized(false);
              setFeedbackChoice(null);
            }}
            className="p-1.5 text-destructive hover:bg-secondary rounded-md transition-colors flex-shrink-0"
            aria-label={t.closeChatLabel}
            title={t.clearChatTitle}
          >
            <X size={18} />
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="flex items-center gap-2 px-3 py-2 sm:px-4 sm:py-3 bg-destructive/10 border-b border-destructive/20 text-sm text-destructive">
          <AlertCircle size={16} className="flex-shrink-0" />
          <p className="flex-1 min-w-0">{error}</p>
          <button
            onClick={() => setError(null)}
            className="flex-shrink-0 hover:opacity-75"
            aria-label="Dismiss error"
          >
            ×
          </button>
        </div>
      )}

      {/* Main Content Area */}
      {!chatStarted && !isInitializing && (
        <div
          key={isMinimized ? "welcome-minimized" : "welcome-full"}
          ref={welcomeScrollRef}
          className={`flex-1 overflow-y-auto px-4 py-6 sm:px-5 flex flex-col items-center gap-4 sm:gap-6 ${
            isMinimized ? "justify-start" : "justify-start sm:justify-center"
          } transition-[opacity,transform,filter] duration-350 ease-[cubic-bezier(0.22,1,0.36,1)] motion-reduce:transition-none ${
            isStartingChat
              ? "opacity-0 translate-y-3 scale-[0.985] blur-[1px]"
              : "opacity-100 translate-y-0 scale-100 blur-0"
          }`}
        >
          {/* Greeting */}
          <div className="text-center">
            <h3 className="text-xl sm:text-2xl font-semibold text-foreground">
              {t.hello}
            </h3>
            <p className="text-sm sm:text-base text-muted-foreground mt-1">
              {t.intro}
            </p>
          </div>

          {/* Info Card */}
          <div className="w-full max-w-xl bg-cyan-50 rounded-2xl p-4 sm:p-6 border border-cyan-200 text-center">
            <h4 className="text-base sm:text-lg font-semibold text-foreground mb-3">
              {t.askAnything}
            </h4>
            <ul className="space-y-2 inline-block text-left mx-auto">
              {t.topics.map((item) => (
                <li
                  key={item}
                  className="flex items-start gap-2 text-sm sm:text-base text-foreground"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-primary flex-shrink-0 mt-1.5" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Quick Questions */}
          <div className="w-full max-w-xl">
            <h4 className="text-center font-semibold text-foreground mb-3 text-sm sm:text-base">
              {t.quickQuestion}
            </h4>
            <div className="flex flex-col gap-2 sm:gap-3">
              {t.quickQuestions.map((q) => (
                <button
                  key={q}
                  onClick={() => handleQuickQuestion(q)}
                  className="w-full text-center px-3 py-2.5 sm:px-4 sm:py-3 border border-border rounded-lg text-sm sm:text-base text-foreground hover:bg-secondary transition-colors active:scale-95"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {isInitializing && !chatStarted && (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="flex justify-center mb-4">
              <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
            </div>
            <p className="text-muted-foreground text-sm">{t.initChat}</p>
          </div>
        </div>
      )}

      {/* Chat Conversation View */}
      {chatStarted && (
        <div
          ref={chatScrollRef}
          className="flex-1 overflow-y-auto px-3 py-4 sm:px-5 sm:py-6 flex flex-col gap-4 sm:gap-6 animate-in fade-in-0 zoom-in-95 slide-in-from-bottom-3 duration-500"
        >
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.isUser ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`flex flex-col ${msg.isUser ? "items-end" : "items-start"} max-w-[85%] sm:max-w-[75%]`}
              >
                <div
                  className={`flex items-start gap-2 ${msg.isUser ? "flex-row-reverse" : ""}`}
                >
                  {!msg.isUser && (
                    <img
                      src={logo}
                      alt="Getmee"
                      className="w-8 h-8 sm:w-9 sm:h-9 rounded-full object-contain flex-shrink-0 mt-0.5"
                    />
                  )}
                  <div
                    className={`rounded-2xl px-3 py-2 sm:px-4 sm:py-3 text-sm leading-relaxed ${
                      msg.isUser
                        ? "bg-blue-500 text-white"
                        : "bg-gray-100 text-gray-900"
                    }`}
                  >
                    {msg.text}
                  </div>
                </div>
                <span
                  className={`text-xs text-muted-foreground mt-1 ${
                    msg.isUser ? "mr-2" : "ml-10 sm:ml-12"
                  }`}
                >
                  {msg.time}
                </span>
              </div>
            </div>
          ))}

          {/* Typing Indicator */}
          {isBotTyping && (
            <div className="flex justify-start">
              <div className="flex items-center gap-2 rounded-2xl px-3 py-2 sm:px-4 sm:py-3 bg-gray-100 w-fit">
                <span className="w-2 h-2 rounded-full bg-gray-400 animate-bounce [animation-delay:-0.3s]" />
                <span className="w-2 h-2 rounded-full bg-gray-400 animate-bounce [animation-delay:-0.15s]" />
                <span className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" />
              </div>
            </div>
          )}

          {!isBotTyping && lastBotMessage && (
            <div className="pt-1">
              <p className="text-xs sm:text-sm text-muted-foreground mb-2">
                {t.feedbackPrompt}
              </p>
              <div className="flex flex-wrap items-center gap-2">
                <button
                  onClick={() => handleFeedback("satisfied")}
                  className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-sm font-medium transition-colors ${
                    feedbackChoice === "satisfied"
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border bg-white text-foreground hover:bg-secondary"
                  }`}
                >
                  <Smile className="w-4 h-4" />
                  {t.satisfiedLabel}
                </button>
                <button
                  onClick={() => handleFeedback("not_satisfied")}
                  className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-sm font-medium transition-colors ${
                    feedbackChoice === "not_satisfied"
                      ? "border-destructive bg-destructive/10 text-destructive"
                      : "border-border bg-white text-foreground hover:bg-secondary"
                  }`}
                >
                  <Frown className="w-4 h-4" />
                  {t.notSatisfiedLabel}
                </button>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      )}

      {/* Input Bar */}
      <div className="border-t border-border bg-white shrink-0">
        <div className="px-3 py-3 sm:px-4 sm:py-3 flex items-center gap-2 sm:gap-3">
          <button
            className="p-1.5 sm:p-2 text-primary hover:bg-secondary rounded-md transition-colors flex-shrink-0"
            aria-label={t.shareLabel}
            title={t.shareLabel}
          >
            <Share2 className="w-4 h-4 sm:w-5 sm:h-5" />
          </button>

          <input
            value={message}
            onChange={(e) => setMessage(e.target.value.slice(0, 500))}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder={t.inputPlaceholder}
            disabled={isBotTyping || isInitializing}
            maxLength={500}
            className="flex-1 min-w-0 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 sm:px-4 sm:py-2.5 text-sm text-foreground placeholder:text-muted-foreground outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          />

          <button
            onClick={handleSend}
            disabled={isBotTyping || isInitializing || !message.trim()}
            className="p-1.5 sm:p-2 text-primary hover:bg-secondary rounded-md transition-colors flex-shrink-0 disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label={t.sendLabel}
            title={t.sendLabel}
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatWidget;
