/**
 * GetMee Chatbot Widget Loader
 *
 * Embed this script on any website (WordPress, static HTML, etc.)
 * It creates a floating chat button that opens the chatbot UI in an iframe.
 *
 * Configuration via window.ChatWidgetConfig:
 *   mode: "floating" | "inline"
 *   position: "bottom-right" | "bottom-left"
 *   targetId: string (required for inline mode)
 *   chatUrl: string (URL where the chatbot app is hosted)
 */

interface ChatWidgetConfig {
  mode?: "floating" | "inline";
  position?: "bottom-right" | "bottom-left";
  targetId?: string;
  chatUrl?: string;
}

declare global {
  interface Window {
    ChatWidgetConfig?: ChatWidgetConfig;
    GetMeeChat?: { init: (config?: ChatWidgetConfig) => void };
  }
}

(function () {
  const DEFAULTS: Required<ChatWidgetConfig> = {
    mode: "floating",
    position: "bottom-right",
    targetId: "",
    chatUrl: "",
  };

  function resolveConfig(): Required<ChatWidgetConfig> {
    const scriptEl = document.currentScript as HTMLScriptElement | null;
    const winCfg = window.ChatWidgetConfig || {};

    // Script data-* attributes override window config
    const chatUrl =
      scriptEl?.getAttribute("data-chat-url") ||
      winCfg.chatUrl ||
      DEFAULTS.chatUrl ||
      new URL("/", scriptEl?.src || window.location.href).origin;

    return {
      mode: (scriptEl?.getAttribute("data-mode") as ChatWidgetConfig["mode"]) || winCfg.mode || DEFAULTS.mode,
      position:
        (scriptEl?.getAttribute("data-position") as ChatWidgetConfig["position"]) ||
        winCfg.position ||
        DEFAULTS.position,
      targetId: scriptEl?.getAttribute("data-target-id") || winCfg.targetId || DEFAULTS.targetId,
      chatUrl,
    };
  }

  function createIframe(chatUrl: string): HTMLIFrameElement {
    const iframe = document.createElement("iframe");
    iframe.src = chatUrl;
    iframe.style.width = "100%";
    iframe.style.height = "100%";
    iframe.style.border = "none";
    iframe.style.display = "block";
    iframe.allow = "clipboard-write";
    iframe.title = "GetMee AI Chatbot";
    return iframe;
  }

  /* ---------- Inline mode ---------- */
  function mountInline(config: Required<ChatWidgetConfig>) {
    const target = document.getElementById(config.targetId);
    if (!target) {
      console.error(`[GetMeeChat] Target element #${config.targetId} not found.`);
      return;
    }
    target.style.position = "relative";
    target.style.overflow = "hidden";
    if (!target.style.height) target.style.height = "600px";
    target.appendChild(createIframe(config.chatUrl));
  }

  /* ---------- Floating mode ---------- */
  function mountFloating(config: Required<ChatWidgetConfig>) {
    const isRight = config.position === "bottom-right";

    // ---- Fab button ----
    const fab = document.createElement("button");
    fab.id = "getmee-chat-fab";
    fab.setAttribute("aria-label", "Open chat");
    Object.assign(fab.style, {
      position: "fixed",
      bottom: "24px",
      [isRight ? "right" : "left"]: "24px",
      [isRight ? "left" : "right"]: "auto",
      width: "60px",
      height: "60px",
      borderRadius: "50%",
      background: "#2a9d8f",
      color: "#fff",
      border: "none",
      cursor: "pointer",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      boxShadow: "0 4px 20px rgba(0,0,0,0.2)",
      zIndex: "99998",
      transition: "transform 0.2s",
    });
    fab.innerHTML = `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`;

    // ---- Chat panel ----
    const panel = document.createElement("div");
    panel.id = "getmee-chat-panel";
    Object.assign(panel.style, {
      position: "fixed",
      bottom: "96px",
      [isRight ? "right" : "left"]: "24px",
      [isRight ? "left" : "right"]: "auto",
      width: "400px",
      maxWidth: "calc(100vw - 32px)",
      height: "600px",
      maxHeight: "calc(100vh - 120px)",
      borderRadius: "16px",
      overflow: "hidden",
      boxShadow: "0 8px 40px rgba(0,0,0,0.15)",
      zIndex: "99999",
      display: "none",
      border: "1px solid #e2e8f0",
    });

    panel.appendChild(createIframe(config.chatUrl));

    // ---- Toggle ----
    let isOpen = false;
    fab.addEventListener("click", () => {
      isOpen = !isOpen;
      panel.style.display = isOpen ? "block" : "none";
      // Switch icon between chat bubble and X
      fab.innerHTML = isOpen
        ? `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`
        : `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`;
    });

    // ---- Mobile responsive: make panel full screen on small screens ----
    const style = document.createElement("style");
    style.textContent = `
      @media (max-width: 480px) {
        #getmee-chat-panel {
          width: 100vw !important;
          height: 100vh !important;
          max-width: 100vw !important;
          max-height: 100vh !important;
          bottom: 0 !important;
          left: 0 !important;
          right: 0 !important;
          border-radius: 0 !important;
          border: none !important;
        }
        #getmee-chat-fab {
          bottom: 16px !important;
          ${isRight ? "right: 16px !important;" : "left: 16px !important;"}
        }
      }
    `;
    document.head.appendChild(style);

    document.body.appendChild(panel);
    document.body.appendChild(fab);
  }

  /* ---------- Init ---------- */
  function init(overrides?: ChatWidgetConfig) {
    if (overrides) {
      window.ChatWidgetConfig = { ...(window.ChatWidgetConfig || {}), ...overrides };
    }
    const config = resolveConfig();

    if (config.mode === "inline" && config.targetId) {
      mountInline(config);
    } else {
      mountFloating(config);
    }
  }

  // Expose global API
  window.GetMeeChat = { init };

  // Auto-init if script has data attributes or window config exists
  const scriptEl = document.currentScript as HTMLScriptElement | null;
  const hasConfig = window.ChatWidgetConfig || scriptEl?.hasAttribute("data-chat-url");

  if (hasConfig) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => init());
    } else {
      init();
    }
  }
})();

