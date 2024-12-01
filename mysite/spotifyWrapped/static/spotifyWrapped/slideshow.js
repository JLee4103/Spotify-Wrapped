// Select all the song elements and the 'Start Slideshow' button
const songs = document.querySelectorAll('.song'); // NodeList of all song elements in the DOM
let currentSongIndex = 0;  // Tracks the index of the currently playing song
let isSlideshowRunning = false; // Tracks whether the slideshow is running

/**
 * Starts the slideshow by playing the first song and enabling the slideshow loop.
 * Logs a message if there are no songs available.
 *
 * @returns {void}
 */
function startSlideshow() {
    console.log("Starting slideshow..."); // Debugging log

    if (songs.length === 0) {
        console.log("No songs to display."); // Debugging log
        return; // Exit the function if there are no songs
    }

    isSlideshowRunning = true; // Set slideshow state to running
    playSong(currentSongIndex); // Play the first song in the list
}

/**
 * Plays the song at the given index in the `songs` list.
 * Highlights the current song and starts its audio preview if available.
 *
 * @param {number} index - The index of the song to play.
 * @returns {void}
 */
function playSong(index) {
    const song = songs[index]; // Get the song element at the specified index
    const audio = song.querySelector('audio'); // Find the audio element inside the song

    song.classList.add('active'); // Add a CSS class to highlight the current song

    // Play the song preview if an audio element exists
    if (audio) {
        audio.play();
    }
}

/**
 * Advances the slideshow to the next song.
 * Stops the current song's audio, hides its display, and moves to the next song in the list.
 * If the slideshow is running, the next song starts automatically.
 *
 * @returns {void}
 */
function nextSong() {
    // Remove the active class from the current song
    songs[currentSongIndex].classList.remove('active');
    const currentAudio = songs[currentSongIndex].querySelector('audio');

    // Pause the current song's audio and reset it to the beginning
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0; // Reset the audio playback position
    }

    // Increment the index to the next song, looping back to the first song if necessary
    currentSongIndex = (currentSongIndex + 1) % songs.length;

    // If the slideshow is running, play the next song
    if (isSlideshowRunning) {
        playSong(currentSongIndex);
    }
}

/**
 * Pauses the slideshow and stops the current song's audio playback.
 * Removes the highlight from the current song and resets the audio to the start.
 *
 * @returns {void}
 */
function pauseSlideshow() {
    console.log("Pausing slideshow..."); // Debugging log
    isSlideshowRunning = false; // Set slideshow state to paused
    songs[currentSongIndex].classList.remove('active'); // Remove the active highlight
    const audio = songs[currentSongIndex].querySelector('audio');

    if (audio) {
        audio.pause(); // Pause the audio playback
        audio.currentTime = 0; // Reset the audio playback position
    }
}

// Event listener for toggling dark mode
const darkModeButton = document.getElementById('toggleDarkMode');
if (darkModeButton) {
    /**
     * Toggles the dark mode class on the body element when the dark mode button is clicked.
     *
     * @returns {void}
     */
    darkModeButton.addEventListener('click', function () {
        document.body.classList.toggle('dark-mode'); // Toggles the dark mode class on the body
    });
}

// Event listener for the 'Start Slideshow' button
const startButton = document.getElementById('startSlideshowButton');
if (startButton) {
    /**
     * Starts the slideshow when the start button is clicked.
     *
     * @returns {void}
     */
    startButton.addEventListener('click', function () {
        console.log("Start slideshow button clicked"); // Debugging log
        startSlideshow(); // Call the function to start the slideshow
    });
} else {
    console.log("Start slideshow button not found"); // Debugging log
}

// Event listener for the 'Pause Slideshow' button
const pauseButton = document.getElementById('pauseSlideshowButton');
if (pauseButton) {
    /**
     * Pauses the slideshow when the pause button is clicked.
     *
     * @returns {void}
     */
    pauseButton.addEventListener('click', pauseSlideshow);
}

// Event listener for clicking the slideshow container to advance to the next song
const slideshowContainer = document.querySelector(".slideshow-container");
if (slideshowContainer) {
    /**
     * Advances to the next song in the slideshow when the slideshow container is clicked.
     * Only advances if the slideshow is running.
     *
     * @returns {void}
     */
    slideshowContainer.addEventListener('click', function () {
        if (isSlideshowRunning) {
            nextSong(); // Move to the next song if the slideshow is running
        }
    });
} else {
    console.log("Slideshow container not found"); // Debugging log
}