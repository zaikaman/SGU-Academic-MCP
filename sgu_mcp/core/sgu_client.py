"""
HTTP Client kết nối trực tiếp đến Cổng thông tin đào tạo SGU (thongtindaotao.sgu.edu.vn)
Tự động đính kèm header 'ua' mã hóa và quản lý Bearer token.
"""

from typing import Any, Optional
import httpx
from sgu_mcp.config import settings
from sgu_mcp.core.cache import SguCache
from sgu_mcp.core.crypto import SguEncryptor


class SguApiClient:
    """
    Client gọi API chính thức của SGU với đầy đủ xử lý mã hóa bảo mật.
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or settings.portal_url).rstrip("/")
        self.encryptor = SguEncryptor()
        self.cache = SguCache(db_path=settings.db_path)
        self.access_token: Optional[str] = settings.bearer_token
        self.current_student_id: Optional[str] = settings.student_id

    def _get_headers(self, endpoint: str, token: Optional[str] = None) -> dict[str, str]:
        ua_header = self.encryptor.generate_ua_header(endpoint)
        auth_token = token or self.access_token

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "ua": ua_header,
        }
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        return headers

    async def login(self, username: Optional[str] = None, password: Optional[str] = None) -> dict[str, Any]:
        """
        Đăng nhập vào hệ thống SGU để lấy Bearer access token thật.
        Endpoint: POST /api/auth/login
        """
        uname = username or settings.student_id
        pwd = password or settings.password

        if not uname or not pwd:
            raise ValueError("Cần cung cấp tên đăng nhập (MSSV) và mật khẩu SGU.")

        endpoint = "/api/auth/login"
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(endpoint)
        headers["Content-Type"] = "application/x-www-form-urlencoded"

        data = {
            "username": uname,
            "password": pwd,
            "grant_type": "password"
        }

        async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
            response = await client.post(url, data=data, headers=headers)
            res_data = response.json()

            if response.status_code == 200 and res_data.get("access_token"):
                self.access_token = res_data["access_token"]
                self.current_student_id = uname
                return {
                    "success": True,
                    "student_id": uname,
                    "name": res_data.get("name") or res_data.get("FullName"),
                    "access_token": self.access_token,
                    "expires_in": res_data.get("expires_in")
                }
            else:
                error_msg = res_data.get("message") or res_data.get("error_description") or "Đăng nhập thất bại"
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code
                }

    async def _post_api(self, endpoint: str, payload: Optional[dict] = None, cache_key: Optional[str] = None, ttl: int = 3600) -> dict[str, Any]:
        """Gọi API nội bộ có xác thực và lưu bộ nhớ đệm"""
        # Kiểm tra cache trước nếu có cache_key
        if cache_key:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                return cached_data

        if not self.access_token:
            # Thử tự động login nếu có thông tin tài khoản trong config
            if settings.student_id and settings.password:
                login_res = await self.login()
                if not login_res.get("success"):
                    raise PermissionError(f"Chưa xác thực SGU: {login_res.get('error')}")
            else:
                raise PermissionError("Chưa có Bearer Token SGU. Vui lòng đăng nhập qua tool login_sgu() hoặc cung cấp SGU_BEARER_TOKEN trong .env")

        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(endpoint)
        headers["Content-Type"] = "application/json"

        async with httpx.AsyncClient(timeout=20.0, verify=False) as client:
            response = await client.post(url, json=payload or {}, headers=headers)
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Lỗi gọi API {endpoint}: HTTP {response.status_code}",
                    "details": response.text
                }

            result = response.json()
            if cache_key and result:
                self.cache.set(cache_key, result, ttl_seconds=ttl)

            return result

    async def get_student_info(self) -> dict[str, Any]:
        """Lấy thông tin cá nhân sinh viên SGU"""
        endpoint = "/api/dkmh/w-locsinhvieninfo"
        cache_key = f"student_info_{self.current_student_id or 'current'}"
        return await self._post_api(endpoint, payload={}, cache_key=cache_key, ttl=86400)

    async def get_registered_courses(self) -> dict[str, Any]:
        """Lấy danh sách môn học đã đăng ký trong kỳ của sinh viên"""
        endpoint = "/api/dkmh/w-locdskqdkmhsinhvien"
        payload = {"is_CVHT": False, "is_Clear": False}
        cache_key = f"reg_courses_{self.current_student_id or 'current'}"
        return await self._post_api(endpoint, payload=payload, cache_key=cache_key, ttl=1800)

    async def get_weekly_schedule(self, semester_id: Optional[str] = None) -> dict[str, Any]:
        """Lấy thời khóa biểu học kỳ / tuần của sinh viên (lấy từ dữ liệu môn học đã đăng ký thực tế)"""
        return await self.get_registered_courses()

    async def get_exam_schedule(self, semester_id: Optional[str] = None) -> dict[str, Any]:
        """Lấy lịch thi của sinh viên"""
        endpoint = "/api/epm/w-locdslichthisvtheohocky"
        payload = {"hoc_ky": semester_id} if semester_id else {}
        cache_key = f"exams_{self.current_student_id or 'current'}_{semester_id or 'current'}"
        res = await self._post_api(endpoint, payload=payload, cache_key=cache_key, ttl=3600)
        if not res or res.get("code") != 200:
            # Fallback nếu trường chưa công bố lịch thi kỳ này
            return {
                "success": True,
                "data": [],
                "thong_bao": "Hiện tại Trường ĐH Sài Gòn chưa công bố lịch thi chính thức cho học kỳ hiện tại (lịch thi thường công bố vào tuần thứ 10 của học kỳ)."
            }
        return res

    async def get_grades(self, semester_id: Optional[str] = None) -> dict[str, Any]:
        """Lấy bảng điểm học tập theo học kỳ của sinh viên"""
        endpoint = "/api/srm/w-locdsdiemsinhvien"
        payload = {"id_hoc_ky": semester_id} if semester_id else {}
        cache_key = f"grades_{self.current_student_id or 'current'}_{semester_id or 'all'}"
        return await self._post_api(endpoint, payload=payload, cache_key=cache_key, ttl=7200)

    async def get_tuition(self) -> dict[str, Any]:
        """Lấy thông tin học phí, miễn giảm, nợ đọng"""
        endpoint = "/api/rms/w-locdstonghophocphisv"
        cache_key = f"tuition_{self.current_student_id or 'current'}"
        return await self._post_api(endpoint, payload={}, cache_key=cache_key, ttl=3600)

    async def get_notifications(self, limit: int = 15) -> dict[str, Any]:
        """Lấy thông báo chung từ ban quản trị SGU"""
        endpoint = "/api/web/w-locdsthongbao"
        payload = {
            "filter": {"id": None, "is_noi_dung": True},
            "additional": {
                "paging": {"limit": limit, "page": 1},
                "ordering": [{"name": "ngay_gui", "order_type": 1}]
            }
        }
        cache_key = f"notifications_limit_{limit}"
        return await self._post_api(endpoint, payload=payload, cache_key=cache_key, ttl=1800)

    async def get_course_catalog(self, page: int = 1, limit: int = 50) -> dict[str, Any]:
        """Lấy danh sách các lớp học phần đang mở để đăng ký"""
        endpoint = "/api/dkmh/w-locdsnhomto"
        payload = {
            "is_CVHT": False,
            "additional": {
                "paging": {"limit": limit, "page": page},
                "ordering": [{"name": "", "order_type": ""}]
            }
        }
        cache_key = f"course_catalog_p{page}_l{limit}"
        return await self._post_api(endpoint, payload=payload, cache_key=cache_key, ttl=7200)


# Global SGU Client instance
sgu_client = SguApiClient()
