document.addEventListener('DOMContentLoaded', () => {
    const addCard = document.getElementById('addCard');
    const selectionModal = document.getElementById('selectionModal');
    const toggleDarkMode = document.getElementById('toggleDarkMode');

    // Default to dark mode if no preference is saved
    if (!localStorage.getItem('darkMode') || localStorage.getItem('darkMode') === 'enabled') {
        document.body.classList.add('dark-mode');
    }
//hi
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
        closeSelectionModal();
    
        // Ensure the correct URL with the period query string
        const slideshowUrl = `/spotifyWrapped/slideshow?period=${encodeURIComponent(period)}`;
        window.location.href = slideshowUrl;
    };
    
});

document.getElementById('toggleDarkMode').addEventListener('click', function() {
    document.body.classList.toggle('dark-mode');
    document.body.classList.toggle('light-mode');
});

// Function to open the modal
function openModal() {
    document.querySelector('.modal').style.display = 'flex';
}

// Function to close the modal
function closeModal() {
    document.querySelector('.modal').style.display = 'none';
}

// Event listener for the close button
document.querySelector('.close-button').addEventListener('click', closeModal);

// Event listener for the "Escape" key
document.addEventListener('keydown', function(event) {
    if (event.key === "Escape") {
        closeModal();
    }
});

