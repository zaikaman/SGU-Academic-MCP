"""
Unit tests cho module SguEncryptor (Mã hóa header 'ua' của SGU)
"""

import base64

from sgu_mcp.core.crypto import SguEncryptor


def test_isapi_extraction():
    enc = SguEncryptor()
    assert enc.isapi("/api/dkmh/w-locsinhvieninfo") == "DKMH/W-LOCSINHVIENINFO"
    assert enc.isapi("api/dkmh/w-locsinhvieninfo") == "DKMH/W-LOCSINHVIENINFO"
    assert enc.isapi("/api/auth/login") == "AUTH/LOGIN"
    assert enc.isapi("/api/web/w-locdstkbtuanusertheohocky") == "WEB/W-LOCDSTKBTUANUSERTHEOHOCKY"
    assert (
        enc.isapi("https://thongtindaotao.sgu.edu.vn/api/web/w-locdshocphisv")
        == "WEB/W-LOCDSHOCPHISV"
    )
    assert enc.isapi("/not-an-endpoint") == ""
    assert enc.isapi("") == ""


def test_ua_header_generation():
    enc = SguEncryptor()
    endpoint = "/api/dkmh/w-locsinhvieninfo"
    ua = enc.generate_ua_header(endpoint)

    assert isinstance(ua, str)
    assert len(ua) > 20

    # Phải giải mã được dạng base64
    decoded = base64.b64decode(ua)
    assert len(decoded) > 10

    # Mỗi lần sinh phải có timestamp và random khác nhau (dynamic header)
    ua2 = enc.generate_ua_header(endpoint)
    assert ua != ua2
