$(document).ready(function () {
    // Populate group options dynamically
    $.getJSON('/groups', function (data) {
        var groupSelect = $('#groupSelect');
        $.each(data, function (index, value) {
            groupSelect.append($('<option>', { value: value, text: value }));
        });
    });

    // Populate professor options dynamically
    $.getJSON('/api/professors', function (data) {
        var professorSelect = $('#professorSelect');
        $.each(data, function (index, value) {
            professorSelect.append($('<option>', { value: value.name + " " + value.surname, text: value.name + " " + value.surname }));
        });
    });

    $('#exportGroupButton').click(function () {
        var fileType = $('#fileTypeGroup').val();
        var groupId = $('#groupSelect').val();
        var exportAll = $('#exportAllGroups').is(':checked');

        var url = `/export_group?fileType=${fileType}`;
        if (!exportAll) {
            url += `&groupId=${groupId}`;
        } else {
            url += `&exportAll=true`;
        }

        $.ajax({
            url: url,
            type: 'GET',
            success: function (response) {
                if (response.message) {
                    alert(response.message);
                }
                if (response.file_path) {
                    const link = document.createElement('a');
                    link.href = `/download/${encodeURIComponent(response.file_path.split('/').pop())}`;
                    link.download = response.file_path.split('/').pop();
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }
                alert('Export successful!')
            },
            error: function (xhr, status, error) {
                try {
                    var err = JSON.parse(xhr.responseText);
                    alert(err.error || 'An error occurred while exporting.');
                } catch (e) {
                    alert('An error occurred while exporting.');
                }
            }
        });
    });

    $('#exportProfessorButton').click(function () {
        var fileType = $('#fileTypeProfessor').val();
        var professor = $('#professorSelect').val();
        var exportAll = $('#exportAllProfessors').is(':checked');

        var url = `/export_professor?fileType=${fileType}`;
        if (!exportAll) {
            url += `&professor=${professor}`;
        } else {
            url += `&exportAll=true`;
        }

        $.ajax({
            url: url,
            type: 'GET',
            success: function (response) {
                if (response.message) {
                    alert(response.message);
                }
                if (response.file_path) {
                    const link = document.createElement('a');
                    link.href = `/download/${encodeURIComponent(response.file_path.split('/').pop())}`;
                    link.download = response.file_path.split('/').pop();
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }
                alert('Export successful!')
            },
            error: function (xhr, status, error) {
                try {
                    var err = JSON.parse(xhr.responseText);
                    alert(err.error || 'An error occurred while exporting.');
                } catch (e) {
                    alert('An error occurred while exporting.');
                }
            }
        });
    });

    $('#exportLV1Button').click(function () {
        var fileType = 'xlsx'; // Change to 'xlsx'
        var url = `/export_lv1?fileType=${fileType}`;
        $.ajax({
            url: url,
            type: 'GET',
            success: function (response) {
                if (response.message) {
                    alert(response.message);
                }
                if (response.file_path) {
                    const link = document.createElement('a');
                    link.href = `/download/${encodeURIComponent(response.file_path.split('/').pop())}`;
                    link.download = response.file_path.split('/').pop();
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }
                alert('Export successful!')
            },
            error: function (xhr, status, error) {
                try {
                    var err = JSON.parse(xhr.responseText);
                    alert(err.error || 'An error occurred while exporting.');
                } catch (e) {
                    alert('An error occurred while exporting.');
                }
            }
        });
    });

    // Populate dynamically the options for promotions
    $.getJSON('/promotions', function (data) {
        var promotionSelect = $('#promotionSelect');
        promotionSelect.append($('<option>', { value: 'all', text: 'All Promotions' }));
        $.each(data, function (index, value) {
            promotionSelect.append($('<option>', { value: value, text: value }));
        });
    });

    $('#exportLV2Button').click(function () {
        var promotion = $('#promotionSelect').val();
        var exportAll = (promotion === 'all');
        var url = exportAll ? `/export_lv2?export_all=true` : `/export_lv2?niveau=${promotion}`;
        $.ajax({
            url: url,
            type: 'GET',
            success: function (response) {
                if (response.message) {
                    alert(response.message);
                }
                if (response.file_path) {
                    const link = document.createElement('a');
                    link.href = `/download/${encodeURIComponent(response.file_path.split('/').pop())}`;
                    link.download = response.file_path.split('/').pop();
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }
                alert('Export successful!');
            },
            error: function (xhr, status, error) {
                try {
                    var err = JSON.parse(xhr.responseText);
                    alert(err.error || 'An error occurred while exporting.');
                } catch (e) {
                    alert('An error occurred while exporting.');
                }
            }
        });
    });
});