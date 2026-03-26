# GetMee Chatbot Frontend - Implementation Instructions

## Scope

This document covers the **frontend** implementation only — a React-based chatbot UI that communicates with the FastAPI backend, plus a vanilla JS widget loader for embedding on external websites (WordPress, etc.).

---

## Project Overview

| Item | Detail |
|------|--------|
| Framework | React 18.3.1 + TypeScript 5.8.3 |
| Build Tool | Vite 8.0.0 |
| Styling | Tailwind CSS 3.4.17 + CSS custom properties (HSL) |
| UI Components | Radix UI (Shadcn) + Lucide icons |
| State Management | React Query (TanStack) + React local state |
| Routing | React Router v6 |
| Dev Server Port | 8080 |
| Backend API | FastAPI on port 8001 |

---

## Architecture

### Two Build Targets

1. **Main App** (`npm run build`) — Full React SPA served at the chatbot URL. This is the chatbot UI that runs inside an iframe when embedded on external sites, or standalone at its own URL.
2. **Widget Loader** (`npm run build:widget`) — Tiny vanilla JS file (~4 KB) that external websites include via a `<script>` tag. It creates a floating chat button and opens the main app inside an iframe.

### Folder Structure

```
frontend/
├── src/                        # Main React chatbot app
│   ├── main.tsx                # React entry point
│   ├── App.tsx                 # Router + providers
│   ├── index.css               # Tailwind + design tokens (HSL)
│   ├── pages/
│   │   └── Index.tsx           # Root page — renders ChatWidget
│   ├── components/
│   │   ├── ChatWidget.tsx      # Main chatbot UI component
│   │   ├── NavLink.tsx         # Navigation link
│   │   └── ui/                 # Shadcn/Radix component library
│   ├── hooks/
│   │   ├── use-mobile.tsx      # Mobile breakpoint detection
│   │   └── use-toast.ts       # Toast notification hook
│   ├── lib/
│   │   └── utils.ts           # Utility functions (cn, classnames)
│   └── assets/
│       └── getmee-logo.svg.png # Bot avatar
├── widget/
│   └── widget.ts              # Vanilla JS widget loader (no React)
├── vite.config.ts             # Main app build config
├── vite.widget.config.ts      # Widget loader build config
├── dist/                      # Main app build output
└── dist-widget/               # Widget loader build output
    └── getmee-chatbot.js      # Single IIFE file for embedding
```

---

## Main Chatbot UI — ChatWidget.tsx

### Requirements

1. **Single component** handles the full chat lifecycle: welcome screen → conversation → email collection
2. **Bilingual UI** — English and Spanish with a toggle button in the header
3. **All UI text** lives in a `translations` object keyed by language code (`en`, `es`)
4. **Quick questions** — 5 pre-built questions per language shown on the welcome screen
5. **Always-visible input bar** at the bottom, even during email collection
6. **Email collection** triggers when API returns `requires_email: true` (fallback/escalation)
7. **Session-based** — generates a unique `session_id` per chat session
8. **Auto-scroll** to latest message

### State

| State | Type | Purpose |
|-------|------|---------|
| `lang` | `"en" \| "es"` | Current UI language |
| `message` | `string` | Current input text |
| `messages` | `Message[]` | Chat history (`{text, isUser, time}`) |
| `chatStarted` | `boolean` | Welcome screen vs active chat |
| `isLoading` | `boolean` | API request in progress |
| `sessionId` | `string` | Unique session identifier |
| `showEmailInput` | `boolean` | Email form visibility |
| `emailAddress` | `string` | User email input |
| `lastFallbackMessage` | `string` | User message that triggered fallback |
| `isSubmittingEmail` | `boolean` | Email submission in progress |

### API Integration

| Endpoint | Method | Payload | When |
|----------|--------|---------|------|
| `/api/chat` | POST | `{ message, session_id, language }` | User sends a chat message |
| `/api/support` | POST | `{ session_id, user_email, user_message, language }` | User submits email for support |

### Translation Keys

Each language object contains:

- `title`, `online`, `greeting`, `subtitle` — Header and welcome text
- `askAbout`, `topics` — Topic list on welcome screen
- `quickQuestionLabel`, `quickQuestions` — Quick question buttons
- `botGreeting` — First bot message when chat starts
- `placeholder` — Input placeholder
- `emailPrompt`, `emailPlaceholder`, `submit`, `skip`, `invalidEmail` — Email form
- `errorMsg`, `emailSuccess`, `emailError` — Error/success messages

### UI Layout

```
┌─────────────────────────────────────────┐
│  [Logo] GetMee AI Assistant  🟢 Online  │
│                          [🌐] [New Chat]│
├─────────────────────────────────────────┤
│                                         │
│  Welcome screen (before chat starts):   │
│    Greeting + topics + quick questions   │
│                                         │
│  OR                                     │
│                                         │
│  Chat messages (after first message):   │
│    Bot message (left, with avatar)      │
│    User message (right, primary color)  │
│    ...                                  │
│    [Loading spinner]                    │
│                                         │
│  Email collection (when fallback):      │
│    [email input] [Submit] [Skip]        │
│                                         │
├─────────────────────────────────────────┤
│  [Type your message...        ] [Send]  │
└─────────────────────────────────────────┘
```

---

## Widget Loader — widget.ts

### Requirements

1. **Pure vanilla JS/TypeScript** — no React, no CSS frameworks, no dependencies
2. **Single IIFE file** built by Vite (~4 KB gzipped)
3. **Two modes**: floating (default) and inline
4. **Configurable** via `window.ChatWidgetConfig` or `data-*` attributes on the script tag
5. **iframe-based** — loads the main chatbot app URL inside an iframe (complete style isolation)
6. **Mobile responsive** — full-screen panel on screens < 480px

### Configuration

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `mode` | `"floating" \| "inline"` | `"floating"` | Widget display mode |
| `position` | `"bottom-right" \| "bottom-left"` | `"bottom-right"` | Floating button position |
| `targetId` | `string` | `""` | DOM element ID for inline mode |
| `chatUrl` | `string` | Script origin | URL of the hosted chatbot app |

### Config Resolution Order

1. Script `data-*` attributes (highest priority)
2. `window.ChatWidgetConfig` object
3. Built-in defaults

### Floating Mode

- **FAB button**: 60×60px circle, teal (#2a9d8f), z-index 99998
- **Chat panel**: 400×600px, rounded corners, shadow, z-index 99999
- **Toggle**: Click FAB to open/close; icon switches between chat bubble and ✕
- **Mobile**: Panel goes full-screen under 480px viewport width

### Inline Mode

- Mounts an iframe directly inside the element specified by `targetId`
- Container defaults to 600px height if none set
- No floating button created

### Embedding Examples

```html
<!-- Floating (default) -->
<script src="https://cdn.example.com/getmee-chatbot.js"
  data-chat-url="https://chat.example.com">
</script>

<!-- Inline -->
<script>
  window.ChatWidgetConfig = {
    mode: "inline",
    targetId: "chat-container",
    chatUrl: "https://chat.example.com"
  };
</script>
<div id="chat-container" style="height:600px"></div>
<script src="https://cdn.example.com/getmee-chatbot.js"></script>

<!-- Manual init -->
<script src="https://cdn.example.com/getmee-chatbot.js"></script>
<script>
  GetMeeChat.init({
    mode: "floating",
    position: "bottom-left",
    chatUrl: "https://chat.example.com"
  });
</script>
```

---

## Design System

### Color Tokens (HSL CSS Custom Properties)

| Token | Light | Usage |
|-------|-------|-------|
| `--primary` | 174 60% 35% (teal) | Buttons, user chat bubbles, links |
| `--primary-foreground` | 0 0% 100% (white) | Text on primary backgrounds |
| `--background` | 0 0% 100% (white) | Page background |
| `--foreground` | 220 15% 20% (dark gray) | Body text |
| `--chat-bubble` | 174 25% 95% (light teal) | Bot message background |
| `--online` | 145 60% 45% (green) | Online status indicator |
| `--border` | 180 20% 88% | Borders and dividers |
| `--muted` | 180 20% 96% | Muted backgrounds |
| `--destructive` | 0 84.2% 60.2% (red) | Error states |
| `--radius` | 0.75rem | Default border radius |

Dark mode tokens are also defined in `index.css` under the `.dark` selector.

---

## Build Commands

| Command | Output | Description |
|---------|--------|-------------|
| `npm run dev` | Dev server :8080 | Start development server with HMR |
| `npm run build` | `dist/` | Production build of the chatbot app |
| `npm run build:widget` | `dist-widget/getmee-chatbot.js` | Build widget loader IIFE |
| `npm run preview` | Preview :4173 | Preview production build locally |
| `npm run test` | — | Run Vitest unit tests |
| `npm run lint` | — | ESLint check |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE` | `http://localhost:8001` | Backend API base URL |

Set in `.env` or `.env.production` for deployment.

---

## Dependencies Summary

### Runtime

- **react**, **react-dom** — UI framework
- **react-router-dom** — Client-side routing
- **@tanstack/react-query** — Server state management
- **@radix-ui/*** — Accessible UI primitives (26+ packages)
- **lucide-react** — Icon library (Send, Mail, Loader2, Globe, etc.)
- **tailwind-merge**, **clsx** — Conditional class utilities
- **sonner** — Toast notifications
- **react-hook-form**, **zod** — Form handling and validation
- **next-themes** — Dark mode support
- **date-fns** — Date formatting

### Dev

- **vite** — Build tool and dev server
- **typescript** — Type checking
- **tailwindcss** — Utility-first CSS
- **eslint** — Code linting
- **vitest** — Unit testing
- **playwright** — E2E testing

---

## Implementation Order

1. Set up Vite + React + TypeScript + Tailwind
2. Define CSS design tokens in `index.css`
3. Install Radix UI / Shadcn components
4. Build `ChatWidget.tsx` with translations object
5. Wire API calls to backend (`/api/chat`, `/api/support`)
6. Add language toggle (Globe icon)
7. Implement email collection flow (fallback handling)
8. Build widget loader (`widget/widget.ts`) as vanilla JS
9. Configure dual Vite builds (app + widget)
10. Test embedding via iframe on sample page
