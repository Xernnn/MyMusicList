function openModal(element) {
    const title = element.getAttribute('data-title');
    const artist = element.getAttribute('data-artist');
    const score = element.getAttribute('data-score');
    const image = element.getAttribute('data-image');

    document.getElementById('modalTitle').textContent = title;
    document.getElementById('modalArtist').textContent = 'Artist: ' + artist;
    document.getElementById('modalScore').value = score;
    document.getElementById('modalImage').src = image;

    // Show or hide the delete button based on whether the song is reviewed
    if (score > 0) {
        document.getElementById('deleteScore').style.display = 'inline-block';
    } else {
        document.getElementById('deleteScore').style.display = 'none';
    }

    document.getElementById('songModal').style.display = 'block';
}

function closeModal() {
    document.getElementById('songModal').style.display = 'none';
}

function saveScore() {
    const newScore = document.getElementById('modalScore').value;
    const title = document.getElementById('modalTitle').textContent;

    fetch('/save_score', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            title: title,
            score: newScore
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload(); // Reload the page to move the song to Reviewed Music
        } else {
            alert('Failed to save score.');
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });

    closeModal();
}

function deleteScore() {
    console.log("Delete button clicked");  // Debugging statement to ensure the function is called

    const title = document.getElementById('modalTitle').textContent;

    console.log("Deleting score for:", title);  // Debugging log

    fetch('/delete_score', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            title: title,
        }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log("Score reset successful");  // Confirm the server responded successfully
            location.reload(); // Reload the page to move the song to Unreviewed Music
        } else {
            console.error('Failed to delete score.', data);  // Log error details
        }
    })
    .catch((error) => {
        console.error('Error during delete score:', error);  // Log any errors that occur
    });

    closeModal();
}

function showThankYouPopup() {
    const thankYouModal = document.getElementById('thankYouModal');
    thankYouModal.style.display = 'block';

    // Close the modal after 2 seconds
    const timeoutId = setTimeout(() => {
        thankYouModal.style.display = 'none';
    }, 2000);

    // Close the modal if clicked
    thankYouModal.addEventListener('click', () => {
        thankYouModal.style.display = 'none';
        clearTimeout(timeoutId);  // Clear the timeout if the modal is closed by clicking
    }, { once: true });  // The event listener is removed after the first click
}
