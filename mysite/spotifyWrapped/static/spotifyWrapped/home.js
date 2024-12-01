/**
 * Retrieves a cookie value by its name.
 * 
 * @param {string} name - The name of the cookie to retrieve.
 * @returns {string|null} The value of the cookie if found, or null if not found.
 */
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

/**
 * Deletes a slideshow after confirmation.
 * 
 * @param {HTMLElement} button - The button element that triggered the delete action.
 * @returns {void}
 */
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
            window.location.reload(); // Refresh the page
        } else {
            alert('Error deleting slideshow: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to delete slideshow: ' + error.message);
    });
}

/**
 * Updates the wrap count displayed on the page.
 * If there are no wraps, it displays a message.
 * 
 * @returns {void}
 */
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

/**
 * Shares a slideshow to the community.
 * 
 * @param {HTMLElement} button - The button element that triggered the share action.
 * @returns {void}
 */
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

/**
 * Shares a slideshow on social media or copies a shareable link to the clipboard.
 * 
 * @param {string} uniqueId - The unique ID of the slideshow to share.
 * @returns {void}
 */
function shareOnSocialMedia(uniqueId) {
    const baseUrl = window.location.origin;
    const shareUrl = `${baseUrl}/spotifyWrapped/shared-slideshow/${uniqueId}/`;

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
        navigator.clipboard.writeText(shareUrl).then(() => {
            alert('Link copied to clipboard! Share it on your favorite platform.');
        }).catch(err => {
            console.error('Error copying link:', err);
            alert('Failed to copy link. Please try again.');
        });
    }
}

/**
 * Generates an image of a slideshow element using html2canvas.
 * 
 * @param {string} uniqueId - The unique ID of the slideshow element to capture.
 * @returns {void}
 */
function generateImageFromSlideshow(uniqueId) {
    const slideshowElement = document.querySelector(`[data-slideshow-id="${uniqueId}"]`);

    if (slideshowElement) {
        html2canvas(slideshowElement).then(canvas => {
            const image = canvas.toDataURL('image/png');

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

/**
 * Opens the share modal by setting its display to 'flex'.
 * 
 * @returns {void}
 */
function openModal() {
    const modal = document.getElementById('shareModal');
    modal.style.display = 'flex';
}

/**
 * Closes the share modal by setting its display to 'none'.
 * 
 * @returns {void}
 */
function closeModal() {
    const modal = document.getElementById('shareModal');
    modal.style.display = 'none';
}