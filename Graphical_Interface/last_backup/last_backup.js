document.getElementById('yes-btn').addEventListener('click', function() {
    document.getElementById('popup').style.display = 'block';
    document.getElementById('confirm-btn').addEventListener('click', confirmRecovery);
});

function closePopup() {
    document.getElementById('popup').style.display = 'none';
}

function confirmRecovery() {
    fetch('/restore_backup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        closePopup();
    })
    .catch(error => {
        alert('An error occurred: ' + error.message);
        closePopup();
    });
}
