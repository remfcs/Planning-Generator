document.addEventListener('DOMContentLoaded', function () {
    // Function to fetch data
    function fetchData(url) {
        return fetch(url)
            .then(response => response.json())
            .catch(error => {
                console.error(`Error fetching data from ${url}:`, error);
                return [];
            });
    }

    // Fetch professors
    fetchData('/api/professors')
        .then(data => {
            console.log('Professors data:', data);
            populateProfessorTable(data);
        });

    // Function to populate the professor table
    function populateProfessorTable(data) {
        console.log('Populating professor table with data:', data);
        const professorList = document.getElementById('professorList');
        professorList.innerHTML = ''; // Clear previous data
        const table = document.createElement('table');
        table.className = 'table table-striped';

        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        const headers = ['Nom', 'Prénom', 'Email', 'Matière', 'Disponibilités'];

        headers.forEach(headerText => {
            const header = document.createElement('th');
            header.textContent = headerText;
            headerRow.appendChild(header);
        });

        thead.appendChild(headerRow);
        table.appendChild(thead);

        const tbody = document.createElement('tbody');
        data.forEach(professor => {
            console.log('Processing professor:', professor);
            const row = document.createElement('tr');

            const nameCell = document.createElement('td');
            nameCell.textContent = professor.name;
            row.appendChild(nameCell);

            const surnameCell = document.createElement('td');
            surnameCell.textContent = professor.surname;
            row.appendChild(surnameCell);

            const emailCell = document.createElement('td');
            emailCell.textContent = professor.email;
            row.appendChild(emailCell);

            const subjectCell = document.createElement('td');
            subjectCell.textContent = professor.subject;
            row.appendChild(subjectCell);

            const availabilityCell = document.createElement('td');
            const availabilityList = professor.availability ? professor.availability.split(',').join('<br>') : '';
            availabilityCell.innerHTML = availabilityList;
            row.appendChild(availabilityCell);

            tbody.appendChild(row);
        });

        table.appendChild(tbody);
        professorList.appendChild(table);
    }
});
