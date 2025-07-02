// Dash clientside callback for dark mode toggle
if (!window.dash_clientside) {
    window.dash_clientside = {};
}

window.dash_clientside.dark_mode = {
    toggleDarkMode: function(n_clicks) {
        // Function to apply dark mode
        const applyDarkMode = (isDark) => {
            if (isDark) {
                document.body.classList.add('dark-mode');
            } else {
                document.body.classList.remove('dark-mode');
            }
            
            // Force charts to update with new theme
            setTimeout(() => {
                window.dispatchEvent(new Event('resize'));
            }, 100);
        };
        
        if (n_clicks) {
            // Toggle dark mode class on body
            const isDarkMode = !document.body.classList.contains('dark-mode');
            
            // Apply the dark mode
            applyDarkMode(isDarkMode);
            
            // Update button text
            const newText = isDarkMode ? '☀️' : '🌙';
            
            // Store preference in local storage
            localStorage.setItem('darkMode', isDarkMode);
            
            return newText;
        }
        
        // Initialize dark mode from localStorage on page load
        const savedDarkMode = localStorage.getItem('darkMode');
        if (savedDarkMode === 'true') {
            // Apply dark mode on page load
            setTimeout(() => {
                applyDarkMode(true);
            }, 0);
            return '☀️';
        }
        
        return '🌙';
    }
};

// Initialize dark mode on page load
document.addEventListener('DOMContentLoaded', function() {
    const savedDarkMode = localStorage.getItem('darkMode');
    if (savedDarkMode === 'true') {
        document.body.classList.add('dark-mode');
    }
});
