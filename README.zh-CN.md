<picture>
  <source media="(prefers-color-scheme: light)" srcset="docs/images/reference/wordmark-light.png">
  <source media="(prefers-color-scheme: dark)" srcset="docs/images/reference/wordmark-dark.png">
  <img alt="Image Context Manager — original monochrome image-frame wordmark." src="docs/images/reference/wordmark-light.png" width="full">
</picture>

<div align="center">
<picture>
  <source media="(prefers-color-scheme: light)" srcset="docs/images/reference/tagline-zh-CN-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="docs/images/reference/tagline-zh-CN-dark.svg">
  <img alt="管理 agent 每轮使用的图片。" src="docs/images/reference/tagline-zh-CN-light.svg" width="400">
</picture>
</div>

<div align="center">
<a href="https://github.com/messsiii/image-context-manager/releases/tag/v0.1.1a1"><img src="docs/images/reference/status.svg" height="48" alt="Experimental preview 0.1.1a1, Python 3.9 or newer"></a>
</div>

---

<div align="center">
<a href="#让图片跟着任务走"><img src="docs/images/reference/badge-demos.svg" alt="demos"></a>
<img width="16" height="1" alt="">
<a href="docs/INTEGRATION.zh-CN.md"><img src="docs/images/reference/badge-docs.svg" alt="docs"></a>
<img width="16" height="1" alt="">
<a href="docs/GUIDE.zh-CN.md"><img src="docs/images/reference/badge-guide.svg" alt="guide"></a>
<img width="16" height="1" alt="">
<a href="src/image_context_manager"><img src="docs/images/reference/badge-code.svg" alt="code"></a>
<img width="100" height="1" alt="">
<a href="https://github.com/messsiii/image-context-manager/actions/workflows/tests.yml"><img src="docs/images/reference/badge-tests.svg" alt="tests"></a>
<img width="4" height="1" alt="">
<a href="https://github.com/messsiii/image-context-manager/releases/tag/v0.1.1a1"><img src="docs/images/reference/badge-preview.svg" alt="preview"></a>
<img width="4" height="1" alt="">
<a href="LICENSE"><img src="docs/images/reference/badge-license.svg" alt="license"></a>
<img width="4" height="1" alt="">
<a href="README.md"><img src="docs/images/reference/badge-language.svg" height="48" alt="language"></a>
</div>

<br/>

<div align="center">
  <a href="docs/GUIDE.zh-CN.md">
    <img src="docs/images/reference/canyon.jpg" alt="Original surreal illustration: a copper-green image frame bridges an orange canyon. A tiny person crosses it." width="720">
  </a>
</div>

<div align="center">

帮助 agent 管理每轮发送的图片。运行[离线示例](#路径-1离线示例)，查看处理前后的请求，或接入自己的 [Python agent 程序](docs/INTEGRATION.zh-CN.md)。原图单独保存，由你的程序决定最终发送什么。

</div>

<br/>

# 让图片跟着任务走。

草稿看完后，可以用已有结论替代旧图；还要比较或核对的图片继续保留，需要时再取回原图。

![离线合成示例回放：实际本地请求文件从3张图片变为2张，再为比较与取回原图恢复到3张。不是模型或ASC会话。](docs/images/reference/demo-zh-CN.gif)

[查看完整离线示例与处理规则 ↗](docs/GUIDE.zh-CN.md)

<br/>

> **供 AI agent 与爬虫阅读：** 从[工作流程](docs/GUIDE.zh-CN.md)、[接入要求](docs/INTEGRATION.zh-CN.md)和[实验结果](experiments/README.md)开始。ICM 是在发送模型请求前处理图片的 Python 组件，目前仍在实验阶段，不是安装后就能在 Codex 中使用的插件。你的 agent 程序需要提供已确认的任务状态，并负责发送请求；用来替代旧图的文字引用不会自动识别图片文字或生成摘要。

# 我需要哪种 Image Context Manager 接入方式？

<picture>
  <source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="docs/images/reference/paths-zh-CN-dark-mobile.svg">
  <source media="(max-width: 600px)" srcset="docs/images/reference/paths-zh-CN-light-mobile.svg">
  <source media="(prefers-color-scheme: dark)" srcset="docs/images/reference/paths-zh-CN-dark.svg">
  <img alt="三种本地用法：离线示例、Python 源码示例，以及接入自己 agent 的 Python 库。都会保留请求副本和原图，不提供云服务。" src="docs/images/reference/paths-zh-CN-light.svg" width="100%">
</picture>

- **[路径 1：离线示例](#路径-1离线示例)：** 不用模型或 API 密钥，查看处理后的本地请求。
- **[路径 2：Python 示例](#路径-2python-示例)：** 从源码目录运行示例。
- **[路径 3：Python 库](#路径-3python-库)：** 先从 Python 跑通，再接入自己的 agent，在每轮发送前处理图片。

# 快速开始

## 路径 1：离线示例

在本地用合成图片演示保留、替换和取回原图的完整过程。需要 Python 3.9+；预览版从源码安装，未发布到 PyPI。

```sh
git clone https://github.com/messsiii/image-context-manager.git
cd image-context-manager
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/icm-demo --out run-data/first
```

[查看生成的报告与请求文件 ↗](docs/GUIDE.zh-CN.md#跑通离线闭环)

无需模型账号或 API 密钥。安装可能联网下载依赖，示例本身离线运行。每次选择新的输出目录。

<br/>

## 路径 2：Python 示例

按上一条路径安装后，从源码目录运行同一套示例：

```sh
.venv/bin/python examples/offline_demo.py --out run-data/example
```

[源码入口 ↗](examples/offline_demo.py) · [完整示例实现 ↗](src/image_context_manager/demo.py)

<br/>

## 路径 3：Python 库

从自己的 Python 代码调用库。先用内置示例跑通，再接入自己 agent 的真实任务状态：

**1. 安装 Image Context Manager（Python >= 3.9）：**

使用路径 1 的源码目录和虚拟环境，然后激活：

```sh
source .venv/bin/activate
```

**2. 选择一个新的本地输出目录：**

```text
run-data/library
```

内置示例使用合成图片，并由示例程序明确标记任务完成，不调用模型，也不读取你的私人截图。

**3. 保存为 `try_icm.py`：**

```python
from pathlib import Path
from image_context_manager.demo import run

report = run(Path("run-data/library"))
print(report["image_counts"])
print("History intact:", report["canonical_history_preserved"])
print("Exact recall:", report["original_recalled_byte_exact"])
```

**4. 运行：**

```sh
python try_icm.py
```

本地文件展示 `initial: 3 → retired: 2 → comparison: 3 → recall: 3`。上方动画回放这些已保存文件，不是模型或 ASC 录屏。

**5. 接到自己的 agent，每轮发送前处理图片：**

由你的 agent 程序保存完整原始对话，并记录每张图的用途和已确认的任务状态。登记请求中直接携带的图片，任务实际完成后保存结果，再由 ICM 决定哪些旧图可以替换为文字。检查处理后的请求，再发送给模型：

```python
# 在你的 agent 程序登记图片并确认任务状态后：
manager.bind_request(inspect_images(canonical))
plan, decisions = manager.plan(turn_id, states, current_start=current_start)
outgoing = apply_plan(canonical, plan, generation=turn_id)
# 由你的程序检查 outgoing 并发送给模型服务。
```

ICM 会检查任务结果的格式及其对应的原图，但不能判断结果是否正确、是否足够完成下一步；这需要你的 agent 程序确认。只要状态标记正确，当前使用、需要比较、待核对或明确要求保留的图片就会继续发送。

[接入要求 ↗](docs/INTEGRATION.zh-CN.md) · [Windows 运行命令 ↗](docs/GUIDE.zh-CN.md#跑通离线闭环)

<br/>

# 将 Image Context Manager 接入你的 agent

由本仓库维护，适用于能决定最终向模型发送哪些内容的 agent 程序。

你的程序提供对话中的全部图片及已确认的使用状态。ICM 在一份请求副本上处理旧图，不改动原始对话。原图会保留，方便比较或重新取回；取回时用 SHA-256 校验，确认文件与原图完全一致。最终的格式检查和发送仍由你的程序负责。

<picture>
  <source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="docs/images/reference/architecture-zh-CN-dark-mobile.svg">
  <source media="(max-width: 600px)" srcset="docs/images/reference/architecture-zh-CN-light-mobile.svg">
  <source media="(prefers-color-scheme: dark)" srcset="docs/images/reference/architecture-zh-CN-dark.svg">
  <img alt="你的 agent 提供对话历史和已确认的任务状态。ICM 检查请求副本并保存原图，最终由你的程序发送。" src="docs/images/reference/architecture-zh-CN-light.svg" width="100%">
</picture>

当前示例格式支持文字，以及直接放在请求中的 PNG/JPEG 图片。暂不处理远程图片链接或模型工具返回的图片，也不会自动识别图片文字或接入默认 Codex。以下片段需要先在你的 agent 程序中完成图片登记，所需信息见[接入要求](docs/INTEGRATION.zh-CN.md)。

```python
from image_context_manager import apply_plan, inspect_images

# manager 已登记图片；states 记录每张图已确认的用途和状态
manager.bind_request(inspect_images(canonical))
plan, decisions = manager.plan(turn_id, states, current_start=current_start)
outgoing = apply_plan(canonical, plan, generation=turn_id)
# 检查实际发送的图片，不要再追加完整原始历史。
```

[可运行示例 ↗](examples/offline_demo.py) · [接入文档 ↗](docs/INTEGRATION.zh-CN.md)

<br/>

# Image Context Manager HTTP 性能测试

<img alt="以往独立HTTP测试环境中的合成任务结果：两组均通过35/35严格检查。优化组与原图组的比值：累计网络发送字节0.3095，每轮等待首个输出的时间中位数0.6881，完整流程耗时中位数0.7291。不代表token或费用节省。" src="docs/images/reference/benchmark-zh-CN.jpg" width="100%">

这里只展示已有测试：在独立运行的 Codex HTTP 测试程序中，用 7 项合成任务做了 5 对 A/B 对照，共完成 70 次严格检查，两组各通过 35/35。优化组 / 原图组的比值为：累计网络发送字节 **0.3095**、每轮等待首个输出的时间（TTFT）中位数 **0.6881**、完整流程耗时（E2E）中位数 **0.7291**。网络字节统计包括启动、加密连接（TLS）、重试和切换备用连接的流量；两项耗时分别统计。这些结果尚不能证明默认 Codex、真实 App Store Connect（ASC）任务或其他场景也有收益，也没有验证费用节省。WebSocket 因消息过大而断开的问题（关闭码 1009）仍未解决。[结果与测试说明 ↗](experiments/README.md)

## 图片何时保留、何时替换，如何接入和取回原图，详见[文档 ↗](docs/GUIDE.zh-CN.md)

<br/>

# 常见问题

<details>
<summary><b>我应该选择哪条路径？</b></summary>

想检查输出，选**离线示例**；想从源码运行，选 **Python 示例**；想接入自己的 agent，选 **Python 库**。三条路径都在本地运行，不提供云端 agent 服务。

</details>

<details>
<summary><b>应该使用什么模型？</b></summary>

这个库不直接调用模型，离线示例也不需要模型。接入后，需要用自己的 agent 和任务实测是否有性能收益。[已有测试](experiments/README.md)只覆盖一个在独立环境中运行的合成流程。

</details>

<details>
<summary><b>能用于 Claude、GPT 或 Gemini 吗？</b></summary>

前提是你的 agent 程序能决定最终请求的全部内容，包括历史图片。本包不负责连接这些模型，也没有统一的模型调用服务。具体见[接入要求](docs/INTEGRATION.zh-CN.md)。

</details>

<details>
<summary><b>需要提供系统提示词吗？</b></summary>

本包不提供或改写 agent 系统提示词。你的程序需要确认任务是否完成、图片是否还要使用；不能仅凭图片里的文字决定停止发送图片。

</details>

<details>
<summary><b>可以增加自己的任务规则吗？</b></summary>

可以，在你的 agent 程序里设置。每次添加图片时，记录来源、版本、任务阶段和用途，并标记哪些图片必须保留。即使已经读完，后续比较版本、检查质量、理解位置关系或执行操作时仍可能需要原图。[决策规则](docs/GUIDE.zh-CN.md#每一轮具体怎么决策)

</details>

<details>
<summary><b>可以免费使用吗？</b></summary>

本项目自行编写的代码和文档采用 [MIT](LICENSE) 许可。离线示例不调用模型；接入你的 agent 后，可能产生模型调用、存储和运行费用。

</details>

<details>
<summary><b>许可条款是什么？</b></summary>

仓库根目录的 MIT 许可覆盖本项目自行编写的代码。改编自 Browser Use 的文档图保留 [MIT 许可和来源说明](docs/images/reference/ATTRIBUTION.md)，研究补丁的上游条款见 [NOTICE](NOTICE)。

</details>

<details>
<summary><b>如何处理私人截图？</b></summary>

你需要决定谁可以访问原图、图片记录和 agent 登录信息，以及这些数据保留多久。原图会保留原始文件格式及 EXIF 信息（例如拍摄时间、位置）。示例只使用合成图片，请勿公开包含私人内容的请求文件。

</details>

<details>
<summary><b>会自动识别任务完成或总结图片吗？</b></summary>

不会。你的 agent 程序需要标记任务状态，并提供实际完成任务得到的结果。ICM 只检查结果格式和图片来源，不能判断结果是否正确、信息是否足够。本组件不会自动识别图片文字、生成摘要、选择裁剪区域或分配子 agent。

</details>

<details>
<summary><b>如何投入生产使用？</b></summary>

先跑离线示例，再按接入要求接到独立测试用的 agent 程序，检查实际发送内容、失败重试、取回原图和任务结果是否正确。默认 Codex 接入、其他任务是否受益，以及通过 WebSocket 替换历史图片的稳定性，尚未验证。[适用性与边界](docs/GUIDE.zh-CN.md#你的宿主适合接入吗)。

</details>

<details>
<summary><b>图片替换后还能恢复原图吗？</b></summary>

可以。比较时，从完整原始对话重新组装请求；也可以调用 `manager.recall(use)`，确认取回的文件与原图一致，再重新添加并标记为需要保留的图片。替换只改变本次发送的请求，不删除原始对话或保存的原图。[完整示例](src/image_context_manager/demo.py)。

</details>

<br/>

## 相关组件

| 组件 | 用途 |
| --- | --- |
| [HistoricalImages](src/image_context_manager/history.py) | 记录图片用途和状态，决定本轮保留哪些图片。 |
| [AssetStore](src/image_context_manager/core.py) | 保存原图，取回时检查文件是否完全一致。 |
| [离线示例](src/image_context_manager/demo.py) | 用合成图片演示替换、比较和取回原图。 |
| [Python 示例](examples/offline_demo.py) | 从源码调用已安装包。 |
| [接入要求](docs/INTEGRATION.zh-CN.md) | 说明 agent 需要提供的对话历史、图片信息和任务状态。 |
| [Codex 研究适配器](experiments/codex/README.md) | 以往 HTTP 实验使用的 Codex 源码修改，仅供研究。 |
| [传输诊断](experiments/websocket-diagnostics/README.md) | 连接测试记录，以及尚未解决的 WebSocket 大消息断开问题。 |

<br/>

## 引用

若在研究或项目中使用 Image Context Manager，可引用：

```bibtex
@software{image_context_manager2026,
  author = {messsiii},
  title = {Image Context Manager},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/messsiii/image-context-manager}
}
```

<br/>

<div align="center">

**原图留下，按任务发送。**

<img src="docs/images/reference/studio.jpg" alt="AI生成的办公室静物示意图，不是作者的真实办公室或创始人照片。" width="400"/>

[![Source](docs/images/reference/footer-source.svg)](https://github.com/messsiii/image-context-manager)
&emsp;&emsp;&emsp;
[![License](docs/images/reference/footer-license.svg)](LICENSE)

</div>

<div align="center"> 实验性开源项目 · AI 生成办公室示意图 · <a href="docs/images/reference/ATTRIBUTION.md">图示与布局来源说明</a> </div>
