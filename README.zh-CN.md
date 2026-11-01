# Image Context Manager

**实验性 Python 组件，面向拥有 agent 请求构建权的开发者。** [English README](README.md)

长任务中，宿主可能反复发送已完成任务的截图。组件根据宿主提供的来源、版本、用途和生命周期，将合适的旧图在**后续请求副本**中替换成来源绑定文字引用，原图保存在外部；比较或召回时恢复原图。它不自动判断任务结束、视觉真值或结果是否足够，也不能替已安装的 Codex 控制隐藏历史。

## 本地运行

Python 3.9+；无需模型、密钥、Rust 或 Codex。未发布 PyPI，请从仓库安装：

```sh
git clone https://github.com/messsiii/image-context-manager.git
cd image-context-manager
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/icm-demo --out run-data/first
```

Windows 使用 `.venv\Scripts\python.exe` / `icm-demo.exe`。安装可能联网下载依赖；示例运行不联网，只生成合成图和明确标注的宿主完成事件。每次选择新的输出目录。

`report.json` 应显示 `initial:3 → retired:2 → comparison:3 → recall:3`。这验证请求副本、保护与恢复，不证明网络提速。接入需要每次从完整 canonical 历史重建请求、按实际顺序登记图片、绑定 URL hash、提交真实结果并确认后续任务足够，再在真正发送前应用计划。

- [详细宿主契约（中文）](docs/INTEGRATION.zh-CN.md)
- [English integration contract](docs/INTEGRATION.md)
- [离线可安装示例源码](src/image_context_manager/demo.py)
- [实验聚合与适用范围](experiments/README.md)

支持静态 PNG/JPEG、单一宿主有序调用。原图和 metadata 可持久化；登记和 receipt 仅在内存，重启须重建。宿主负责权限、备份、保留期、删除与 schema 适配。默认 Codex 未接通历史变换 hook；隔离 Codex 补丁仅用于研究。

历史合成 HTTP 实验 70/70 严格正确，发送量、TTFT 中位数、完整工作流 E2E 中位数分别减少 69.05%、31.19%、27.09%；这些结果不能外推为默认 Codex、真实 ASC 或普遍收益。五图大请求的 WS 1009 故障已复现但未修复，精确阈值与拒绝层未确定。发布没有重新调用模型。

首个公开版本为 `0.1.1a1` preview，沿用 integration 0.1.1 行为。第一方组件采用 [MIT](LICENSE)，Codex 派生补丁单独遵循上游 Apache-2.0 等条款，见 [NOTICE](NOTICE)。
