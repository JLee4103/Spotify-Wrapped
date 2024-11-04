const addCard = document.getElementById('addCard');
const selectionModal = document.getElementById('selectionModal');

// Show the modal when the add card is clicked
addCard.addEventListener('click', () => {
    selectionModal.style.display = 'flex';
});

// Close modal function
function closeSelectionModal() {
    selectionModal.style.display = 'none';
}

// Start Spotify Wrapped based on selected time period
async function startWrapped(period) {
    closeSelectionModal();
    alert(`Generating Spotify Wrapped for ${period}`);

    try {
        const response = await fetch(`http://localhost/api/wrapped?period=${encodeURIComponent(period)}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const result = await response.json();
        console.log("Data saved", result);
    } catch (error) {
        console.error("Error saving data", error);
    }
}
