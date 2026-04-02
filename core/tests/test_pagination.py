from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from core.pagination import CustomPagination

FAKE_DATA = list(range(1, 201))


def make_request(query_string: str = ""):
    factory = APIRequestFactory()
    request = factory.get(f"/{query_string}")
    return Request(request)


def test_pagination_default_page_size():
    paginator = CustomPagination()
    request = make_request()
    qs = paginator.paginate_queryset(FAKE_DATA, request)
    assert len(qs) == 10  # type: ignore


def test_pagination_size_query_param():
    paginator = CustomPagination()
    request = make_request("?size=5")
    qs = paginator.paginate_queryset(FAKE_DATA, request)
    assert len(qs) == 5  # type:ignore


def test_pagination_max_size():
    paginator = CustomPagination()
    request = make_request("?size=500")
    qs = paginator.paginate_queryset(FAKE_DATA, request)
    assert len(qs) == 100  # type:ignore


def test_pagination_correct_next_page():
    paginator = CustomPagination()
    request = make_request("?page=2")
    qs = paginator.paginate_queryset(FAKE_DATA, request)
    assert qs[0] == 11  # type:ignore


def test_pagination_has_correct_fields():
    paginator = CustomPagination()
    request = make_request()
    paginator.paginate_queryset(FAKE_DATA, request)
    response = paginator.get_paginated_response([])
    assert "count" in response.data  # type:ignore
    assert "next" in response.data  # type:ignore
    assert "previous" in response.data  # type:ignore
    assert "results" in response.data  # type:ignore


def test_pagination_first_page_without_previous():
    paginator = CustomPagination()
    request = make_request()
    paginator.paginate_queryset(FAKE_DATA, request)
    response = paginator.get_paginated_response([])
    assert response.data["previous"] is None  # type:ignore


def test_pagination_last_page_without_next():
    paginator = CustomPagination()
    request = make_request("?page=20")  # 200 itens / 10 por página = 20 páginas
    paginator.paginate_queryset(FAKE_DATA, request)
    response = paginator.get_paginated_response([])
    assert response.data["next"] is None  # type:ignore
