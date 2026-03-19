# Human Support Flow

## Purpose

When the chatbot cannot find an answer, it should ask the user for confirmation before connecting to human support, instead of automatically escalating.

---

## Flow Steps

1. **Backend detects no relevant answer**
   → Returns `fallback_used = true`

2. **Frontend receives response**

3. **Frontend shows message:**
   > "I couldn't find this information. Do you need help from a support agent?"

4. **Display buttons:**
   - ✅ Yes, contact support
   - 🔄 No, I'll try again

5. **User action:**
   - **If YES →** Show support message (e.g., contact email or form)
   - **If NO →** Allow user to re-ask the question

---

## Frontend Logic

```javascript
if (response.fallback_used) {
  showSupportOptions = true;
}
```

---

## React UI Example

```jsx
{response.fallback_used && (
  <div className="support-box">
    <p>I couldn't find this information. Do you need help from a support agent?</p>

    <button onClick={handleSupportYes}>
      Yes, contact support
    </button>

    <button onClick={handleSupportNo}>
      No, I'll try again
    </button>
  </div>
)}
```

---

## Button Handlers

### YES → Support

```javascript
const handleSupportYes = () => {
  setMessages(prev => [
    ...prev,
    {
      role: "bot",
      text: "Please contact support at support@email.com"
    }
  ]);
};
```

### NO → Continue Chat

```javascript
const handleSupportNo = () => {
  setMessages(prev => [
    ...prev,
    {
      role: "bot",
      text: "Sure, please try asking your question differently 😊"
    }
  ]);
};
```

---

## Key Points

- Ask user confirmation before escalation
- Avoid unnecessary support requests
- Keep flow simple (prototype stage)
- Frontend controls the interaction
- Backend only signals `fallback_used`

---

## Presentation Slide Summary

| Step | Action |
|------|--------|
| 1 | Backend returns `fallback_used = true` |
| 2 | Frontend shows: "Do you need help from a support agent?" |
| 3 | User clicks **Yes** → Show support contact |
| 4 | User clicks **No** → Allow re-asking |

> **Design Principle:** The chatbot asks before escalating. No automatic support tickets. Frontend handles the user interaction; backend only signals when fallback was used.
