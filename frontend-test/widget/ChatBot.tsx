import { useState, useRef, useEffect } from "react";

/* ──────────── Types ──────────── */
type Language = "en" | "es";

type Message = {
  text: string;
  isUser: boolean;
  time: string;
};

/* ──────────── i18n ──────────── */
const t = {
  en: {
    title: "GetMee AI Assistant",
    online: "Online",
    greeting: "Hello 👋",
    subtitle: "I'm the GetMee AI Assistant",
    askAbout: "Ask me anything about:",
    topics: ["Interview preparation", "Resume tips", "Using the GetMee platform"],
    quickLabel: "Quick Questions:",
    quickQuestions: [
      "How does AI scoring work?",
      "Interview preparation tips",
      "How do I improve my answers?",
      "What is GetMee?",
      "How to create a strong resume?",
    ],
    botGreeting: "Hello! I'm GetMee AI Assistant. How can I help you today?",
    placeholder: "Type your message...",
    emailPrompt: "Enter your email to connect with support",
    emailPlaceholder: "your.email@example.com",
    submit: "Submit",
    skip: "Skip",
    invalidEmail: "Please enter a valid email address.",
    errorMsg: "Sorry, something went wrong. Please try again.",
    emailError: "Failed to submit your request. Please try again.",
    poweredBy: "Powered by GetMee",
  },
  es: {
    title: "Asistente IA GetMee",
    online: "En línea",
    greeting: "Hola 👋",
    subtitle: "Soy el Asistente IA de GetMee",
    askAbout: "Pregúntame sobre:",
    topics: ["Preparación para entrevistas", "Consejos para currículum", "Uso de la plataforma GetMee"],
    quickLabel: "Preguntas rápidas:",
    quickQuestions: [
      "¿Cómo funciona la puntuación con IA?",
      "Consejos para preparar entrevistas",
      "¿Cómo puedo mejorar mis respuestas?",
      "¿Qué es GetMee?",
      "¿Cómo crear un currículum sólido?",
    ],
    botGreeting: "¡Hola! Soy el Asistente IA de GetMee. ¿En qué puedo ayudarte hoy?",
    placeholder: "Escribe tu mensaje...",
    emailPrompt: "Ingresa tu correo para contactar con soporte",
    emailPlaceholder: "tu.correo@ejemplo.com",
    submit: "Enviar",
    skip: "Omitir",
    invalidEmail: "Por favor ingresa un correo electrónico válido.",
    errorMsg: "Lo sentimos, algo salió mal. Inténtalo de nuevo.",
    emailError: "No se pudo enviar tu solicitud. Inténtalo de nuevo.",
    poweredBy: "Desarrollado por GetMee",
  },
};

/* ──────────── SVG icons (inline to avoid dependencies) ──────────── */
const IconSend = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" />
  </svg>
);
const IconX = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
  </svg>
);
const IconMinus = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="5" y1="12" x2="19" y2="12" />
  </svg>
);
const IconChat = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
  </svg>
);
const IconMail = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="4" width="20" height="16" rx="2" /><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
  </svg>
);
const IconGlobe = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" /><line x1="2" y1="12" x2="22" y2="12" /><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
  </svg>
);
const Spinner = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ animation: "getmee-spin 1s linear infinite" }}>
    <path d="M21 12a9 9 0 1 1-6.219-8.56" />
  </svg>
);

/* ──────────── Helpers ──────────── */
const getTime = () =>
  new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: true });

const generateSessionId = () =>
  `session_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;

/* ──────────── Styles ──────────── */
const COLORS = {
  primary: "#2a9d8f",
  primaryFg: "#ffffff",
  bg: "#ffffff",
  fg: "#2d3748",
  muted: "#718096",
  border: "#e2e8f0",
  bubbleBg: "#edf7f6",
  bubbleFg: "#2d3748",
  userBubbleBg: "#2a9d8f",
  userBubbleFg: "#ffffff",
  secondary: "#f0faf9",
  online: "#48bb78",
  danger: "#e53e3e",
};

const styles = {
  /* Fab button */
  fab: {
    position: "fixed" as const,
    bottom: "24px",
    right: "24px",
    width: "60px",
    height: "60px",
    borderRadius: "50%",
    background: COLORS.primary,
    color: COLORS.primaryFg,
    border: "none",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    boxShadow: "0 4px 20px rgba(0,0,0,0.2)",
    zIndex: 99999,
    transition: "transform 0.2s",
  },
  /* Chat window */
  window: {
    position: "fixed" as const,
    bottom: "96px",
    right: "24px",
    width: "400px",
    maxWidth: "calc(100vw - 32px)",
    height: "600px",
    maxHeight: "calc(100vh - 120px)",
    borderRadius: "16px",
    background: COLORS.bg,
    boxShadow: "0 8px 40px rgba(0,0,0,0.15)",
    display: "flex",
    flexDirection: "column" as const,
    overflow: "hidden",
    zIndex: 99999,
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    fontSize: "14px",
    color: COLORS.fg,
    border: `1px solid ${COLORS.border}`,
  },
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "14px 16px",
    borderBottom: `1px solid ${COLORS.border}`,
    flexShrink: 0,
  },
  headerLeft: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
  },
  headerLogo: {
    width: "40px",
    height: "40px",
    borderRadius: "50%",
    objectFit: "contain" as const,
  },
  headerTitle: {
    margin: 0,
    fontSize: "16px",
    fontWeight: 600,
    color: COLORS.fg,
  },
  headerStatus: {
    display: "flex",
    alignItems: "center",
    gap: "5px",
    fontSize: "12px",
    color: COLORS.muted,
  },
  onlineDot: {
    width: "8px",
    height: "8px",
    borderRadius: "50%",
    background: COLORS.online,
  },
  headerActions: {
    display: "flex",
    alignItems: "center",
    gap: "4px",
  },
  headerBtn: {
    background: "none",
    border: "none",
    cursor: "pointer",
    padding: "6px",
    borderRadius: "6px",
    color: COLORS.muted,
    display: "flex",
    alignItems: "center",
    transition: "background 0.15s",
  },
  langToggle: {
    background: COLORS.secondary,
    border: `1px solid ${COLORS.border}`,
    cursor: "pointer",
    padding: "4px 8px",
    borderRadius: "12px",
    fontSize: "11px",
    fontWeight: 600,
    color: COLORS.primary,
    display: "flex",
    alignItems: "center",
    gap: "4px",
    transition: "background 0.15s",
  },
  /* Welcome screen */
  welcome: {
    flex: 1,
    overflowY: "auto" as const,
    padding: "24px 20px",
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    gap: "20px",
  },
  greetingTitle: {
    fontSize: "22px",
    fontWeight: 600,
    margin: 0,
    textAlign: "center" as const,
  },
  greetingSub: {
    color: COLORS.muted,
    margin: "4px 0 0",
    textAlign: "center" as const,
  },
  infoCard: {
    width: "100%",
    background: COLORS.bubbleBg,
    borderRadius: "14px",
    padding: "18px 20px",
  },
  infoTitle: {
    margin: "0 0 10px",
    fontSize: "15px",
    fontWeight: 600,
  },
  topicItem: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    padding: "3px 0",
    fontSize: "13px",
    color: COLORS.bubbleFg,
  },
  topicDot: {
    width: "6px",
    height: "6px",
    borderRadius: "50%",
    background: COLORS.primary,
    flexShrink: 0,
  },
  quickSection: {
    width: "100%",
  },
  quickLabel: {
    textAlign: "center" as const,
    fontWeight: 600,
    margin: "0 0 12px",
    fontSize: "14px",
  },
  quickBtn: {
    width: "100%",
    textAlign: "left" as const,
    padding: "10px 14px",
    border: `1px solid ${COLORS.border}`,
    borderRadius: "10px",
    background: COLORS.bg,
    cursor: "pointer",
    fontSize: "13px",
    color: COLORS.fg,
    marginBottom: "8px",
    transition: "background 0.15s",
  },
  /* Messages area */
  messages: {
    flex: 1,
    overflowY: "auto" as const,
    padding: "16px",
    display: "flex",
    flexDirection: "column" as const,
    gap: "16px",
  },
  msgRow: (isUser: boolean) => ({
    display: "flex",
    justifyContent: isUser ? "flex-end" : "flex-start",
  }),
  msgCol: (isUser: boolean) => ({
    display: "flex",
    flexDirection: "column" as const,
    alignItems: isUser ? "flex-end" : "flex-start",
    maxWidth: "80%",
  }),
  msgBubbleRow: (isUser: boolean) => ({
    display: "flex",
    alignItems: "flex-start",
    gap: "8px",
    flexDirection: (isUser ? "row-reverse" : "row") as "row" | "row-reverse",
  }),
  botAvatar: {
    width: "32px",
    height: "32px",
    borderRadius: "50%",
    objectFit: "contain" as const,
    flexShrink: 0,
    marginTop: "2px",
  },
  bubble: (isUser: boolean) => ({
    borderRadius: "16px",
    padding: "10px 14px",
    fontSize: "13px",
    lineHeight: "1.5",
    background: isUser ? COLORS.userBubbleBg : COLORS.bubbleBg,
    color: isUser ? COLORS.userBubbleFg : COLORS.bubbleFg,
    wordBreak: "break-word" as const,
  }),
  msgTime: (isUser: boolean) => ({
    fontSize: "11px",
    color: COLORS.muted,
    marginTop: "4px",
    ...(isUser ? { marginRight: "4px" } : { marginLeft: "40px" }),
  }),
  /* Email form */
  emailForm: {
    margin: "0 auto",
    width: "100%",
    maxWidth: "320px",
    background: COLORS.secondary,
    borderRadius: "14px",
    padding: "14px",
    display: "flex",
    flexDirection: "column" as const,
    gap: "10px",
  },
  emailLabel: {
    display: "flex",
    alignItems: "center",
    gap: "6px",
    fontSize: "13px",
    fontWeight: 500,
  },
  emailInput: {
    borderRadius: "10px",
    border: `1px solid ${COLORS.border}`,
    padding: "8px 12px",
    fontSize: "13px",
    outline: "none",
    width: "100%",
    boxSizing: "border-box" as const,
  },
  emailBtns: {
    display: "flex",
    gap: "8px",
  },
  emailSubmit: {
    flex: 1,
    background: COLORS.primary,
    color: COLORS.primaryFg,
    border: "none",
    borderRadius: "10px",
    padding: "8px",
    fontSize: "13px",
    fontWeight: 500,
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "6px",
  },
  emailSkip: {
    background: "none",
    border: "none",
    padding: "8px 12px",
    fontSize: "13px",
    color: COLORS.muted,
    cursor: "pointer",
    borderRadius: "10px",
  },
  /* Input bar */
  inputBar: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    padding: "10px 14px",
    borderTop: `1px solid ${COLORS.border}`,
    flexShrink: 0,
  },
  textInput: {
    flex: 1,
    border: `1px solid ${COLORS.border}`,
    borderRadius: "10px",
    padding: "9px 14px",
    fontSize: "13px",
    outline: "none",
    background: COLORS.secondary,
    color: COLORS.fg,
    boxSizing: "border-box" as const,
  },
  sendBtn: {
    background: "none",
    border: "none",
    cursor: "pointer",
    color: COLORS.primary,
    padding: "6px",
    borderRadius: "6px",
    display: "flex",
    alignItems: "center",
  },
  poweredBy: {
    textAlign: "center" as const,
    fontSize: "11px",
    color: COLORS.muted,
    padding: "4px 0 8px",
    flexShrink: 0,
  },
};

/* ──────────── Component ──────────── */
interface ChatBotProps {
  apiBase?: string;
  logoUrl?: string;
}

export default function ChatBot({ apiBase = "http://localhost:8001", logoUrl }: ChatBotProps) {
  const [open, setOpen] = useState(false);
  const [lang, setLang] = useState<Language>("en");
  const [chatStarted, setChatStarted] = useState(false);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(generateSessionId);

  // Email
  const [showEmailInput, setShowEmailInput] = useState(false);
  const [emailAddress, setEmailAddress] = useState("");
  const [lastFallbackMsg, setLastFallbackMsg] = useState("");
  const [isSubmittingEmail, setIsSubmittingEmail] = useState(false);

  const endRef = useRef<HTMLDivElement>(null);
  const i = t[lang];

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  /* ── API calls ── */
  const sendToApi = async (userText: string) => {
    setIsLoading(true);
    try {
      const res = await fetch(`${apiBase}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userText, session_id: sessionId, language: lang }),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data = await res.json();
      setMessages((prev) => [...prev, { text: data.answer, isUser: false, time: getTime() }]);
      if (data.requires_email) {
        setShowEmailInput(true);
        setLastFallbackMsg(userText);
      }
    } catch {
      setMessages((prev) => [...prev, { text: i.errorMsg, isUser: false, time: getTime() }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitEmail = async () => {
    if (!emailAddress.trim()) return;
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailAddress)) {
      setMessages((prev) => [...prev, { text: i.invalidEmail, isUser: false, time: getTime() }]);
      return;
    }
    setIsSubmittingEmail(true);
    try {
      const res = await fetch(`${apiBase}/api/support`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          user_email: emailAddress,
          user_message: lastFallbackMsg,
          language: lang,
        }),
      });
      if (!res.ok) throw new Error("Support error");
      const data = await res.json();
      setShowEmailInput(false);
      setEmailAddress("");
      setMessages((prev) => [...prev, { text: data.message, isUser: false, time: getTime() }]);
    } catch {
      setMessages((prev) => [...prev, { text: i.emailError, isUser: false, time: getTime() }]);
    } finally {
      setIsSubmittingEmail(false);
    }
  };

  const handleQuickQuestion = (q: string) => {
    setMessages([
      { text: i.botGreeting, isUser: false, time: getTime() },
      { text: q, isUser: true, time: getTime() },
    ]);
    setChatStarted(true);
    sendToApi(q);
  };

  const handleSend = () => {
    if (!message.trim() || isLoading) return;
    const text = message;
    setMessages((prev) => [...prev, { text, isUser: true, time: getTime() }]);
    setMessage("");
    if (!chatStarted) {
      setChatStarted(true);
      setMessages((prev) => {
        const greet: Message = { text: i.botGreeting, isUser: false, time: getTime() };
        return [greet, ...prev];
      });
    }
    sendToApi(text);
  };

  const resetChat = () => {
    setChatStarted(false);
    setMessages([]);
    setShowEmailInput(false);
    setEmailAddress("");
  };

  /* ── Render ── */
  if (!open) {
    return (
      <button style={styles.fab} onClick={() => setOpen(true)} aria-label="Open chat">
        <IconChat />
      </button>
    );
  }

  return (
    <>
      {/* Keyframes for spinner */}
      <style>{`@keyframes getmee-spin { to { transform: rotate(360deg); } }`}</style>

      {/* Floating chat window */}
      <div style={styles.window}>
        {/* Header */}
        <div style={styles.header}>
          <div style={styles.headerLeft}>
            {logoUrl && <img src={logoUrl} alt="Logo" style={styles.headerLogo} />}
            <div>
              <h3 style={styles.headerTitle}>{i.title}</h3>
              <div style={styles.headerStatus}>
                <span style={styles.onlineDot} />
                {i.online}
              </div>
            </div>
          </div>
          {/* Header controls: language dropdown, minimize, close */}
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginLeft: "auto" }}>
            <select
              aria-label="Select language"
              value={lang}
              onChange={e => setLang(e.target.value as Language)}
              style={{
                borderRadius: "12px",
                fontSize: "12px",
                padding: "4px 8px",
                border: `1px solid ${COLORS.border}`,
                background: COLORS.secondary,
                color: COLORS.primary,
                cursor: "pointer",
                outline: "none",
                fontWeight: 600,
                minWidth: "80px",
              }}
            >
              <option value="en">English</option>
              <option value="es">Español</option>
            </select>
            <button
              aria-label={open ? (chatStarted ? "Minimize chat" : "Minimize chatbot") : "Expand chat"}
              title="Minimize"
              onClick={() => setOpen(false)}
              style={{
                background: "none",
                border: "none",
                cursor: "pointer",
                padding: "6px",
                borderRadius: "6px",
                color: COLORS.muted,
                display: "flex",
                alignItems: "center",
                transition: "background 0.15s",
              }}
            >
              <IconMinus />
            </button>
            <button
              aria-label="Close chat"
              title="Close"
              onClick={() => setOpen(false)}
              style={{
                background: "none",
                border: "none",
                cursor: "pointer",
                padding: "6px",
                borderRadius: "6px",
                color: COLORS.muted,
                display: "flex",
                alignItems: "center",
                transition: "background 0.15s",
              }}
            >
              <IconX />
            </button>
          </div>
        </div>

        {/* Welcome screen */}
        {!chatStarted && (
          <div style={styles.welcome}>
            <div>
              <h2 style={styles.greetingTitle}>{i.greeting}</h2>
              <p style={styles.greetingSub}>{i.subtitle}</p>
            </div>

            <div style={styles.infoCard}>
              <h4 style={styles.infoTitle}>{i.askAbout}</h4>
              {i.topics.map((topic) => (
                <div key={topic} style={styles.topicItem}>
                  <span style={styles.topicDot} />
                  {topic}
                </div>
              ))}
            </div>

            <div style={styles.quickSection}>
              <h4 style={styles.quickLabel}>{i.quickLabel}</h4>
              {i.quickQuestions.map((q) => (
                <button
                  key={q}
                  style={styles.quickBtn}
                  onClick={() => handleQuickQuestion(q)}
                  onMouseEnter={(e) => (e.currentTarget.style.background = COLORS.secondary)}
                  onMouseLeave={(e) => (e.currentTarget.style.background = COLORS.bg)}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Chat messages */}
        {chatStarted && (
          <div style={styles.messages}>
            {messages.map((msg, idx) => (
              <div key={idx} style={styles.msgRow(msg.isUser)}>
                <div style={styles.msgCol(msg.isUser)}>
                  <div style={styles.msgBubbleRow(msg.isUser)}>
                    {!msg.isUser && logoUrl && (
                      <img src={logoUrl} alt="Bot" style={styles.botAvatar} />
                    )}
                    <div style={styles.bubble(msg.isUser)}>{msg.text}</div>
                  </div>
                  <span style={styles.msgTime(msg.isUser)}>{msg.time}</span>
                </div>
              </div>
            ))}

            {isLoading && (
              <div style={styles.msgRow(false)}>
                <div style={styles.msgCol(false)}>
                  <div style={styles.msgBubbleRow(false)}>
                    {logoUrl && <img src={logoUrl} alt="Bot" style={styles.botAvatar} />}
                    <div style={styles.bubble(false)}>
                      <Spinner />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {showEmailInput && (
              <div style={styles.emailForm}>
                <div style={styles.emailLabel}>
                  <IconMail />
                  <span>{i.emailPrompt}</span>
                </div>
                <input
                  type="email"
                  value={emailAddress}
                  onChange={(e) => setEmailAddress(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSubmitEmail()}
                  placeholder={i.emailPlaceholder}
                  style={styles.emailInput}
                />
                <div style={styles.emailBtns}>
                  <button
                    onClick={handleSubmitEmail}
                    disabled={isSubmittingEmail}
                    style={{ ...styles.emailSubmit, opacity: isSubmittingEmail ? 0.6 : 1 }}
                  >
                    {isSubmittingEmail ? <Spinner /> : <IconSend />}
                    {i.submit}
                  </button>
                  <button
                    onClick={() => { setShowEmailInput(false); setEmailAddress(""); }}
                    style={styles.emailSkip}
                  >
                    {i.skip}
                  </button>
                </div>
              </div>
            )}

            <div ref={endRef} />
          </div>
        )}

        {/* Input bar (always visible when chat started) */}
        {chatStarted && (
          <div style={styles.inputBar}>
            <input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder={i.placeholder}
              disabled={isLoading}
              style={{ ...styles.textInput, opacity: isLoading ? 0.6 : 1 }}
            />
            <button
              onClick={handleSend}
              disabled={isLoading}
              style={{ ...styles.sendBtn, opacity: isLoading ? 0.5 : 1 }}
            >
              <IconSend />
            </button>
          </div>
        )}

        {/* Input bar on welcome screen */}
        {!chatStarted && (
          <div style={styles.inputBar}>
            <input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder={i.placeholder}
              style={styles.textInput}
            />
            <button onClick={handleSend} style={styles.sendBtn}>
              <IconSend />
            </button>
          </div>
        )}

        <div style={styles.poweredBy}>{i.poweredBy}</div>
      </div>
    </>
  );
}
