import pytest


@pytest.fixture
def context(request_factory, admin_user):
    request = request_factory.post("/")
    request.user = admin_user
    return {"request": request}
