# -*- coding: utf-8 -*-
"""全局测试配置：环境地址、测试账号、AI 慢用例开关。
所有值均可用环境变量覆盖，便于本地/CI 切换。"""
import os

# 被测 Java 服务基址（前端经 Vite 代理最终也指向它）
BASE_URL = os.getenv("AIWEAR_BASE_URL", "http://127.0.0.1:8081")

# 本地测试 Redis（用于注入验证码，绕过真实邮件；仅测试环境使用）
REDIS_HOST = os.getenv("AIWEAR_REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("AIWEAR_REDIS_PORT", "6379"))

# 用户名+密码 登录账号（auth 接口对不含 @ 的账号：不存在即自动注册）
AUTO_USER = os.getenv("AIWEAR_AUTO_USER", "autotest_user")
AUTO_PWD = os.getenv("AIWEAR_AUTO_PWD", "Auto@123456")

# 第二个账号，用于越权/隔离测试
AUTO_USER2 = os.getenv("AIWEAR_AUTO_USER2", "autotest_user_b")
AUTO_PWD2 = os.getenv("AIWEAR_AUTO_PWD2", "Auto@B123456")

# 邮箱验证码登录用的测试邮箱（验证码从 Redis 直接读取，不真正收邮件）
AUTO_EMAIL = os.getenv("AIWEAR_AUTO_EMAIL", "autotest_mail@qq.com")

# 是否执行调用大模型的慢用例（编辑/合并，单次 30~60s 且产生 API 费用）
# 默认关闭；设 RUN_AI=1 开启
RUN_AI = os.getenv("RUN_AI", "0") == "1"

# 通用请求超时（秒）。AI 用例单独放宽
TIMEOUT = int(os.getenv("AIWEAR_TIMEOUT", "30"))
AI_TIMEOUT = int(os.getenv("AIWEAR_AI_TIMEOUT", "180"))

# 测试用样例图片（项目 uploads 目录下已存在的真实服装图）
SAMPLE_IMAGE = os.getenv(
    "AIWEAR_SAMPLE_IMAGE",
    r"D:\code\项目\AiWearJava\uploads\images\1936d0e99a6441c49f9c62168aa81043.jpg",
)
SAMPLE_IMAGE2 = os.getenv(
    "AIWEAR_SAMPLE_IMAGE2",
    r"D:\code\项目\AiWearJava\uploads\images\271e9f7158cb43dbb58418ac0fe32097.jpg",
)
