# AiWear 服装搭配 AI 应用 · 测试报告与自动化工程

> 在线测试报告（Allure）：本仓库由 GitHub Pages 自动发布，链接见 README 顶部/仓库 About。

## 1. 被测系统简介

基于 LangChain 的 AI 服装搭配应用，三服务架构：

```
Vue3 前端(Vite) ──> Java Spring Boot(:8081) ──> Python Flask + LangChain(:5000)
                        │   │                        │
                      MySQL Redis              CLIP向量检索 / DashScope图像模型
```

核心链路：注册登录（邮箱验证码/JWT）→ 图片上传（OSS+向量化入库）→ 文搜图/图搜图 → AI 图片编辑/双图合并 → 历史记录。

## 2. 测试策略

| 层级 | 工具 | 范围 |
|---|---|---|
| 接口自动化 | pytest + requests + Allure | Java 全部 8 个端点：正常/异常/边界/鉴权/越权 |
| 契约验证 | 接口自动化内嵌 | Java↔Python 4 个 API 契约的可用性 |
| 安全测试 | 接口自动化 | 无/篡改 token、跨用户数据隔离、SQL 注入、登出失效性 |
| AI 效果评测 | 慢用例（`RUN_AI=1` 门控） | 编辑/合并出图链路 + 耗时采集（大模型输出不确定，采用结构化断言+耗时记录） |

设计要点：
- **验证码旁路**：测试环境直接向 Redis 注入验证码完成邮箱登录用例，不依赖真实邮件（`test_login_by_email_code`）；
- **数据脱敏**：Allure 附件写盘前对 `password/token/verificationCode` 与 JWT 串统一脱敏（`api/client.sanitize`），保证报告可公开；
- **费用可控**：调用大模型的慢用例默认 skip，按需开启。

## 3. 缺陷与发现（首轮）

| 编号 | 级别 | 描述 |
|---|---|---|
| BUG-001 | 中 | 合并接口耗时(≈60s)达到前端 axios 超时阈值，页面呈现"假失败"，实际结果已落库（历史记录可见） |
| FIND-002 | 低 | 搜索接口无入参校验，下游异常被捕获后返回空列表且业务码仍为成功 |
| FIND-003 | 中 | 登出仅删除 Redis 缓存，鉴权只验签名——登出后 token 依然可用，无服务端失效 |
| FIND-004 | 低 | 注册用户名无格式校验，SQL 注入串被当作合法用户名入库（参数化查询未造成绕过，但产生脏数据） |
| FIND-005 | 高(环境) | 共享 Redis 因磁盘持久化故障(MISCONF)拒写，导致登录/注册全链路不可用——定位过程见报告附录 |

## 4. 如何复现

```bash
# 1) 拉起依赖中间件（MySQL:3307 / Redis:6379）
docker compose up -d

# 2) 启动被测服务（Java :8081 / Python :5000，见各自仓库）

# 3) 运行测试并生成报告
pip install -r requirements.txt
pytest                                    # 快速用例（不产生模型费用）
RUN_AI=1 pytest                           # 含 AI 编辑/合并慢用例
allure generate report/allure-results -o report/html --clean
```

## 5. 目录结构

```
├── api/            接口封装层（client + 三业务域 endpoints）
├── tests/          用例层：user / file / search / ai / security
├── config.py       环境与账号配置（全部支持环境变量覆盖）
├── conftest.py     登录态、双账号、样例图等 fixtures
├── docker-compose.yml  测试中间件一键环境
└── report/html/    Allure 静态报告（Pages 发布物）
```

Continuous deployment: push → GitHub Actions → Pages。
