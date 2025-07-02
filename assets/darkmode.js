// Dark mode toggle functionality
document.addEventListener('DOMContentLoaded', function() {
  // Find the dark mode toggle button
  const darkModeToggle = document.getElementById('dark-mode-toggle');
  
  if (darkModeToggle) {
    // Add click event listener
    darkModeToggle.addEventListener('click', function() {
      // Toggle dark mode class on body
      document.body.classList.toggle('dark-mode');
      
      // Update button text
      darkModeToggle.innerHTML = document.body.classList.contains('dark-mode') ? '☀️' : '🌙';
      
      // Update all charts by triggering a window resize (this will cause charts to re-render)
      window.dispatchEvent(new Event('resize'));
      
      // Store preference in local storage
      localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
    });
    
    // Check for saved preference
    const savedDarkMode = localStorage.getItem('darkMode');
    if (savedDarkMode === 'true') {
      document.body.classList.add('dark-mode');
      darkModeToggle.innerHTML = '☀️';
      // Update charts
      window.dispatchEvent(new Event('resize'));
    }
  }
});
