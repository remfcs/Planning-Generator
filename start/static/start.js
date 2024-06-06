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
    formData.append('teachers', JSON.stringify(teachers));

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





let teachers = [];


function addTeacher() {
    event.preventDefault(); // Prevent form submission

    const name = document.getElementById('name').value.trim();
    const surname = document.getElementById('surname').value.trim();
    const email = document.getElementById('email').value.trim();
    const subject = document.getElementById('subject').value;

    const checkboxes = document.querySelectorAll('#availability-section .day-time:checked');
    const availabilities = Array.from(checkboxes).map(cb => cb.value);

    if (!name || !surname || !email) {
        alert('All fields must be filled out.');
        return;
    }
    if (!/\S+@\S+\.\S+/.test(email)) {
        alert('Please enter a valid email address.');
        return;
    }

    console.log(availabilities)

    const teacherData = {
        id: Date.now(),  // Unique ID for each teacher for tracking/modifications
        name,
        surname,
        email,
        subject,
        availabilities
    };

    console.log(teacherData)

    teachers.push(teacherData);  // Add to the local array

    // Update UI
    const li = document.createElement('li');
    li.setAttribute('id', `teacher-${teacherData.id}`);
    li.textContent = `${name} ${surname} (${email}, ${subject}, availabilities: ${availabilities}) `;
    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = 'Delete';
    deleteBtn.classList.add('btn', 'cancel-btn');
    deleteBtn.onclick = () => removeTeacher(teacherData.id);
    li.appendChild(deleteBtn);
    document.getElementById('teacher-list').appendChild(li);

    resetTeacherForm();  // Reset form fields
}

function removeTeacher(id) {
    teachers = teachers.filter(teacher => teacher.id !== id);
    document.getElementById(`teacher-${id}`).remove();
}

function resetTeacherForm() {
    // Reset all text inputs
    document.getElementById('name').value = '';
    document.getElementById('surname').value = '';
    document.getElementById('email').value = '';

    // Reset the select dropdown to its first option
    document.getElementById('subject').selectedIndex = 0;

    // Reset all checkboxes within the form
    const checkboxes = document.querySelectorAll('#teacherForm input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
}

function modifyTeacher() {
    // Implémentez ici la logique de modification de l'enseignant
}

function createPlanning() {
    // Implémentez ici la création du planning
}

function cancelPlanning() {
    // Implémentez ici l'annulation de la création du planning
}
