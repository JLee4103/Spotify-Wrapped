// Select all the song elements and the 'Start Slideshow' button
const songs = document.querySelectorAll('.song');
let currentSongIndex = 0;  // Track the index of the currently playing song
let isSlideshowRunning = false;

// Function to start the slideshow
function startSlideshow() {
    console.log("Starting slideshow..."); // Debugging log

    if (songs.length === 0) {
        console.log("No songs to display."); // Debugging log
        return;
    }

    isSlideshowRunning = true;
    playSong(currentSongIndex);
}

// Function to play the current song
function playSong(index) {
    const song = songs[index];
    const audio = song.querySelector('audio');  // Select the audio element inside the song

    song.classList.add('active');  // Show the current song

    // Play the song preview if available
    if (audio) {
        audio.play();
    }
}

// Function to go to the next song
function nextSong() {
    // Hide the current song
    songs[currentSongIndex].classList.remove('active');
    const currentAudio = songs[currentSongIndex].querySelector('audio');

    // Pause the audio if it's playing
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;  // Reset the audio to the start
    }

    // Increment the index to the next song
    currentSongIndex = (currentSongIndex + 1) % songs.length;

    // Play the next song if the slideshow is running
    if (isSlideshowRunning) {
        playSong(currentSongIndex);
    }
}

// Function to pause the slideshow
function pauseSlideshow() {
    console.log("Pausing slideshow..."); // Debugging log
    isSlideshowRunning = false;
    songs[currentSongIndex].classList.remove('active');
    const audio = songs[currentSongIndex].querySelector('audio');
    if (audio) {
        audio.pause();  // Pause the audio
        audio.currentTime = 0;  // Reset the audio to the start
    }
}

// Toggle dark mode
const darkModeButton = document.getElementById('toggleDarkMode');
darkModeButton.addEventListener('click', function () {
    document.body.classList.toggle('dark-mode');
});

// Start slideshow button event listener
const startButton = document.getElementById('startSlideshowButton');
if (startButton) {
    startButton.addEventListener('click', function () {
        console.log("Start slideshow button clicked"); // Debugging log
        startSlideshow();
    });
} else {
    console.log("Start slideshow button not found"); // Debugging log
}

// Pause slideshow button event listener
document.getElementById('pauseSlideshowButton')?.addEventListener('click', pauseSlideshow);

// Event listener to advance the slideshow on click
const slideshowContainer = document.querySelector(".slideshow-container");
slideshowContainer.addEventListener('click', function () {
    if (isSlideshowRunning) {
        nextSong();
    }
});


