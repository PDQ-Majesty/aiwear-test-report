# -*- coding: utf-8 -*-
"""文件模块接口测试：上传、我的图片、异常文件。"""
import allure

import config
from api.client import assert_biz_ok


@allure.epic("AiWear 服装搭配")
@allure.feature("图片管理")
class TestFileUpload:

    @allure.story("上传图片")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("上传合法服装图片成功并返回可访问 URL")
    def test_upload_valid_image(self, file_api):
        data = assert_biz_ok(file_api.upload_image(config.SAMPLE_IMAGE),
                             msg="上传合法图片")
        assert data.get("url"), f"响应缺少 url: {data}"
        assert data.get("url").startswith("http"), "url 非可访问地址"
        assert data.get("fileName"), "响应缺少 fileName"

    @allure.story("上传图片-异常")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("上传非图片文件(txt)应被拒绝")
    def test_upload_non_image_rejected(self, file_api):
        resp = file_api.upload_bytes(
            "evil.txt", b"hello i am not an image", "text/plain")
        assert resp.json().get("code") != 200, "非图片文件竟然上传成功"

    @allure.story("上传图片-异常")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("上传空文件应被拒绝")
    def test_upload_empty_file(self, file_api):
        resp = file_api.upload_bytes("empty.jpg", b"", "image/jpeg")
        assert resp.json().get("code") != 200, "空文件竟然上传成功"

    @allure.story("我的图片")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("上传后可在『我的图片』列表中看到")
    def test_my_images_contains_upload(self, file_api):
        up = assert_biz_ok(file_api.upload_image(config.SAMPLE_IMAGE2),
                           msg="上传用于列表校验的图片")
        url = up.get("url")
        listing = assert_biz_ok(file_api.my_images(), msg="查询我的图片")
        assert isinstance(listing, list), "我的图片应返回列表"
        assert any(url == (item.get("ossUrl") or item.get("url"))
                   for item in listing), f"列表未包含刚上传的图片 {url}"
