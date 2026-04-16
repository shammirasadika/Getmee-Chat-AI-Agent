# FE Instruction: Remove iframe Architecture — Bundle Chatbot as Self-Contained Widget

## Principle

> We already built the chatbot as a widget, so WordPress only needs to load our script.
> The chatbot will render itself and connect to our backend independently.
> **We don't use iframe — we use JavaScript.**

---

## Current Architecture (WRONG)

```
WordPress page
├── wordpress/getmee-chatbot.js          ← SEPARATE hand-written loader (duplicate logic)
│   ├── Creates its own FAB button       ← duplicate of ChatBot.tsx FAB
│   ├── Creates panel container          ← duplicate wrapper (double border/shadow)
│   ├── Creates iframe                   ← loads chatbot from separate URL
│   │   └── ChatBot.tsx (React)          ← runs inside iframe on different origin
│   │       ├── Has its own FAB          ← hidden behind iframe, never seen
│   │       ├── Has minimize button      ← clicks intercepted by overlay
│   │       └── Has close button         ← clicks intercepted by overlay
│   ├── Creates overlay buttons          ← invisible 40×40px buttons on top of iframe
│   └── Manages its own open/close state ← competes with React state
│
frontend/widget/widget.ts               ← ANOTHER loader with same iframe logic
│   └── Also creates iframe + FAB       ← third copy of same logic
│
frontend/dist-widget/getmee-chatbot.js  ← built from widget.ts, still uses iframe
```

### 6 Specific Issues

| # | Issue | File | Problem |
|---|-------|------|---------|
| 1 | **Duplicate FAB button** | `wordpress/getmee-chatbot.js` lines 76-99 | WordPress creates its own FAB, but `ChatBot.tsx` already renders one (line 565-568). Two FABs exist. |
| 2 | **Duplicate panel container** | `wordpress/getmee-chatbot.js` lines 101-118 | WordPress creates `#getmee-chat-panel` with sizing/shadow/border, but `ChatBot.tsx` has `styles.window` with its own. Double wrapper = double border, double shadow. |
| 3 | **Overlay hack buttons** | `wordpress/getmee-chatbot.js` lines 121-162 | Transparent invisible buttons positioned on top of iframe to intercept clicks on buttons that already exist in React. Breaks on any layout change. |
| 4 | **Competing state machines** | `wordpress/getmee-chatbot.js` lines 164-198 | WordPress has `isOpen`, `isMinimized`, `openPanel()`, `closePanel()`. React also has `const [open, setOpen] = useState(false)`. Two state machines fight each other. |
| 5 | **WordPress owns responsive CSS** | `wordpress/getmee-chatbot.js` lines 233-248 | WordPress injects `@media (max-width: 480px)` styles. The widget should handle its own responsiveness. |
| 6 | **Two separate loader scripts** | `widget.ts` + `wordpress/getmee-chatbot.js` | Two files with duplicated logic (both create FAB, panel, iframe, toggle). One is TypeScript source, other is hand-written JS copy. |

### Root Cause

The build config (`vite.widget.config.ts`) explicitly says:
```
// Widget loader is pure vanilla JS/TS — no React needed
```
This means the built `dist-widget/getmee-chatbot.js` is just an iframe loader — it does NOT contain the chatbot. The actual chatbot (`ChatBot.tsx` with React) runs on a separate server and is loaded via iframe `src`. This is the opposite of what we want.

---

## Target Architecture (CORRECT)

```
WordPress page
├── <script> window.ChatWidgetConfig = { apiBase: "https://api.getmee.ai" } </script>
├── <script src="https://cdn.getmee.ai/getmee-chatbot.js"></script>
│        ↓
│   getmee-chatbot.js (single file, contains everything)
│   ├── React (bundled in)
│   ├── ChatBot component (bundled in)
│   ├── All styles (inline, no external CSS)
│   ├── Creates its own DOM container
│   ├── Renders chatbot directly into page
│   └── Connects to backend API independently
│
│   NO iframe. NO separate server. NO WordPress logic.
```

### Flow

```
1. WordPress page loads
2. Our script loads (single JS file)
3. Script creates a container div in the DOM
4. Script renders React ChatBot component into it
5. Chatbot runs independently (calls our backend API)
6. WordPress does NOTHING else
```

### Rules

- ✅ Script auto-initializes (no manual trigger needed)
- ✅ Creates its own DOM container
- ✅ Does NOT depend on WordPress styles
- ✅ Handles its own positioning (fixed bottom-right)
- ✅ All UI components live in frontend
- ❌ Don't rebuild UI inside WordPress
- ❌ Don't modify WordPress core
- ❌ Don't tightly couple with WP
- ❌ Don't use iframe

---

## Changes Required

### 1. Rewrite `frontend/widget/widget.ts` → `frontend/widget/widget.tsx`

The current `widget.ts` is a vanilla JS iframe loader. Replace it with a React entry point that bundles the chatbot directly.

**Delete current content of `widget.ts` and create `widget.tsx`:**

```tsx
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
  // Ensure our container doesn't inherit WordPress styles
  container.style.cssText = "all: initial; position: fixed; z-index: 99999; font-family: system-ui, -apple-system, sans-serif;";
  document.body.appendChild(container);

  const root = createRoot(container);
  root.render(
    <ChatBot
      apiBase={config.apiBase || "http://localhost:8001"}
      logoUrl={config.logoUrl}
    />
  );
}

// Expose global init for manual initialization
window.GetMeeChat = { init: mount };

// Auto-initialize if config exists
const scriptEl = document.currentScript as HTMLScriptElement | null;
const hasConfig = window.ChatWidgetConfig || scriptEl?.hasAttribute("data-api-base");

if (hasConfig) {
  const config: ChatWidgetConfig = {
    ...(window.ChatWidgetConfig || {}),
    apiBase: scriptEl?.getAttribute("data-api-base") || window.ChatWidgetConfig?.apiBase,
    logoUrl: scriptEl?.getAttribute("data-logo-url") || window.ChatWidgetConfig?.logoUrl,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => mount(config));
  } else {
    mount(config);
  }
}
```

---

### 2. Update `frontend/vite.widget.config.ts` — Bundle React

Current config explicitly excludes React. Change it to bundle everything into one file.

**Replace entire file:**

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// Widget builds ChatBot + React into a single self-contained IIFE bundle
export default defineConfig({
  plugins: [react()],
  build: {
    lib: {
      entry: path.resolve(__dirname, "widget/widget.tsx"),
      name: "GetMeeChat",
      fileName: () => "getmee-chatbot.js",
      formats: ["iife"],
    },
    outDir: "dist-widget",
    emptyOutDir: true,
    minify: "esbuild",
    rollupOptions: {
      output: {
        inlineDynamicImports: true,
      },
    },
    // Bundle size will be ~150-200KB gzipped (React + component)
    // This is acceptable for a self-contained widget
    cssCodeSplit: false,
  },
  define: {
    "process.env.NODE_ENV": JSON.stringify("production"),
  },
});
```

**Key change:** Added `react()` plugin and changed entry to `.tsx`. React is now bundled INTO the output file instead of loaded from iframe.

---

### 3. Update `frontend/widget/ChatBot.tsx` — Remove FAB, always render

Currently `ChatBot.tsx` renders its own FAB button and manages open/close state. Since the widget now renders directly (no iframe wrapper), **ChatBot.tsx should keep its own FAB and open/close state** — it IS the complete widget.

No changes needed to ChatBot.tsx for the basic migration. The component already:
- Has its own FAB button (when `open === false`)
- Has its own chat window (when `open === true`)
- Has minimize and close buttons
- Manages its own state
- Connects to the API independently

The only thing to verify: `ChatBot.tsx` uses inline styles (not Tailwind/CSS files), so it will work without any external stylesheets. ✅ Already confirmed — all styles are inline via the `styles` object.

---

### 4. Simplify `wordpress/getmee-chatbot.js`

This file should **no longer exist as a loader**. WordPress pages just need:

```html
<!-- Option A: Config object + script -->
<script>
  window.ChatWidgetConfig = {
    apiBase: "https://api.getmee.ai",
    logoUrl: "https://getmee.ai/logo.png"
  };
</script>
<script src="https://cdn.getmee.ai/getmee-chatbot.js"></script>

<!-- Option B: Data attributes -->
<script
  src="https://cdn.getmee.ai/getmee-chatbot.js"
  data-api-base="https://api.getmee.ai"
  data-logo-url="https://getmee.ai/logo.png"
></script>

<!-- Option C: Manual init -->
<script src="https://cdn.getmee.ai/getmee-chatbot.js"></script>
<script>
  GetMeeChat.init({ apiBase: "https://api.getmee.ai" });
</script>
```

**Delete or replace** `wordpress/getmee-chatbot.js` — it is no longer needed.

---

### 5. Update WordPress HTML pages

All WordPress HTML files (`index.html`, `about.html`, `contact.html`, `features.html`) currently load the old iframe-based script. Update them to use the new simple embed.

**Replace the old script tag in each file with:**

```html
<script>
  window.ChatWidgetConfig = {
    apiBase: "https://api.getmee.ai"
  };
</script>
<script src="./getmee-chatbot.js"></script>
```

---

### 6. Build and deploy

```bash
cd frontend
npm run build:widget
```

Output: `frontend/dist-widget/getmee-chatbot.js` — a single self-contained file with React + ChatBot bundled in. Copy this file to wherever WordPress can serve it (CDN, WordPress uploads, etc.).

---

## Before vs After comparison

| Aspect | Before (iframe) | After (direct JS) |
|--------|-----------------|-------------------|
| How chatbot loads | iframe src → separate server | Script renders directly into page |
| Files WordPress needs | `getmee-chatbot.js` (280 lines of duplicate logic) | `<script src="...">` tag only |
| React bundled? | No, runs on separate server | Yes, bundled into single JS file |
| FAB button | 2 competing FABs (WP + React) | 1 FAB (React only) |
| Close/minimize | Overlay hack intercepts React buttons | React buttons work directly |
| State management | 2 state machines (WP JS + React) | 1 state machine (React) |
| Responsive CSS | WordPress injects its own @media rules | ChatBot handles its own |
| Cross-origin issues | Yes (iframe = separate origin) | No (same page) |
| Bundle size | Small loader + full app on server | ~150-200KB gzipped (React + component) |
| Loader scripts | 3 files (widget.ts, WP getmee-chatbot.js, dist-widget/) | 1 file (dist-widget/getmee-chatbot.js) |

---

## Files to change

| File | Action |
|------|--------|
| `frontend/widget/widget.ts` | **Delete** — replaced by widget.tsx |
| `frontend/widget/widget.tsx` | **Create** — new React entry point |
| `frontend/vite.widget.config.ts` | **Update** — add React plugin, change entry to .tsx |
| `frontend/widget/ChatBot.tsx` | **No changes** — already self-contained |
| `wordpress/getmee-chatbot.js` | **Delete** — no longer needed |
| `wordpress/*.html` | **Update** — simplify script tags |
| `frontend/dist-widget/getmee-chatbot.js` | **Rebuild** — `npm run build:widget` |

---

## Testing Checklist

- [ ] `npm run build:widget` produces single `getmee-chatbot.js` in `dist-widget/`
- [ ] WordPress pages load chatbot by just including the script tag
- [ ] FAB button appears (bottom-right) on WordPress pages
- [ ] Clicking FAB opens chatbot window
- [ ] Minimize button minimizes chatbot
- [ ] Close button closes chatbot, FAB reappears
- [ ] Chat messages send and receive from backend API
- [ ] Language toggle works (EN/ES)
- [ ] Email support flow works
- [ ] Mobile responsive (< 480px) — chatbot goes fullscreen
- [ ] No iframe in DOM when inspecting
- [ ] No duplicate FAB/buttons in DOM
- [ ] WordPress styles don't leak into chatbot (due to `all: initial` on container)
- [ ] Script works with `ChatWidgetConfig`, data attributes, and manual `GetMeeChat.init()`
