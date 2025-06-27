# AllReady API 문서화

이 프로젝트에서는 `drf-spectacular` 패키지를 사용하여 자동으로 API 문서를 생성합니다.

## 🚀 사용법

### 1. 개발 서버 실행

```bash
python manage.py runserver
```

### 2. API 문서 접근

개발 서버 실행 후 다음 URL들을 통해 API 문서에 접근할 수 있습니다:

-   **Swagger UI**: `http://localhost:8000/api/docs/`

    -   인터랙티브한 API 문서
    -   API를 직접 테스트할 수 있는 환경 제공

-   **ReDoc**: `http://localhost:8000/api/redoc/`

    -   깔끔하고 읽기 쉬운 API 문서
    -   더 나은 가독성을 위한 레이아웃

-   **OpenAPI Schema**: `http://localhost:8000/api/schema/`
    -   원시 OpenAPI 3.0 스키마 JSON

## 📋 API 엔드포인트 개요

### Feed API

-   **POST** `/feed/api/create/` - 피드 생성
-   **GET** `/feed/api/feeds/` - 피드 목록 조회
-   **GET** `/feed/api/{feed_id}/` - 피드 상세 조회
-   **POST** `/feed/api/{feed_id}/like/` - 피드 좋아요/취소
-   **POST** `/feed/api/{feed_id}/bookmark/` - 피드 북마크/취소
-   **GET** `/feed/api/myfeeds/` - 내가 작성한 피드 목록
-   **GET** `/feed/api/mybookmarks/` - 내가 북마크한 피드 목록

### Planner API

#### 여행 계획 관리

-   **GET** `/api/plan/travelplan/` - 여행 계획 목록
-   **POST** `/api/plan/travelplan/` - 여행 계획 생성
-   **GET** `/api/plan/travelplan/{id}/` - 여행 계획 상세
-   **PUT/PATCH** `/api/plan/travelplan/{id}/` - 여행 계획 수정
-   **DELETE** `/api/plan/travelplan/{id}/` - 여행 계획 삭제
-   **POST** `/api/plan/travelplan/{id}/confirm/` - 여행 계획 확정

#### 목적지 관리

-   **GET** `/api/plan/destination/` - 목적지 목록 조회
-   **POST** `/api/plan/destination/` - 목적지 추가/수정

#### 출발지 관리

-   **GET** `/api/plan/origin/` - 출발지 목록 조회
-   **POST** `/api/plan/origin/` - 출발지 추가/수정

#### 템플릿 페이지

-   **GET** `/plan/start/` - 여행 계획 시작 페이지 (원본 템플릿 URL)
-   **GET** `/api/plan/template/start/` - 여행 계획 시작 페이지 (API 문서화된 버전)

### Flight API

-   **GET** `/api/flight/search/` - 항공편 검색
-   **GET** `/api/flight/candidates/` - 항공편 후보 조회
-   **POST** `/api/flight/select/` - 항공편 선택
-   **POST** `/api/flight/book/` - 항공편 예약
-   **GET** `/api/flight/airport-near-origin/` - 출발지 근처 공항 조회
-   **GET** `/api/flight/airport-near-dest/` - 목적지 근처 공항 조회

## 🛠️ 관리 명령어

### API 스키마 생성

```bash
# JSON 형식으로 스키마 생성
python manage.py generate_api_schema

# YAML 형식으로 스키마 생성
python manage.py generate_api_schema --format yaml

# 특정 파일명으로 저장
python manage.py generate_api_schema --output my_api_schema.json
```

### drf-spectacular 기본 명령어

```bash
# 스키마 검증
python manage.py spectacular --validate

# 스키마를 파일로 출력
python manage.py spectacular --file schema.yml
```

## 🎯 인증

API 문서에서 인증이 필요한 엔드포인트를 테스트하려면:

1. Django 관리자 페이지(`/admin/`)에서 로그인
2. 세션 기반 인증이 자동으로 적용됨
3. Swagger UI에서 "Authorize" 버튼을 통해 인증 상태 확인

## 📚 추가 기능

### 태그별 API 그룹화

-   **Feed**: 피드 관련 API
-   **Planner**: 여행 계획 관련 API
-   **Flight**: 항공편 관련 API

### 검색 및 필터링

-   피드 API에서 검색어, 정렬 기준 지원
-   여행 계획 API에서 날짜, 제목별 정렬 지원

### 페이지네이션

-   기본 페이지 크기: 12개
-   `page` 파라미터로 페이지 이동
-   `page_size` 파라미터로 크기 조정 (최대: 120개)

## 🔧 개발자를 위한 팁

### 새로운 API에 문서화 추가하기

```python
from drf_spectacular.utils import extend_schema
from drf_spectacular.openapi import OpenApiParameter

@extend_schema(
    tags=["YourApp"],
    summary="API 간단 설명",
    description="API 상세 설명",
    parameters=[
        OpenApiParameter(
            name="param_name",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="파라미터 설명",
        ),
    ],
)
class YourAPIView(APIView):
    # 구현
    pass
```

### ViewSet에 문서화 추가하기

```python
@extend_schema_view(
    list=extend_schema(tags=["YourApp"], summary="목록 조회"),
    create=extend_schema(tags=["YourApp"], summary="생성"),
    retrieve=extend_schema(tags=["YourApp"], summary="상세 조회"),
)
class YourViewSet(viewsets.ModelViewSet):
    # 구현
    pass
```

## 🚨 주의사항

-   개발 환경에서만 사용하세요 (`DEBUG = True`)
-   프로덕션 환경에서는 API 문서 URL을 비활성화하거나 접근 제한을 설정하세요
-   민감한 정보가 API 문서에 노출되지 않도록 주의하세요
