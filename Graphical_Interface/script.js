document.addEventListener('DOMContentLoaded', function () {
    const filterForm = document.getElementById('filterForm');

    // Function to fetch data
    function fetchData(url) {
        return fetch(url)
            .then(response => response.json())
            .catch(error => {
                console.error(`Error fetching data from ${url}:`, error);
                return [];
            });
    }

    // Fetch initial student data
    fetchData('/students')
        .then(data => {
            console.log('Initial student data:', data);
            populateStudentTable(data);
        });

    // Fetch professors
    fetchData('/professors')
        .then(data => {
            console.log('Professors data:', data);
            const professorSelect = document.getElementById('professeur');
            professorSelect.innerHTML = '<option value="">Sélectionner Professeur</option>';
            data.forEach(prof => {
                const option = document.createElement('option');
                option.value = prof;
                option.textContent = prof;
                professorSelect.appendChild(option);
            });
        });

    // Fetch languages
    fetchData('/languages')
        .then(data => {
            console.log('Languages data:', data);
            const languageSelect = document.getElementById('langue');
            languageSelect.innerHTML = '<option value="">Sélectionner Langue</option>';
            data.forEach(lang => {
                const option = document.createElement('option');
                option.value = lang;
                option.textContent = lang;
                languageSelect.appendChild(option);
            });
        });

    // Fetch groups
    fetchData('/groups')
        .then(data => {
            console.log('Groups data:', data);
            const groupSelect = document.getElementById('group_lv1');
            groupSelect.innerHTML = '<option value="">Sélectionner Groupe LV1</option>';
            data.forEach(group => {
                const option = document.createElement('option');
                option.value = group;
                option.textContent = group;
                groupSelect.appendChild(option);
            });
        });

    // Add event listeners to filter elements
    document.getElementById('studentName').addEventListener('input', applyFilters);
    document.getElementById('niveau').addEventListener('change', applyFilters);
    document.getElementById('professeur').addEventListener('change', applyFilters);
    document.getElementById('langue').addEventListener('change', applyFilters);
    document.getElementById('group_lv1').addEventListener('change', applyFilters);

    // Function to populate the student table
    function populateStudentTable(data) {
        const studentList = document.getElementById('studentList');
        studentList.innerHTML = ''; // Clear previous data
        const table = document.createElement('table');
        table.className = 'table table-striped';

        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        const headers = ['NOM', 'Prénom', 'Email', 'Classe', 'Groupe LV1', 'Langue', 'Professeur'];

        headers.forEach(headerText => {
            const header = document.createElement('th');
            header.textContent = headerText;
            headerRow.appendChild(header);
        });

        thead.appendChild(headerRow);
        table.appendChild(thead);

        const tbody = document.createElement('tbody');
        data.forEach(student => {
            const row = document.createElement('tr');

            const lastNameCell = document.createElement('td');
            lastNameCell.textContent = student.Surname;
            row.appendChild(lastNameCell);

            const firstNameCell = document.createElement('td');
            firstNameCell.textContent = student.Name;
            row.appendChild(firstNameCell);

            const emailCell = document.createElement('td');
            emailCell.textContent = student.Email;
            row.appendChild(emailCell);

            const classCell = document.createElement('td');
            classCell.textContent = student.Class;
            row.appendChild(classCell);

            const groupLv1Cell = document.createElement('td');
            groupLv1Cell.textContent = student.GROUP_LV1;
            row.appendChild(groupLv1Cell);

            const languageCell = document.createElement('td');
            languageCell.textContent = student.Language;
            row.appendChild(languageCell);

            const teacherCell = document.createElement('td');
            teacherCell.textContent = `${student.TeacherName} ${student.TeacherSurname}`;
            row.appendChild(teacherCell);

            tbody.appendChild(row);
        });

        table.appendChild(tbody);
        studentList.appendChild(table);
    }

    // Function to apply filters
    function applyFilters() {
        const studentName = document.getElementById('studentName').value.toLowerCase();
        const niveau = document.getElementById('niveau').value;
        const professeur = document.getElementById('professeur').value;
        const langue = document.getElementById('langue').value;
        const groupLv1 = document.getElementById('group_lv1').value;

        let query = '/students?';
        if (studentName) query += `name=${studentName}&`;
        if (niveau) query += `niveau=${niveau}&`;
        if (professeur) query += `professeur=${professeur}&`;
        if (langue) query += `langue=${langue}&`;
        if (groupLv1) query += `group_lv1=${groupLv1}&`;

        fetchData(query.slice(0, -1))
            .then(data => {
                console.log('Filtered student data:', data);
                populateStudentTable(data);
            });
    }
});
