/**
 * LabMan Theme Switcher
 * Handles light/dark theme switching with localStorage persistence
 */

(function () {
    'use strict';

    const THEME_KEY = 'labman-theme';
    const THEME_LIGHT = 'light';
    const THEME_DARK = 'dark';

    /**
     * Get the current theme from localStorage or system preference
     */
    function getCurrentTheme() {
        // Check localStorage first
        const savedTheme = localStorage.getItem(THEME_KEY);
        if (savedTheme) {
            return savedTheme;
        }

        // Check system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return THEME_DARK;
        }

        return THEME_LIGHT;
    }

    /**
     * Apply theme to the document
     */
    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem(THEME_KEY, theme);

        // Update theme toggle button icon if it exists
        updateThemeToggleIcon(theme);
    }

    /**
     * Toggle between light and dark themes
     */
    function toggleTheme() {
        const currentTheme = getCurrentTheme();
        const newTheme = currentTheme === THEME_LIGHT ? THEME_DARK : THEME_LIGHT;
        applyTheme(newTheme);
    }

    /**
     * Update the theme toggle button icon
     */
    function updateThemeToggleIcon(theme) {
        const toggleBtn = document.getElementById('theme-toggle');
        if (!toggleBtn) return;

        const icon = toggleBtn.querySelector('.theme-icon');
        if (!icon) return;

        if (theme === THEME_DARK) {
            icon.textContent = '☀️';
            toggleBtn.setAttribute('aria-label', 'Switch to light mode');
            toggleBtn.setAttribute('title', 'Switch to light mode');
        } else {
            icon.textContent = '🌙';
            toggleBtn.setAttribute('aria-label', 'Switch to dark mode');
            toggleBtn.setAttribute('title', 'Switch to dark mode');
        }
    }

    /**
     * Initialize theme on page load
     */
    function initTheme() {
        const theme = getCurrentTheme();
        applyTheme(theme);
    }

    /**
     * Setup theme toggle button event listener
     */
    function setupThemeToggle() {
        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', toggleTheme);
        }
    }

    /**
     * Listen for system theme changes
     */
    function setupSystemThemeListener() {
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

            // Only apply system theme if user hasn't manually set a preference
            mediaQuery.addEventListener('change', (e) => {
                if (!localStorage.getItem(THEME_KEY)) {
                    applyTheme(e.matches ? THEME_DARK : THEME_LIGHT);
                }
            });
        }
    }

    // Initialize theme immediately (before DOM loads) to prevent flash
    initTheme();

    // Setup event listeners when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setupThemeToggle();
            setupSystemThemeListener();
        });
    } else {
        setupThemeToggle();
        setupSystemThemeListener();
    }

    // Expose toggle function globally for manual calls if needed
    window.labmanTheme = {
        toggle: toggleTheme,
        set: applyTheme,
        get: getCurrentTheme
    };
})();
