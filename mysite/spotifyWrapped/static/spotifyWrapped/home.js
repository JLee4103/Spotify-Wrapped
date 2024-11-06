document.addEventListener('DOMContentLoaded', () => {
    const addCard = document.getElementById('addCard');
    const selectionModal = document.getElementById('selectionModal');
    const toggleDarkMode = document.getElementById('toggleDarkMode');

    // Default to dark mode if no preference is saved
    if (!localStorage.getItem('darkMode') || localStorage.getItem('darkMode') === 'enabled') {
        document.body.classList.add('dark-mode');
    }

    addCard.addEventListener('click', () => {
        selectionModal.style.display = 'flex';
    });

    window.closeSelectionModal = function() {
        selectionModal.style.display = 'none';
    };

    toggleDarkMode.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        
        // Save preference to localStorage
        if (document.body.classList.contains('dark-mode')) {
            localStorage.setItem('darkMode', 'enabled');
        } else {
            localStorage.setItem('darkMode', 'disabled');
        }
    });

    window.startWrapped = async function(period) {
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
    };
});


