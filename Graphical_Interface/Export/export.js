$(document).ready(function () {
    // Peupler dynamiquement les options des groupes
    $.getJSON('/groups', function (data) {
        var groupSelect = $('#groupSelect');
        $.each(data, function (index, value) {
            groupSelect.append($('<option>', { value: value, text: value }));
        });
    });

    // Peupler dynamiquement les options des professeurs
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

        window.location.href = url;
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

        window.location.href = url;
    });

    $('#exportLV1Button').click(function () {
        var fileType = 'xlsx'; // Change to 'xlsx'
        var url = `/export_lv1?fileType=${fileType}`;
        window.location.href = url;
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
        window.location.href = url;
    });
});
