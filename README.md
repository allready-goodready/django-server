# AllReady - 여행 계획 및 피드 공유 플랫폼

## 📋 프로젝트 소개

**AllReady**는 여행자들이 여행 계획을 세우고, 여행 경험을 공유할 수 있는 통합 플랫폼입니다.
여행 계획부터 항공편 검색, 여행 후기 공유까지 한 곳에서 모든 여행 관련 서비스를 제공합니다.

## ✨ 주요 기능

### 🗓️ 여행 계획 (Travel Planner)

-   여행 계획 생성 및 관리
-   출발지 및 목적지 설정
-   여행 날짜 및 예산 설정
-   계획 상태 관리 (임시저장/확정)

### 📸 여행 피드 (Travel Feed)

-   여행 사진 및 후기 공유
-   이미지 다중 업로드 지원
-   좋아요 및 북마크 기능
-   위치 기반 피드 작성
-   피드 검색 및 필터링

### ✈️ 항공편 검색 (Flight Search)

-   실시간 항공편 검색
-   항공편 비교 및 선택
-   예약 데이터 관리
-   공항 위치 기반 검색

### 🔍 검색 및 지도 기능

-   장소 검색 (Google API 연동)
-   지도 기반 위치 선택
-   좌표 기반 위치 저장

## 🛠️ 사용 기술

### Backend

-   **Django 4.2.21** - 웹 프레임워크
-   **Django REST Framework** - API 개발
-   **MySQL** - 데이터베이스
-   **drf-spectacular** - API 문서화

### Frontend

-   **Bootstrap 5** - UI 프레임워크 (django-bootstrap5 사용)
-   **Vanilla JavaScript** - 동적 기능 구현 (피드 목록, 페이지네이션, 모달 등)
-   **jQuery 3.4.1** - 외부 라이브러리 지원
-   **Cropper.js 1.5.13** - 이미지 크롭 기능
-   **Google Material Icons** - 아이콘 라이브러리 (북마크, 검색 등)
-   **CSS3** - 커스텀 스타일링, Flexbox, Transitions

### 외부 API

-   **Google Maps API** - 지도 및 장소 검색 (Places API 포함)
-   **Amadeus API** - 항공편 검색
-   **Cloudinary** - 이미지 저장 및 관리

### 개발 도구

-   **Black** - 코드 포맷팅
-   **Flake8** - 코드 린팅
-   **django-environ** - 환경변수 관리
-   **Crispy Forms** - Django 폼 렌더링

## 📁 프로젝트 구조

```
allready/
├── config/                    # 프로젝트 설정
│   ├── settings.py           # Django 설정
│   ├── urls.py              # 메인 URL 설정
│   └── management/          # 관리 명령어
├── accounts/                 # 사용자 계정 관리
├── feed/                    # 피드 관련 기능
│   ├── models.py           # 피드, 이미지, 좋아요, 북마크 모델
│   ├── views.py            # 피드 뷰 로직
│   ├── serializers.py      # API 시리얼라이저
│   └── templates/          # 피드 템플릿
├── planner/                 # 여행 계획 기능
│   ├── models.py           # 여행계획, 위치 모델
│   ├── services.py         # 비즈니스 로직
│   └── templates/          # 계획 템플릿
├── flight/                  # 항공편 검색 기능
│   ├── models.py           # 항공편 선택 모델
│   ├── services.py         # 외부 API 연동
│   └── templates/          # 항공편 템플릿
├── static/                  # 정적 파일
│   ├── css/                # 스타일시트
│   ├── js/                 # JavaScript 파일
│   └── images/             # 이미지 파일
└── templates/               # 공통 템플릿
    ├── base.html           # 기본 템플릿
    └── common/             # 공통 컴포넌트
```

## 🖥️ 구현 화면

### 피드 관련 화면

-   **피드 목록** (`feed_list.html`) - 모든 피드 조회
-   **피드 상세** (`feed_detail.html`) - 피드 상세 정보 및 상호작용
-   **피드 작성** (`feed_create.html`) - 새 피드 작성
-   **피드 업로드** (`feed_upload.html`) - 이미지 업로드
-   **피드 크롭** (`feed_crop.html`) - 이미지 편집
-   **지도 모달** (`feed_map_modal.html`) - 위치 선택
-   **검색 모달** (`feed_search_modal.html`) - 피드 검색

### 여행 계획 화면

-   **계획 시작** (`plan_start.html`) - 여행 계획 시작 페이지
-   **출발지 선택** (`origin_select.html`) - 출발지 설정
-   **목적지 선택** (`destination_select.html`) - 목적지 설정

### 항공편 검색 화면

-   **항공편 검색** (`flight_search.html`) - 항공편 검색 및 선택

### 공통 UI 컴포넌트

-   **네비게이션 바** (`navbar.html`) - 사이트 전체 내비게이션
-   **기본 레이아웃** (`base.html`) - 전체 페이지 레이아웃

## 🚀 프로젝트 실행 방법

### 1. 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env` 파일을 생성하고 다음 내용을 추가:

```bash
# 데이터베이스 설정
DATABASE_URL=mysql://사용자명:비밀번호@localhost:3306/데이터베이스명

# 외부 API 키
GOOGLE_API_KEY=your_google_api_key
AMADEUS_CLIENT_ID=your_amadeus_client_id
AMADEUS_CLIENT_SECRET=your_amadeus_client_secret

# Cloudinary 설정 (선택사항)
CLOUDINARY_URL=cloudinary://your_cloudinary_config
```

### 3. 데이터베이스 설정

```bash
# 마이그레이션 파일 생성
python manage.py makemigrations

# 마이그레이션 실행
python manage.py migrate

# 관리자 계정 생성
python manage.py createsuperuser
```

### 4. 개발 서버 실행

```bash
# 개발 서버 시작
python manage.py runserver

# 브라우저에서 접속
# http://localhost:8000
```

### 5. API 문서 확인

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

-   **Swagger UI**: `http://localhost:8000/api/docs/`
-   **ReDoc**: `http://localhost:8000/api/redoc/`
-   **API 스키마**: `http://localhost:8000/api/schema/`

## 📚 추가 정보

### 권장 개발 환경

-   **Python**: 3.11.9
-   **Django**: 4.2.x (LTS)
-   **MySQL**: 8.4.x
-   **Node.js**: 최신 LTS (프론트엔드 도구용)

---

**AllReady** - 모든 여행 준비를 한 곳에서 ✈️🌍
