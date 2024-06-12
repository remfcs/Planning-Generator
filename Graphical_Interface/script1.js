document.addEventListener('DOMContentLoaded', function () {
    const filterForm = document.getElementById('filterForm');

    function fetchData(url) {
        return fetch(url)
            .then(response => response.json())
            .catch(error => {
                console.error(`Error fetching data from ${url}:`, error);
                return [];
            });
    }

    let allLanguages = [];
    let allGroups = [];
    let allProfessors = [];

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
            allProfessors = data; // Store all professors
            updateProfessorOptions(allProfessors, '', '');
        });

    // Fetch languages
    fetchData('/languages')
        .then(data => {
            console.log('Languages data:', data);
            allLanguages = data; // Store all languages
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
    fetchData('/groups')
        .then(data => {
            console.log('Groups data:', data);
            allGroups = data; // Store all groups
            updateGroupOptions(allGroups, '', ''); // Update with empty filters initially
        });

    // Function to update group options based on selected language
    function updateGroupOptions(selectedLanguage, selectedNiveau) {
        const groupSelect = document.getElementById('group_lv1');
        groupSelect.innerHTML = '<option value="">Select an LV1 Group</option>';

        let query = '/groups?';
        if (selectedLanguage) query += `language=${selectedLanguage}&`;
        if (selectedNiveau) query += `niveau=${selectedNiveau}&`;

        fetchData(query.slice(0, -1))
            .then(groups => {
                groups.forEach(group => {
                    const option = document.createElement('option');
                    option.value = group;
                    option.textContent = group;
                    groupSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error fetching groups:', error);
            });
    }

    // Function to update professor options based on selected language and group
    function updateProfessorOptions() {
        const selectedLanguage = document.getElementById('langue').value;
        const selectedGroup = document.getElementById('group_lv1').value;
        const selectedNiveau = document.getElementById('niveau').value;

        console.log(`Selected values for professors - Language: ${selectedLanguage}, Group: ${selectedGroup}, Niveau: ${selectedNiveau}`);

        const professorSelect = document.getElementById('professeur');
        professorSelect.innerHTML = '<option value="">Select a Teacher</option>';

        let query = '/api/professors?';
        if (selectedLanguage) query += `language=${selectedLanguage}&`;
        if (selectedGroup) query += `group=${selectedGroup}&`;
        if (selectedNiveau) query += `niveau=${selectedNiveau}&`;

        console.log(`Fetching professors with query: ${query.slice(0, -1)}`);

        fetch(query.slice(0, -1))
            .then(response => response.json())
            .then(professors => {
                console.log('Professors received:', professors);
                professors.forEach(prof => {
                    const option = document.createElement('option');
                    option.value = `${prof.name} ${prof.surname}`;
                    option.textContent = `${prof.name} ${prof.surname}`;
                    professorSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error fetching professors:', error);
            });
    }

    // Add event listeners to filter elements
    document.getElementById('studentName').addEventListener('input', applyFilters);
    document.getElementById('niveau').addEventListener('change', function () {
        const selectedNiveau = this.value;
        const selectedLanguage = document.getElementById('langue').value;
        const selectedGroup = document.getElementById('group_lv1').value;
        console.log(`Niveau changed: ${selectedNiveau}`);
        updateGroupOptions(selectedLanguage, selectedNiveau);
        updateProfessorOptions(selectedLanguage, selectedGroup, selectedNiveau);
        applyFilters();
    });

    document.getElementById('professeur').addEventListener('change', function () {
        const selectedProfessor = this.value;
        if (selectedProfessor === "") {
            resetLanguageAndGroupOptions();
            applyFilters();
        } else {
            fetchData(`/api/professor_details?professor=${encodeURIComponent(selectedProfessor)}`)
                .then(data => {
                    updateLanguageOptions(data.languages);
                    updateGroupOptions(data.groups);
                    applyFilters(); // Appliquer les filtres après la mise à jour des options
                    // Appel supplémentaire pour filtrer les étudiants par professeur
                    fetchData(`/students?professeur=${encodeURIComponent(selectedProfessor)}`)
                        .then(data => {
                            console.log('Filtered student data by professor:', data);
                            populateStudentTable(data);
                        });
                })
                .catch(error => {
                    console.error('Error fetching professor details:', error);
                });
        }
    });
    document.getElementById('langue').addEventListener('change', function () {
        const selectedLanguage = this.value;
        const selectedNiveau = document.getElementById('niveau').value;
        const selectedGroup = document.getElementById('group_lv1').value;
        console.log(`Language changed: ${selectedLanguage}`);
        updateGroupOptions(selectedLanguage, selectedNiveau);
        updateProfessorOptions(selectedLanguage, selectedGroup, selectedNiveau);
        applyFilters();
    });
    document.getElementById('group_lv1').addEventListener('change', function () {
        const selectedGroup = this.value;
        const selectedLanguage = document.getElementById('langue').value;
        const selectedNiveau = document.getElementById('niveau').value;
        console.log(`Group changed: ${selectedGroup}`);
        updateProfessorOptions(selectedLanguage, selectedGroup, selectedNiveau);
        applyFilters();
    });

    // Add event listener to reset filters button
    document.getElementById('resetFilters').addEventListener('click', function () {
        // Reset all filters
        document.getElementById('studentName').value = '';
        document.getElementById('niveau').value = '';
        document.getElementById('professeur').value = '';
        document.getElementById('langue').value = '';
        document.getElementById('group_lv1').value = '';

        // Reset language and group options to all available
        resetLanguageAndGroupOptions();

        // Reset professor options to all available
        updateProfessorOptions(allProfessors, '', '');

        // Apply filters after resetting options
        applyFilters();
    });

    // Function to populate the student table
    function populateStudentTable(data) {
        const studentList = document.getElementById('studentList');
        studentList.innerHTML = ''; // Clear previous data
        const table = document.createElement('table');
        table.className = 'table table-striped';

        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        const headers = ['NAME', 'Firstname', 'Email', 'Class Level', 'Group', 'Language', 'Teacher'];

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
        if (professeur) query += `professeur=${encodeURIComponent(professeur)}&`;
        if (langue) query += `langue=${langue}&`;
        if (groupLv1) query += `group_lv1=${groupLv1}&`;

        fetchData(query.slice(0, -1))  // Remove the last '&'
            .then(data => {
                console.log('Filtered student data:', data);
                populateStudentTable(data);
            });
    }

    function resetLanguageAndGroupOptions() {
        const languageSelect = document.getElementById('langue');
        languageSelect.innerHTML = '<option value="">Select a language</option>';
        allLanguages.forEach(lang => {
            const option = document.createElement('option');
            option.value = lang;
            option.textContent = lang;
            languageSelect.appendChild(option);
        });

        const groupSelect = document.getElementById('group_lv1');
        groupSelect.innerHTML = '<option value="">Select an LV1 Group</option>';
        allGroups.forEach(group => {
            const option = document.createElement('option');
            option.value = group;
            option.textContent = group;
            groupSelect.appendChild(option);
        });
    }

    function updateLanguageOptions(languages) {
        const languageSelect = document.getElementById('langue');
        languageSelect.innerHTML = '<option value="">Select a language</option>';
        languages.forEach(lang => {
            const option = document.createElement('option');
            option.value = lang;
            option.textContent = lang;
            languageSelect.appendChild(option);
        });
    }

    function updateGroupOptions(selectedLanguage, selectedNiveau) {
        const groupSelect = document.getElementById('group_lv1');
        groupSelect.innerHTML = '<option value="">Select an LV1 Group</option>';

        let query = '/groups?';
        if (selectedLanguage) query += `language=${selectedLanguage}&`;
        if (selectedNiveau) query += `niveau=${selectedNiveau}&`;

        fetchData(query.slice(0, -1))
            .then(groups => {
                groups.forEach(group => {
                    const option = document.createElement('option');
                    option.value = group;
                    option.textContent = group;
                    groupSelect.appendChild(option);
                });
            });
    }

    function updateProfessorOptions() {
        const selectedLanguage = document.getElementById('langue').value;
        const selectedGroup = document.getElementById('group_lv1').value;
        const selectedNiveau = document.getElementById('niveau').value;

        console.log(`Selected values for professors - Language: ${selectedLanguage}, Group: ${selectedGroup}, Niveau: ${selectedNiveau}`);

        const professorSelect = document.getElementById('professeur');
        professorSelect.innerHTML = '<option value="">Select a Teacher</option>';

        let query = '/api/professors?';
        if (selectedLanguage) query += `language=${selectedLanguage}&`;
        if (selectedGroup) query += `group=${selectedGroup}&`;
        if (selectedNiveau) query += `niveau=${selectedNiveau}&`;

        console.log(`Fetching professors with query: ${query.slice(0, -1)}`);

        fetch(query.slice(0, -1))
            .then(response => response.json())
            .then(professors => {
                console.log('Professors received:', professors);
                professors.forEach(prof => {
                    const option = document.createElement('option');
                    option.value = `${prof.name} ${prof.surname}`;
                    option.textContent = `${prof.name} ${prof.surname}`;
                    professorSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error fetching professors:', error);
            });
    }

    document.getElementById('studentName').addEventListener('input', applyFilters);
    document.getElementById('niveau').addEventListener('change', function () {
        const selectedNiveau = this.value;
        const selectedLanguage = document.getElementById('langue').value;
        const selectedGroup = document.getElementById('group_lv1').value;
        console.log(`Niveau changed: ${selectedNiveau}`);
        updateGroupOptions(selectedLanguage, selectedNiveau);
        updateProfessorOptions(selectedLanguage, selectedGroup, selectedNiveau);
        applyFilters();
    });
    document.getElementById('professeur').addEventListener('change', function () {
        const selectedProfessor = this.value;
        if (selectedProfessor === "") {
            resetLanguageAndGroupOptions();
            applyFilters();
        } else {
            fetchData(`/api/professor_details?professor=${encodeURIComponent(selectedProfessor)}`)
                .then(data => {
                    updateLanguageOptions(data.languages);
                    updateGroupOptions(data.groups);
                    applyFilters(); // Appliquer les filtres après la mise à jour des options
                })
                .catch(error => {
                    console.error('Error fetching professor details:', error);
                });
        }
    });
    document.getElementById('langue').addEventListener('change', function () {
        const selectedLanguage = this.value;
        const selectedNiveau = document.getElementById('niveau').value;
        const selectedGroup = document.getElementById('group_lv1').value;
        console.log(`Language changed: ${selectedLanguage}`);
        updateGroupOptions(selectedLanguage, selectedNiveau);
        updateProfessorOptions(selectedLanguage, selectedGroup, selectedNiveau);
        applyFilters();
    });
    document.getElementById('group_lv1').addEventListener('change', function () {
        const selectedGroup = this.value;
        const selectedLanguage = document.getElementById('langue').value;
        const selectedNiveau = document.getElementById('niveau').value;
        console.log(`Group changed: ${selectedGroup}`);
        updateProfessorOptions(selectedLanguage, selectedGroup, selectedNiveau);
        applyFilters();
    });

    document.getElementById('resetFilters').addEventListener('click', function () {
        resetFilters();
    });

    function populateStudentTable(data) {
        const studentList = document.getElementById('studentList');
        studentList.innerHTML = ''; // Clear previous data
        const table = document.createElement('table');
        table.className = 'table table-striped';

        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        const headers = ['NAME', 'Firstname', 'Email', 'Class Level', 'Group', 'Language', 'Teacher'];

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

    function applyFilters() {
        const studentName = document.getElementById('studentName').value.toLowerCase();
        const niveau = document.getElementById('niveau').value;
        const professeur = document.getElementById('professeur').value;
        const langue = document.getElementById('langue').value;
        const groupLv1 = document.getElementById('group_lv1').value;

        let query = '/students?';
        if (studentName) query += `name=${studentName}&`;
        if (niveau) query += `niveau=${niveau}&`;
        if (professeur) query += `professeur=${encodeURIComponent(professeur)}&`;
        if (langue) query += `langue=${langue}&`;
        if (groupLv1) query += `group_lv1=${groupLv1}&`;

        fetchData(query.slice(0, -1))  // Remove the last '&'
            .then(data => {
                console.log('Filtered student data:', data);
                populateStudentTable(data);
            });
    }

    function resetFilters() {
        document.getElementById('studentName').value = '';
        document.getElementById('niveau').value = '';
        document.getElementById('professeur').value = '';
        document.getElementById('langue').value = '';
        document.getElementById('group_lv1').value = '';

        // Reset language and group options to all available
        resetLanguageAndGroupOptions();

        // Reset professor options to all available
        updateProfessorOptions(allProfessors, '', '');

        // Apply filters after resetting options
        applyFilters();
    }

    function resetLanguageAndGroupOptions() {
        const languageSelect = document.getElementById('langue');
        languageSelect.innerHTML = '<option value="">Select a language</option>';
        allLanguages.forEach(lang => {
            const option = document.createElement('option');
            option.value = lang;
            option.textContent = lang;
            languageSelect.appendChild(option);
        });

        const groupSelect = document.getElementById('group_lv1');
        groupSelect.innerHTML = '<option value="">Select an LV1 Group</option>';
        allGroups.forEach(group => {
            const option = document.createElement('option');
            option.value = group;
            option.textContent = group;
            groupSelect.appendChild(option);
        });
    }

    function updateLanguageOptions(languages) {
        const languageSelect = document.getElementById('langue');
        languageSelect.innerHTML = '<option value="">Select a language</option>';
        languages.forEach(lang => {
            const option = document.createElement('option');
            option.value = lang;
            option.textContent = lang;
            languageSelect.appendChild(option);
        });
    }

    function updateGroupOptions(selectedLanguage, selectedNiveau) {
        const groupSelect = document.getElementById('group_lv1');
        groupSelect.innerHTML = '<option value="">Select an LV1 Group</option>';

        let query = '/groups?';
        if (selectedLanguage) query += `language=${selectedLanguage}&`;
        if (selectedNiveau) query += `niveau=${selectedNiveau}&`;

        fetchData(query.slice(0, -1))
            .then(groups => {
                groups.forEach(group => {
                    const option = document.createElement('option');
                    option.value = group;
                    option.textContent = group;
                    groupSelect.appendChild(option);
                });
            });
    }

    function updateProfessorOptions() {
        const selectedLanguage = document.getElementById('langue').value;
        const selectedGroup = document.getElementById('group_lv1').value;
        const selectedNiveau = document.getElementById('niveau').value;

        console.log(`Selected values for professors - Language: ${selectedLanguage}, Group: ${selectedGroup}, Niveau: ${selectedNiveau}`);

        const professorSelect = document.getElementById('professeur');
        professorSelect.innerHTML = '<option value="">Select a Teacher</option>';

        let query = '/api/professors?';
        if (selectedLanguage) query += `language=${selectedLanguage}&`;
        if (selectedGroup) query += `group=${selectedGroup}&`;
        if (selectedNiveau) query += `niveau=${selectedNiveau}&`;

        console.log(`Fetching professors with query: ${query.slice(0, -1)}`);

        fetch(query.slice(0, -1))
            .then(response => response.json())
            .then(professors => {
                console.log('Professors received:', professors);
                professors.forEach(prof => {
                    const option = document.createElement('option');
                    option.value = `${prof.name} ${prof.surname}`;
                    option.textContent = `${prof.name} ${prof.surname}`;
                    professorSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error fetching professors:', error);
            });
    }

    document.getElementById('studentName').addEventListener('input', applyFilters);
    document.getElementById('niveau').addEventListener('change', function () {
        const selectedNiveau = this.value;
        const selectedLanguage = document.getElementById('langue').value;
        const selectedGroup = document.getElementById('group_lv1').value;
        console.log(`Niveau changed: ${selectedNiveau}`);
        updateGroupOptions(selectedLanguage, selectedNiveau);
        updateProfessorOptions(selectedLanguage, selectedGroup, selectedNiveau);
        applyFilters();
    });
    document.getElementById('professeur').addEventListener('change', function () {
        const selectedProfessor = this.value;
        if (selectedProfessor === "") {
            resetLanguageAndGroupOptions();
            applyFilters();
        } else {
            fetchData(`/api/professor_details?professor=${encodeURIComponent(selectedProfessor)}`)
                .then(data => {
                    updateLanguageOptions(data.languages);
                    updateGroupOptions(data.groups);
                    applyFilters();
                })
                .catch(error => {
                    console.error('Error fetching professor details:', error);
                });
        }
    });

    document.getElementById('langue').addEventListener('change', function () {
        const selectedLanguage = this.value;
        const selectedNiveau = document.getElementById('niveau').value;
        const selectedGroup = document.getElementById('group_lv1').value;
        console.log(`Language changed: ${selectedLanguage}`);
        updateGroupOptions(selectedLanguage, selectedNiveau);
        updateProfessorOptions(selectedLanguage, selectedGroup, selectedNiveau);
        applyFilters();
    });

    document.getElementById('group_lv1').addEventListener('change', function () {
        const selectedGroup = this.value;
        const selectedLanguage = document.getElementById('langue').value;
        const selectedNiveau = document.getElementById('niveau').value;
        console.log(`Group changed: ${selectedGroup}`);
        updateProfessorOptions(selectedLanguage, selectedGroup, selectedNiveau);
        applyFilters();
    });

    document.getElementById('resetFilters').addEventListener('click', function () {
        resetFilters();
    });

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

    function applyFilters() {
        const studentName = document.getElementById('studentName').value.toLowerCase();
        const niveau = document.getElementById('niveau').value;
        const professeur = document.getElementById('professeur').value;
        const langue = document.getElementById('langue').value;
        const groupLv1 = document.getElementById('group_lv1').value;

        let query = '/students?';
        if (studentName) query += `name=${studentName}&`;
        if (niveau) query += `niveau=${niveau}&`;
        if (professeur) query += `professeur=${encodeURIComponent(professeur)}&`;
        if (langue) query += `langue=${langue}&`;
        if (groupLv1) query += `group_lv1=${groupLv1}&`;

        fetchData(query.slice(0, -1))  // Remove the last '&'
            .then(data => {
                console.log('Filtered student data:', data);
                populateStudentTable(data);
            });
    }

    function resetFilters() {
        document.getElementById('studentName').value = '';
        document.getElementById('niveau').value = '';
        document.getElementById('professeur').value = '';
        document.getElementById('langue').value = '';
        document.getElementById('group_lv1').value = '';

        // Reset language and group options to all available
        resetLanguageAndGroupOptions();

        // Reset professor options to all available
        updateProfessorOptions(allProfessors, '', '');

        // Apply filters after resetting options
        applyFilters();
    }

    function resetLanguageAndGroupOptions() {
        const languageSelect = document.getElementById('langue');
        languageSelect.innerHTML = '<option value="">Select a language</option>';
        allLanguages.forEach(lang => {
            const option = document.createElement('option');
            option.value = lang;
            option.textContent = lang;
            languageSelect.appendChild(option);
        });

        const groupSelect = document.getElementById('group_lv1');
        groupSelect.innerHTML = '<option value="">Select an LV1 Group</option>';
        allGroups.forEach(group => {
            const option = document.createElement('option');
            option.value = group;
            option.textContent = group;
            groupSelect.appendChild(option);
        });
    }

    function updateLanguageOptions(languages) {
        const languageSelect = document.getElementById('langue');
        languageSelect.innerHTML = '<option value="">Select a language</option>';
        languages.forEach(lang => {
            const option = document.createElement('option');
            option.value = lang;
            option.textContent = lang;
            languageSelect.appendChild(option);
        });
    }

    function updateGroupOptions(selectedLanguage, selectedNiveau) {
        const groupSelect = document.getElementById('group_lv1');
        groupSelect.innerHTML = '<option value="">Select an LV1 Group</option>';

        let query = '/groups?';
        if (selectedLanguage) query += `language=${selectedLanguage}&`;
        if (selectedNiveau) query += `niveau=${selectedNiveau}&`;

        fetchData(query.slice(0, -1))
            .then(groups => {
                groups.forEach(group => {
                    const option = document.createElement('option');
                    option.value = group;
                    option.textContent = group;
                    groupSelect.appendChild(option);
                });
            });
    }

    function updateProfessorOptions() {
        const selectedLanguage = document.getElementById('langue').value;
        const selectedGroup = document.getElementById('group_lv1').value;
        const selectedNiveau = document.getElementById('niveau').value;

        console.log(`Selected values for professors - Language: ${selectedLanguage}, Group: ${selectedGroup}, Niveau: ${selectedNiveau}`);

        const professorSelect = document.getElementById('professeur');
        professorSelect.innerHTML = '<option value="">Select a Teacher</option>';

        let query = '/api/professors?';
        if (selectedLanguage) query += `language=${selectedLanguage}&`;
        if (selectedGroup) query += `group=${selectedGroup}&`;
        if (selectedNiveau) query += `niveau=${selectedNiveau}&`;

        console.log(`Fetching professors with query: ${query.slice(0, -1)}`);

        fetch(query.slice(0, -1))
            .then(response => response.json())
            .then(professors => {
                console.log('Professors received:', professors);
                professors.forEach(prof => {
                    const option = document.createElement('option');
                    option.value = `${prof.name} ${prof.surname}`;
                    option.textContent = `${prof.name} ${prof.surname}`;
                    professorSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error fetching professors:', error);
            });
    }
});