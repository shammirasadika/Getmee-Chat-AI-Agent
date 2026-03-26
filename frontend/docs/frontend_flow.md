# GetMee Chatbot Frontend - System Flow

## Overview

This document describes the user-facing flows in the frontend chatbot application and how they connect to the FastAPI backend.

---

## 1. Application Bootstrap Flow

```mermaid
graph TD
    A[Browser loads page] --> B[main.tsx creates React root]
    B --> C[App.tsx renders providers]
    C --> D[QueryClientProvider]
    C --> E[TooltipProvider]
    C --> F[Toaster]
    D --> G[BrowserRouter]
    G --> H{"Route?"}
    H -->|"/"| I[Index.tsx]
    H -->|"*"| J[NotFound page]
    I --> K[ChatWidget component mounts]
    K --> L[Generate unique sessionId]
    K --> M[Set default language = en]
    K --> N[Show welcome screen]
```

---

## 2. Chat Message Flow

```mermaid
sequenceDiagram
    participant U as User
    participant CW as ChatWidget
    participant API as Backend /api/chat

    U->>CW: Types message + clicks Send (or Enter)
    CW->>CW: Add bot greeting (if first message)
    CW->>CW: Add user message to messages[]
    CW->>CW: Set isLoading = true
    CW->>API: POST /api/chat {message, session_id, language}
    API-->>CW: {answer, language, sources, fallback_used, requires_email}

    alt requires_email = false
        CW->>CW: Add bot answer to messages[]
    else requires_email = true
        CW->>CW: Add bot answer to messages[]
        CW->>CW: Show email collection form
    end

    CW->>CW: Set isLoading = false
    CW->>CW: Auto-scroll to bottom
```

### Chat Request Payload

```json
{
  "message": "How does AI scoring work?",
  "session_id": "session_1711468800_abc1234",
  "language": "en"
}
```

### Chat Response Payload

```json
{
  "answer": "AI scoring uses natural language processing to...",
  "language": "en",
  "sources": ["document1.pdf"],
  "fallback_used": false,
  "requires_email": false
}
```

---

## 3. Quick Question Flow

```mermaid
graph TD
    A[User on welcome screen] --> B[Clicks a quick question button]
    B --> C[Add bot greeting to messages]
    B --> D[Add selected question as user message]
    B --> E[Set chatStarted = true]
    B --> F[Call sendToApi with question text]
    F --> G[Same flow as Chat Message Flow above]
```

Quick questions are defined per language in the `translations` object — 5 for English, 5 for Spanish. They change instantly when the user toggles language before starting a chat.

---

## 4. Language Toggle Flow

```mermaid
graph TD
    A[User clicks Globe icon in header]
    A --> B{Current lang?}
    B -->|en| C[Set lang = es]
    B -->|es| D[Set lang = en]
    C --> E[All UI text re-renders in Spanish]
    D --> F[All UI text re-renders in English]
    E --> G[Next API call sends language: es]
    F --> H[Next API call sends language: en]
```

### Key Behavior

- Language toggle is **always available** in the header
- Switching language updates **all visible UI text** immediately (welcome screen, placeholders, buttons)
- The `language` field is sent with every `/api/chat` and `/api/support` request
- Chat history messages are **not re-translated** — only new messages use the new language
- Backend responds in the language specified in the request

---

## 5. Email Collection / Escalation Flow

When the backend cannot find relevant information in the knowledge base, it returns `requires_email: true`. The frontend then collects the user's email to escalate to human support.

```mermaid
sequenceDiagram
    participant U as User
    participant CW as ChatWidget
    participant Chat as Backend /api/chat
    participant Sup as Backend /api/support

    U->>CW: Sends question
    CW->>Chat: POST /api/chat {message, session_id, language}
    Chat-->>CW: {answer, fallback_used: true, requires_email: true}
    CW->>CW: Show fallback answer + email form

    alt User submits email
        U->>CW: Enters email + clicks Submit
        CW->>CW: Validate email format (regex)

        alt Valid email
            CW->>Sup: POST /api/support {session_id, user_email, user_message, language}
            Sup-->>CW: {message: "Support request saved"}
            CW->>CW: Hide email form
            CW->>CW: Show success message
        else Invalid email
            CW->>CW: Show "Please enter a valid email" message
        end

    else User clicks Skip
        U->>CW: Clicks Skip button
        CW->>CW: Hide email form
        CW->>CW: Continue normal chat
    end
```

### Support Request Payload

```json
{
  "session_id": "session_1711468800_abc1234",
  "user_email": "user@example.com",
  "user_message": "How do I reset my password?",
  "language": "en"
}
```

---

## 6. New Chat Flow

```mermaid
graph TD
    A[User clicks New Chat button in header]
    A --> B[Clear messages array]
    A --> C[Set chatStarted = false]
    A --> D[Hide email form]
    A --> E[Welcome screen re-appears]
    A --> F[Session ID remains the same]
```

---

## 7. Widget Embedding Flow

This flow describes how the widget loader (`getmee-chatbot.js`) works when embedded on an external website.

### Floating Mode

```mermaid
sequenceDiagram
    participant WP as WordPress Page
    participant WL as Widget Loader (JS)
    participant IF as Iframe
    participant App as Chatbot React App

    WP->>WL: <script> tag loads getmee-chatbot.js
    WL->>WL: Read config (data-* attrs / window.ChatWidgetConfig)
    WL->>WP: Inject FAB button (floating circle, z-index 99998)
    WL->>WP: Inject chat panel (hidden, z-index 99999)
    WL->>IF: Create iframe with src = chatUrl

    Note over WP: User sees floating chat button

    WP->>WL: User clicks FAB
    WL->>WL: Toggle panel visibility
    WL->>WL: Switch icon (chat bubble ↔ ✕)

    Note over IF: Iframe loads chatbot app
    IF->>App: React app renders ChatWidget
    App->>App: Full chat functionality inside iframe
```

### Inline Mode

```mermaid
sequenceDiagram
    participant WP as WordPress Page
    participant WL as Widget Loader (JS)
    participant Div as Target <div>
    participant App as Chatbot React App

    WP->>WL: <script> tag loads getmee-chatbot.js
    WL->>WL: Read config (mode: "inline", targetId)
    WL->>Div: Find element by targetId
    WL->>Div: Append iframe with src = chatUrl
    Div->>App: React app renders inside container
```

### Config Resolution

```mermaid
graph TD
    A[Widget Loader starts] --> B{Script data-* attributes?}
    B -->|Yes| C[Use data-* values]
    B -->|No| D{window.ChatWidgetConfig?}
    D -->|Yes| E[Use window config values]
    D -->|No| F[Use defaults]
    C --> G[Merge: data-* > window > defaults]
    E --> G
    F --> G
    G --> H{mode?}
    H -->|floating| I[Mount floating button + panel]
    H -->|inline| J[Mount iframe in target element]
```

---

## 8. Error Handling Flow

```mermaid
graph TD
    A[API call fails] --> B{Which endpoint?}

    B -->|/api/chat| C[Show error message in chat]
    C --> D["Sorry, something went wrong. Please try again."]
    C --> E[isLoading = false]
    C --> F[User can retry]

    B -->|/api/support| G[Show email error in chat]
    G --> H["Failed to submit your request. Please try again."]
    G --> I[isSubmittingEmail = false]
    G --> J[Email form stays visible for retry]
```

All error messages are fully translated (English and Spanish) and displayed as bot messages in the chat.

---

## 9. Complete User Journey

```mermaid
graph TD
    Start([User opens chatbot]) --> Welcome[Welcome screen with quick questions]

    Welcome --> Q{How does user start?}
    Q -->|Quick question| QQ[Click a quick question button]
    Q -->|Type message| TM[Type in input + Send]
    Q -->|Toggle language| TL[Click Globe → switch EN/ES]
    TL --> Welcome

    QQ --> Chat[Chat conversation active]
    TM --> Chat

    Chat --> Send[User sends message]
    Send --> API[POST /api/chat]
    API --> Check{requires_email?}

    Check -->|No| BotReply[Bot shows answer]
    BotReply --> Chat

    Check -->|Yes| Fallback[Bot shows fallback + email form]
    Fallback --> EmailChoice{User choice?}
    EmailChoice -->|Submit email| Support[POST /api/support → success]
    EmailChoice -->|Skip| Chat
    Support --> Chat

    Chat --> NewChat{Click New Chat?}
    NewChat -->|Yes| Welcome
    NewChat -->|No| Chat

    style Start fill:#2a9d8f,color:#fff
    style Welcome fill:#e0f5f2
    style Chat fill:#e0f5f2
    style Fallback fill:#fff3cd
    style Support fill:#d4edda
```
