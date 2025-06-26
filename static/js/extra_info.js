$(document).ready(function () {
    const urlParams = new URLSearchParams(window.location.search);
    const countryCode = urlParams.get('country_code');

    // 기존: 팁 + 환율
    $.get('/api/onboard/extra-info/', function (data) {
        $('#tip1').text(data.tip1);
        $('#tip2').text(data.tip2);
    });

    $.get(`/api/onboard/exchange-rate/?base=KRW&target=USD`, function (data) {
        if (data && data.rate) {
            $('#currency').text(`1 ${data.base} ≈ ${data.rate} ${data.target} (기준일: ${data.date})`);
        } else {
            $('#currency').text('환율 정보를 불러올 수 없습니다.');
        }
    });

    // 추가: 백신 정보
    $.get(`/api/onboard/required-vaccines/?country_code=${countryCode}`, function (data) {
        const list = $('#vaccine-list');
        list.empty();
        if (data.length === 0) {
            list.append('<li>요구되는 백신이 없습니다.</li>');
        } else {
            data.forEach(v => {
                list.append(`<li>${v.vaccine_name}: ${v.description}</li>`);
            });
        }
    });
});
