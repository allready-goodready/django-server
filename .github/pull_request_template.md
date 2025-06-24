<!--
  🚀 통합 PR 템플릿
  하나의 기능 단위로 PR 생성 시 사용하세요.
  해당되지 않는 항목은 삭제한 뒤 PR 을 생성해주세요.
-->

## 📌 요약 (Summary)

<!-- PR의 목적과 주요 변경 사항을 간단히 서술하세요 -->

예) 여행 계획 생성 API 및 UI 기능 추가

---

## 📂 WBS 기반 작업 분류

- **대분류**:
  1. 여행 피드 / 2. 여행지 정보 제공 / 3. 여행 계획 생성 / 4. 사용자 인증/관리 / etc.  
     예) 3. 여행 계획 생성
- **상세 코드**:  
  FD-01, PLAN_ENV_SETUP 등

---

## ✏️ 작업 내용 (Details)

### 1. 백엔드

- **View**

  ```text
  PlanCreateView, PlanListView 등
  ```

- **Model**

  ```text
  TravelPlan, Location 등
  ```

- **URL**

  ```text
  URL: `/api/plans/`, `/api/plans/<id>/`
  ```

- **외부 API**

  ```text
  외부 API: Googlemaps.py의 GooglePlacesNearby로 공항 탐색
  ```

- **DB 마이그레이션**

  ```text
  planner/models/TravelPlan
  - title 속성 CharField → UUID
  ```

---

### 2. 프론트엔드

- **화면 요소 (HTML / Bootstrap 컴포넌트)**

  ```text
  템플릿: feed_list.html, plan_detail.html 등
  컴포넌트: Card, Modal 등
  ```

- **디자인 요소 (CSS / Bootstrap 커스터마이징)**

  ```text
  CSS 파일/클래스: static/css/feed.css 등
  선택자 오버라이드: $theme-colors, custom.scss 등
  ```

- **화면 제어 로직 (JS / Axios)**

  ```text
  JS 파일: static/js/feed.js 등
  Axios 호출: axios.get('/api/plans/'), axios.post('/api/feeds/') 등
  ```

---

## 🔗 관련 이슈 (Related Issue)

Closes #<이슈 번호>

---
