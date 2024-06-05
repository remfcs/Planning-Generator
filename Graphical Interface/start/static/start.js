// script.js

document.addEventListener('DOMContentLoaded', () => {
    setupUploadArea('students-upload-area', 'students-file', 'students-uploaded-files');
    setupUploadArea('level-upload-area', 'level-file', 'level-uploaded-files');
});

function setupUploadArea(uploadAreaId, fileInputId, uploadedFilesId) {
    const uploadArea = document.getElementById(uploadAreaId);
    const fileInput = document.getElementById(fileInputId);
    const uploadedFiles = document.getElementById(uploadedFilesId);

    uploadArea.addEventListener('dragover', (event) => {
        event.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (event) => {
        event.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = event.dataTransfer.files;
        handleFiles(files, uploadedFiles);
    });

    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', () => {
        const files = fileInput.files;
        handleFiles(files, uploadedFiles);
    });
}

function triggerFileInput(fileInputId) {
    const fileInput = document.getElementById(fileInputId);
    fileInput.click();
}

function handleFiles(files, uploadedFiles) {
    Array.from(files).forEach(file => {
        const fileElement = document.createElement('div');
        fileElement.classList.add('uploaded-file');
        fileElement.textContent = file.name;
        
        const deleteButton = document.createElement('button');
        deleteButton.textContent = 'Delete';
        deleteButton.classList.add('btn', 'cancel-btn');
        deleteButton.addEventListener('click', () => {
            fileElement.remove();
        });

        fileElement.appendChild(deleteButton);
        uploadedFiles.appendChild(fileElement);
    });
}

function showInfo(event) {
    const info = event.target.getAttribute('data-info');
    document.getElementById('popup-text').textContent = info;
    document.getElementById('info-popup').style.display = 'block';
}

function closePopup() {
    document.getElementById('info-popup').style.display = 'none';
}

function addTeacher() {
    // Implémentez ici la logique d'ajout d'enseignant
}

function modifyTeacher() {
    // Implémentez ici la logique de modification de l'enseignant
}

function submitEstimate() {
    // Implémentez ici la soumission de l'estimation
}

function createPlanning() {
    // Implémentez ici la création du planning
}

function cancelPlanning() {
    // Implémentez ici l'annulation de la création du planning
}
