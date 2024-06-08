$(document).ready(function () {
    // Example: Populate groupSelect with group options dynamically
    $.ajax({
        url: '/groups',
        method: 'GET',
        success: function (data) {
            var groupSelect = $('#groupSelect');
            data.forEach(function (group) {
                groupSelect.append(new Option(group, group));
            });
        }
    });

    $('#exportButton').click(function () {
        var fileType = $('#fileType').val();
        var groupId = $('#groupSelect').val();
        var exportAll = $('#exportAllGroups').is(':checked');

        var params = {
            fileType: fileType,
            groupId: groupId,
            exportAll: exportAll
        };

        $.ajax({
            url: '/export_file',
            method: 'GET',
            data: params,
            xhrFields: {
                responseType: 'blob'
            },
            success: function (data, status, xhr) {
                var blob = new Blob([data], { type: xhr.getResponseHeader('Content-Type') });
                var downloadUrl = URL.createObjectURL(blob);
                var a = document.createElement('a');
                a.href = downloadUrl;
                a.download = xhr.getResponseHeader('Content-Disposition').split('filename=')[1];
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            },
            error: function (xhr, status, error) {
                alert('Failed to export file: ' + error);
            }
        });
    });
});
