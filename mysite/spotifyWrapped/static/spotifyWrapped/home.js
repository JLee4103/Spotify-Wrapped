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

    // Open the selection modal when the add card is clicked
    addCard.addEventListener('click', () => {
        selectionModal.style.display = 'flex';
    });

    // Close the selection modal
    window.closeSelectionModal = function() {
        selectionModal.style.display = 'none';
    };

    // When a time period is selected, navigate to the slideshow view with the selected period
    window.startWrapped = function(period) {
        closeSelectionModal();
        const slideshowUrl = `/spotifyWrapped/slideshow?period=${encodeURIComponent(period)}`;
        window.location.href = slideshowUrl;
    };

    // Event listener for the close button
    document.querySelector('.close-button').addEventListener('click', () => {
        selectionModal.style.display = 'none';
    });

    // Event listener for the "Escape" key to close the modal
    document.addEventListener('keydown', function(event) {
        if (event.key === "Escape") {
            selectionModal.style.display = 'none';
        }
    });
});
