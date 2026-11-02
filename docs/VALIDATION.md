# 0.2.0a1 validation / 验证记录

2026-11-02. Scope: local tools, installation and a small functional host check; **not a performance acceptance report**.

| Check / 检查 | Result / 结果 |
|---|---|
| Clean Python 3.9.6 environment, installed wheel, Pillow 11.3.0 | 29/29 tests passed with runtime network/process calls blocked / 禁止运行时网络与子进程后，29 项测试通过 |
| Compression and cropping / 压缩与裁剪 | Output bytes checked; no larger compressed replacement; native crop pixels, alpha and coordinate mapping checked / 检查实际字节、不增大替换文件、原始裁剪像素、透明度和坐标映射 |
| Persistence and recall / 保存与召回 | Reopen registry; exact original-byte recall; corruption, stale results and conflicts checked / 重启读取、原图字节一致、损坏及过期结果与冲突保护通过 |
| Installation / 安装 | Both host layouts, packaged templates, overwrite refusal, wrapper execution and paths with spaces checked / 两种目录、打包资源、拒绝覆盖、脚本运行和含空格路径通过 |
| Audit regression checks / 审计问题回归 | Independent pending handoff files; non-object result JSON returns a structured error without changing state / 多个待处理视觉任务使用独立交接文件；非对象结果 JSON 返回结构化错误且不改变状态 |
| Skill validation / skill 检查 | skill-creator quick validator passed / 格式验证通过 |
| Codex 0.162.1 functional session / 功能会话 | Installed skill discovered; wrapper invoked; native `icm-visual-worker` spawned; synthetic title read as `ICM TEST 4729`; source-bound result saved; completed `prepare` returned text; recalled SHA-256 matched / 安装发现、工具调用、原生子 agent 看合成图、文字结果保存、完成后返回文字、原图哈希一致，链路通过 |
| Claude Code 2.1.294 actual session / 实际会话 | **Unverified**: local account could not receive replies; installation and file operations passed separately / **未验证**：当前本地账号无法接收回复；安装和文件操作已单独通过 |
| Independent documentation review / 独立文档审查 | Both languages, desktop and 390px previews, rendered Mermaid and navigation passed; small diagram labels on narrow screens have a text alternative / 两语桌面与窄屏预览、图示与导航通过；窄屏小字提供文字说明 |

The Codex check used the installed local CLI and the existing Codex login, not a separate model API client. It tested a synthetic reading task, not a complete ASC workflow. Worker invocation was confirmed in the session's native `spawn_agent` call with `agent_type=icm-visual-worker`. Local fixture, raw host logs and machine-specific paths remain private. The observed title and original hash were checked against the fixture; none of this measures model latency or wire bytes.

Codex 检查使用安装后的本地 CLI 和现有账号，没有额外编写模型 API 客户端。任务是读取合成图，不是真实完整 ASC 流程；会话原生调用记录确认使用 `icm-visual-worker`。原始日志、图片及本机路径不公开。标题与原图哈希已对照检查，但这些证据不包含模型延迟或网络字节测量。

**Still unverified / 仍未验证:** default-host history removal, complete real-task A/B performance, cumulative request bytes including retries/fallbacks, billing/token savings, and WebSocket repair. The existing hard acceptance threshold is unchanged. Earlier synthetic HTTP experiments belong to a separate setup; see [experiment boundaries](../experiments/README.md).

**仍未通过真实收益验收。** 本版提供可运行的 skill 与工具，不将本地压缩或一次功能会话当成真实多轮提速证据。
