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
    K: canvas.width * 0.5,
    L: canvas.width * 0.7
};
const laneWidth = 70;
const noteHeight = 70;
const bucketHeight = 70;
const bucketY = canvas.height - bucketHeight - 10;
const constantNoteSpeed = 7;
const noteSpacing = 60;
const possibleKeys = ["A", "S", "K", "L"];

// Bucket colors and default/active colors
const defaultBucketColor = "#2f3542";
const activeBucketColor = "#1e90ff";
const bucketColors = {
    A: defaultBucketColor,
    S: defaultBucketColor,
    K: defaultBucketColor,
    L: defaultBucketColor
};

// Function to start the countdown
function startCountdown() {
    countdownDisplay.style.display = "block";
    playButton.style.display = "none";
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
    gameContainer.style.display = "block";
    score = 0;
    notes = [];
    gameActive = true;
    updateScore();
    gameLoop();

    setInterval(createNote, 300);
}

// Function to create a new note in a specific lane
function createNote() {
    const randomKey = possibleKeys[Math.floor(Math.random() * possibleKeys.length)];
    let newY = notes.filter(note => note.key === randomKey).length * noteSpacing - 250;

    const note = {
        x: lanes[randomKey],
        y: newY,
        speed: constantNoteSpeed,
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
    notes = notes.filter(note => note.y < canvas.height);
}

// Function to draw the notes, lanes, and buckets
function drawNotes() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw the lanes with outlines
    Object.keys(lanes).forEach(key => {
        // Draw lane background
        ctx.fillStyle = "#2f3542";
        ctx.fillRect(lanes[key], 0, laneWidth, canvas.height);

        // Draw lane outline
        ctx.strokeStyle = "#57606f";  // Outline color
        ctx.lineWidth = 2;
        ctx.strokeRect(lanes[key], 0, laneWidth, canvas.height);
    });

    // Draw each bucket with its current color
    Object.keys(lanes).forEach(key => {
        ctx.fillStyle = bucketColors[key];
        ctx.fillRect(lanes[key], bucketY, laneWidth, bucketHeight);  // Draw bucket area
    });

    // Draw the notes and their assigned, stylized keys
    notes.forEach(note => {
        // Draw the note box
        ctx.fillStyle = "#ff4757";
        ctx.fillRect(note.x, note.y, note.width, note.height);

        // Set the font style and size for the key letter
        ctx.fillStyle = "#fff";
        ctx.font = "bold 20px Arial";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";

        // Calculate the center position for the key letter within the note
        const textX = note.x + note.width / 2;
        const textY = note.y + note.height / 2;

        // Draw the key letter
        ctx.fillText(note.key, textX, textY);
    });
}

// Function to update and display the score
function updateScore() {
    scoreDisplay.textContent = `Score: ${score}`;
}

// Keydown event listener to hit the notes and change bucket color
document.addEventListener("keydown", (event) => {
    if (gameActive) {
        const keyPressed = event.key.toUpperCase();
        notes.forEach((note, index) => {
            // Check if the correct key is pressed and if the note intersects with the bucket
            if (keyPressed === note.key &&
                note.y + note.height >= bucketY &&
                note.y <= bucketY + bucketHeight &&
                note.x === lanes[keyPressed]) {
                score += 10;
                updateScore();
                notes.splice(index, 1);
            }
        });

        // Change the bucket color for the key pressed
        if (bucketColors[keyPressed] !== undefined) {  
            bucketColors[keyPressed] = activeBucketColor;
            setTimeout(() => {
                bucketColors[keyPressed] = defaultBucketColor;
            }, 200);  
        }
    }
});

// Function for the game loop
function gameLoop() {
    if (!gameActive) return;

    notes.forEach((note, index) => {
        if(note.y > bucketHeight + bucketY) {
            gameActive = false;
        }
    })

    updateNotes();
    drawNotes();
    requestAnimationFrame(gameLoop);
}

// Event listener to start the countdown when "Play" button is clicked
playButton.addEventListener("click", startCountdown);
