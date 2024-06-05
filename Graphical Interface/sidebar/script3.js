// script.js
document.getElementById('toggle-btn').addEventListener('click', function() {
    var sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('open');
    if (sidebar.classList.contains('open')) {
        document.body.style.marginLeft = '260px';
    } else {
        document.body.style.marginLeft = '0';
    }
});
