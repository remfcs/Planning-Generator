$(document).ready(function () {
    // Charger les groupes
    $.get("/groups", function (data) {
        data.forEach(function (group) {
            $("#groupSelect").append(new Option(group, group));
        });
    });

    // Charger les professeurs
    $.get("/api/professors", function (data) {
        data.forEach(function (professor) {
            $("#professorSelect").append(new Option(professor.name + " " + professor.surname, professor.name + " " + professor.surname));
        });
    });

    // Exporter les groupes
    $("#exportGroupButton").click(function () {
        let fileType = $("#fileTypeGroup").val();
        let groupId = $("#groupSelect").val();
        let exportAll = $("#exportAllGroups").prop('checked');

        let url = `/export_group?fileType=${fileType}`;
        if (!exportAll) {
            url += `&groupId=${groupId}`;
        } else {
            url += `&exportAll=true`;
        }

        window.location.href = url;
    });

    // Exporter les professeurs
    $("#exportProfessorButton").click(function () {
        let fileType = $("#fileTypeProfessor").val();
        let professorName = $("#professorSelect").val();
        let exportAll = $("#exportAllProfessors").prop('checked');

        let url = `/export_professor?fileType=${fileType}`;
        if (!exportAll) {
            url += `&professor=${professorName}`;
        } else {
            url += `&exportAll=true`;
        }

        window.location.href = url;
    });
});
