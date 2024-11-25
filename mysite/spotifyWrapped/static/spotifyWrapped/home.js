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
    const body = document.body;

    // Remove all theme classes first
    body.classList.remove('dark-mode', 'light-mode', 'ocean-mode');

    // Get current theme from localStorage
    const currentTheme = localStorage.getItem('theme') || 'light';

    // Cycle through themes
    if (currentTheme === 'light') {
        body.classList.add('dark-mode');
        localStorage.setItem('theme', 'dark');
    } else if (currentTheme === 'dark') {
        body.classList.add('ocean-mode');
        localStorage.setItem('theme', 'ocean');
    } else {
        body.classList.add('light-mode');
        localStorage.setItem('theme', 'light');
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

function deleteSlideshow(button) {
    // Confirm deletion
    if (confirm('Are you sure you want to delete this slideshow?')) {
        const period = button.dataset.period;
        console.log('Attempting to delete period:', period); // Debug logging

        // Send the delete request to the server
        fetch("{% url 'spotifyWrapped:delete_slideshow' %}", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                period: period
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Find and remove the card from the DOM
                const card = button.closest('.wrap-card') || button.closest('.card');
                if (card) {
                    card.remove();
                    showNotification('Slideshow deleted successfully', true);
                }
            } else {
                showNotification('Error deleting slideshow: ' + (data.error || 'Unknown error'), false);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error deleting slideshow: ' + error.message, false);
        });
    }
}

// Function to show a notification on success or error
function showNotification(message, isSuccess) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${isSuccess ? 'success' : 'error'}`;
    notification.style.display = 'block';

    // Hide notification after 3 seconds
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

// Helper function to get the CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}