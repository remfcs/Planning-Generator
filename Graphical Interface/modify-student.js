function showForm() {
    const addStudentForm = document.getElementById('addStudentForm');
    const deleteStudentForm = document.getElementById('deleteStudentForm');
    const changeStudentClassForm = document.getElementById('changeStudentClassForm');
    const changeTeacherTimeSlotForm = document.getElementById('changeTeacherTimeSlotForm');

    addStudentForm.classList.add('hidden');
    deleteStudentForm.classList.add('hidden');
    changeStudentClassForm.classList.add('hidden');
    changeTeacherTimeSlotForm.classList.add('hidden');

    if (document.getElementById('addStudent').checked) {
        addStudentForm.classList.remove('hidden');
    } else if (document.getElementById('deleteStudent').checked) {
        deleteStudentForm.classList.remove('hidden');
    } else if (document.getElementById('changeStudentClass').checked) {
        changeStudentClassForm.classList.remove('hidden');
    } else if (document.getElementById('changeTeacher').checked) {
        changeTeacherTimeSlotForm.classList.remove('hidden');
    }
}

function sendData(url, data) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Operation successful');
        } else {
            alert('Operation failed');
        }
    });
}

function addStudent() {
    const data = {
        name: document.querySelector('#addStudentForm input[placeholder="Name"]').value,
        first_name: document.querySelector('#addStudentForm input[placeholder="First name"]').value,
        promo: document.querySelector('#addStudentForm select').value,
        email: document.querySelector('#addStudentForm input[placeholder="@epfedu.fr"]').value,
        english_level: document.querySelector('#addStudentForm input[placeholder="English level /10"]').value,
        lv2: document.querySelector('#addStudentForm select').value,
        lv2_level: document.querySelector('#addStudentForm input[placeholder="LV2 level /10"]').value,
        reduced_exam: document.querySelector('#addStudentForm input[type="checkbox"]').checked
    };
    sendData('/add_student', data);
}

function deleteStudent() {
    const data = {
        name: document.querySelector('#deleteStudentForm input[placeholder="Search student by name"]').value
    };
    sendData('/delete_student', data);
}

function changeStudentClass() {
    const data = {
        name: document.querySelector('#changeStudentClassForm input[placeholder="Student name"]').value,
        new_class: document.querySelector('#changeStudentClassForm select').value
    };
    sendData('/change_student_class', data);
}

function changeTeacherTimeSlot() {
    const data = {
        name: document.querySelector('#changeTeacherTimeSlotForm input[placeholder="Teacher name"]').value,
        new_time_slot: document.querySelector('#changeTeacherTimeSlotForm input[placeholder="New time slot"]').value
    };
    sendData('/change_teacher_time_slot', data);
}

window.onload = showForm;
document.querySelectorAll('input[name="modifyOption"]').forEach(el => {
    el.addEventListener('change', showForm);
});
