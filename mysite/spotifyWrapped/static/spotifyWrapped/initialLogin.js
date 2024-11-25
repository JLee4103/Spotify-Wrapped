function redirectToSpotify() {
        window.location.href = "{% url 'spotifyWrapped:spotify_login' %}";
    }
// Open the modal
function openTranslateModal() {
    document.getElementById("translateModal").style.display = "block";
}

// Close the modal
function closeTranslateModal() {
    document.getElementById("translateModal").style.display = "none";
}

// Google Translate
function googleTranslateElementInit() {
    new google.translate.TranslateElement({pageLanguage: 'en'}, 'google_translate_element');
}


//Audio player
const audio = document.getElementById("audioPlayer");
  function playAudio() {
    audio.play().catch(error => {
      console.error("Playback error:", error);
    });
  }

//Volume Slider
document.addEventListener("DOMContentLoaded", () => {
    const audioPlayer = document.getElementById("audioPlayer");
    const volumeControl = document.getElementById("volumeControl");

    // Set initial volume
    audioPlayer.volume = volumeControl.value;

    // Update volume when the slider changes
    volumeControl.addEventListener("input", () => {
        audioPlayer.volume = volumeControl.value;
    });
});

//Play Pause Button
const playPauseBtn = document.getElementById("playPauseBtn");

// Add event listener for play/pause button
playPauseBtn.addEventListener('click', function() {
    if (audio.paused) {
        audio.play(); // Play the audio
        playPauseBtn.textContent = 'Pause'; // Change button text to 'Pause'
    } else {
        audio.pause(); // Pause the audio
        playPauseBtn.textContent = 'Play'; // Change button text to 'Play'
    }
});

const byd = document.getElementById("byd");
byd.background
