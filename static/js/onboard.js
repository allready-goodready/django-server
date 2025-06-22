document.addEventListener("DOMContentLoaded", function () {
    const countrySelect = document.getElementById("countries");
    const interestSelect = document.getElementById("interests");
  
    // CSRF Token 세팅
    function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
          const trimmed = cookie.trim();
          if (trimmed.startsWith(name + "=")) {
            cookieValue = decodeURIComponent(trimmed.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
    const csrftoken = getCookie("csrftoken");
  
    // 1. 초기 렌더링용 나라/관심사 목록 불러오기
    function loadOptions() {
      // 나라
      fetch("/api/countries/")
        .then((res) => res.json())
        .then((data) => {
          data.forEach((c) => {
            const opt = new Option(c.name, c.id);
            countrySelect.appendChild(opt);
          });
        });
  
      // 관심사
      fetch("/api/interests/")
        .then((res) => res.json())
        .then((data) => {
          data.forEach((i) => {
            const opt = new Option(i.name, i.id);
            interestSelect.appendChild(opt);
          });
        });
    }
  
    // 2. 유저가 기존에 저장한 온보딩 정보 불러오기
    function loadUserOnboarding() {
      fetch("/onboard/load/")
        .then((res) => {
          if (res.status === 204) return null;
          return res.json();
        })
        .then((data) => {
          if (!data) return;
          for (let opt of countrySelect.options) {
            if (data.countries.includes(parseInt(opt.value))) {
              opt.selected = true;
            }
          }
          for (let opt of interestSelect.options) {
            if (data.interests.includes(parseInt(opt.value))) {
              opt.selected = true;
            }
          }
        });
    }
  
    // 3. 온보딩 정보 저장
    document.getElementById("onboarding-form").addEventListener("submit", function (e) {
      e.preventDefault();
      const selectedCountries = Array.from(countrySelect.selectedOptions).map((opt) => opt.value);
      const selectedInterests = Array.from(interestSelect.selectedOptions).map((opt) => opt.value);
  
      fetch("/onboard/save/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({
          countries: selectedCountries,
          interests: selectedInterests,
        }),
      })
        .then((res) => res.json())
        .then((data) => {
          alert(data.message);
        });
    });
  
    loadOptions();
    loadUserOnboarding();
  });
  