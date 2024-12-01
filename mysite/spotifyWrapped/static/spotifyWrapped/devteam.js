document.addEventListener("DOMContentLoaded", () => {
    const contactForm = document.getElementById("contactForm");

    contactForm.addEventListener("submit", (event) => {
        event.preventDefault();

        const formData = new FormData(contactForm);
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

        fetch("{% url 'spotifyWrapped:contact_dev_team' %}", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
            },
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    alert("Your message has been sent successfully!");
                    contactForm.reset(); // Clear the form
                } else {
                    alert("Failed to send message: " + data.error);
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                alert("An unexpected error occurred. Please try again.");
            });
    });
});


// Utility function to get CSRF token
function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
        const trimmed = cookie.trim();
        if (trimmed.startsWith(name + '=')) {
            return trimmed.substring(name.length + 1);
        }
    }
    return null;
}

