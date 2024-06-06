let formData = new FormData();

document.addEventListener('DOMContentLoaded', () => {
    setupUploadArea('students-upload-area', 'students-file', 'students-uploaded-files');
    setupUploadArea('level-upload-area', 'level-file', 'level-uploaded-files');
    document.getElementById('create-planning-btn').addEventListener('click', uploadAllFiles);
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
        handleFiles(files, uploadedFiles, fileInput);  // **Modifié**
    });

    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', () => {
        const files = fileInput.files;
        handleFiles(files, uploadedFiles, fileInput);  // **Modifié**
    });
}

function handleFiles(files, uploadedFiles, fileInput) {
    Array.from(files).forEach(file => {
        const fileElement = document.createElement('div');
        fileElement.classList.add('uploaded-file');
        fileElement.textContent = file.name;

        const deleteButton = document.createElement('button');
        deleteButton.textContent = 'Delete';
        deleteButton.classList.add('btn', 'cancel-btn');
        deleteButton.addEventListener('click', () => {
            fileElement.remove();
            removeFileFromFormData(file, fileInput.name);  // **Modifié**
        });

        fileElement.appendChild(deleteButton);
        uploadedFiles.appendChild(fileElement);

        addFileToFormData(file, fileInput.name);  // **Modifié**
    });
}

function addFileToFormData(file, inputName) {
    formData.append(inputName, file);  // **Ajouté**
    console.log(`Ajouté ${file.name} à FormData sous la clé ${inputName}`);  // **Ajouté**
}

function removeFileFromFormData(file, inputName) {
    const newFormData = new FormData();
    formData.forEach((value, key) => {
        if (!(key === inputName && value.name === file.name)) {
            newFormData.append(key, value);
        }
    });
    formData = newFormData;
    console.log(`Supprimé ${file.name} de FormData sous la clé ${inputName}`);  // **Ajouté**
}

function uploadAllFiles(event) {
    event.preventDefault();

    // **Ajout des autres champs de formulaire à formData**
    const estimateNumberStudent = document.getElementById('estimate_number_student').value;
    const halfdaySlot = document.getElementById('halfday_slot').value;
    formData.append('estimate_number_student', estimateNumberStudent);
    formData.append('halfday_slot', halfdaySlot);

    console.log('FormData avant l\'envoi:');
    formData.forEach((value, key) => {
        console.log(key, value.name);
    });

    fetch('/submit', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        formData = new FormData(); // Réinitialiser formData après l'envoi
    })
    .catch(error => {
        console.error('Error:', error);
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
