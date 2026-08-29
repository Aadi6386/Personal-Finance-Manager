document.addEventListener("DOMContentLoaded", function () {

    const flashMessages = document.querySelectorAll(".flash-message");

    flashMessages.forEach(function (message) {

        setTimeout(function () {

            message.style.opacity = "0";
            message.style.transition = "opacity 0.4s ease";

            setTimeout(function () {
                message.remove();
            }, 400);

        }, 4000);

    });


    const deleteForms = document.querySelectorAll(".delete-form");

    deleteForms.forEach(function (form) {

        form.addEventListener("submit", function (event) {

            const confirmed = confirm(
                "Are you sure you want to delete this item?"
            );

            if (!confirmed) {
                event.preventDefault();
            }

        });

    });


    const amountInputs = document.querySelectorAll(
        'input[type="number"]'
    );

    amountInputs.forEach(function (input) {

        input.addEventListener("input", function () {

            if (Number(input.value) < 0) {
                input.value = "";
            }

        });

    });

});
