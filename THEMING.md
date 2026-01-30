# LabMan Theming System

This document describes the centralized theming system for LabMan, including how to use it, customize it, and extend it.

## Overview

LabMan uses a centralized CSS variable-based theming system that supports:
- **Light and Dark modes** with smooth transitions
- **Automatic theme detection** based on system preferences
- **Manual theme switching** with persistent user preferences
- **Easy customization** through CSS variables

## Quick Start

### Using the Theme Switcher

Users can toggle between light and dark themes by clicking the theme toggle button (🌙/☀️) in the navigation bar. The selected theme is automatically saved and will persist across sessions.

### System Preference Detection

If a user hasn't manually selected a theme, LabMan will automatically use their system's color scheme preference. The theme will also update automatically if the system preference changes.

## Architecture

### CSS Variables

All theme colors and styles are defined using CSS custom properties (variables) in `/labman/static/css/style.css`. The variables are organized into categories:

#### Color Categories

1. **Primary Colors** - Main brand colors
   - `--primary`, `--primary-light`, `--primary-dark`, `--primary-hover`

2. **Secondary Colors** - Accent and complementary colors
   - `--secondary`, `--accent`

3. **Action Colors** - Semantic colors for user feedback
   - Success: `--success`, `--success-light`, `--success-text`, `--success-hover`
   - Error: `--error`, `--error-light`, `--error-text`, `--error-hover`
   - Warning: `--warning`, `--warning-light`, `--warning-text`, `--warning-hover`
   - Info: `--info`, `--info-light`, `--info-text`

4. **Background Colors**
   - `--bg-primary`, `--bg-secondary`, `--bg-tertiary`, `--bg-hover`, `--bg-card`

5. **Text Colors**
   - `--text-primary`, `--text-secondary`, `--text-tertiary`, `--text-inverse`

6. **Border Colors**
   - `--border-primary`, `--border-secondary`, `--border-focus`

7. **Shadow Colors**
   - `--shadow-sm`, `--shadow-md`, `--shadow-lg`, `--shadow-xl`

8. **Component-Specific**
   - Navbar: `--navbar-bg`, `--navbar-text`, `--navbar-hover`
   - Gantt Chart: `--gantt-bg`, `--gantt-tooltip-bg`

### Theme Implementation

Themes are implemented using the `data-theme` attribute on the `<html>` element:

```css
/* Light Theme (Default) */
:root,
[data-theme="light"] {
    --primary: #8B4513;
    /* ... other variables */
}

/* Dark Theme */
[data-theme="dark"] {
    --primary: #D2691E;
    /* ... other variables */
}
```

### JavaScript Theme Switcher

The theme switcher (`/labman/static/js/theme-switcher.js`) handles:
- Theme initialization on page load
- Theme toggling via button click
- LocalStorage persistence
- System preference detection
- Automatic icon updates

## Customization Guide

### Changing Theme Colors

To customize colors for either theme:

1. Open `/labman/static/css/style.css`
2. Locate the theme section (`:root` for light, `[data-theme="dark"]` for dark)
3. Modify the desired CSS variable values
4. Save and refresh your browser

**Example:** Change the primary color in light mode:

```css
:root,
[data-theme="light"] {
    --primary: #2E7D32; /* Changed from brown to green */
    /* ... */
}
```

### Adding New CSS Variables

To add new theme variables:

1. Define the variable in both light and dark theme sections:

```css
:root,
[data-theme="light"] {
    /* ... existing variables ... */
    --my-custom-color: #FF5722;
}

[data-theme="dark"] {
    /* ... existing variables ... */
    --my-custom-color: #FF7043;
}
```

2. Use the variable in your CSS:

```css
.my-element {
    background-color: var(--my-custom-color);
}
```

### Creating a New Theme

To add a third theme (e.g., "high-contrast"):

1. Add a new theme section in `style.css`:

```css
[data-theme="high-contrast"] {
    --primary: #000000;
    --bg-primary: #FFFFFF;
    --text-primary: #000000;
    /* ... define all variables ... */
}
```

2. Update `theme-switcher.js` to include the new theme:

```javascript
const THEME_HIGH_CONTRAST = 'high-contrast';

function cycleTheme() {
    const themes = [THEME_LIGHT, THEME_DARK, THEME_HIGH_CONTRAST];
    const currentTheme = getCurrentTheme();
    const currentIndex = themes.indexOf(currentTheme);
    const nextIndex = (currentIndex + 1) % themes.length;
    applyTheme(themes[nextIndex]);
}
```

3. Update the theme toggle button to cycle through themes instead of toggling.

## Best Practices

### Using Theme Variables

✅ **DO:**
- Always use CSS variables for colors, shadows, and theme-dependent values
- Use semantic variable names (e.g., `--text-primary` instead of `--color-1`)
- Test changes in both light and dark modes

❌ **DON'T:**
- Hardcode color values in CSS (e.g., `color: #333333`)
- Use inline styles with hardcoded colors
- Forget to define variables in both themes

### Adding New Components

When creating new components:

1. Use existing CSS variables wherever possible
2. If new variables are needed, add them to both themes
3. Ensure the component looks good in both light and dark modes
4. Test the transition between themes

### Accessibility

- Maintain sufficient color contrast ratios (WCAG AA: 4.5:1 for normal text)
- Test with screen readers
- Ensure the theme toggle button has proper ARIA labels
- Don't rely solely on color to convey information

## Programmatic Theme Control

The theme switcher exposes a global API for programmatic control:

```javascript
// Get current theme
const currentTheme = window.labmanTheme.get();

// Set theme
window.labmanTheme.set('dark');

// Toggle theme
window.labmanTheme.toggle();
```

## Troubleshooting

### Theme Not Persisting

**Issue:** Theme resets to default on page reload.

**Solution:** Check browser's localStorage settings. Some privacy modes block localStorage.

### Flash of Unstyled Content (FOUC)

**Issue:** Brief flash of wrong theme on page load.

**Solution:** The theme-switcher.js is loaded in the `<head>` and initializes immediately. Ensure it's loaded before the stylesheet.

### Colors Not Updating

**Issue:** Some elements don't change color when switching themes.

**Solution:** Check if the element uses hardcoded colors instead of CSS variables. Update to use variables.

### Theme Toggle Button Not Working

**Issue:** Clicking the button doesn't change the theme.

**Solution:** 
1. Check browser console for JavaScript errors
2. Ensure `theme-switcher.js` is loaded correctly
3. Verify the button has `id="theme-toggle"`

## File Reference

### Core Files

- **CSS:** `/labman/static/css/style.css` - Theme variables and styles
- **JavaScript:** `/labman/static/js/theme-switcher.js` - Theme switching logic
- **Template:** `/labman/templates/base.html` - Theme toggle button

### Key Sections in style.css

- Lines 1-165: Theme variable definitions
- Lines 166-168: Global transition rules
- Lines 218-243: Theme toggle button styles

## Examples

### Example 1: Custom Button with Theme Support

```css
.my-button {
    background-color: var(--primary);
    color: var(--text-inverse);
    border: 1px solid var(--border-primary);
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    transition: all 0.3s ease;
}

.my-button:hover {
    background-color: var(--primary-hover);
    box-shadow: 0 4px 8px var(--shadow-md);
}
```

### Example 2: Themed Card Component

```html
<div class="card">
    <h2 style="color: var(--primary);">Card Title</h2>
    <p style="color: var(--text-secondary);">Card content goes here.</p>
</div>
```

The card will automatically adapt to the current theme because it uses CSS variables.

### Example 3: Conditional Styling Based on Theme

```javascript
// Get current theme
const theme = window.labmanTheme.get();

// Apply theme-specific logic
if (theme === 'dark') {
    // Do something specific for dark mode
    console.log('Dark mode is active');
}
```

## Contributing

When contributing to LabMan, please:

1. Use the existing CSS variables for all color-related styling
2. Test your changes in both light and dark modes
3. Add new variables to both themes if needed
4. Update this documentation if you add new theme features
5. Ensure smooth transitions between themes

## Support

For issues or questions about the theming system:

1. Check this documentation first
2. Review the troubleshooting section
3. Inspect the browser console for errors
4. Check that CSS variables are properly defined in both themes

---

**Last Updated:** 2026-01-30  
**Version:** 1.0
