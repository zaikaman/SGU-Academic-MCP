"""
Unit tests cho module SguApiClient (sgu_mcp/core/sgu_client.py)
Mocking HTTP requests để kiểm thử toàn diện 100% các nhánh
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from sgu_mcp.config import settings
from sgu_mcp.core.sgu_client import SguApiClient


@pytest.mark.asyncio
async def test_sgu_client_init(tmp_path):
    client = SguApiClient(base_url="https://test.sgu.edu.vn/")
    assert client.base_url == "https://test.sgu.edu.vn"

    default_client = SguApiClient()
    assert default_client.base_url == settings.portal_url.rstrip("/")


def test_get_headers():
    client = SguApiClient()
    client.access_token = None

    # Without token
    headers_no_token = client._get_headers("/api/test")
    assert "ua" in headers_no_token
    assert "Authorization" not in headers_no_token

    # With client.access_token
    client.access_token = "client_tok"
    headers_client_token = client._get_headers("/api/test")
    assert headers_client_token["Authorization"] == "Bearer client_tok"

    # With explicit token override
    headers_override = client._get_headers("/api/test", token="override_tok")
    assert headers_override["Authorization"] == "Bearer override_tok"


@pytest.mark.asyncio
async def test_login_missing_credentials(monkeypatch):
    client = SguApiClient()
    monkeypatch.setattr(settings, "student_id", None)
    monkeypatch.setattr(settings, "password", None)

    with pytest.raises(ValueError, match="Cần cung cấp tên đăng nhập"):
        await client.login(username=None, password=None)


@pytest.mark.asyncio
async def test_login_success():
    client = SguApiClient()

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "access_token": "test_access_token",
        "name": "Nguyễn Văn A",
        "expires_in": 7200,
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        res = await client.login("3122410001", "password123")

        assert res["success"] is True
        assert res["student_id"] == "3122410001"
        assert res["name"] == "Nguyễn Văn A"
        assert res["access_token"] == "test_access_token"
        assert client.access_token == "test_access_token"
        assert client.current_student_id == "3122410001"


@pytest.mark.asyncio
async def test_login_success_fullname_fallback():
    client = SguApiClient()

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "access_token": "test_token_2",
        "FullName": "Trần Thị B",
        "expires_in": 3600,
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        res = await client.login("3122410002", "password456")

        assert res["success"] is True
        assert res["name"] == "Trần Thị B"


@pytest.mark.asyncio
async def test_login_failure():
    client = SguApiClient()

    # Case 1: with message
    mock_resp1 = MagicMock()
    mock_resp1.status_code = 400
    mock_resp1.json.return_value = {"message": "Tài khoản hoặc mật khẩu không chính xác."}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp1
        res = await client.login("3122410001", "wrong_pass")
        assert res["success"] is False
        assert "không chính xác" in res["error"]

    # Case 2: with error_description
    mock_resp2 = MagicMock()
    mock_resp2.status_code = 401
    mock_resp2.json.return_value = {"error_description": "Invalid credentials"}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp2
        res = await client.login("3122410001", "wrong_pass")
        assert res["success"] is False
        assert res["error"] == "Invalid credentials"

    # Case 3: generic error
    mock_resp3 = MagicMock()
    mock_resp3.status_code = 500
    mock_resp3.json.return_value = {}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp3
        res = await client.login("3122410001", "wrong_pass")
        assert res["success"] is False
        assert res["error"] == "Đăng nhập thất bại"


@pytest.mark.asyncio
async def test_post_api_cache_hit(tmp_path):
    client = SguApiClient()
    client.cache.db_path = str(tmp_path / "test_cache_client.db")
    client.cache._init_db()

    client.cache.set("cached_key", {"data": "cached_val"})
    res = await client._post_api("/api/test", cache_key="cached_key")
    assert res == {"data": "cached_val"}


@pytest.mark.asyncio
async def test_post_api_no_token_no_credentials(monkeypatch):
    client = SguApiClient()
    client.access_token = None
    monkeypatch.setattr(settings, "student_id", None)
    monkeypatch.setattr(settings, "password", None)

    with pytest.raises(PermissionError, match="Chưa có Bearer Token SGU"):
        await client._post_api("/api/test")


@pytest.mark.asyncio
async def test_post_api_auto_login_success(monkeypatch, tmp_path):
    client = SguApiClient()
    client.cache.db_path = str(tmp_path / "test_cache_autologin.db")
    client.cache._init_db()
    client.access_token = None

    monkeypatch.setattr(settings, "student_id", "3122410001")
    monkeypatch.setattr(settings, "password", "pass123")

    mock_login = AsyncMock(return_value={"success": True, "access_token": "auto_token"})
    monkeypatch.setattr(client, "login", mock_login)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"code": 200, "data": [1, 2, 3]}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        res = await client._post_api("/api/test", cache_key="new_key")
        assert res == {"code": 200, "data": [1, 2, 3]}
        assert client.cache.get("new_key") == {"code": 200, "data": [1, 2, 3]}


@pytest.mark.asyncio
async def test_post_api_auto_login_failure(monkeypatch):
    client = SguApiClient()
    client.access_token = None

    monkeypatch.setattr(settings, "student_id", "3122410001")
    monkeypatch.setattr(settings, "password", "pass123")

    mock_login = AsyncMock(return_value={"success": False, "error": "Login failed"})
    monkeypatch.setattr(client, "login", mock_login)

    with pytest.raises(PermissionError, match="Chưa xác thực SGU: Login failed"):
        await client._post_api("/api/test")


@pytest.mark.asyncio
async def test_post_api_http_error():
    client = SguApiClient()
    client.access_token = "valid_tok"

    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "Internal Server Error"

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        res = await client._post_api("/api/error")
        assert res["success"] is False
        assert "HTTP 500" in res["error"]
        assert res["details"] == "Internal Server Error"


@pytest.mark.asyncio
async def test_api_wrapper_methods(monkeypatch):
    client = SguApiClient()
    client.access_token = "tok"
    client.current_student_id = "3122410099"

    mock_post = AsyncMock()
    monkeypatch.setattr(client, "_post_api", mock_post)

    # get_student_info
    mock_post.return_value = {"code": 200, "data": {"ma_sv": "3122410099"}}
    res = await client.get_student_info()
    assert res["data"]["ma_sv"] == "3122410099"
    mock_post.assert_called_with(
        "/api/dkmh/w-locsinhvieninfo", payload={}, cache_key="student_info_3122410099", ttl=86400
    )

    # get_registered_courses
    mock_post.return_value = {"code": 200, "data": {"ds_kqdkmh": []}}
    res = await client.get_registered_courses()
    assert "ds_kqdkmh" in res["data"]

    # get_weekly_schedule
    res_sched = await client.get_weekly_schedule("20241")
    assert res_sched == res

    # get_exam_schedule with success
    mock_post.return_value = {"code": 200, "data": [{"ten_mon": "Toán"}]}
    res_exam = await client.get_exam_schedule("20241")
    assert res_exam["code"] == 200

    # get_exam_schedule with fallback (code != 200 or empty)
    mock_post.return_value = {"code": 404}
    res_exam_fallback = await client.get_exam_schedule()
    assert res_exam_fallback["success"] is True
    assert "chưa công bố lịch thi" in res_exam_fallback["thong_bao"]

    # get_grades (with and without semester_id)
    mock_post.return_value = {"code": 200, "data": {"ds_diem_hocky": []}}
    await client.get_grades("20241")
    await client.get_grades(None)

    # get_tuition
    mock_post.return_value = {"code": 200, "data": {}}
    await client.get_tuition()

    # get_notifications
    mock_post.return_value = {"code": 200, "data": {"ds_thong_bao": []}}
    await client.get_notifications(limit=5)

    # get_course_catalog
    mock_post.return_value = {"code": 200, "data": {"ds_nhom_to": []}}
    await client.get_course_catalog(page=2, limit=25)


@pytest.mark.asyncio
async def test_get_student_info_no_current_student(monkeypatch):
    client = SguApiClient()
    client.access_token = "tok"
    client.current_student_id = None

    mock_post = AsyncMock(return_value={"code": 200})
    monkeypatch.setattr(client, "_post_api", mock_post)

    await client.get_student_info()
    mock_post.assert_called_with(
        "/api/dkmh/w-locsinhvieninfo", payload={}, cache_key="student_info_current", ttl=86400
    )


@pytest.mark.asyncio
async def test_post_api_without_cache_key(monkeypatch):
    client = SguApiClient()
    client.access_token = "tok"

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"code": 200, "data": "ok"}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        res = await client._post_api("/api/test", payload={}, cache_key=None)
        assert res == {"code": 200, "data": "ok"}

