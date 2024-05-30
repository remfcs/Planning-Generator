document.addEventListener('DOMContentLoaded', function () {
    const filterForm = document.getElementById('filterForm');

    fetch('/students')
        .then(response => response.json())
        .then(data => {
            populateStudentTable(data);
        })
        .catch(error => console.error('Error fetching student data:', error));

    fetch('/professors')
        .then(response => response.json())
        .then(data => {
            const professorSelect = document.getElementById('professeur');
            professorSelect.innerHTML = '<option value="">Sélectionner Professeur</option>'; // Add default option
            data.forEach(prof => {
                const option = document.createElement('option');
                option.value = prof;
                option.textContent = prof;
                professorSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error fetching professors data:', error));

    fetch('/languages')
        .then(response => response.json())
        .then(data => {
            const languageSelect = document.getElementById('langue');
            languageSelect.innerHTML = '<option value="">Sélectionner Langue</option>'; // Add default option
            data.forEach(lang => {
                const option = document.createElement('option');
                option.value = lang;
                option.textContent = lang;
                languageSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error fetching languages data:', error));

    filterForm.addEventListener('submit', function (event) {
        event.preventDefault();
        applyFilters();
    });

    function populateStudentTable(data) {
        const studentList = document.getElementById('studentList');
        studentList.innerHTML = ''; // Clear existing content
        const table = document.createElement('table');
        table.className = 'table table-striped';

        // Create table header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        const headers = ['NOM', 'Prénom', 'Email', 'Classe', 'LV1', 'Groupe LV1', 'Professeur'];

        headers.forEach(headerText => {
            const header = document.createElement('th');
            header.textContent = headerText;
            headerRow.appendChild(header);
        });

        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Create table body
        const tbody = document.createElement('tbody');
        data.forEach(student => {
            const row = document.createElement('tr');

            const firstNameCell = document.createElement('td');
            firstNameCell.textContent = student.Name; // Prénom
            row.appendChild(firstNameCell);

            const lastNameCell = document.createElement('td');
            lastNameCell.textContent = student.Surname; // Nom
            row.appendChild(lastNameCell);

            const emailCell = document.createElement('td');
            emailCell.textContent = student.Email; // Email
            row.appendChild(emailCell);

            const classCell = document.createElement('td');
            classCell.textContent = student.Class; // Classe
            row.appendChild(classCell);

            const lv1Cell = document.createElement('td');
            lv1Cell.textContent = student.LV1; // LV1
            row.appendChild(lv1Cell);

            const groupLv1Cell = document.createElement('td');
            groupLv1Cell.textContent = student.GROUP_LV1; // Groupe LV1
            row.appendChild(groupLv1Cell);

            const teacherCell = document.createElement('td');
            teacherCell.textContent = student.TeacherName + ' ' + student.TeacherSurname; // Professeur
            row.appendChild(teacherCell);

            tbody.appendChild(row);
        });

        table.appendChild(tbody);
        studentList.appendChild(table);
    }

    function applyFilters() {
        const studentName = document.getElementById('studentName').value.toLowerCase();
        const niveau = document.getElementById('niveau').value;
        const professeur = document.getElementById('professeur').value;
        const langue = document.getElementById('langue').value;

        let query = '/students?';
        if (studentName) query += `name=${studentName}&`;
        if (niveau) query += `niveau=${niveau}&`;
        if (professeur) query += `professeur=${professeur}&`;
        if (langue) query += `langue=${langue}&`;

        fetch(query.slice(0, -1)) // Remove trailing '&'
            .then(response => response.json())
            .then(data => {
                populateStudentTable(data);
            })
            .catch(error => console.error('Error fetching student data:', error));
    }
});
