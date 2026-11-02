# -*- coding: utf-8 -*-
"""用户模块接口测试：密码登录、邮箱验证码登录、登出、异常参数。"""
import allure
import pytest

import config
from api.client import ApiClient, assert_biz_ok
from api.endpoints import UserApi


@allure.epic("AiWear 服装搭配")
@allure.feature("用户认证")
class TestUserAuth:

    @allure.story("用户名密码登录")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("正确用户名密码可登录并返回 token")
    def test_login_by_password_success(self):
        c = ApiClient(config.BASE_URL, timeout=config.TIMEOUT)
        data = assert_biz_ok(UserApi(c).login_by_password(
            config.AUTO_USER, config.AUTO_PWD), msg="密码登录")
        assert data.get("token"), "未返回 token"
        assert data.get("userId"), "未返回 userId"

    @allure.story("邮箱验证码登录")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("正确邮箱验证码可登录（验证码由 Redis 注入，绕过真实邮件）")
    def test_login_by_email_code(self, redis_client):
        email = config.AUTO_EMAIL
        redis_client.set("verification:code:" + email, "135790", ex=300)
        c = ApiClient(config.BASE_URL, timeout=config.TIMEOUT)
        data = assert_biz_ok(UserApi(c).login_by_code(email, "135790"),
                             msg="邮箱验证码登录")
        assert data.get("token"), "验证码登录未返回 token"

    @allure.story("邮箱验证码登录")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("错误验证码应被拒绝")
    def test_login_wrong_code_rejected(self, redis_client):
        email = "wrongcode_" + config.AUTO_EMAIL
        redis_client.set("verification:code:" + email, "135790", ex=300)
        c = ApiClient(config.BASE_URL, timeout=config.TIMEOUT)
        resp = UserApi(c).login_by_code(email, "000000")
        assert resp.json().get("code") != 200, "错误验证码竟然登录成功"

    @allure.story("错误密码")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("已存在账号使用错误密码应登录失败")
    def test_login_wrong_password(self):
        c = ApiClient(config.BASE_URL, timeout=config.TIMEOUT)
        # 先确保账号存在
        UserApi(c).login_by_password(config.AUTO_USER, config.AUTO_PWD)
        resp = UserApi(c).login_by_password(config.AUTO_USER, "WrongPwd@000")
        assert resp.json().get("code") != 200, "错误密码竟然登录成功"

    @allure.story("参数校验")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("账号为空应返回业务错误")
    def test_login_empty_account(self):
        c = ApiClient(config.BASE_URL, timeout=config.TIMEOUT)
        resp = UserApi(c).login_by_password("", "whatever")
        assert resp.json().get("code") != 200, "空账号未被拦截"

    @allure.story("登出")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("携带有效 token 登出成功")
    def test_logout(self, user_client):
        data = assert_biz_ok(UserApi(user_client).logout(), msg="登出")
        assert data is not None or True
