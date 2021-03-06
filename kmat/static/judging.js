$(function () {
    const $spinner = $('<span class="spinner-border spinner-border-sm mb-1 mr-2" role="status" aria-hidden="true"></span>')

    function flash(message, type) {
        if (type === undefined || type === null) {
            type = "primary";
        }

        $("#flashes").append(`
        <div class="alert alert-${type}" role="alert">
            ${message}
        </div>
        `);
    }

    $(".save-button").on('click', function (event) {
        event.preventDefault();
        var $this = $(this);

        var $form = $this.parent().siblings(".modal-body").find("form");
        if (!$form[0].checkValidity()) {
            $form.addClass("was-validated")
            return;
        }
        $this.prop("disabled", true);
        $this.prepend($spinner);
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
        axios.post(submissionid, formJSON)
            .then(function () {
                flash("Done!");
                $modal = $this.parents(".modal")
                var modalId = $modal.attr("id")
                var $badge = $(`li[data-target='#${modalId}'`).find("span")

                $badge.removeClass("badge-danger")
                $badge.addClass("badge-success")
                $badge.html("Judged")
            })
            .catch(function (error) {
                if (error.response) {
                    flash("An error has occured.", "danger")
                } else {
                    flash(error.message, "danger");
                }

            })
            .finally(function () {
                $this.parents(".modal").modal("hide");
                $this.find($spinner).remove();
                $this.prop("disabled", false);
            });
    });
})
