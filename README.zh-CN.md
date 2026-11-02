<div align="center">
<picture>
  <source media="(prefers-color-scheme: light)" srcset="docs/images/reference/wordmark-v2-light.png">
  <source media="(prefers-color-scheme: dark)" srcset="docs/images/reference/wordmark-v2-dark.png">
  <img alt="ICM — Image Context Manager. Stacked image frames and monochrome lettering." src="docs/images/reference/wordmark-v2-light.png" width="100%">
</picture>
</div>

<div align="center">
<picture>
  <source media="(prefers-color-scheme: light)" srcset="docs/images/reference/tagline-zh-CN-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="docs/images/reference/tagline-zh-CN-dark.svg">
  <img alt="管理 agent 每轮使用的图片。" src="docs/images/reference/tagline-zh-CN-light.svg" width="400">
</picture>
</div>

<div align="center">
<a href="https://github.com/messsiii/image-context-manager/releases/tag/v0.2.0a1"><img src="docs/images/reference/status.svg" height="48" alt="Experimental preview 0.2.0a1, Python 3.9 or newer"></a>
</div>

---

<div align="center">
<a href="#安装"><img src="docs/images/reference/badge-install.svg" alt="Install"></a>
<img width="16" height="1" alt="">
<a href="#怎么用"><img src="docs/images/reference/badge-use.svg" alt="Use"></a>
<img width="16" height="1" alt="">
<a href="#图片到底怎么处理"><img src="docs/images/reference/badge-workflow.svg" alt="Workflow"></a>
<img width="16" height="1" alt="">
<a href="src/image_context_manager"><img src="docs/images/reference/badge-code.svg" alt="code"></a>
<img width="100" height="1" alt="">
<a href="https://github.com/messsiii/image-context-manager/actions/workflows/tests.yml"><img src="docs/images/reference/badge-tests.svg" alt="tests"></a>
<img width="4" height="1" alt="">
<a href="https://github.com/messsiii/image-context-manager/releases/tag/v0.2.0a1"><img src="docs/images/reference/badge-preview.svg" alt="preview"></a>
<img width="4" height="1" alt="">
<a href="LICENSE"><img src="docs/images/reference/badge-license.svg" alt="license"></a>
<img width="4" height="1" alt="">
<a href="README.md" title="English"><img src="docs/images/reference/badge-language-en.svg" height="48" alt="English"></a>
</div>

<br/>

<div align="center">
  <img src="docs/images/reference/canyon.jpg" alt="Illustration: an image frame bridges a canyon." width="720">
</div>

**面向 Computer Use agent 的图片上下文管理工具。** Image Context Manager（ICM）为 Claude Code 和 Codex 提供 skill 与本地工具，按任务选择原图、裁剪图、压缩图或文字结论，支持子 agent 看图，并在需要时取回原图。

## 要解决的问题：Computer Use 不断产生截图

Computer Use（让 agent 操作浏览器和桌面软件）会反复执行：**看屏幕 → 操作 → 检查结果**。浏览页面、填写表单、验收界面、迭代素材，都会在过程中不断产生截图。旧图如果持续进入后续模型输入，即使每张图很小，历史也会越积越大。反复携带这些历史，会增加请求传输量和模型输入负担，也可能拖慢后续操作。过时页面和多个素材版本还会干扰对当前状态的判断。

这是 Computer Use 接入中共同面对的问题。Anthropic 的 [Computer Use 实践指南](https://claude.com/resources/articles/best-practices-for-computer-and-browser-use-with-claude)也专门讨论了截图累积、旧图清理和上下文压缩。我们关注的是：**下一步还需要哪些图片信息、用什么形式保留、什么时候取回原图**。下面用五类工作场景和实测数据具体展开。

# 快速开始

## 安装

需要 Python 3.9+，以及 Claude Code 或 Codex：

```sh
git clone https://github.com/messsiii/image-context-manager.git
cd image-context-manager
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/icm install --agent both --project /absolute/path/to/your-project
```

把 `/absolute/path/to/your-project` 换成你的项目绝对路径。只安装一种 agent 时，将 `both` 改为 `codex` 或 `claude`。

安装后请保留本仓库和 `.venv` 的位置，工具会使用其中的 Python 环境。

## 怎么用

在你的项目里**新开一个 Claude Code 或 Codex 会话**，告诉它：

> 用 image-context-manager 管理本次任务的截图和视觉素材。

例如：检查两版 App Store 截图，比较标题和排版；修改后重新核对，需要时取回旧版本。

## 图片到底怎么处理

<div align="center">
<picture>
  <source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="docs/images/reference/tool-workflow-zh-CN-dark-mobile.svg">
  <source media="(max-width: 600px)" srcset="docs/images/reference/tool-workflow-zh-CN-light-mobile.svg">
  <source media="(prefers-color-scheme: dark)" srcset="docs/images/reference/tool-workflow-zh-CN-dark.svg">
  <img alt="图片处理流程：判断用途、准备图片、看图核对、保存结论，并按需取回原图。" src="docs/images/reference/tool-workflow-zh-CN-light.svg" width="720">
</picture>
</div>

先判断用途，再选择处理方式。读一句标题可以只看局部，判断整体排版则保留完整画面；看图子 agent 可以只回传文字。正在使用、等待核验或需要比较的图片保留必要细节，结论核对完成且足够使用后复用文字，需要复查时取回原图。

## 哪些工作会遇到这个问题

| 完整工作场景 | 图片里要完成的任务 | 容易遇到的问题 |
| --- | --- | --- |
| 开发与验收 | 找控件、检查布局、比较修改前后 | 多轮截图累积，旧界面容易与当前状态混淆 |
| 软件操作与业务办理 | 读表单、定位操作区域、核对状态 | 页面变化后旧截图和坐标失效；已上传与已提交容易混淆 |
| 视觉素材制作与迭代 | 读文案、判断质量、比较版本 | 草稿和候选版反复出现，全部压缩又可能丢失验收细节 |
| 材料阅读与成果整理 | 提取文字、理解图表和空间关系 | 重复识读；只留文字或局部可能丢掉表头、单位和关联 |
| 模型测试与评估 | 识字、定位、判断关系、比较输出 | 两组输入或历史不一致，会把材料差异误当作策略收益 |

ASC 提审把**素材制作**和**后台操作**串在同一会话里：既要区分草稿、候选和最终版，也要核对上传、提交状态。图片会在这些任务之间反复使用。

图片任务可先分为七类：**读内容、找目标、认状态、理解关系、判断质量、比较变化、提取操作信息**。同一张图可能承担多项任务，读完文字不代表比较或核验也结束了。即使每张图都小，重复看图、版本管理和何时复用结论仍然需要处理。

## 实测数据

### 多轮图片累积：五组 A/B，70 轮

**验证的问题：用文字结论替换已完成任务的旧图，能否减少传输和耗时，同时保持答案正确？**

实验通过真实 Codex 会话调用模型，使用合成图片材料和隔离 HTTP 配置；没有登录 ASC、上传素材或提交审核。每组 A、B 都从空会话开始，使用相同材料、问题和模型设置，连续执行七轮：

| 处理环节 | A：保留原图历史 | B：按任务处理旧图 |
| --- | --- | --- |
| 新图片 | 输入原图 | 输入同样的原图 |
| 已完成任务的旧图片 | 后续继续携带 | 符合预设条件后，用已完成任务的文字结果替换 |
| 后续复查 | 查看历史原图 | 按需取回原图 |

七轮依次为：**草稿读取 → 版本对比 → 上传状态 → 版本选择 → 提交状态 → 召回比较 → 最终核对**。“上传状态”和“提交状态”是读图回答问题，不是真实后台操作。何时任务完成、哪些旧图可以替换，由实验程序指定，本轮不验证 agent 自主判断这些条件的能力。

共五组独立 A/B 对照、十个会话、70 轮，全部执行完毕，未选择性剔除失败轮次。质量按每轮预设答案检查；速度分别记录首个 token 等待与完整七轮耗时。

| 指标 | A：保留原图历史 | B：按任务处理旧图 | 变化 |
| --- | --- | --- | --- |
| 五组累计进程发送量 | 305.26 MB | 94.48 MB | 减少 69.0% |
| 完整七轮流程耗时中位数 | 57.32 秒 | 41.79 秒 | 减少 27.1% |
| 答案检查通过 | 35 / 35 | 35 / 35 | 本组检查均通过 |

<div align="center">
  <a href="docs/images/reference/benchmark-zh-CN.jpg">
    <img src="docs/images/reference/benchmark-zh-CN.jpg" alt="五组七轮 Codex 会话的进程发送量与完整流程耗时 A/B 对照" width="100%">
  </a>
</div>

每个点代表一个完整七轮会话：横轴为进程发送量（MiB），纵轴为流程耗时（秒）。数据来自上述 Codex HTTP 合成图片实验。 点击图表可查看原图并放大。

单轮首个 token 等待时间的中位数减少 31.2%。流程耗时包含准备和处理，不含固定观测等待。发送量来自进程网络计数，包含启动、控制通信、TLS、重试和回退；MB 按 1,000,000 字节计算，不是图片文件大小或 token 用量。没有测得费用节省。[原始汇总](experiments/http-results.json) · [实验条件与依据](experiments/README.md)

**结论边界：这组结果支持该机制在上述合成实验条件下有效，不代表安装 skill 后的真实 Computer Use 工作流已证明提速。** 真实任务仍需把自主判断、图片处理、子 agent、召回、失败重试和缓存变化的全部开销纳入对照。

### 大图片请求：失败重试会放大开销

另一组 WebSocket 诊断记录到：

| 图片请求 | 压缩后的请求帧 | 结果 | 首个 token 等待 |
| --- | --- | --- | --- |
| 4 张大图 | 10.60 MB | WebSocket 成功，无重试 | 11.47 秒 |
| 5 张大图，两次试验 | 约 13.24 MB | 1009 → 回退 HTTP | 57.02 秒 / 57.44 秒 |

五张图的每次试验都有 6 次发送收到 1009，随后回退 HTTP；两次进程发送量分别为 92.88 MB、92.90 MB。同样五张图在隔离 HTTP 对照中发送了 13.24 MB，首个 token 等待 10.37 秒。这说明只看文件压缩率不够，还要记录失败、重试和完整耗时；这些样本尚不能确定通用大小上限，ICM 也没有修复该 WebSocket 问题。[诊断数据](experiments/websocket-results.json)

## 接入范围

skill 和本地工具负责准备后续图片输入、保存结论和取回原图，**无法删除已经进入 Claude Code / Codex 会话历史的图片**。如果你开发的 agent 能控制每轮完整请求，可接入 Python 库管理历史图片：[接入要求](docs/INTEGRATION.zh-CN.md)。

当前版本为实验版。27 项本地测试通过，Codex 功能会话已验证工具调用、子 agent 看图、保存结论和原图取回；真实工作流的提速仍需单独对照验证。[验证记录](docs/VALIDATION.md)

[命令、更新与卸载](docs/AGENT-SETUP.zh-CN.md) · [参与贡献](CONTRIBUTING.zh-CN.md) · [版本记录](CHANGELOG.md) · [许可](NOTICE) · [配图来源](docs/images/reference/ATTRIBUTION.md)

<br/>

<div align="center">
<p>README 的布局与视觉风格参考了 <a href="https://github.com/browser-use/browser-use">Browser Use</a>。</p>

[![Source](docs/images/reference/footer-source.svg)](https://github.com/messsiii/image-context-manager)
&emsp;
[![License](docs/images/reference/footer-license.svg)](LICENSE)
</div>
