"""
Module mã hóa Header 'ua' cho hệ thống đào tạo SGU (thongtindaotao.sgu.edu.vn)
Thuật toán reverse-engineered từ script portal của AQTech/PSC.
"""

import base64
import random
import time


class SguEncryptor:
    """
    Tạo header 'ua' bắt buộc cho mọi request gửi tới API của trường SGU.
    Thuật toán kết hợp tên endpoint, timestamp, bitwise XOR với seed key và base64 encoding.
    """

    def __init__(self):
        self.cn = "%\\6SaCzTYFe~Wua?ak"
        self.a = "Phapix"
        raw_seed = [
            0x3A, 0x2B, 0xC5, 0x85, 0x4, 0xA5, 0x6E, 0x3, 0x2C, 0xCA, 0xBA, 0x1C,
            0x76, 0xB1, 0x20, 0x5E, 0xDB, 0x6, 0xC7, 0x1B, 0x65, 0xBF, 0x42, 0x73,
            0xEA, 0x78, 0xA, 0xEC, 0x68, 0x6C, 0x4A, 0xF7, 0x44, 0xC6, 0x3E, 0xCB,
            0x11, 0x66, 0xB9, 0x2A,
        ]
        self.sc = raw_seed[-36:-4]

    def _rk(self, index: int) -> list[int]:
        step = (index % 3) + 1
        return [self.sc[(index + t * step) % len(self.sc)] for t in range(10)]

    def _ec(self, input_str: str, key: int) -> list[int]:
        reversed_key = self._rk(key)[::-1]
        char_codes = [ord(c) for c in input_str]
        extended_key = (reversed_key * ((len(char_codes) // len(reversed_key)) + 1))[:len(char_codes)]
        return [code ^ extended_key[i] for i, code in enumerate(char_codes)]

    def _mc(self, s: str, length: int, offset: int) -> str:
        return s[-length:][:length - offset]

    def isapi(self, endpoint: str) -> str:
        """
        Trích xuất tên API sau tiền tố '/api/' để mã hóa.
        Ví dụ: '/api/dkmh/w-locsinhvieninfo' -> 'DKMH/W-LOCSINHVIENINFO'
        """
        prefix = self._mc(self.a, 4, 1)  # 'api'
        ep = endpoint.lower() if endpoint else ""
        if ep.startswith(prefix + "/"):
            ep = "/" + ep
        if ("/" + prefix + "/") in ep:
            return ep.split("/" + prefix + "/")[1].upper()
        return ""

    def gc(self, input_str: str) -> str:
        """Sinh chuỗi mã hóa với timestamp ngẫu nhiên"""
        ts = int(time.time() * 1000)
        r1 = random.randint(10, 99)
        r2 = random.randint(10, 99)
        key_str = f"{r1}{ts}{r2}{input_str}"
        r3 = random.randint(0, 31)
        encrypted_chars = [r3 + 32] + self._ec(key_str, r3)
        return base64.b64encode(bytes(encrypted_chars)).decode("utf-8")

    def generate_ua_header(self, endpoint: str) -> str:
        """
        Tạo giá trị header 'ua' hoàn chỉnh từ URL endpoint.
        """
        api_name = self.isapi(endpoint)
        return self.gc(api_name)
