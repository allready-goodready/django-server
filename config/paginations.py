from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    """
    기본 페이지네이션:
    - 한 페이지당 12개
    - query param으로 page_size 조정 가능 (최대 100)
    """

    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 100
