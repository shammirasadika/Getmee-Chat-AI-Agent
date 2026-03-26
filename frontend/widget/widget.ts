type WidgetMode = "floating" | "inline";
type WidgetPosition = "bottom-right" | "bottom-left" | "top-right" | "top-left";

type ChatWidgetConfig = {
  mode?: WidgetMode;
  position?: WidgetPosition;
  targetId?: string;
  uiUrl?: string;
  iframePath?: string;
  openOnLoad?: boolean;
  buttonLabel?: string;
  zIndex?: number;
  inlineHeight?: string;
};

declare global {
  interface Window {
    ChatWidgetConfig?: ChatWidgetConfig;
  }
}

const getScriptOrigin = (): string | null => {
  const currentScript = document.currentScript;
  if (currentScript instanceof HTMLScriptElement && currentScript.src) {
    return new URL(currentScript.src).origin;
  }

  const scriptElements = document.getElementsByTagName("script");
  const lastScript = scriptElements[scriptElements.length - 1];
  if (lastScript?.src) {
    return new URL(lastScript.src).origin;
  }

  return null;
};

const DEFAULT_UI_URL = getScriptOrigin() ?? window.location.origin;

const DEFAULT_CONFIG: Required<
  Pick<
    ChatWidgetConfig,
    | "mode"
    | "position"
    | "targetId"
    | "uiUrl"
    | "iframePath"
    | "openOnLoad"
    | "buttonLabel"
    | "zIndex"
    | "inlineHeight"
  >
> = {
  mode: "floating",
  position: "bottom-right",
  targetId: "getmee-chatbot",
  uiUrl: DEFAULT_UI_URL,
  iframePath: "/",
  openOnLoad: false,
  buttonLabel: "Chat with Getmee AI",
  zIndex: 2147483000,
  inlineHeight: "min(760px, 90vh)",
};

const getConfig = (): typeof DEFAULT_CONFIG => {
  const userConfig = window.ChatWidgetConfig ?? {};
  return {
    ...DEFAULT_CONFIG,
    ...userConfig,
  };
};

const createIframe = (config: typeof DEFAULT_CONFIG): HTMLIFrameElement => {
  const iframe = document.createElement("iframe");
  const baseUrl = config.uiUrl.replace(/\/$/, "");
  const path = config.iframePath.startsWith("/")
    ? config.iframePath
    : `/${config.iframePath}`;

  iframe.src = `${baseUrl}${path}`;
  iframe.title = "Getmee AI Assistant";
  iframe.setAttribute("loading", "lazy");
  iframe.style.width = "100%";
  iframe.style.height = "100%";
  iframe.style.border = "0";
  iframe.style.background = "#fff";
  return iframe;
};

const applyFloatingPosition = (
  el: HTMLElement,
  position: WidgetPosition,
): void => {
  el.style.position = "fixed";

  const offset = "16px";
  if (position.includes("bottom")) {
    el.style.bottom = offset;
  } else {
    el.style.top = offset;
  }

  if (position.includes("right")) {
    el.style.right = offset;
  } else {
    el.style.left = offset;
  }
};

const mountFloatingWidget = (config: typeof DEFAULT_CONFIG): void => {
  const root = document.createElement("div");
  root.id = "getmee-chat-widget-root";
  root.style.zIndex = String(config.zIndex);
  applyFloatingPosition(root, config.position);
  root.style.display = "flex";
  root.style.flexDirection = "column";
  root.style.gap = "12px";
  root.style.alignItems = config.position.includes("right")
    ? "flex-end"
    : "flex-start";

  const panel = document.createElement("div");
  panel.style.width = "min(420px, calc(100vw - 32px))";
  panel.style.height = "min(760px, calc(100vh - 32px))";
  panel.style.maxHeight = "calc(100vh - 32px)";
  panel.style.border = "1px solid #d7e6e3";
  panel.style.borderRadius = "16px";
  panel.style.overflow = "hidden";
  panel.style.background = "#fff";
  panel.style.boxShadow = "0 18px 45px rgba(10, 48, 43, 0.22)";

  let hasLoadedIframe = false;

  const ensureIframeLoaded = (): void => {
    if (hasLoadedIframe) {
      return;
    }

    const iframe = createIframe(config);
    panel.appendChild(iframe);
    hasLoadedIframe = true;
  };

  const toggle = document.createElement("button");
  toggle.type = "button";
  toggle.textContent = config.buttonLabel;
  toggle.setAttribute("aria-expanded", String(config.openOnLoad));
  toggle.style.height = "44px";
  toggle.style.padding = "0 16px";
  toggle.style.border = "0";
  toggle.style.borderRadius = "9999px";
  toggle.style.background = "#14907d";
  toggle.style.color = "#fff";
  toggle.style.font =
    "600 14px/1 system-ui, -apple-system, Segoe UI, sans-serif";
  toggle.style.cursor = "pointer";
  toggle.style.boxShadow = "0 8px 22px rgba(20, 144, 125, 0.35)";

  let isOpen = config.openOnLoad;
  panel.style.display = isOpen ? "block" : "none";

  if (isOpen) {
    ensureIframeLoaded();
  }

  toggle.addEventListener("click", () => {
    isOpen = !isOpen;
    if (isOpen) {
      ensureIframeLoaded();
    }
    panel.style.display = isOpen ? "block" : "none";
    toggle.setAttribute("aria-expanded", String(isOpen));
  });

  root.appendChild(panel);
  root.appendChild(toggle);
  document.body.appendChild(root);
};

const mountInlineWidget = (config: typeof DEFAULT_CONFIG): void => {
  const target = document.getElementById(config.targetId);
  if (!target) {
    console.warn(
      `[Getmee Widget] Inline mode failed: missing target element #${config.targetId}.`,
    );
    return;
  }

  const wrapper = document.createElement("div");
  wrapper.id = "getmee-chat-inline-root";
  wrapper.style.width = "100%";
  wrapper.style.height = config.inlineHeight;
  wrapper.style.minHeight = "520px";
  wrapper.style.border = "1px solid #d7e6e3";
  wrapper.style.borderRadius = "16px";
  wrapper.style.overflow = "hidden";
  wrapper.style.background = "#fff";

  const iframe = createIframe(config);
  iframe.style.height = "100%";
  wrapper.appendChild(iframe);
  target.appendChild(wrapper);
};

const bootstrap = (): void => {
  const config = getConfig();
  if (config.mode === "inline") {
    mountInlineWidget(config);
    return;
  }

  mountFloatingWidget(config);
};

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", bootstrap);
} else {
  bootstrap();
}

export {};
