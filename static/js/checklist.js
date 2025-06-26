$(document).ready(function () {
    const urlParams = new URLSearchParams(window.location.search);
    const countryCode = urlParams.get('country_code');

    $.get(`/api/onboard/checklist/?country_code=${countryCode}`, function (data) {
        const $list = $('#checklist-items');
        data.forEach(function (item) {
            const checkbox = `
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" value="${item.id}" id="item-${item.id}">
                    <label class="form-check-label" for="item-${item.id}">${item.content}</label>
                </div>`;
            $list.append(checkbox);
        });
    });

    $('#save-checklist').click(function () {
        const checked = [];
        $('input:checked').each(function () {
            checked.push(parseInt($(this).val()));
        });

        $.ajax({
            url: '/api/onboard/checklist/save/',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ items: checked }),
            success: function () {
                alert('저장되었습니다.');
                window.location.href = '/onboard/extra-info/';
            }
        });
    });
});
