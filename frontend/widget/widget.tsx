/**
 * GetMee Chatbot Widget — Self-contained React entry point
 *
 * This script renders the chatbot directly into the page (no iframe).
 * WordPress or any host site only needs to load this script.
 *
 * Configuration:
 *   Option A: window.ChatWidgetConfig = { apiBase: "...", logoUrl: "..." }
 *   Option B: <script src="..." data-api-base="..." data-logo-url="..."></script>
 *   Option C: GetMeeChat.init({ apiBase: "..." })
 */

import React from "react";
import { createRoot } from "react-dom/client";
import ChatBot from "./ChatBot";

interface ChatWidgetConfig {
  apiBase?: string;
  logoUrl?: string;
  position?: "bottom-right" | "bottom-left";
}

declare global {
  interface Window {
    ChatWidgetConfig?: ChatWidgetConfig;
    GetMeeChat?: { init: (config?: ChatWidgetConfig) => void };
  }
}

function mount(config: ChatWidgetConfig = {}) {
  // Don't mount twice
  if (document.getElementById("getmee-chatbot-root")) return;

  const container = document.createElement("div");
  container.id = "getmee-chatbot-root";
  // Ensure our container doesn't inherit host page styles
  container.style.cssText =
    "all: initial; position: fixed; z-index: 99999; font-family: system-ui, -apple-system, sans-serif;";
  document.body.appendChild(container);

  const root = createRoot(container);
  root.render(
    <ChatBot
      apiBase={config.apiBase || "http://localhost:8001"}
      logoUrl={config.logoUrl}
    />
  );
}

// Expose global API for manual initialization
window.GetMeeChat = { init: mount };

// Auto-initialize if config exists
const scriptEl = document.currentScript as HTMLScriptElement | null;
const hasConfig =
  window.ChatWidgetConfig || scriptEl?.hasAttribute("data-api-base");

if (hasConfig) {
  const config: ChatWidgetConfig = {
    ...(window.ChatWidgetConfig || {}),
    apiBase:
      scriptEl?.getAttribute("data-api-base") ||
      window.ChatWidgetConfig?.apiBase,
    logoUrl:
      scriptEl?.getAttribute("data-logo-url") ||
      window.ChatWidgetConfig?.logoUrl,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => mount(config));
  } else {
    mount(config);
  }
}
