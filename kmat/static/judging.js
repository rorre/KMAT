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
        if (element.name == "submissionId") return;
        formJSON['scores'].push(element);
    });

    var submissionid = $form.find("input[name='submissionId']").val();
    axios.post(submissionid, formJSON).then(function (response) {
        if (response.status != 200) {
            flash("An error has occured.", "danger");
        }

        $(this).parent("modal").modal("hide");
    });
});