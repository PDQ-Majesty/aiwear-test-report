# -*- coding: utf-8 -*-
"""HTTP 客户端封装：统一 base_url、鉴权头、响应断言、Allure 附件。
附件写入前对密码/token 脱敏，保证报告可公开。"""
import re

import allure
import requests

# 键/值均可能被单引号(Python repr)或双引号(JSON)包裹，两种都要覆盖
_SECRET_KEY_RE = re.compile(
    r"((?:['\"](?:password|token|verificationCode|access[_-]?key[_-]?secret)['\"]\s*:\s*))"
    r"(['\"])[^'\"]*\2",
    re.IGNORECASE,
)


def sanitize(text):
    """把 dict/JSON 文本里的敏感字段值替换为 ***，并对 JWT 串截断。
    兼容 Python repr(单引号) 与 JSON(双引号) 两种序列化形态。"""
    text = _SECRET_KEY_RE.sub(r'\1\2***\2', str(text))
    text = re.sub(r"eyJ[A-Za-z0-9_\-]{10,}[.][A-Za-z0-9_\-.]+",
                  lambda m: m.group(0)[:12] + "...<masked>", text)
    return text


class ApiClient:
    """轻量 API 客户端。token 为空表示匿名请求（用于鉴权类用例）。"""

    def __init__(self, base_url, token=None, timeout=30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def set_token(self, token):
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        else:
            self.session.headers.pop("Authorization", None)

    def _attach(self, name, content):
        allure.attach(sanitize(content), name=name,
                      attachment_type=allure.attachment_type.TEXT)

    def request(self, method, path, *, json=None, params=None,
                files=None, data=None, headers=None, timeout=None):
        url = self.base_url + path
        resp = self.session.request(
            method, url, json=json, params=params, files=files,
            data=data, headers=headers, timeout=timeout or self.timeout,
        )
        self._attach(f"{method} {path} 请求",
                     {"json": json, "params": params, "data": data})
        try:
            body = resp.json()
        except ValueError:
            body = resp.text
        self._attach(f"{method} {path} 响应[HTTP {resp.status_code}]", body)
        return resp

    def get(self, path, **kw):
        return self.request("GET", path, **kw)

    def post(self, path, **kw):
        return self.request("POST", path, **kw)


def assert_biz_ok(resp, msg=""):
    """断言 HTTP 200 且业务 code==200，返回 data 字段。"""
    assert resp.status_code == 200, f"{msg} HTTP={resp.status_code} body={resp.text[:200]}"
    body = resp.json()
    assert body.get("code") == 200, f"{msg} 业务码={body.get('code')} message={body.get('message')}"
    return body.get("data")
