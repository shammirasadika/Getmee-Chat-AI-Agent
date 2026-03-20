import { useState, useRef, useEffect } from "react";
import { X, Minimize2, Maximize2, Send, Share2 } from "lucide-react";
import logo from "@/assets/getmee-logo.svg.png";

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

const ChatWidget = () => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [chatStarted, setChatStarted] = useState(false);
  const [isFullScreen, setIsFullScreen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const addBotReply = (userText: string) => {
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          text: `I'd be happy to help you with "${userText}"! Could you please tell me specifically what you'd like to know?`,
          isUser: false,
          time: getTime(),
        },
      ]);
    }, 1000);
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
    addBotReply(question);
  };

  const handleSend = () => {
    if (!message.trim()) return;
    const userMsg: Message = { text: message, isUser: true, time: getTime() };
    setMessages((prev) => [...prev, userMsg]);
    addBotReply(message);
    setMessage("");
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
                className="flex-1 bg-secondary rounded-lg px-4 py-2.5 text-foreground placeholder:text-muted-foreground outline-none focus:ring-2 focus:ring-ring text-sm"
              />
              <button
                onClick={handleSend}
                className="p-2 text-primary hover:bg-secondary rounded-md transition-colors shrink-0"
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
