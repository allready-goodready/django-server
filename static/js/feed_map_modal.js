// static/js/feed_map_modal.js

window.addEventListener("DOMContentLoaded", function () {
  // 1) 모달/요소 캐싱
  const mapModal    = document.getElementById("select_on_map_modal");
  const closeMapBtn = document.getElementById("close_map_modal");
  const mapCanvas   = document.getElementById("map_canvas");
  const placeMapIcon = document.getElementById("place_map_icon"); // 작성 모달의 지도 아이콘

  let map, marker, geocoder;

  // 2) 지도 아이콘 클릭 → 모달 열기 + 지도 초기화
  placeMapIcon?.addEventListener("click", function () {
    mapModal.style.display = "flex";
    document.body.style.overflowY = "hidden";

    if (!map) {
      initMap();
    }
  });

  // 3) 지도 초기화 함수
  function initMap() {
    geocoder = new google.maps.Geocoder();

    // 초기 좌표 (예: 서울 시청 근처)
    const initialLatLng = { lat: 37.5665, lng: 126.9780 };

    // 지도 생성
    map = new google.maps.Map(mapCanvas, {
      center: initialLatLng,
      zoom: 12,
    });

    // 클릭 위치에 마커 찍고, 역지오코딩해서 위치 정보 업데이트
    map.addListener("click", function (event) {
      const clickedLatLng = event.latLng;

      // 기존 마커 있으면 삭제
      if (marker) {
        marker.setMap(null);
      }

      // 새로운 마커 생성
      marker = new google.maps.Marker({
        position: clickedLatLng,
        map: map,
      });

      // 지도 중심 이동(optional)
      map.panTo(clickedLatLng);

      // 위도/경도 추출
      const lat = clickedLatLng.lat();
      const lng = clickedLatLng.lng();

      // 역지오코딩 수행
      geocoder.geocode({ location: clickedLatLng }, function (results, status) {
        let placeName = "";
        if (status === "OK" && results[0]) {
          placeName = results[0].formatted_address;
        } else {
          console.warn("역지오코딩 실패:", status);
        }

        // placeName, lat, lng 를 console.log로 확인
        console.log("지도 선택 → 주소:", placeName, "위도:", lat, "경도:", lng);

        // hidden input / readonly input 에 값 채우기
        document.getElementById("input_place").value = placeName;
        document.getElementById("input_lat").value   = lat;
        document.getElementById("input_lng").value   = lng;
      });
    });
  }

  // 4) X 버튼 클릭 → 모달 닫기
  closeMapBtn?.addEventListener("click", function () {
    mapModal.style.display = "none";
    document.body.style.overflowY = "visible";
  });

  // 5) 모달 바깥 클릭 → 모달 닫기
  window.addEventListener("click", function (e) {
    if (e.target === mapModal) {
      mapModal.style.display = "none";
      document.body.style.overflowY = "visible";
    }
  });
});
