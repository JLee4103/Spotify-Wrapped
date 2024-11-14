const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const scoreDisplay = document.getElementById("scoreDisplay");
const playButton = document.getElementById("playButton");
const gameContainer = document.getElementById("gameContainer");
const countdownDisplay = document.createElement("div");
countdownDisplay.className = "countdown";
document.body.appendChild(countdownDisplay);

let score = 0;
let notes = [];
let gameActive = false;
let countdown = 3;

// Define the lanes/buckets for A, S, D, F
const lanes = {
    A: canvas.width * 0.1,
    S: canvas.width * 0.3,
    D: canvas.width * 0.5,
    F: canvas.width * 0.7
};
const laneWidth = 70;      // Increased width of each lane for larger notes
const noteHeight = 30;     // Increased height for larger notes
const hitBarY = canvas.height - 80;   // Y-position of the hit bar
const hitBarThickness = 20;           // Increased thickness of the hit bar
const hitTolerance = 30;              // Expanded tolerance range for hitting notes
const constantNoteSpeed = 1.5;        // Set a constant speed for all notes
const noteSpacing = 60;               // Distance between each note (in pixels)
const possibleKeys = ["A", "S", "D", "F"];

// Function to start the countdown
function startCountdown() {
    countdownDisplay.style.display = "block";
    playButton.style.display = "none"; // Hide the play button
    countdownDisplay.textContent = countdown;
    const countdownInterval = setInterval(() => {
        countdown--;
        if (countdown > 0) {
            countdownDisplay.textContent = countdown;
        } else {
            clearInterval(countdownInterval);
            countdownDisplay.style.display = "none";
            startGame();
        }
    }, 1000);
}

// Function to start the game
function startGame() {
    gameContainer.style.display = "block"; // Show the game container
    score = 0;
    notes = [];
    gameActive = true;
    updateScore();
    gameLoop();

    // Spawn notes at fixed intervals (every 2 seconds in this case)
    setInterval(createNote, 2000);  // Note creation interval set to 2 seconds
}

// Function to create a new note in a specific lane
function createNote() {
    const randomKey = possibleKeys[Math.floor(Math.random() * possibleKeys.length)];

    // Calculate the new note's y position (spawn from top, spaced by noteSpacing)
    let newY = notes.filter(note => note.key === randomKey).length * noteSpacing;

    const note = {
        x: lanes[randomKey],
        y: newY,
        speed: constantNoteSpeed,  // Use constant speed for all notes
        width: laneWidth,
        height: noteHeight,
        key: randomKey
    };
    notes.push(note);
}

// Function to update the position of each note
function updateNotes() {
    notes.forEach(note => {
        note.y += note.speed;
    });
    notes = notes.filter(note => note.y < canvas.height); // Remove notes that fall off the screen
}

// Function to draw the notes, lanes, and hit bar
function drawNotes() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw the lanes
    ctx.fillStyle = "#2f3542";
    Object.values(lanes).forEach(x => {
        ctx.fillRect(x, 0, laneWidth, canvas.height);
    });

    // Draw the hit bar at the bottom
    ctx.fillStyle = "#57606f";
    ctx.fillRect(0, hitBarY, canvas.width, hitBarThickness);

    // Draw the notes and their assigned keys
    notes.forEach(note => {
        ctx.fillStyle = "#ff4757";
        ctx.fillRect(note.x, note.y, note.width, note.height);
        ctx.fillStyle = "#fff";
        ctx.font = "18px Arial";
        ctx.fillText(note.key, note.x + 20, note.y + 20); // Display the assigned key on the note
    });
}

// Function to update and display the score
function updateScore() {
    scoreDisplay.textContent = `Score: ${score}`;
}

// Keydown event listener to hit the notes
document.addEventListener("keydown", (event) => {
    if (gameActive) {
        const keyPressed = event.key.toUpperCase();
        notes.forEach((note, index) => {
            // Check if the correct key is pressed and if the note is within the tolerance range of the hit bar
            if (keyPressed === note.key && note.y >= hitBarY - hitTolerance && note.y <= hitBarY + hitTolerance) {
                score += 10;
                updateScore();
                notes.splice(index, 1); // Remove the note if hit correctly
            }
        });
    }
});

// Function for the game loop
function gameLoop() {
    if (!gameActive) return;

    updateNotes();
    drawNotes();
    requestAnimationFrame(gameLoop);
}

// Event listener to start the countdown when "Play" button is clicked
playButton.addEventListener("click", startCountdown);
