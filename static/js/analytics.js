document.addEventListener("DOMContentLoaded", function () {

    const progressBars = document.querySelectorAll(".progress-fill");

    progressBars.forEach(function (bar) {

        const width = bar.style.width;

        bar.style.width = "0%";

        setTimeout(function () {
            bar.style.width = width;
        }, 100);

    });

});
