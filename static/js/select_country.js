$(document).ready(function () {
    $.get('/api/onboard/countries/', function (data) {
        const $select = $('#country-select');
        data.forEach(function (country) {
            $select.append(`<option value="${country.code}">${country.name}</option>`);
        });
    });

    $('#next-button').click(function () {
        const selected = $('#country-select').val();
        if (selected) {
            window.location.href = `/onboard/checklist/?country_code=${selected}`;
        }
    });
});
