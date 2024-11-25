document.addEventListener('DOMContentLoaded', () => {
    const addCard = document.getElementById('addCard');
    const selectionModal = document.getElementById('selectionModal');
    const themeToggleButton = document.getElementById('toggleDarkMode');

    // Apply saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
    }

    // Handle dark mode toggle
    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', () => {
            const body = document.body;
            if (body.classList.contains('dark-mode')) {
                body.classList.remove('dark-mode');
                localStorage.setItem('theme', 'light');
            } else {
                body.classList.add('dark-mode');
                localStorage.setItem('theme', 'dark');
            }
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
