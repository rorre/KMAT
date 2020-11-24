function flash(message, type) {
    if (type === undefined || type === null) {
        type = "primary";
    }

    $("#flashes").append(```
    <div class="alert alert-${type}" role="alert">
        ${message}
    </div>
    ```);
}

$(".save-button").on('click', function () {
    var $form = $(this).parent().siblings(".modal-body").find("form");
    if (!$form[0].checkValidity()) {
        $form.addClass("was-validated")
        return;
    }
    var formArray = $form.serializeArray();

    var formJSON = {
        'scores': [],
        'comment': "",
    };
    formArray.forEach(element => {
        if (element.name == "comment") {
            formJSON.comment = element.value;
            return;
        }
        formJSON['scores'].push(element);
    });

    var submissionid = $form.find("input[name='submissionId']").val();
    $.post("/" + submissionid, formJSON, function (data, status, xhr) {
        if (status != "success") {
            flash("An error has occured.", "danger");
        }

        $(this).parent("modal").modal("hide");
    });
});