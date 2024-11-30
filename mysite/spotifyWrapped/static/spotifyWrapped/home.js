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

function deleteSlideshow(button) {
    if (!confirm('Are you sure you want to delete this slideshow?')) {
        return;
    }

    const slideshowId = button.getAttribute('data-slideshow-id');
    const card = button.closest('.wrap-card');

    fetch(`/spotifyWrapped/delete-slideshow/${slideshowId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            card.remove();
            updateWrapCount();
            alert('Slideshow deleted successfully');
        } else {
            alert('Error deleting slideshow: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to delete slideshow: ' + error.message);
    });
}

function updateWrapCount() {
    const wrapCount = document.getElementById('wrapCount');
    if (wrapCount) {
        const currentWraps = document.querySelectorAll('.wrap-card').length;
        wrapCount.textContent = currentWraps;
        
        if (currentWraps === 0) {
            const gridContainer = document.getElementById('gridContainer');
            const progressTracker = document.createElement('div');
            progressTracker.className = 'progress-tracker';
            progressTracker.innerHTML = '<p>You\'ve created <span id="wrapCount">0</span> Spotify Wraps!</p>';
            gridContainer.appendChild(progressTracker);
        }
    }
}


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

    const wrapCount = document.getElementById('wrapCount');
    if (wrapCount) {  // Only proceed if element exists
        const currentWraps = document.querySelectorAll('.wrap-card').length;
        wrapCount.textContent = currentWraps;
        
        if (currentWraps > 0) {
            const addCard = document.querySelector('.add-card');
            if (addCard) {
                addCard.classList.remove('pulse');
            }
        }
    }

    function startWrapped(period) {
        const feedback = document.createElement('div');
        feedback.className = 'feedback-message';
        feedback.textContent = `Generating Spotify Wrap for: ${period}`;
        document.body.appendChild(feedback);
    
        setTimeout(() => {
            // Simulate redirection
            feedback.textContent = `Redirecting to your new Spotify Wrap...`;
            setTimeout(() => window.location.href = `/spotifyWrapped/slideshow?period=${encodeURIComponent(period)}`, 1000);
        }, 2000);
    }
    

});
document.addEventListener('DOMContentLoaded', () => {
    const wrapImages = document.querySelectorAll('.wrap-cover-image');

    wrapImages.forEach((img) => {
        img.onerror = () => {
            img.style.display = 'none';
            const placeholder = document.createElement('div');
            placeholder.classList.add('no-cover-placeholder');
            placeholder.textContent = 'No Cover Available';
            img.parentNode.appendChild(placeholder);
        };
    });
});
