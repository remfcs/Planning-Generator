document.addEventListener('DOMContentLoaded', function() {
    fetch('sidebar2.html')
        .then(response => response.text())
        .then(data => {
            document.getElementById('sidebar-container').innerHTML = data;
            
            const toggleBtn = document.getElementById('toggle-btn');
            const sidebar = document.getElementById('sidebar');

            toggleBtn.addEventListener('click', function() {
                sidebar.classList.toggle('collapsed');
            });
        });
});
