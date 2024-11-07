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

// Function to play the current song and set up the transition to the next song
function playSong(index) {
    const song = songs[index];
    const audio = song.querySelector('audio');  // Select the audio element inside the song

    // If there's no audio preview, skip to the next song
    if (!audio) {
        nextSong();
        return;
    }

    song.classList.add('active');  // Show the current song
    audio.play();  // Play the song preview

    // Stop the audio after 8 seconds
    setTimeout(() => {
        audio.pause();  // Stop the song
        nextSong();     // Go to the next song
    }, 8000); // 8000 milliseconds = 8 seconds
}

// Function to go to the next song
function nextSong() {
    // Hide the current song
    songs[currentSongIndex].classList.remove('active');

    // Increment the index to the next song
    currentSongIndex = (currentSongIndex + 1) % songs.length;

    // If the slideshow is still running, play the next song
    if (isSlideshowRunning) {
        playSong(currentSongIndex);
    }
}

// Function to pause the slideshow and reset it
function pauseSlideshow() {
    console.log("Pausing slideshow..."); // Debugging log
    isSlideshowRunning = false;
    songs[currentSongIndex].classList.remove('active');
    const audio = songs[currentSongIndex].querySelector('audio');
    if (audio) {
        audio.pause();  // Pause the audio
    }
}

// Function to toggle dark mode
const darkModeButton = document.getElementById('toggleDarkMode');
darkModeButton.addEventListener('click', function () {
    document.body.classList.toggle('dark-mode');
});

// Event listener to start the slideshow when the "Start Slideshow" button is clicked
const startButton = document.getElementById('startSlideshowButton');
if (startButton) {
    startButton.addEventListener('click', function () {
        console.log("Start slideshow button clicked"); // Debugging log
        startSlideshow();
    });
} else {
    console.log("Start slideshow button not found"); // Debugging log
}

// Event listener to pause the slideshow when the "Pause Slideshow" button is clicked
document.getElementById('pauseSlideshowButton')?.addEventListener('click', pauseSlideshow);
