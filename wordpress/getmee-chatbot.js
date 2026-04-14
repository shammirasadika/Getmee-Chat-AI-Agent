/**
 * GetMee Chatbot Widget Loader (WordPress Embed)
 * Adds working minimize and close controls without changing frontend code.
 */
(function () {
  const DEFAULTS = {
    mode: "floating",
    position: "bottom-right",
    targetId: "",
    chatUrl: "",
  };

  function resolveConfig() {
    const scriptEl = document.currentScript;
    const winCfg = window.ChatWidgetConfig || {};
    const chatUrl =
      scriptEl?.getAttribute("data-chat-url") ||
      winCfg.chatUrl ||
      DEFAULTS.chatUrl ||
      new URL("/", scriptEl?.src || window.location.href).origin;

    return {
      mode: scriptEl?.getAttribute("data-mode") || winCfg.mode || DEFAULTS.mode,
      position:
        scriptEl?.getAttribute("data-position") ||
        winCfg.position ||
        DEFAULTS.position,
      targetId:
        scriptEl?.getAttribute("data-target-id") ||
        winCfg.targetId ||
        DEFAULTS.targetId,
      chatUrl,
    };
  }

  function createIframe(chatUrl) {
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

  function mountInline(config) {
    const target = document.getElementById(config.targetId);
    if (!target) {
      console.error(
        "[GetMeeChat] Target element #" + config.targetId + " not found.",
      );
      return;
    }
    target.style.position = "relative";
    target.style.overflow = "hidden";
    if (!target.style.height) target.style.height = "600px";
    target.appendChild(createIframe(config.chatUrl));
  }

  function mountFloating(config) {
    const isRight = config.position === "bottom-right";
    const FAB_BOTTOM = 24;
    const FAB_SIZE = 60;
    const PANEL_OPEN_BOTTOM = "96px";
    const EXPANDED_HEIGHT = "600px";
    const EXPANDED_MAX_HEIGHT = "calc(100vh - 120px)";
    const MINIMIZED_HEIGHT = "78px";
    const MINIMIZED_BOTTOM = FAB_BOTTOM + FAB_SIZE + "px";

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
      fontSize: "2rem",
      fontWeight: "bold",
    });
    fab.textContent = "";

    const panel = document.createElement("div");
    panel.id = "getmee-chat-panel";
    Object.assign(panel.style, {
      position: "fixed",
      bottom: PANEL_OPEN_BOTTOM,
      [isRight ? "right" : "left"]: "24px",
      [isRight ? "left" : "right"]: "auto",
      width: "400px",
      maxWidth: "calc(100vw - 32px)",
      height: EXPANDED_HEIGHT,
      maxHeight: EXPANDED_MAX_HEIGHT,
      borderRadius: "16px",
      overflow: "hidden",
      boxShadow: "0 8px 40px rgba(0,0,0,0.15)",
      zIndex: "99999",
      display: "none",
      border: "1px solid #e2e8f0",
      background: "#fff",
    });

    const iframe = createIframe(config.chatUrl);
    panel.appendChild(iframe);

    // Overlay click zones align with the in-chat header minimize and close icons.
    const controlsOverlay = document.createElement("div");
    controlsOverlay.id = "getmee-panel-controls-overlay";
    Object.assign(controlsOverlay.style, {
      position: "absolute",
      top: "8px",
      right: "8px",
      height: "48px",
      width: "120px",
      display: "flex",
      justifyContent: "flex-end",
      alignItems: "center",
      gap: "8px",
      zIndex: "2",
      pointerEvents: "none",
    });

    const makeControlButton = function (id, label) {
      const btn = document.createElement("button");
      btn.id = id;
      btn.type = "button";
      btn.setAttribute("aria-label", label);
      btn.title = label;
      Object.assign(btn.style, {
        width: "40px",
        height: "40px",
        border: "none",
        background: "transparent",
        cursor: "pointer",
        pointerEvents: "auto",
      });
      return btn;
    };

    const minimizeBtn = makeControlButton(
      "getmee-panel-minimize",
      "Minimize chat",
    );
    const closeBtn = makeControlButton("getmee-panel-close", "Close chat");

    controlsOverlay.appendChild(minimizeBtn);
    controlsOverlay.appendChild(closeBtn);
    panel.appendChild(controlsOverlay);

    let isOpen = false;
    let isMinimized = false;

    const applyExpandedState = function () {
      isMinimized = false;
      panel.setAttribute("data-minimized", "false");
      panel.style.bottom = PANEL_OPEN_BOTTOM;
      panel.style.height = EXPANDED_HEIGHT;
      panel.style.maxHeight = EXPANDED_MAX_HEIGHT;
      iframe.style.pointerEvents = "auto";
    };

    const applyMinimizedState = function () {
      isMinimized = true;
      panel.setAttribute("data-minimized", "true");
      panel.style.bottom = MINIMIZED_BOTTOM;
      panel.style.height = MINIMIZED_HEIGHT;
      panel.style.maxHeight = MINIMIZED_HEIGHT;
      iframe.style.pointerEvents = "none";
    };

    const closePanel = function () {
      isOpen = false;
      isMinimized = false;
      panel.style.display = "none";
      panel.setAttribute("data-minimized", "false");
      panel.style.bottom = PANEL_OPEN_BOTTOM;
      fab.textContent = "";
      fab.setAttribute("aria-label", "Open chat");
    };

    const openPanel = function () {
      isOpen = true;
      panel.style.display = "block";
      applyExpandedState();
      fab.textContent = "";
      fab.setAttribute("aria-label", "Open chat");
    };

    fab.addEventListener("click", function () {
      if (isOpen) {
        closePanel();
      } else {
        openPanel();
      }
    });

    minimizeBtn.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      if (!isOpen) {
        openPanel();
      }

      if (isMinimized) {
        applyExpandedState();
      } else {
        applyMinimizedState();
      }
    });

    closeBtn.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      closePanel();
    });

    const style = document.createElement("style");
    style.textContent =
      '\n      @media (max-width: 480px) {\n        #getmee-chat-panel:not([data-minimized="true"]) {\n          width: 100vw !important;\n          height: 100vh !important;\n          max-width: 100vw !important;\n          max-height: 100vh !important;\n          bottom: 0 !important;\n          left: 0 !important;\n          right: 0 !important;\n          border-radius: 0 !important;\n          border: none !important;\n        }\n        #getmee-chat-panel[data-minimized="true"] {\n          width: calc(100vw - 16px) !important;\n          max-width: calc(100vw - 16px) !important;\n          height: ' +
      MINIMIZED_HEIGHT +
      " !important;\n          max-height: " +
      MINIMIZED_HEIGHT +
      " !important;\n          bottom: 76px !important;\n          left: 8px !important;\n          right: 8px !important;\n          border-radius: 12px !important;\n        }\n        #getmee-chat-fab {\n          bottom: 16px !important;\n          " +
      (isRight ? "right: 16px !important;" : "left: 16px !important;") +
      "\n        }\n      }\n    ";
    document.head.appendChild(style);
    document.body.appendChild(panel);
    document.body.appendChild(fab);
  }

  function init(overrides) {
    if (overrides) {
      window.ChatWidgetConfig = Object.assign(
        {},
        window.ChatWidgetConfig || {},
        overrides,
      );
    }
    const config = resolveConfig();
    if (config.mode === "inline" && config.targetId) {
      mountInline(config);
    } else {
      mountFloating(config);
    }
  }

  window.GetMeeChat = { init: init };

  const scriptEl = document.currentScript;
  const hasConfig =
    window.ChatWidgetConfig || scriptEl?.hasAttribute("data-chat-url");
  if (hasConfig) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", function () {
        init();
      });
    } else {
      init();
    }
  }
})();
