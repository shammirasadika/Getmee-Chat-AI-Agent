# GetMee Chatbot Widget Integration Guide

## Overview

The GetMee Chatbot Widget is a JavaScript-based embeddable chat interface that can be integrated into any website. It supports both **floating** and **inline** modes with flexible positioning options.

## Architecture

```
┌─────────────────────────────────────────┐
│   Client Website (WordPress/Any)         │
│                                          │
│  <script src="widget.js"></script>       │
│                                          │
│  <div id="getmee-chatbot"></div>         │
│  (for inline mode)                       │
│                                          │
└─────────────────────────────────────────┘
                    ↓↑
        (iframe communicates via postMessage)
                    ↓↑
┌─────────────────────────────────────────┐
│   GetMee Chatbot UI (Hosted)             │
│   - React + Vite Application             │
│   - Full responsive design               │
│   - Connected to GetMee Backend API      │
└─────────────────────────────────────────┘
```

## Features

✅ **Floating Mode** - Widget appears as a floating button + panel in corner
✅ **Inline Mode** - Widget embeds within a specific page element
✅ **Mobile Responsive** - Adapts to all screen sizes
✅ **Lazy Loading** - Floating widget iframe loads on first open
✅ **Configurable** - Customize position, label, size, etc.
✅ **Session Management** - Maintains chat sessions with backend
✅ **Error Handling** - Graceful fallbacks for offline mode
✅ **Cross-Origin** - Supports cross-domain embedding

## Quick Start

### 1. Installation - For Your Website

Add this single script tag to your website (e.g., WordPress footer):

```html
<!-- GetMee Chatbot Widget -->
<script src="https://chatbot.getmee.com/widget.js"></script>

<!-- Optional: Configure widget behavior -->
<script>
  window.ChatWidgetConfig = {
    mode: "floating", // 'floating' or 'inline'
    position: "bottom-right", // 'bottom-right', 'bottom-left', 'top-right', 'top-left'
    uiUrl: "https://chatbot.getmee.com",
    buttonLabel: "Chat with Getmee AI",
    openOnLoad: false, // Auto-open on page load
    zIndex: 2147483000, // Ensure it appears on top
  };
</script>
```

### 2. For Inline Mode

If you want the chatbot to appear inside a specific page section:

```html
<!-- Add a container where you want the chatbot -->
<div id="getmee-chatbot"></div>

<!-- Load widget -->
<script src="https://chatbot.getmee.com/widget.js"></script>

<!-- Configure for inline mode -->
<script>
  window.ChatWidgetConfig = {
    mode: "inline",
    targetId: "getmee-chatbot", // Must match your container ID
    inlineHeight: "min(760px, 90vh)", // Optional: customize height
  };
</script>
```

## Configuration Options

```typescript
interface ChatWidgetConfig {
  // Display mode
  mode?: "floating" | "inline"; // Default: 'floating'

  // Position (floating mode only)
  position?: "bottom-right" | "bottom-left" | "top-right" | "top-left"; // Default: 'bottom-right'

  // URLs
  uiUrl?: string; // Default: widget script origin
  iframePath?: string; // Default: '/'

  // Container (inline mode)
  targetId?: string; // Default: 'getmee-chatbot'
  inlineHeight?: string; // Default: 'min(760px, 90vh)'

  // Behavior
  openOnLoad?: boolean; // Default: false
  buttonLabel?: string; // Default: 'Chat with Getmee AI'
  zIndex?: number; // Default: 2147483000

  // Custom styling (coming soon)
  theme?: "light" | "dark";
  primaryColor?: string;
  accentColor?: string;
}
```

## Frontend Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatWidget.tsx          # Main chat UI (responsive)
│   │   ├── ui/                     # shadcn/ui components
│   │   └── NavLink.tsx
│   ├── services/
│   │   └── chat.service.ts         # API communication layer
│   ├── hooks/
│   │   ├── use-toast.ts
│   │   └── use-mobile.tsx
│   ├── pages/
│   │   ├── Index.tsx               # Main page
│   │   └── NotFound.tsx
│   ├── App.tsx                     # Root component with routing
│   ├── main.tsx                    # Entry point
│   └── index.css
├── widget/
│   ├── widget.ts                   # Widget controller (embedded script)
│   └── widget-types.ts             # Type definitions
├── index.html                      # Main app HTML
├── vite.config.ts                  # Build configuration
├── package.json
└── tsconfig.json
```

## How It Works

### Floating Mode Flow

```
1. User visits WordPress site
2. widget.js loads automatically
3. Creates chat button in bottom-right (configurable)
4. User clicks button → chat panel opens
5. Panel loads chatbot UI via iframe
6. Chat initializes backend session
7. Messages sent/received via iframe communication
```

### Inline Mode Flow

```
1. Website has <div id="getmee-chatbot"></div>
2. window.ChatWidgetConfig specifies inline mode
3. widget.js creates iframe inside that div
4. Chatbot loads and works within the space
5. No floating button, fully integrated
```

## API Integration

The frontend ChatWidget communicates with the backend API:

### Endpoints Used (Backend Team)

```
POST /api/chat/send
- Request: { message, sessionId, timestamp }
- Response: { reply, isStreaming }

POST /api/chat/session
- Request: { userId, timestamp }
- Response: { sessionId }

DELETE /api/chat/session/{sessionId}
- Closes session

GET /api/chat/history/{sessionId}
- Response: { messages: [] }

POST /api/chat/feedback
- Request: { messageId, rating, sessionId, timestamp }
```

### Mock Mode (Development)

The ChatWidget is configured for **mock mode** by default (see `.env`):

- Generates intelligent bot responses locally
- No backend required for testing
- Switch to production API by changing `.env.production`

## Deployment

### Development

```bash
npm run dev
# Runs on http://localhost:8081
```

### Production Build

```bash
npm run build
# Builds main app to dist/app/
# Builds widget script to dist/widget/widget.js
```

### Hosting Requirements

1. **Main UI**: Host at https://chatbot.getmee.com
   - Serve index.html from dist/app/
   - Configure CORS headers to allow iframe embedding
   - SSL/HTTPS required

2. **Widget Script**: Host at https://chatbot.getmee.com/widget.js
   - Serve widget.js from dist/widget/
   - Make accessible to any domain

### CORS Configuration (Backend)

Ensure backend allows requests from widget:

```
Access-Control-Allow-Origin: https://chatbot.getmee.com
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: POST, GET, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

## Mobile Responsiveness

✅ ChatWidget automatically adapts to:

- Mobile phones (< 768px) - Full viewport
- Tablets (768px - 1024px) - Responsive layout
- Desktop (> 1024px) - Standard 420x760px panel

CSS Breakpoints:

- `sm:` - 640px (Tailwind)
- `md:` - 768px
- `lg:` - 1024px

## Features Implemented

### UI Components

- ✅ Message display (user + bot)
- ✅ Input field with send button
- ✅ Typing indicator (animated dots)
- ✅ Quick question buttons
- ✅ Header with status indicator
- ✅ Responsive design
- ✅ Error handling banner
- ✅ Session initialization

### Widget Features

- ✅ Floating mode with toggle
- ✅ Inline mode with target element
- ✅ Configurable positioning
- ✅ Lazy loading iframe
- ✅ Custom styling (button, shadow, border)
- ✅ Responsive dimensions
- ✅ Z-index management

### Service Features

- ✅ Message sending
- ✅ Session management
- ✅ Chat history retrieval
- ✅ Feedback submission
- ✅ Mock response generation
- ✅ Error fallback handling
- ✅ Graceful API degradation

## Troubleshooting

### Widget Not Showing

1. Check browser console for errors
2. Verify `window.ChatWidgetConfig` is set correctly
3. Ensure widget.js is loaded before config
4. Check that target element exists (for inline mode)

### Chat Not Loading

1. Check backend API is running
2. Verify API URL in `.env` is correct
3. Check CORS headers on backend
4. Look at Network tab in DevTools for API calls

### Styling Issues

1. Check iframe has correct CSS loaded
2. Verify Tailwind config in vite.config.ts
3. Check for CSS conflicts on parent page

## Development Notes

### Tech Stack

- **Framework**: React 18 + TypeScript
- **Build**: Vite
- **Styling**: Tailwind CSS + shadcn/ui
- **Form Handling**: React Hook Form
- **API**: Fetch API (replace with axios if needed)
- **Testing**: Vitest + Playwright

### Key Files to Modify

1. **ChatWidget.tsx** - Main UI component
   - Add new chat features here
   - Modify styling
   - Change quick questions

2. **chat.service.ts** - API Communication
   - Update API endpoints
   - Add new service methods
   - Implement streaming responses

3. **widget.ts** - Widget Controller
   - Change widget styling
   - Add iframe attributes
   - Modify button behavior

4. **.env** - Environment Variables
   - Point to backend API
   - Toggle mock mode
   - Configure URLs

## Next Steps

1. ✅ Deploy main UI to production
2. ✅ Deploy widget script to production
3. 🔄 Backend team: Integrate chat API endpoints
4. 🔄 Backend team: Set up session management
5. 🔄 Client: Add widget script to WordPress
6. Test end-to-end chat functionality
7. Collect feedback and iterate

## Support

For issues or questions:

1. Check this guide first
2. Review browser console errors
3. Check Network tab in DevTools
4. Contact development team with error logs
