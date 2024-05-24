document.addEventListener('DOMContentLoaded', function () {
    fetch('/students')
        .then(response => response.json())
        .then(data => {
            const studentList = document.getElementById('studentList');
            const table = document.createElement('table');
            table.className = 'table table-striped';

            // Create table header
            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            const headers = ['Prénom', 'Nom', 'Email', 'Classe', 'LV1', 'Groupe LV1'];

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
                firstNameCell.textContent = student[1]; // Prénom
                row.appendChild(firstNameCell);

                const lastNameCell = document.createElement('td');
                lastNameCell.textContent = student[0]; // Nom
                row.appendChild(lastNameCell);

                const emailCell = document.createElement('td');
                emailCell.textContent = student[2]; // Email
                row.appendChild(emailCell);

                const classCell = document.createElement('td');
                classCell.textContent = student[3]; // Classe
                row.appendChild(classCell);

                const lv1Cell = document.createElement('td');
                lv1Cell.textContent = student[4]; // LV1
                row.appendChild(lv1Cell);

                const groupLv1Cell = document.createElement('td');
                groupLv1Cell.textContent = student[5]; // Groupe LV1
                row.appendChild(groupLv1Cell);

                tbody.appendChild(row);
            });

            table.appendChild(tbody);
            studentList.appendChild(table);

            // Apply scrolling effect
            applyScrollEffect();
        })
        .catch(error => console.error('Error fetching student data:', error));
});

function applyScrollEffect() {
    const table = document.querySelector('.table');
    const scrollSpeed = 50; // Adjust scroll speed as needed
    let scrollPos = 0;

    function scrollTable() {
        scrollPos++;
        table.scrollTo({
            top: scrollPos,
            left: scrollPos,
            behavior: 'smooth'
        });
        if (scrollPos >= table.scrollHeight - table.clientHeight && scrollPos >= table.scrollWidth - table.clientWidth) {
            scrollPos = 0; // Reset scroll position
        }
    }

    setInterval(scrollTable, scrollSpeed);
}
