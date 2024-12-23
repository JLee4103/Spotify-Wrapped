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
            alert('Slideshow deleted successfully.');
            // Refresh the page after successful deletion
            window.location.reload();
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

function shareToCommunity(button) {
    const slideshowId = button.getAttribute('data-slideshow-id');
    
    fetch(`/spotifyWrapped/share-to-community/${slideshowId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Successfully shared to community!');
            button.disabled = true;
            button.textContent = 'Shared';
        } else {
            alert('Error sharing slideshow: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to share slideshow');
    });
}


document.addEventListener('DOMContentLoaded', () => {
    // Add click handler for wrap cards
    document.querySelectorAll('.wrap-card').forEach(card => {
        card.addEventListener('click', function(e) {
            // Don't trigger if clicking a button or sharing elements
            if (e.target.closest('button') || 
                e.target.closest('.share-button') || 
                e.target.closest('.delete-button')) {
                return;
            }
            
            const period = this.querySelector('h3').textContent.split(' - ')[1];
            if (period) {
                window.location.href = `/spotifyWrapped/slideshow/?period=${encodeURIComponent(period)}`;
            }
        });
    });

    // Add hover styles to your CSS
    const style = document.createElement('style');
    style.textContent = `
        .wrap-card {
            cursor: pointer;
            transition: transform 0.2s ease;
        }
        .wrap-card:hover {
            transform: scale(1.02);
        }
    `;
    document.head.appendChild(style);
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

function shareOnSocialMedia(uniqueId) {
    const baseUrl = window.location.origin; // Get base URL
    const shareUrl = `${baseUrl}/spotifyWrapped/shared-slideshow/${uniqueId}/`;

    // Open a modal or use navigator.share for sharing
    if (navigator.share) {
        navigator.share({
            title: 'Check out my Spotify Wrapped!',
            text: 'Here are my Spotify Wrapped stats!',
            url: shareUrl,
        }).then(() => {
            console.log('Thanks for sharing!');
        }).catch(err => {
            console.error('Error sharing:', err);
        });
    } else {
        // Fallback: Copy the URL and alert
        navigator.clipboard.writeText(shareUrl).then(() => {
            alert('Link copied to clipboard! Share it on your favorite platform.');
        }).catch(err => {
            console.error('Error copying link:', err);
            alert('Failed to copy link. Please try again.');
        });
    }
}

function generateImageFromSlideshow(uniqueId) {
    const slideshowElement = document.querySelector(`[data-slideshow-id="${uniqueId}"]`);

    if (slideshowElement) {
        html2canvas(slideshowElement).then(canvas => {
            const image = canvas.toDataURL('image/png');
            
            // Open the image in a new tab or allow downloading
            const link = document.createElement('a');
            link.download = 'spotify-wrapped.png';
            link.href = image;
            link.click();
        }).catch(err => {
            console.error('Error generating image:', err);
            alert('Failed to generate image. Please try again.');
        });
    }
}
function openModal() {
    const modal = document.getElementById('shareModal');
    modal.style.display = 'flex';
}

function closeModal() {
    const modal = document.getElementById('shareModal');
    modal.style.display = 'none';
}
