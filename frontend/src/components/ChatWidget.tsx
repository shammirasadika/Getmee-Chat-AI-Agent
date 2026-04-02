  // Type guard for fallback message object
  function isFallbackObj(msg: unknown): msg is { _botDirectedSupport?: boolean; _source?: string } {
    return (
      typeof msg === "object" &&
      msg !== null &&
      ("_botDirectedSupport" in msg || "_source" in msg)
    );
  }
import { useState, useRef, useEffect } from "react";
import { Send, Mail, Loader2, Globe, RotateCcw, MessageCircle, Sparkles, SmilePlus, Frown, Upload } from "lucide-react";
import ReactMarkdown from "react-markdown";
import logo from "@/assets/getmee-logo.svg.png";

const API_BASE = import.meta.env.VITE_API_BASE || "";

type Language = "en" | "es";

const translations = {
  en: {
    title: "GetMee AI Assistant",
    online: "Online",
    greeting: "Hello 👋",
    subtitle: "I'm the GetMee AI Assistant. How can I help you today?",
    askAbout: "I can help you with:",
    topics: [
      "Login & account access",
      "Platform features & setup",
      "User & group management",
    ],
    quickQuestionLabel: "Try asking:",
    quickQuestions: [
      "I can't log into my account",
      "How does white-label onboarding work?",
      "I didn't receive my login email",
      "The app keeps crashing",
      "The video is not loading",
    ],
    botGreeting: "Hello! I'm GetMee AI Assistant. How can I help you today?",
    placeholder: "Type your message...",
    newChat: "New Chat",
    emailPrompt: "Please share your email so our support team can assist you",
    emailPlaceholder: "your.email@example.com",
    submit: "Submit",
    skip: "Skip",
    invalidEmail: "Please enter a valid email address.",
    errorMsg: "Sorry, something went wrong. Please try again.",
    emailSuccess: "Thank you! A team member will contact you soon.",
    emailError: "Failed to submit your request. Please try again.",
    optional_comment: "Optional comment",
    satisfied: "Satisfied",
    not_satisfied: "Not Satisfied",
    was_this_helpful: "Was this helpful?",
    feedback_thank_you: "Thank you for your feedback!",
    feedback_prompt: "Please rate your experience.",
    cancel: "Cancel",
  },
  es: {
    title: "Asistente IA GetMee",
    online: "En línea",
    greeting: "Hola 👋",
    subtitle: "Soy el Asistente IA de GetMee. ¿En qué puedo ayudarte hoy?",
    askAbout: "Puedo ayudarte con:",
    topics: [
      "Inicio de sesión y acceso",
      "Funciones y configuración de la plataforma",
      "Gestión de usuarios y grupos",
    ],
    quickQuestionLabel: "Intenta preguntar:",
    quickQuestions: [
      "No puedo iniciar sesión en mi cuenta",
      "¿Cómo funciona la incorporación de marca blanca?",
      "No recibí mi correo de inicio de sesión",
      "La aplicación se sigue cerrando",
      "El video no se carga",
    ],
    botGreeting:
      "¡Hola! Soy el Asistente IA de GetMee. ¿En qué puedo ayudarte hoy?",
    placeholder: "Escribe tu mensaje...",
    newChat: "Nuevo Chat",
    emailPrompt: "Comparte tu correo para que nuestro equipo pueda ayudarte",
    emailPlaceholder: "tu.correo@ejemplo.com",
    submit: "Enviar",
    skip: "Omitir",
    invalidEmail: "Por favor ingresa un correo electrónico válido.",
    errorMsg: "Lo sentimos, algo salió mal. Inténtalo de nuevo.",
    emailSuccess: "¡Gracias! Un miembro del equipo te contactará pronto.",
    emailError: "No se pudo enviar tu solicitud. Inténtalo de nuevo.",
    optional_comment: "Comentario opcional",
    satisfied: "Satisfecho",
    not_satisfied: "No satisfecho",
    was_this_helpful: "¿Fue útil?",
    feedback_thank_you: "¡Gracias por tus comentarios!",
    feedback_prompt: "Por favor califica tu experiencia.",
    cancel: "Cancelar",
  },
};

type Message = {
  text: string;
  isUser: boolean;
  time: string;
  messageId?: string;
};

const getTime = () =>
  new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  });

const generateSessionId = () =>
  `session_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;

/* ---- Typing dots animation ---- */
const TypingIndicator = () => (
  <div className="flex items-center gap-1 px-1 py-0.5">
    <span className="w-2 h-2 rounded-full bg-muted-foreground/60 animate-bounce [animation-delay:0ms]" />
    <span className="w-2 h-2 rounded-full bg-muted-foreground/60 animate-bounce [animation-delay:150ms]" />
    <span className="w-2 h-2 rounded-full bg-muted-foreground/60 animate-bounce [animation-delay:300ms]" />
  </div>
);


const ChatWidget = () => {
  const [lang, setLang] = useState<Language>("en");
    // Translation object for current language
    const i = translations[lang];
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [chatStarted, setChatStarted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(generateSessionId);

  // UI state
  const [showRecontactConfirmation, setShowRecontactConfirmation] = useState(false);
  const [pendingRecontactMsg, setPendingRecontactMsg] = useState<string|null>(null);
  const [pendingRecontactData, setPendingRecontactData] = useState<any>(null);
  const [recontactLoading, setRecontactLoading] = useState(false);
  const [recontactJustHandled, setRecontactJustHandled] = useState(false);
  const [showSupportForm, setShowSupportForm] = useState(false);
  const [supportEmail, setSupportEmail] = useState("");
  const [supportSubmitLabel, setSupportSubmitLabel] = useState("");
  const [supportPopupMessage, setSupportPopupMessage] = useState("");
  const [supportComment, setSupportComment] = useState("");
  const [lastFallbackMessage, setLastFallbackMessage] = useState<any>(null);
  const [showSessionRating, setShowSessionRating] = useState(false);
  const [pendingSessionRating, setPendingSessionRating] = useState(false);
  const [sessionRating, setSessionRating] = useState(0);
  const [feedbackMap, setFeedbackMap] = useState<{[key: string]: string}>({});
  const [isMinimized, setIsMinimized] = useState(false);
  const [isClosed, setIsClosed] = useState(false);
  const [isSubmittingEmail, setIsSubmittingEmail] = useState(false);
  // For email input (legacy, if needed)
  const [showEmailInput, setShowEmailInput] = useState(false);
  const [emailAddress, setEmailAddress] = useState("");

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const sendToApi = async (userText: string, extraPayload: any = {}) => {
    // If this is a new user message, always reset confirmation state
    if (!extraPayload.recontact_confirmed && !extraPayload.recontact_declined) {
      setShowRecontactConfirmation(false);
      setPendingRecontactMsg(null);
      setPendingRecontactData(null);
      setRecontactLoading(false);
    }
    setIsLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userText,
          session_id: sessionId,
          language: lang,
          ...extraPayload,
        }),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data = await res.json();

      // Always show bot answer as chat bubble
      setMessages((prev) => [
        ...prev,
        { text: data.answer, isUser: false, time: getTime(), messageId: data.message_id },
      ]);

      // Handle recontact confirmation UI
      if (data.show_recontact_confirmation && !recontactJustHandled) {
        setShowRecontactConfirmation(true);
        setPendingRecontactMsg(data.answer);
        setPendingRecontactData(data);
        setShowSupportForm(false);
        setRecontactLoading(false);
        return;
      }

      // Show support form if both flags are true
      if (data.requires_email === true && data.show_support_options === true) {
        setShowRecontactConfirmation(false);
        setPendingRecontactMsg(null);
        setPendingRecontactData(null);
        setRecontactLoading(false);
        setRecontactJustHandled(false);
        setSupportEmail(data.prefilled_email || "");
        setSupportSubmitLabel(data.support_submit_label || i.submit);
        setSupportPopupMessage(data.answer || i.emailPrompt);
        setSupportComment("");
        setShowSupportForm(true);
        setLastFallbackMessage(userText);
        return;
      }
      // Hide confirmation and popup if not needed
      setShowRecontactConfirmation(false);
      setPendingRecontactMsg(null);
      setPendingRecontactData(null);
      setShowSupportForm(false);
      setRecontactJustHandled(false);
    } catch (err) {
      console.error("Chat API error:", err);
      setMessages((prev) => [
        ...prev,
        { text: i.errorMsg, isUser: false, time: getTime() },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  /* ---- API: Submit email for support escalation ---- */

  const handleQuickQuestion = (question: string) => {
    setMessages([
      { text: i.botGreeting, isUser: false, time: getTime() },
      { text: question, isUser: true, time: getTime() },
    ]);
    setChatStarted(true);
    sendToApi(question);
  };

  const handleSend = () => {
    if (!message.trim() || isLoading) return;
    const text = message;
    if (!chatStarted) {
      setMessages([
        { text: i.botGreeting, isUser: false, time: getTime() },
        { text, isUser: true, time: getTime() },
      ]);
      setChatStarted(true);
    } else {
      setMessages((prev) => [
        ...prev,
        { text, isUser: true, time: getTime() },
      ]);
    }
    setMessage("");
    sendToApi(text);
    inputRef.current?.focus();
  };

    // Only one handleSubmitEmail should exist (the one using supportEmail)
    const handleSubmitEmail = async () => {
      if (!supportEmail.trim()) return;

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(supportEmail)) {
        setMessages((prev) => [
          ...prev,
          { text: i.invalidEmail, isUser: false, time: getTime() },
        ]);
        return;
      }

      setIsSubmittingEmail(true);
      try {
        // Determine the source for support escalation
        let source = "rag_fallback";
        if (showSessionRating) {
          source = "user_unsatisfied";
        } else if (
          isFallbackObj(lastFallbackMessage) && lastFallbackMessage._botDirectedSupport
        ) {
          source = "bot_directed_support";
        } else if (
          isFallbackObj(lastFallbackMessage) && lastFallbackMessage._source
        ) {
          source = lastFallbackMessage._source;
        }

        const res = await fetch(`${API_BASE}/api/support/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            session_id: sessionId,
            user_email: supportEmail,
            user_message: supportComment || lastFallbackMessage,
            language: lang,
            source,
          }),
        });
        if (!res.ok) throw new Error(`Support API error: ${res.status}`);
        const data = await res.json();

        setShowSupportForm(false);
        setSupportEmail("");
        setMessages((prev) => [
          ...prev,
          { text: data.message || i.emailSuccess, isUser: false, time: getTime() },
        ]);
        setSupportComment("");
        setSupportSubmitLabel(i.submit);
        // After closing email popup, if session rating was pending, show it now
        if (pendingSessionRating) {
          setShowSessionRating(true);
          setPendingSessionRating(false);
        }
      } catch (err) {
        setMessages((prev) => [
          ...prev,
          { text: i.emailError, isUser: false, time: getTime() },
        ]);
      } finally {
        setIsSubmittingEmail(false);
      }
    };

    // Language dropdown state
    const [showLangDropdown, setShowLangDropdown] = useState(false);

    // Feedback handler stub
    const handleFeedback = (messageId: string, type: string) => {
      setFeedbackMap((prev) => ({ ...prev, [messageId]: type }));
    };

    // Session rating submit stub
    const submitSessionRating = () => {
      setShowSessionRating(false);
      setSessionRating(0);
      setSupportComment("");
    };

    return (
      <div className="fixed inset-0 z-50 flex flex-col h-screen w-screen bg-background overflow-hidden">
        {/* Session rating UI (if shown) */}
        {showSessionRating && (
          <div className="absolute inset-0 bg-black/30 flex items-center justify-center z-50">
            <div className="bg-white rounded-2xl p-6 shadow-lg w-full max-w-xs flex flex-col gap-3">
              <div className="flex items-center gap-2.5 text-sm font-semibold text-foreground">
                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                  <span className="text-yellow-400 text-xl">★</span>
                </div>
                <span>{i.feedback_prompt || (lang === 'es' ? 'Por favor califica tu experiencia.' : 'Please rate your experience.')}</span>
              </div>
              <div className="flex gap-1 mb-2 justify-center">
                {[1,2,3,4,5].map((star) => (
                  <button
                    key={star}
                    className={
                      star <= sessionRating
                        ? "text-yellow-400 text-2xl"
                        : "text-gray-300 text-2xl"
                    }
                    onClick={() => setSessionRating(star)}
                    aria-label={`Rate ${star}`}
                  >
                    ★
                  </button>
                ))}
              </div>
              <textarea
                className="w-full border rounded p-2 mb-2 text-sm"
                rows={2}
                placeholder={i.optional_comment || (lang === 'es' ? 'Comentario opcional' : 'Optional comment')}
                value={supportComment}
                onChange={e => setSupportComment(e.target.value)}
              />
              <div className="flex gap-2">
                <button
                  className="flex-1 bg-primary text-primary-foreground rounded-xl px-4 py-2.5 text-sm font-semibold hover:opacity-90 transition-all disabled:opacity-50 flex items-center justify-center gap-2 shadow-sm"
                  onClick={submitSessionRating}
                  disabled={sessionRating < 1 || sessionRating > 5}
                >
                  {i.submit || (lang === 'es' ? 'Enviar' : 'Submit')}
                </button>
                <button
                  className="px-4 py-2.5 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-background rounded-xl transition-all border border-transparent hover:border-border"
                  onClick={() => setShowSessionRating(false)}
                >
                  {i.cancel || (lang === 'es' ? 'Cancelar' : 'Cancel')}
                </button>
              </div>
            </div>
          </div>
        )}
      {/* ──── Header ──── */}
      <header className="flex items-center justify-between px-3 py-3 sm:px-5 sm:py-4 shrink-0 border-b border-border bg-white">
        <div className="flex items-center gap-2 sm:gap-3 min-w-0">
          <img
            src={logo}
            alt="Getmee"
            className="w-10 h-10 sm:w-12 sm:h-12 object-contain flex-shrink-0"
          />
          <div className="min-w-0">
            <h2 className="text-base sm:text-lg font-semibold text-foreground truncate">
              {i.title}
            </h2>
            <div className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-green-500 flex-shrink-0" />
              <span className="text-xs sm:text-sm text-muted-foreground">
                {i.online}
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {/* Language Dropdown */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setShowLangDropdown((prev) => !prev)}
              className="h-6 sm:h-6 md:h-7 min-w-[56px] sm:min-w-[64px] md:min-w-[92px] inline-flex items-center justify-between gap-1 rounded-lg border border-primary bg-primary px-2 text-[10px] sm:text-[11px] md:text-sm text-white outline-none focus:ring-2 focus:ring-primary"
              aria-label="Language"
              title="Language"
              aria-expanded={showLangDropdown}
            >
              <span className="md:hidden">{lang === "en" ? "EN" : "ES"}</span>
              <span className="hidden md:inline">{lang === "en" ? "English" : "Espanol"}</span>
              <svg className="w-3 h-3" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" /></svg>
            </button>
            {showLangDropdown && (
              <div className="absolute right-0 mt-2 w-20 sm:w-24 md:w-32 rounded-lg border border-border bg-white p-1 shadow-lg z-20">
                <button
                  type="button"
                  onClick={() => {
                    setLang("en");
                    setShowLangDropdown(false);
                  }}
                  className={`w-full rounded-md px-2 py-1.5 text-left text-xs md:text-sm transition-colors ${
                    lang === "en"
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
                    setLang("es");
                    setShowLangDropdown(false);
                  }}
                  className={`w-full rounded-md px-2 py-1.5 text-left text-xs md:text-sm transition-colors ${
                    lang === "es"
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
          {/* Minimize Icon */}
          <button
            type="button"
            onClick={() => {/* implement minimize logic here */}}
            className="p-1.5 text-muted-foreground hover:bg-secondary rounded-md transition-colors flex-shrink-0"
            aria-label="Minimize chat"
            title="Minimize chat"
          >
            <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M8 12h8" /></svg>
          </button>
          {/* Close Icon */}
          <button
            type="button"
            onClick={() => {/* implement close logic here */}}
            className="p-1.5 text-destructive hover:bg-secondary rounded-md transition-colors flex-shrink-0"
            aria-label="Close chat"
            title="Close chat"
          >
            <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M18 6L6 18M6 6l12 12" /></svg>
          </button>
        </div>
      </header>

      {/* ──── Welcome screen ──── */}
      {!chatStarted && !isMinimized && !isClosed && (
        <div className="flex-1 overflow-y-auto px-5 py-8 flex flex-col items-center gap-6">
          {/* Greeting */}
          <div className="text-center space-y-2">
            {/* Removed chat bubble icon */}
            <h3 className="text-2xl font-bold text-foreground tracking-tight">
              {i.greeting}
            </h3>
            <p className="text-muted-foreground text-sm max-w-xs mx-auto leading-relaxed">
              {i.subtitle}
            </p>
          </div>

          {/* Topics */}
          <div className="w-full max-w-md bg-gradient-to-br from-chat-bubble to-chat-bubble/60 rounded-2xl p-5 shadow-sm border border-border/50 mx-auto text-center">
            <h4 className="text-sm font-bold text-foreground mb-3 flex items-center gap-2 justify-center text-center">
              <Sparkles size={14} className="text-primary" />
              {i.askAbout}
            </h4>
            <ul className="space-y-2">
              {i.topics.map((item) => (
                <li
                  key={item}
                  className="flex items-center gap-2.5 text-sm text-foreground/80 justify-center"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-primary shrink-0" />
                  {item}
                </li>
              ))}
            </ul>
          </div>

          {/* Quick questions */}
          <div className="w-full max-w-md mx-auto text-center">
            <h4 className="text-sm font-bold text-foreground mb-3 text-center">
              {i.quickQuestionLabel}
            </h4>
            <div className="flex flex-col gap-2 items-center">
              {i.quickQuestions.map((q) => (
                <button
                  key={q}
                  onClick={() => handleQuickQuestion(q)}
                  className="group w-full text-center px-4 py-3 bg-background border border-border rounded-xl text-sm text-foreground hover:border-primary/40 hover:bg-primary/5 hover:shadow-sm transition-all"
                >
                  <span className="group-hover:text-primary transition-colors">
                    {q}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ──── Chat messages ──── */}
      {chatStarted && !isMinimized && !isClosed && (
        <div className="flex-1 overflow-y-auto px-4 sm:px-5 py-5 flex flex-col gap-5">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.isUser ? "justify-end" : "justify-start"} animate-in fade-in slide-in-from-bottom-2 duration-200`}
            >
              <div
                className={`flex flex-col ${msg.isUser ? "items-end" : "items-start"} max-w-[85%] sm:max-w-[75%]`}
              >
                <div
                  className={`flex items-end gap-2.5 ${msg.isUser ? "flex-row-reverse" : ""}`}
                >
                  {!msg.isUser && (
                    <div className="w-8 h-8 rounded-full bg-white shadow-sm flex items-center justify-center shrink-0 border border-border/50">
                      <img
                        src={logo}
                        alt="GetMee"
                        className="w-6 h-6 object-contain"
                      />
                    </div>
                  )}
                  <div
                    className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                      msg.isUser
                        ? "bg-primary text-primary-foreground rounded-br-md shadow-sm whitespace-pre-wrap"
                        : "bg-chat-bubble text-foreground rounded-bl-md shadow-sm border border-border/30 prose prose-sm prose-neutral max-w-none [&_p]:my-1 [&_ul]:my-1 [&_ol]:my-1 [&_li]:my-0.5 [&_h1]:text-base [&_h2]:text-sm [&_h3]:text-sm [&_strong]:text-foreground [&_a]:text-primary"
                    }`}
                  >
                    {msg.isUser ? (
                      msg.text
                    ) : (
                      <>
                        <ReactMarkdown>{msg.text}</ReactMarkdown>
                        {/* Show Yes/No confirmation if needed */}
                        {showRecontactConfirmation && pendingRecontactMsg === msg.text && (
                          <div className="flex gap-3 mt-3">
                            <button
                              className="px-4 py-1.5 rounded-lg bg-primary text-white font-semibold hover:bg-primary/90 transition-all"
                              onClick={async () => {
                                if (recontactLoading) return;
                                setRecontactLoading(true);
                                setShowRecontactConfirmation(false);
                                setPendingRecontactMsg(null);
                                setPendingRecontactData(null);
                                setRecontactJustHandled(true);
                                await sendToApi("Contact support again", { recontact_confirmed: true });
                              }}
                              disabled={isLoading || recontactLoading}
                            >
                              Yes
                            </button>
                            <button
                              className="px-4 py-1.5 rounded-lg bg-muted text-foreground font-semibold hover:bg-muted/80 border border-border transition-all"
                              onClick={async () => {
                                if (recontactLoading) return;
                                setRecontactLoading(true);
                                setShowRecontactConfirmation(false);
                                setPendingRecontactMsg(null);
                                setPendingRecontactData(null);
                                setRecontactJustHandled(true);
                                await sendToApi("No thanks", { recontact_declined: true });
                              }}
                              disabled={isLoading || recontactLoading}
                            >
                              No
                            </button>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                </div>
                <span
                  className={`text-[10px] text-muted-foreground/70 mt-1.5 ${msg.isUser ? "mr-1" : "ml-10"}`}
                >
                  {msg.time}
                </span>
                {/* Feedback buttons for bot messages */}
                {!msg.isUser && msg.messageId && (
                  <div className="flex items-center gap-2.5 ml-10 mt-2">
                    {feedbackMap[msg.messageId] === "sending" ? (
                      <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-muted/50 border border-border/40">
                        <Loader2 size={14} className="animate-spin text-primary" />
                        <span className="text-xs text-muted-foreground">Submitting...</span>
                      </div>
                    ) : feedbackMap[msg.messageId] ? (
                      <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border ${
                        feedbackMap[msg.messageId] === "positive"
                          ? "bg-primary/5 border-primary/20"
                          : "bg-destructive/5 border-destructive/20"
                      }`}>
                        {feedbackMap[msg.messageId] === "positive" ? (
                          <SmilePlus size={15} className="text-primary" />
                        ) : (
                          <Frown size={15} className="text-destructive" />
                        )}
                        <span className={`text-xs font-semibold ${
                          feedbackMap[msg.messageId] === "positive" ? "text-primary" : "text-destructive"
                        }`}>
                          {feedbackMap[msg.messageId] === "positive" ? i.satisfied || (lang === 'es' ? 'Satisfecho' : 'Satisfied') : i.not_satisfied || (lang === 'es' ? 'No satisfecho' : 'Not Satisfied')}
                        </span>
                        <span className="text-xs text-muted-foreground">— {i.feedback_thank_you || (lang === 'es' ? '¡Gracias por tus comentarios!' : 'Thank you!')}</span>
                      </div>
                    ) : (
                      <>
                        <span className="text-[11px] text-muted-foreground/60 mr-0.5">{i.was_this_helpful || (lang === 'es' ? '¿Fue útil?' : 'Was this helpful?')}</span>
                        <button
                          onClick={() => handleFeedback(msg.messageId!, "positive")}
                          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-primary/5 text-primary border border-primary/20 hover:bg-primary/15 hover:border-primary/40 hover:shadow-sm active:scale-95 transition-all"
                        >
                          <SmilePlus size={15} />
                          {i.satisfied || (lang === 'es' ? 'Satisfecho' : 'Satisfied')}
                        </button>
                        <button
                          onClick={() => handleFeedback(msg.messageId!, "negative")}
                          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-destructive/5 text-destructive border border-destructive/20 hover:bg-destructive/15 hover:border-destructive/40 hover:shadow-sm active:scale-95 transition-all"
                        >
                          <Frown size={15} />
                          {i.not_satisfied || (lang === 'es' ? 'No satisfecho' : 'Not Satisfied')}
                        </button>
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Typing indicator */}
          {isLoading && (
            <div className="flex justify-start animate-in fade-in duration-200">
              <div className="flex items-end gap-2.5 max-w-[80%]">
                <div className="w-8 h-8 rounded-full bg-white shadow-sm flex items-center justify-center shrink-0 border border-border/50">
                  <img
                    src={logo}
                    alt="GetMee"
                    className="w-6 h-6 object-contain"
                  />
                </div>
                <div className="rounded-2xl rounded-bl-md px-4 py-3 bg-chat-bubble shadow-sm border border-border/30">
                  <TypingIndicator />
                </div>
              </div>
            </div>
          )}

          {/* Support form popup — controlled by backend flags, not just chat bubble */}
          {showSupportForm && (
            <div className="mx-auto w-full max-w-sm bg-gradient-to-br from-secondary to-secondary/80 rounded-2xl p-5 flex flex-col gap-3 shadow-sm border border-border/50 animate-in fade-in slide-in-from-bottom-3 duration-300">
              <div className="flex items-center gap-2.5 text-sm font-semibold text-foreground">
                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                  <Mail size={15} className="text-primary" />
                </div>
                <span>{supportPopupMessage}</span>
              </div>
              <input
                type="email"
                value={supportEmail}
                onChange={(e) => setSupportEmail(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSubmitEmail()}
                placeholder={i.emailPlaceholder}
                className="bg-background rounded-xl px-4 py-2.5 text-foreground placeholder:text-muted-foreground outline-none focus:ring-2 focus:ring-primary/50 border border-border text-sm transition-shadow"
                autoFocus
              />
              <textarea
                className="w-full border rounded p-2 mb-2 text-sm"
                rows={2}
                placeholder={i.optional_comment || (lang === 'es' ? 'Comentario opcional' : 'Optional comment')}
                value={supportComment}
                onChange={e => setSupportComment(e.target.value)}
              />
              <div className="flex gap-2">
                <button
                  onClick={handleSubmitEmail}
                  disabled={isSubmittingEmail}
                  className="flex-1 bg-primary text-primary-foreground rounded-xl px-4 py-2.5 text-sm font-semibold hover:opacity-90 transition-all disabled:opacity-50 flex items-center justify-center gap-2 shadow-sm"
                >
                  {isSubmittingEmail ? (
                    <Loader2 size={15} className="animate-spin" />
                  ) : (
                    <Send size={15} />
                  )}
                  {supportSubmitLabel}
                </button>
                <button
                  onClick={() => {
                    setShowSupportForm(false);
                    setSupportEmail("");
                    setSupportComment("");
                    if (pendingSessionRating) setPendingSessionRating(false);
                  }}
                  className="px-4 py-2.5 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-background rounded-xl transition-all border border-transparent hover:border-border"
                >
                  {i.skip}
                </button>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      )}

      {/* ──── Input bar — always visible ──── */}
      <div className="border-t border-border px-4 sm:px-5 py-3 bg-background/80 backdrop-blur-sm shrink-0">
        <form
          className="flex items-center gap-2 max-w-3xl mx-auto"
          onSubmit={e => {
            e.preventDefault();
            if (!message.trim() || isLoading) return;
            const text = message;
            if (!chatStarted) {
              setMessages([
                { text: i.botGreeting, isUser: false, time: getTime() },
                { text, isUser: true, time: getTime() },
              ]);
              setChatStarted(true);
            } else {
              setMessages((prev) => [
                ...prev,
                { text, isUser: true, time: getTime() },
              ]);
            }
            setMessage("");
            sendToApi(text);
            inputRef.current?.focus();
          }}
        >
          <div className="flex items-center border rounded-full px-3 py-2 bg-white shadow-sm mt-4 flex-1">
            <Upload className="text-primary mr-2" size={20} />
            <input
              ref={inputRef}
              type="text"
              className="flex-1 border-none outline-none bg-transparent text-sm"
              placeholder={i.placeholder}
              value={message}
              onChange={e => setMessage(e.target.value)}
              disabled={isLoading}
              aria-label="Type your message"
            />
            <button
              type="submit"
              className="ml-2 bg-primary hover:bg-green-600 text-primary-foreground rounded-full p-2 transition-colors flex items-center justify-center disabled:opacity-50"
              disabled={isLoading || !message.trim()}
              aria-label="Send message"
            >
              <Send size={20} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatWidget;
