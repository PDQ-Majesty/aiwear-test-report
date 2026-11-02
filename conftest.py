# -*- coding: utf-8 -*-
"""pytest fixtures：客户端、登录态、样例数据。登录用 用户名+密码 流程，
不依赖真实邮件；邮箱验证码流程单独在用例里通过 Redis 注入验证。"""
import allure
import pytest
import redis

import config
from api.client import ApiClient, assert_biz_ok
from api.endpoints import UserApi, FileApi, RecordApi


@pytest.fixture(scope="session")
def anon_client():
    return ApiClient(config.BASE_URL, token=None, timeout=config.TIMEOUT)


@allure.step("登录并获取 token: {account}")
def _login(account, password):
    c = ApiClient(config.BASE_URL, timeout=config.TIMEOUT)
    u = UserApi(c)
    resp = u.login_by_password(account, password)
    data = assert_biz_ok(resp, msg=f"账号 {account} 登录")
    assert data and data.get("token"), f"登录未返回 token: {data}"
    return data["token"], data.get("userId")


@pytest.fixture(scope="session")
def token_a():
    tok, _ = _login(config.AUTO_USER, config.AUTO_PWD)
    return tok


@pytest.fixture(scope="session")
def token_b():
    tok, _ = _login(config.AUTO_USER2, config.AUTO_PWD2)
    return tok


@pytest.fixture(scope="session")
def user_client(token_a):
    return ApiClient(config.BASE_URL, token=token_a, timeout=config.TIMEOUT)


@pytest.fixture(scope="session")
def user_client_b(token_b):
    return ApiClient(config.BASE_URL, token=token_b, timeout=config.TIMEOUT)


@pytest.fixture()
def user_api(user_client):
    return UserApi(user_client)


@pytest.fixture()
def file_api(user_client):
    return FileApi(user_client)


@pytest.fixture()
def record_api(user_client):
    return RecordApi(user_client)


@pytest.fixture()
def anon_api(anon_client):
    return UserApi(anon_client), FileApi(anon_client), RecordApi(anon_client)


@pytest.fixture(scope="session")
def uploaded_image_url(user_client):
    fa = FileApi(user_client)
    resp = fa.upload_image(config.SAMPLE_IMAGE)
    data = assert_biz_ok(resp, msg="上传样例图片1")
    url = data.get("ossUrl") or data.get("url") or data.get("fileUrl")
    assert url, f"上传响应未含图片地址: {data}"
    return url


@pytest.fixture(scope="session")
def uploaded_image_url2(user_client):
    fa = FileApi(user_client)
    resp = fa.upload_image(config.SAMPLE_IMAGE2)
    data = assert_biz_ok(resp, msg="上传样例图片2")
    url = data.get("ossUrl") or data.get("url") or data.get("fileUrl")
    assert url, f"上传响应未含图片地址: {data}"
    return url


@pytest.fixture()
def redis_client():
    """本地测试 Redis，用于读取/注入邮箱验证码。"""
    return redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT,
                       db=0, decode_responses=True,
                       socket_timeout=5, socket_connect_timeout=5)
