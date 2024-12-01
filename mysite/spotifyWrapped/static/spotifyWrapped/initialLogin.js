/**
 * The HTML audio player element used for audio playback.
 *
 * @type {HTMLAudioElement}
 */
const audio = document.getElementById("audioPlayer");

/**
 * Redirects the user to the Spotify login page.
 * Uses a Django URL template tag to construct the URL.
 * 
 * @returns {void}
 */
function redirectToSpotify() {
    window.location.href = "{% url 'spotifyWrapped:spotify_login' %}";
}

/**
 * Opens the translate modal by changing its display style to "block".
 * 
 * @returns {void}
 */
function openTranslateModal() {
    document.getElementById("translateModal").style.display = "block";
}

/**
 * Closes the translate modal by changing its display style to "none".
 * 
 * @returns {void}
 */
function closeTranslateModal() {
    document.getElementById("translateModal").style.display = "none";
}

/**
 * Initializes the Google Translate widget on the page.
 * Adds a translation dropdown at the element with ID `google_translate_element`.
 * 
 * @returns {void}
 */
function googleTranslateElementInit() {
    new google.translate.TranslateElement({ pageLanguage: 'en' }, 'google_translate_element');
}

/**
 * Plays the audio using the audio player element.
 * Logs any playback errors to the console.
 * 
 * @returns {void}
 */
function playAudio() {
    audio.play().catch(error => {
        console.error("Playback error:", error); // Log playback errors
    });
}

// Volume slider functionality
document.addEventListener("DOMContentLoaded", () => {
    const audioPlayer = document.getElementById("audioPlayer");
    const volumeControl = document.getElementById("volumeControl");

    // Set initial volume of the audio player
    audioPlayer.volume = volumeControl.value;

    /**
     * Updates the volume of the audio player when the slider value changes.
     * 
     * @returns {void}
     */
    volumeControl.addEventListener("input", () => {
        audioPlayer.volume = volumeControl.value;
    });
});

// Play/Pause button functionality
const playPauseBtn = document.getElementById("playPauseBtn");

/**
 * Toggles between playing and pausing the audio.
 * Updates the button text to reflect the current state (Play/Pause).
 * 
 * @returns {void}
 */
playPauseBtn.addEventListener('click', function () {
    if (audio.paused) {
        audio.play(); // Play the audio
        playPauseBtn.textContent = 'Pause'; // Change button text to 'Pause'
    } else {
        audio.pause(); // Pause the audio
        playPauseBtn.textContent = 'Play'; // Change button text to 'Play'
    }

});


// Access a custom element by its ID
const byd = document.getElementById("byd");

// Ensure 'byd' exists and manipulate its background property
if (byd) {
    /**
     * Example of accessing the background property of an element.
     * Modify or inspect `byd.background` here as needed.
     */
    byd.background = "exampleBackgroundValue"; // Replace with the desired value
}