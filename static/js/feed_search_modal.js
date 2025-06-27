// static/js/feed_search_modal.js

let autocomplete;

// 장소 이름을 간결하고 국가 포함되게 정리하는 함수
function simplifyPlaceName(place) {
  const comps = place.address_components;
  if (!comps) return place.name;

  const country = comps.find(c => c.types.includes("country"))?.long_name;
  const city = comps.find(c => c.types.includes("administrative_area_level_1"))?.long_name;
  const town = comps.find(c => c.types.includes("locality") || c.types.includes("sublocality"))?.long_name;
  const name = place.name;

  let parts;

  // 해외: "체코 프라하", 국내: "서울 창덕궁" 식으로 구성
  if (country !== "대한민국") {
     parts = [country, town || city, name];
  } else {
     parts = [city, name];
  }

  // 중복 제거 (도시만 선택하는 경우 스페인 마드리드 마드리드 → 스페인 마드리드)
  // 대신 마드리드 왕궁을 선택할 경우 스페인 마드리드 마드리드 왕궁 으로 저장
  const uniqueParts = [...new Set(parts.filter(Boolean))];

  return uniqueParts.join(" ");
}

document.addEventListener("DOMContentLoaded", function () {
  // 주요 DOM 요소들
  const inputEl = document.getElementById("place_input");
  const suggestionsEl = document.getElementById("place_suggestions");
  const searchModal = document.getElementById("search_place_modal");
  const closeBtn = document.getElementById("close_search_modal");

  // 구글 자동완성 서비스/상세정보 서비스 초기화
  const autocompleteService = new google.maps.places.AutocompleteService();
  const placesService = new google.maps.places.PlacesService(document.createElement("div"));

  // 사용자가 입력할 때마다 장소 예측 목록 보여주기
  inputEl.addEventListener("input", function () {
    const query = inputEl.value.trim();
    if (!query) {
      suggestionsEl.innerHTML = "";
      return;
    }

    // 장소 예측 요청
    autocompleteService.getPlacePredictions({ input: query }, function (predictions, status) {
      if (status !== google.maps.places.PlacesServiceStatus.OK || !predictions) {
        suggestionsEl.innerHTML = "";
        return;
      }

      // 예측 결과 목록 렌더링
      suggestionsEl.innerHTML = "";
      predictions.forEach(pred => {
        const li = document.createElement("li");
        li.classList.add("list-group-item", "list-group-item-action");
        li.textContent = pred.description;
        li.dataset.placeId = pred.place_id;
        suggestionsEl.appendChild(li);
      });
    });
  });

  // 예측 리스트에서 항목 클릭 시 장소 상세 정보 가져와서 입력값에 저장
  suggestionsEl.addEventListener("click", function (e) {
    const li = e.target.closest("li");
    const placeId = li?.dataset?.placeId;
    if (!placeId) return;

    // 선택된 장소의 상세 정보 요청
    placesService.getDetails(
      { placeId: placeId, fields: ["name", "geometry", "address_components"] },
      function (placeResult, status) {
        if (status !== google.maps.places.PlacesServiceStatus.OK || !placeResult?.geometry) {
          console.error("Place details 조회 실패:", status);
          return;
        }

        // 장소 이름 간결하게 정리
        const name = simplifyPlaceName(placeResult);
        const lat = placeResult.geometry.location.lat();
        const lng = placeResult.geometry.location.lng();

        // input에 값 채워넣기
        document.getElementById("input_place").value = name;
        document.getElementById("input_lat").value = lat;
        document.getElementById("input_lng").value = lng;

        // 모달 닫기
        suggestionsEl.innerHTML = "";
        searchModal.style.display = "none";
        document.body.style.overflowY = "visible";
      }
    );
  });

  // X 버튼 클릭 시 모달 닫기
  closeBtn.addEventListener("click", () => {
    suggestionsEl.innerHTML = "";
    searchModal.style.display = "none";
    document.body.style.overflowY = "visible";
  });

  // 모달 바깥 클릭 시 닫기
  window.addEventListener("click", function (e) {
    if (e.target === searchModal) {
      suggestionsEl.innerHTML = "";
      searchModal.style.display = "none";
      document.body.style.overflowY = "visible";
    }
  });

  // 장소 검색 버튼 클릭 → 모달 열기
  document.getElementById("place_search_modal")?.addEventListener("click", () => {
    searchModal.style.display = "flex";
  });
});
