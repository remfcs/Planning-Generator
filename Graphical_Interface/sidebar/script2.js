// script.js
document.addEventListener('DOMContentLoaded', function() {
    fetch('../sidebar/sidebar2.html')
        .then(response => response.text())
        .then(data => {
            document.getElementById('sidebar-container').innerHTML = data;

            const toggleBtn = document.getElementById('toggle-btn');
            const sidebar = document.getElementById('sidebar');

            toggleBtn.addEventListener('click', function() {
                sidebar.classList.toggle('collapsed');
                if (!sidebar.classList.contains('collapsed')) {
                    document.body.style.marginLeft = '260px';
                } else {
                    document.body.style.marginLeft = '0';
                }
            });
        });
});
