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
    fetchData('/api/professors')
        .then(data => {
            console.log('Professors data:', data);
            const professorSelect = document.getElementById('professeur');
            professorSelect.innerHTML = '<option value="">Select a Teacher</option>';
            data.forEach(prof => {
                const option = document.createElement('option');
                option.value = `${prof.name} ${prof.surname}`; // Use full name as value
                option.textContent = `${prof.name} ${prof.surname}`; // Display full name
                professorSelect.appendChild(option);
            });
        });

    // Fetch languages
    fetchData('/languages')
        .then(data => {
            console.log('Languages data:', data);
            const languageSelect = document.getElementById('langue');
            languageSelect.innerHTML = '<option value="">Select a language</option>';
            data.forEach(lang => {
                const option = document.createElement('option');
                option.value = lang;
                option.textContent = lang;
                languageSelect.appendChild(option);
            });
        });

    // Fetch all groups and store them for filtering
    let allGroups = [];
    fetchData('/groups')
        .then(data => {
            console.log('Groups data:', data);
            allGroups = data; // Store all groups
            updateGroupOptions(allGroups, '');
        });

    // Function to update group options based on selected language
    function updateGroupOptions(groups, selectedLanguage) {
        const groupSelect = document.getElementById('group_lv1');
        groupSelect.innerHTML = '<option value="">Select an LV1 Group</option>';
        groups.forEach(group => {
            if (!selectedLanguage || group.endsWith(selectedLanguage) || group.endsWith(`_${selectedLanguage}_D`)) {
                const option = document.createElement('option');
                option.value = group;
                option.textContent = group;
                groupSelect.appendChild(option);
            }
        });
    }

    // Add event listeners to filter elements
    document.getElementById('studentName').addEventListener('input', applyFilters);
    document.getElementById('niveau').addEventListener('change', applyFilters);
    document.getElementById('professeur').addEventListener('change', applyFilters);
    document.getElementById('langue').addEventListener('change', function () {
        const selectedLanguage = this.value;
        updateGroupOptions(allGroups, selectedLanguage);
        applyFilters(); // Apply filters after updating group options
    });
    document.getElementById('group_lv1').addEventListener('change', applyFilters);

    // Function to populate the student table
    function populateStudentTable(data) {
        const studentList = document.getElementById('studentList');
        studentList.innerHTML = ''; // Clear previous data
        const table = document.createElement('table');
        table.className = 'table table-striped';

        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        const headers = ['NAME', 'Firstname', 'Email', 'Class Level', 'LV1 Group', 'Language', 'Teacher'];

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
        if (professeur) query += `professeur=${encodeURIComponent(professeur)}&`;  // encodeURIComponent to handle spaces
        if (langue) query += `langue=${langue}&`;
        if (groupLv1) query += `group_lv1=${groupLv1}&`;

        fetchData(query.slice(0, -1))
            .then(data => {
                console.log('Filtered student data:', data);
                populateStudentTable(data);
            });
    }
});
