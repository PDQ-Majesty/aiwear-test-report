# -*- coding: utf-8 -*-
"""AI 编辑/合并慢用例（调用大模型，单次 30~60s 且产生费用）。
默认跳过；设环境变量 RUN_AI=1 执行。"""
import time

import allure
import pytest

import config
from api.client import assert_biz_ok


@allure.epic("AiWear 服装搭配")
@allure.feature("AI 图像生成")
@pytest.mark.skipif(not config.RUN_AI, reason="AI 慢用例默认跳过（设 RUN_AI=1 开启）")
class TestAiEditMerge:

    @allure.story("图片编辑")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("单图编辑返回临时URL与持久化saveUrl，并落库历史记录")
    def test_edit_image(self, file_api, record_api, uploaded_image_url):
        start = time.time()
        data = assert_biz_ok(
            file_api.edit(uploaded_image_url, "把背景换成纯白色",
                          timeout=config.AI_TIMEOUT),
            msg="图片编辑")
        cost = time.time() - start
        allure.attach(f"编辑耗时 {cost:.1f}s", name="耗时")
        assert data.get("url") or data.get("saveUrl"), "编辑未返回结果图地址"

        recs = assert_biz_ok(record_api.my(action="edit"), msg="查询edit历史")
        assert any(r.get("action") == "edit" for r in recs), "编辑未落历史记录"

    @allure.story("图片合并")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("双图合并返回结果并落库（关联缺陷BUG-001：前端60s超时导致结果不展示）")
    def test_merge_images(self, file_api, record_api,
                          uploaded_image_url, uploaded_image_url2):
        start = time.time()
        data = assert_biz_ok(
            file_api.merge(uploaded_image_url, uploaded_image_url2,
                           "把图1的上衣穿到图2人物身上", timeout=config.AI_TIMEOUT),
            msg="图片合并")
        cost = time.time() - start
        allure.attach(f"合并耗时 {cost:.1f}s（前端超时阈值=60s）", name="耗时")
        assert data.get("url") or data.get("saveUrl"), "合并未返回结果图地址"

        recs = assert_biz_ok(record_api.my(action="merge"), msg="查询merge历史")
        assert any(r.get("action") == "merge" for r in recs), "合并未落历史记录"
