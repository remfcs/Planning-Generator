document.addEventListener('DOMContentLoaded', function () {
    const exportButton = document.getElementById('exportButton');

    exportButton.addEventListener('click', function () {
        const fileType = document.getElementById('fileType').value;
        window.location.href = `/export?fileType=${fileType}`;
    });
});