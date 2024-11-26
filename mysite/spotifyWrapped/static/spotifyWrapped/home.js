document.addEventListener('DOMContentLoaded', () => {
    const themeToggleButton = document.getElementById('toggleDarkMode');

    // Define the available themes
    const themes = ['light', 'dark', 'vibrant'];
    let currentThemeIndex = themes.indexOf(localStorage.getItem('theme')) || 0;

    // Function to apply a theme
    const applyTheme = (theme) => {
        const body = document.body;
        body.classList.remove(...themes); // Remove all theme classes
        body.classList.add(theme); // Add the selected theme class
        localStorage.setItem('theme', theme); // Save the selected theme
    };

    // Apply saved theme preference on load
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);

    // Handle theme toggle
    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', () => {
            currentThemeIndex = (currentThemeIndex + 1) % themes.length; // Cycle through themes
            applyTheme(themes[currentThemeIndex]);
        });
    }

    // Open the selection modal
    if (addCard) {
        addCard.addEventListener('click', () => {
            selectionModal.style.display = 'flex';
            selectionModal.setAttribute('aria-hidden', 'false');
        });
    }

    // Close the selection modal
    function closeSelectionModal() {
        selectionModal.style.display = 'none';
        selectionModal.setAttribute('aria-hidden', 'true');
    }

    // Start wrapped slideshow
    function startWrapped(period) {
        closeSelectionModal();
        const slideshowUrl = `/spotifyWrapped/slideshow?period=${encodeURIComponent(period)}`;
        window.location.href = slideshowUrl;
    }

    // Event listener for the close button
    const closeButton = selectionModal?.querySelector('.close-button');
    if (closeButton) {
        closeButton.addEventListener('click', closeSelectionModal);
    }

    // Event listener for the "Escape" key to close the modal
    document.addEventListener('keydown', (event) => {
        if (event.key === "Escape") {
            closeSelectionModal();
        }
    });

    // Expose necessary functions
    window.closeSelectionModal = closeSelectionModal;
    window.startWrapped = startWrapped;
});
