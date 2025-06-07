// static/js/feed_search_modal.js

let autocomplete;
function initAutocomplete() {
  const input = document.getElementById("place_input");
  autocomplete = new google.maps.places.Autocomplete(input);


  autocomplete.addListener("place_changed", () => {
    const place = autocomplete.getPlace();
    if (!place.geometry) {
      alert("장소 정보를 불러올 수 없습니다.");
      return;
    }

    const name = place.name;
    const lat = place.geometry.location.lat();
    const lng = place.geometry.location.lng();

    // 여행지 입력칸에 값 채워넣기
    document.getElementById("input_place").value = name;
    document.getElementById("input_lat").value = lat;
    document.getElementById("input_lng").value = lng;

    // 모달 닫기
    document.getElementById("search_place_modal").style.display = "none";
  });
}

// 모달 열기/닫기 버튼
document.getElementById("place_search_modal")?.addEventListener("click", () => {
  document.getElementById("search_place_modal").style.display = "flex";
  initAutocomplete();  // 모달 열릴 때 초기화
});

document.getElementById("close_search_modal")?.addEventListener("click", () => {
  document.getElementById("search_place_modal").style.display = "none";
});



// Google Places AutocompleteService와 PlacesService 를 사용해서
// 사용자가 입력할 때마다 자동완성 예측 목록을 가져오고,
// 사용자가 선택하면 place 정보를 꺼내서 hidden input에 채운다.

window.addEventListener("DOMContentLoaded", function () {
  // 1) AutocompleteService 및 PlacesService 초기화
  const autocompleteService = new google.maps.places.AutocompleteService();
  const placesService = new google.maps.places.PlacesService(document.createElement("div"));

  // 2) DOM 요소 캐싱
  const inputEl = document.getElementById("place_input");
  const suggestionsEl = document.getElementById("place_suggestions");
  const searchModal = document.getElementById("search_place_modal");
  const closeBtn = document.getElementById("close_search_modal");

  // 3) 입력 이벤트가 발생할 때마다 예측 결과를 가져와서 화면에 렌더
  inputEl.addEventListener("input", function () {
    const query = inputEl.value.trim();
    if (!query) {
      suggestionsEl.innerHTML = "";
      return;
    }

    // AutocompleteService.getPlacePredictions 호출
    autocompleteService.getPlacePredictions(
      { input: query },
      function (predictions, status) {
        if (status !== google.maps.places.PlacesServiceStatus.OK || !predictions) {
          suggestionsEl.innerHTML = "";
          return;
        }

        // 예측 목록 렌더
        suggestionsEl.innerHTML = ""; // 먼저 비우기
        predictions.forEach(pred => {
          const li = document.createElement("li");
          li.classList.add("list-group-item", "list-group-item-action");
          li.textContent = pred.description;
          li.dataset.placeId = pred.place_id; // 클릭 시 장소 ID 가져갈 용도
          suggestionsEl.appendChild(li);
        });
      }
    );
  });

  // 4) 예측 리스트 클릭 이벤트 (사용자 선택)
  suggestionsEl.addEventListener("click", function (e) {
    const li = e.target.closest("li");
    if (!li) return;
    const placeId = li.dataset.placeId;
    if (!placeId) return;

    // PlacesService.getDetails 로 선택된 장소의 상세 정보(이름, 좌표 등)를 받아옴
    placesService.getDetails(
      { placeId: placeId, fields: ["name", "geometry"] },
      function (placeResult, status) {
        if (status !== google.maps.places.PlacesServiceStatus.OK || !placeResult || !placeResult.geometry) {
          console.error("Place details 조회 실패:", status);
          return;
        }

        const name  = placeResult.name;
        const lat   = placeResult.geometry.location.lat();
        const lng   = placeResult.geometry.location.lng();
        console.log("선택된 장소 → 이름:", name, "위도:", lat, "경도:", lng);

        // 5) 검색창에 선택한 장소 이름, 위도/경도 값을 hidden input에 채우기
        // (feed_create.html 쪽에 input_place, input_lat, input_lng가 있다고 가정)
        document.getElementById("input_place").value = name;
        document.getElementById("input_lat").value   = lat;
        document.getElementById("input_lng").value   = lng;

        // 6) 모달 닫기 및 clean up
        suggestionsEl.innerHTML = "";
        searchModal.style.display = "none";
        document.body.style.overflowY = "visible";
      }
    );
  });

  // 7) 모달 안 닫기 버튼(✕) 클릭
  closeBtn.addEventListener("click", function () {
    suggestionsEl.innerHTML = "";
    searchModal.style.display = "none";
    document.body.style.overflowY = "visible";
  });

  // 8) 바깥 클릭으로 모달 닫기 (클릭한 target이 모달 백그라운드 영역이면 닫기)
  window.addEventListener("click", function (e) {
    if (e.target === searchModal) {
      suggestionsEl.innerHTML = "";
      searchModal.style.display = "none";
      document.body.style.overflowY = "visible";
    }
  });
});