# GetMee WordPress Integration - Setup & Documentation

## Overview

This folder contains a complete WordPress/HTML website integration demonstrating how to embed the GetMee AI Chatbot into a website. This is a sample single-page WordPress-like site built with HTML, CSS, and vanilla JavaScript for testing the chatbot embedding.

## 📁 Folder Structure

```
wordpress/
├── index.html                 # Main homepage with hero section and features
├── about.html                 # About GetMee page
├── contact.html              # Contact page with form
├── features.html             # Features showcase page
├── getmee-chatbot.js         # Embedded chatbot widget (compiled)
├── css/
│   └── style.css            # Main stylesheet
└── README.md                 # This file
```

## 🚀 Getting Started

### Option 1: Direct File Access (Easiest)
Simply open `index.html` in a browser. The site will work locally without any server setup.

```bash
# On Windows
start index.html

# On macOS
open index.html

# On Linux
xdg-open index.html
```

### Option 2: Local Server (Recommended for Testing)
For better performance and to avoid CORS issues, run a local server:

```bash
# Using Python 3
python -m http.server 8000

# Using Node.js (http-server)
npx http-server

# Using PHP
php -S localhost:8000
```

Then access: `http://localhost:8000`

## 📱 Pages Included

1. **index.html** - Homepage
   - Hero section with CTA buttons
   - Features showcase
   - Use cases
   - Widget demo section
   - Embedded chatbot (floating)

2. **about.html** - About Page
   - Company story and mission
   - Core values
   - Statistics
   - Team section
   - Call-to-action

3. **contact.html** - Contact Page
   - Contact form
   - Contact information
   - FAQ section
   - Quick links

4. **features.html** - Features Page
   - Core features grid
   - Advanced features with details
   - Integration examples
   - Performance metrics

## 🤖 Chatbot Widget Configuration

The chatbot is embedded on every page using the `getmee-chatbot.js` script. You can configure it in two ways:

### Configuration via Window Object

In the HTML `<head>` or before the script tag:

```html
<script>
  window.ChatWidgetConfig = {
    mode: 'floating',              // 'floating' or 'inline'
    position: 'bottom-right',      // 'bottom-right' or 'bottom-left'
    chatUrl: 'http://localhost:8080/'  // URL of the chatbot app
  };
</script>
<script src="getmee-chatbot.js"></script>
```

### Configuration via Script Attributes

```html
<script 
  src="getmee-chatbot.js"
  data-mode="floating"
  data-position="bottom-right"
  data-chat-url="http://localhost:8080/">
</script>
```

### Configuration Options

| Option | Values | Description |
|--------|--------|-------------|
| `mode` | `floating`, `inline` | Floating button or embedded in page |
| `position` | `bottom-right`, `bottom-left` | Position for floating mode |
| `chatUrl` | URL string | Where the chatbot app is hosted |
| `targetId` | Element ID | Required for inline mode |

### Inline Mode Example

For inline embedding in a specific container:

```html
<div id="chat-container" style="width: 100%; height: 600px;"></div>

<script>
  window.ChatWidgetConfig = {
    mode: 'inline',
    targetId: 'chat-container',
    chatUrl: 'http://localhost:8080/'
  };
</script>
<script src="getmee-chatbot.js"></script>
```

## 🎨 Styling & UI Components

The website uses a modern, responsive design with:

- **Colors**: Teal primary (#2a9d8f), Orange accent (#e76f51)
- **Responsive grid layouts**: Mobile-friendly design
- **Feature cards**: Showcasing key capabilities
- **Hero sections**: Eye-catching CTAs
- **Footer**: Standard website footer with links

### CSS Custom Properties

```css
--primary-color: #2a9d8f;
--secondary-color: #e76f51;
--accent-color: #f4a261;
--light-bg: #f5f5f5;
--dark-text: #264653;
--border-color: #e2e8f0;
```

## 🔧 Customization

### Adding Your Own Pages

1. Copy an existing HTML file (e.g., `about.html`)
2. Update the content
3. Keep the header/footer navigation consistent
4. Include the chatbot script at the end

### Modifying Colors

Edit `css/style.css` and change the CSS custom properties:

```css
:root {
  --primary-color: #YOUR_COLOR;
  --secondary-color: #YOUR_COLOR;
  /* ... */
}
```

### Changing Chatbot URL

Update the `data-chat-url` in all HTML files:

```html
<script>
  window.ChatWidgetConfig = {
    chatUrl: 'https://your-chatbot-url.com/'
  };
</script>
```

## 🧪 Testing the Integration

### Test Floating Mode
- Open any page
- Click the floating button in the bottom-right corner
- Verify the chat widget opens/closes

### Test Inline Mode
1. Create a test HTML file:
```html
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
  <h1>Inline Chatbot Test</h1>
  <div id="chat" style="width: 400px; height: 500px; border: 1px solid #ccc;"></div>
  
  <script>
    window.ChatWidgetConfig = {
      mode: 'inline',
      targetId: 'chat',
      chatUrl: 'http://localhost:8080/'
    };
  </script>
  <script src="getmee-chatbot.js"></script>
</body>
</html>
```

### Verify Bot Responses
- Test with various questions
- Check multilingual support
- Verify email escalation feature
- Test feedback collection

## 📊 Performance Considerations

- **Bundle Size**: `getmee-chatbot.js` is ~3KB gzipped
- **Load Time**: Minimal impact on page load time
- **Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge)
- **Mobile**: Fully responsive design

## 🔒 Security Notes

- The widget runs in an iframe for isolation
- Communication is handled via postMessage API
- No sensitive data stored in localStorage
- CSRF protection through same-origin policy

## 🚢 Deployment

### Deploy to a Web Server

1. Copy all files to your web server
2. Update the `chatUrl` to point to your production chatbot URL
3. Ensure proper CORS headers are configured
4. Set up SSL/HTTPS for production

### WordPress Plugin Integration

To use this in WordPress:

1. Upload files to `wp-content/plugins/getmee-chatbot/`
2. Create a PHP file to enqueue scripts:

```php
<?php
function enqueue_getmee_chatbot() {
    wp_enqueue_script('getmee-chatbot', plugin_dir_url(__FILE__) . 'getmee-chatbot.js');
}
add_action('wp_enqueue_scripts', 'enqueue_getmee_chatbot');
?>
```

### Static Site Hosting

Deploy to any static hosting:
- GitHub Pages
- Netlify
- Vercel
- AWS S3 + CloudFront
- Google Cloud Storage

## 📚 Additional Resources

- **Chatbot App**: http://localhost:8080/
- **Backend API**: http://localhost:8001/
- **Swagger Docs**: http://localhost:8001/docs

## 🐛 Troubleshooting

### Chatbot Not Appearing
- Check console for errors (F12 → Console)
- Verify `chatUrl` is correct
- Ensure chatbot server is running

### Iframe Cross-Origin Issues
- Verify CORS headers are set correctly
- Check browser console for CORS errors
- Use HTTPS on production

### Styling Issues
- Clear browser cache (Ctrl+Shift+R)
- Check CSS file path
- Verify media queries for responsive design

## 📞 Support

For issues or questions:
- Check the FAQ section on `contact.html`
- Review the features page for capabilities
- Contact support at support@getmee.io

## 📝 Notes

- This is a **sample WordPress site** for testing/demonstration
- The original React chatbot code inside `frontend/` remains unchanged
- All WordPress-related files are contained in this folder
- The chatbot widget is completely separate from React and pure vanilla JavaScript

---

**Last Updated**: April 15, 2026
**Version**: 1.0
**Status**: Ready for Testing
