# WordPress Widget Implementation Guide

## Quick Start

This guide shows you how to embed the GetMee Chatbot on any WordPress site or HTML page.

## 📋 Prerequisites

- GetMee Chatbot running at `http://localhost:8080/`
- The compiled widget file: `getmee-chatbot.js`
- Basic HTML knowledge

## 🔧 Implementation Methods

### Method 1: Floating Widget (Easiest)

Add this code to the end of your HTML `<body>` tag:

```html
<script>
  window.ChatWidgetConfig = {
    mode: "floating",
    position: "bottom-right",
    chatUrl: "http://localhost:8080/",
  };
</script>
<script src="path/to/getmee-chatbot.js"></script>
```

**Result**: A floating chat button appears in the bottom-right corner.

### Method 2: Inline Widget

Add a container anywhere in your page:

```html
<div id="getmee-widget" style="width: 100%; height: 600px;"></div>

<script>
  window.ChatWidgetConfig = {
    mode: "inline",
    targetId: "getmee-widget",
    chatUrl: "http://localhost:8080/",
  };
</script>
<script src="path/to/getmee-chatbot.js"></script>
```

**Result**: Chat widget embedded directly in the page at the specified location.

### Method 3: WordPress Plugin

For WordPress sites, create a plugin:

```php
<?php
/**
 * Plugin Name: GetMee Chatbot
 * Description: Embed GetMee AI Chatbot on your WordPress site
 * Version: 1.0
 */

// Add admin settings page
add_action('admin_menu', function() {
    add_options_page(
        'GetMee Settings',
        'GetMee Chatbot',
        'manage_options',
        'getmee-settings',
        'render_getmee_settings'
    );
});

function render_getmee_settings() {
    $chat_url = get_option('getmee_chat_url', 'http://localhost:8080/');
    $position = get_option('getmee_position', 'bottom-right');

    ?>
    <div class="wrap">
        <h1>GetMee Chatbot Settings</h1>
        <form method="post" action="options.php">
            <?php settings_fields('getmee-settings'); ?>

            <table class="form-table">
                <tr>
                    <th scope="row"><label for="chat_url">Chat URL</label></th>
                    <td>
                        <input type="url" id="chat_url" name="getmee_chat_url"
                               value="<?php echo esc_url($chat_url); ?>"
                               class="regular-text">
                    </td>
                </tr>
                <tr>
                    <th scope="row"><label for="position">Position</label></th>
                    <td>
                        <select id="position" name="getmee_position">
                            <option value="bottom-right" <?php selected($position, 'bottom-right'); ?>>Bottom Right</option>
                            <option value="bottom-left" <?php selected($position, 'bottom-left'); ?>>Bottom Left</option>
                        </select>
                    </td>
                </tr>
            </table>

            <?php submit_button(); ?>
        </form>
    </div>
    <?php
}

// Register settings
add_action('admin_init', function() {
    register_setting('getmee-settings', 'getmee_chat_url');
    register_setting('getmee-settings', 'getmee_position');
});

// Enqueue widget on frontend
add_action('wp_footer', function() {
    $chat_url = get_option('getmee_chat_url', 'http://localhost:8080/');
    $position = get_option('getmee_position', 'bottom-right');
    ?>
    <script>
        window.ChatWidgetConfig = {
            mode: 'floating',
            position: '<?php echo esc_js($position); ?>',
            chatUrl: '<?php echo esc_url($chat_url); ?>'
        };
    </script>
    <script src="<?php echo plugin_dir_url(__FILE__); ?>getmee-chatbot.js"></script>
    <?php
});
?>
```

### Method 4: Via Theme Customizer

Add to your theme's `functions.php`:

```php
function getmee_customize_register($wp_customize) {
    $wp_customize->add_section('getmee_section', array(
        'title' => 'GetMee Chatbot',
        'priority' => 30,
    ));

    $wp_customize->add_setting('getmee_url', array(
        'default' => 'http://localhost:8080/',
    ));

    $wp_customize->add_control('getmee_url', array(
        'label' => 'Chat URL',
        'section' => 'getmee_section',
        'type' => 'url',
    ));
}
add_action('customize_register', 'getmee_customize_register');

// Enqueue in footer
add_action('wp_footer', function() {
    $chat_url = get_theme_mod('getmee_url', 'http://localhost:8080/');
    ?>
    <script>
        window.ChatWidgetConfig = { chatUrl: '<?php echo esc_url($chat_url); ?>' };
    </script>
    <script src="<?php echo get_theme_file_uri('/js/getmee-chatbot.js'); ?>"></script>
    <?php
});
```

## 🎯 Configuration Reference

### Floating Mode

```javascript
window.ChatWidgetConfig = {
  mode: "floating", // Show floating button
  position: "bottom-right", // or 'bottom-left'
  chatUrl: "https://chat.yoursite.com/",
};
```

**Features:**

- Floating chat button
- Click to open/close panel
- Mobile responsive
- Non-intrusive

### Inline Mode

```javascript
window.ChatWidgetConfig = {
  mode: "inline", // Embed directly
  targetId: "chat-container", // HTML element ID
  chatUrl: "https://chat.yoursite.com/",
};
```

**Requirements:**

- Target element must exist
- Must have width and height
- Container CSS: `position: relative; overflow: hidden;`

## 🎨 Styling the Widget

### Override Button Styles

Create CSS after the widget script:

```css
#getmee-chat-fab {
  background-color: #your-color !important;
  width: 70px !important;
  height: 70px !important;
}
```

### Custom Panel Styles

```css
#getmee-chat-panel {
  border-radius: 24px !important;
  width: 450px !important;
  height: 650px !important;
  box-shadow: 0 10px 50px rgba(0, 0, 0, 0.2) !important;
}
```

## 🔌 JavaScript API

### Initialize Programmatically

```javascript
// Initialize with config
GetMeeChat.init({
  mode: "floating",
  position: "bottom-right",
  chatUrl: "http://localhost:8080/",
});

// Or re-initialize with new config
GetMeeChat.init({
  chatUrl: "https://new-url.com/",
});
```

### Listen to Events

```javascript
// Detect when widget loads
window.addEventListener("message", (event) => {
  if (event.data?.type === "getmee-ready") {
    console.log("Chat widget is ready!");
  }
});
```

## 🧪 Testing Checklist

- [ ] Widget appears on page
- [ ] Floating button works (if floating mode)
- [ ] Click to open/close works
- [ ] Chat messages send/receive
- [ ] Multiple language switching works
- [ ] Email escalation works
- [ ] Feedback rating works
- [ ] Mobile responsive
- [ ] No console errors
- [ ] CORS headers correct

## 🐛 Common Issues

### Widget Not Appearing

**Check:**

1. Correct `chatUrl` pointing to running app
2. Script loaded after DOM ready
3. No console errors
4. Chatbot app is running (`http://localhost:8080`)

### Communication Not Working

**Check:**

1. CORS headers set correctly
2. Same protocol (HTTP/HTTPS)
3. No firewall blocking requests
4. Network tab shows requests

### Mobile Issues

**Check:**

1. Viewport meta tag present
2. Responsive CSS working
3. Touch events supported
4. Full-screen on mobile

## 🚀 Production Deployment

1. **Update Chat URL**

   ```javascript
   chatUrl: "https://your-production-url.com/";
   ```

2. **Enable CORS**

   ```python
   CORS_ALLOWED_ORIGINS = [
       "https://yoursite.com",
       "https://www.yoursite.com",
   ]
   ```

3. **Use HTTPS**
   - All URLs must use HTTPS
   - Certificates must be valid

4. **Monitor Performance**
   - Check Network tab
   - Verify response times
   - Monitor errors

## 📞 Support

For issues:

1. Check browser console (F12)
2. Verify all configuration
3. Test with simple HTML page first
4. Check network requests
5. Contact support@getmee.io

---

**Version**: 1.0  
**Last Updated**: April 15, 2026
