document.addEventListener('DOMContentLoaded', () => {
    const addCard = document.getElementById('addCard');
    const selectionModal = document.getElementById('selectionModal');
    const toggleDarkMode = document.getElementById('toggleDarkMode');

    // Default to dark mode if no preference is saved
    if (!localStorage.getItem('darkMode') || localStorage.getItem('darkMode') === 'enabled') {
        document.body.classList.add('dark-mode');
    }

    addCard.addEventListener('click', () => {
        selectionModal.style.display = 'flex';
    });

    window.closeSelectionModal = function() {
        selectionModal.style.display = 'none';
    };

    toggleDarkMode.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        
        // Save preference to localStorage
        if (document.body.classList.contains('dark-mode')) {
            localStorage.setItem('darkMode', 'enabled');
        } else {
            localStorage.setItem('darkMode', 'disabled');
        }
    });

    // When a time period is selected, navigate to the slideshow view with the selected period
    window.startWrapped = function(period) {
        closeSelectionModal();  // Close the modal when a period is selected

        // Redirect to the slideshow view, passing the selected period as a query parameter
        const slideshowUrl = `/slideshow?period=${encodeURIComponent(period)}`;
        window.location.href = slideshowUrl;
    };
});
