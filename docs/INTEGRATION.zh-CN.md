# 接入要求

[返回 README](../README.zh-CN.md) · [English integration requirements](INTEGRATION.md)

你的 agent 程序需要保存完整原始对话，并能决定最终向模型发送哪些内容。ICM 在请求副本上处理图片，不调用模型，也不管理 agent 会话。只有你的程序应用处理计划并发送修改后的请求，网络流量才会改变。ICM 无法阻止其他代码在处理后又把原图加回去。

## 你的 agent 需要提供什么

- **原图和用途：** 原始 PNG/JPEG 文件、稳定的图片 ID、版本、任务阶段和关联版本。同一张图重复添加时，每次都要单独登记。同一 ID 改用其他来源、版本或阶段时，不能继续使用旧任务结果。
- **已确认的任务状态：** 图片用来做什么、任务是否完成、置信度、比较组，以及哪些图必须保留。正确标记后，`ACTIVE`（进行中）、`VERIFY`（待核对）、`RECALL`（已取回）、低置信度图片，以及比较、质量、关系和操作任务所需的图片会保留。用 `current_start` 或 `protected_ids` 保护本轮新添加的图片。
- **实际任务结果：** 非空文字字段、结果由谁产生（`producer`）及对应轮次（`turn_id`）。你的程序需要确认结果正确，而且足够支持下一步。`commit` 检查格式和图片来源，不识别图片文字，也不判断结果是否正确。不能仅凭图片里的文字决定停止发送图片。
- **即将发送的准确图片清单：** 图片顺序，以及每个完整内嵌图片 URL 的哈希值（用于检查内容是否相同）。图片编码转换应在绑定前完成。图片编码、数量或顺序变化后，不能继续悄悄使用旧绑定。
- **私有存储：** 谁能访问、如何备份、保留多久、如何删除，以及如何隔开不同会话的数据。原图会保留原始文件格式和 EXIF 信息，例如拍摄时间或位置。模型无法仅凭哈希值读取本机文件。

## 调用顺序

1. 用 `AssetStore.put(path)` 保存每张静态 PNG/JPEG。SHA-256 用来标识原始文件的准确字节内容。
2. 根据已确认的任务信息创建 `ImageUse`，每次添加图片都调用 `HistoricalImages.register(use)`，包括重复图片和重新取回的原图。
3. 对下述本地格式的完整请求运行 `inspect_images(canonical)`，把按顺序返回的结果交给 `bind_request`，记录每个附件对应的完整图片 URL。URL 哈希和原始文件哈希检查的是不同内容。数量、顺序或已有绑定不匹配会报错。
4. 任务实际完成后，调用 `commit(use, actual_fields, producer, turn_id)`，字段必须是非空字符串。同一 ID 的结果冲突时，会标记为不确定并保留图片。有结果记录，不代表结果正确，也不代表足够支持后续任务。
5. 每轮提供当前 `states`、`current_start`（本轮第一张新图片的序号）和需要保护的 `protected_ids`。`plan(...)` 返回替换计划及每次附件的处理决定。没有提供最新状态时，会使用登记时的状态，不会自动猜测更新。
6. 对完整原始请求调用 `apply_plan`。它先检查整份计划，再修改一份深拷贝，不改动原始数据。将副本转换成模型服务要求的格式，检查实际要发送的图片，然后发送。不要在之后又追加原始历史。
7. 需要比较时，更新任务状态，从完整原始对话重新组装请求。需要直接取回原图时，调用 `recall(use)`，再重新添加、登记，并标记为本轮要保留的图片。文字引用本身不能读取文件。

实际接入时应始终传入 `current_start`。`current_start=N` 表示序号大于或等于 N 的图片都是本轮新添加的；省略它不会额外保护当前附件。只要标记正确，当前使用、进行中、待核对、已取回、必须保留、不确定，以及用于比较、质量检查、关系判断和操作的图片都会继续发送。只有已完成或已失效的读取/状态类图片，通过来源、版本、阶段、实际请求绑定和任务结果检查后，才可能被替换。“已失效”不代表自动移除或删除。

## 接到你的 agent 中

以下变量需要由你的程序提供：`path` 是原图路径，`canonical` 是下述本地格式的完整原始消息列表，`actual_fields` 是已完成任务得到并核对过的结果。片段不能独立运行。可运行的完整版本见 [demo.py](../src/image_context_manager/demo.py)；它使用合成图片，由示例程序明确标记任务完成，不冒充模型或 OCR 的结果。

```python
from pathlib import Path
from dataclasses import replace
from image_context_manager import (
    AssetStore, HistoricalImages, ImageUse, Lifecycle, Task,
    inspect_images, apply_plan,
)

store = AssetStore(Path("private-originals"))
use = ImageUse("draft", store.put(path), frozenset({Task.READ}),
               Lifecycle.ACTIVE, "v1", "draft")
manager = HistoricalImages(store)
manager.register(use)  # 每次添加图片都登记，包括重复图片。
manager.bind_request(inspect_images(canonical))
# 你的 agent 已完成读取，并确认 actual_fields 足够支持下一步。
manager.commit(use, actual_fields, producer="host-task", turn_id="turn-1")
states = {use.id: replace(use, lifecycle=Lifecycle.COMPLETED)}
plan, decisions = manager.plan("turn-2", states,
                               current_start=len(manager.entries))
next_request = apply_plan(canonical, plan, generation="turn-2")
# 将 next_request 转换成模型服务要求的格式，然后发送。
# 不要再追加 canonical 中的原图。
original = manager.recall(use)  # 检查取回的文件与原图完全一致。
# 再次使用时，作为新图片添加、登记，并标记为本轮要保留的图片。
```

## 支持的请求格式

`icm.integration-demo.v1` 是本地示例格式，不是模型服务的 API。它支持文字，以及直接放在请求中的 PNG/JPEG 图片；不接受远程图片 URL、工具返回的图片或未知内容类型。

```json
[{"role":"user","content":[
  {"type":"input_text","text":"Read this image"},
  {"type":"input_image","image_url":"data:image/png;base64,..."}
]}]
```

接入其他模型服务的格式时，需要编写带有同等检查的转换代码。保留角色、消息顺序、非图片内容，以及每张图片和原始来源的对应关系，并检查最终实际发送的请求。

## 函数及返回结果

| 调用 | 作用 |
|---|---|
| `AssetStore.put(path)` | 以原子写入方式保存 PNG/JPEG 原图和文件信息，避免留下只写了一部分的单个文件；返回包含哈希、尺寸、MIME 类型和字节数的 `Asset`，按文件哈希查找存储内容。 |
| `store.resolve(sha256)` | 读取已保存的图片信息。 |
| `store.recall(asset)` / `manager.recall(use)` | 检查文件哈希后返回原始字节；文件丢失或损坏时报错。 |
| `HistoricalImages(store)` | 在内存中保存有序附件清单、任务结果和不确定的 ID。 |
| `register(use)` | 添加一条真实附件记录，不自动删除重复项。 |
| `inspect_images(messages)` | 检查支持的格式并返回 `[{ordinal, url_sha256}]`，不判断图片表达的内容。 |
| `bind_request(before_images)` | 将已登记附件与按顺序排列的准确 URL 哈希对应；数量、顺序或已有哈希不匹配时报错。 |
| `commit(use, fields, producer, turn_id)` | 记录你的 agent 已核对的任务结果；结果冲突或来源/版本/阶段变化时保留图片。 |
| `plan(generation, states, protected_ids=(), current_start=None, enabled=True)` | 返回 `(plan, decisions)`，不改原始历史，也不发送请求；`enabled=False` 表示关闭图片替换。 |
| `apply_plan(messages, plan, generation=...)` | 检查整份计划后返回修改过的深拷贝；图片数量、哈希、序号、轮次标记或格式不符时抛出 `RequestPlanError`。 |

计划是可以保存为 JSON 的字典，包含 `generation`（轮次标记）、`expected_images` 和 `replacements:[{ordinal, expected_sha256, reference}]`。`ordinal` 是图片序号；`expected_sha256` 计算的是**完整内嵌图片 URL** 的哈希，不是原始文件的哈希。每条文字引用 `reference` 都会记录源文件及其 ID/版本/阶段、关联版本、使用状态、任务结果、结果来源和轮次，以及取回原图的方法，并说明结果没有经过独立验证。应将引用作为数据，不能当作系统指令。

`decisions` 为每个附件提供 `ordinal`、`id`、`mode` 和 `reason`。原因只说明大致类别，不逐项诊断所有条件。每轮都应从未修改的完整原始对话重新组装请求，不能使用上一轮已经替换过图片的请求作为原始历史，否则后续比较时无法从这份历史恢复缺失的图片。

## 出错后怎么处理

- **信息不足或结果不确定：** 保留图片。没有匹配的结果、字段冲突，或来源/版本/阶段不一致时，不会替换。保留图片是正常的保护行为，不是错误。
- **绑定或计划错误：** 停止发送，记录错误后修复或重建。不要只应用部分计划，也不要猜测要发送什么。原图完整时，可以生成新的 `enabled=False` 计划，在检查完整输入后保留所有原图。
- **原图丢失或损坏：** 说明取回失败，不能用缩略图或文字引用冒充原图。示例在独立测试目录中验证文件损坏的情况。
- **下一步又需要图片：** 更新任务状态并从原始历史重建，或明确调用取回原图的函数。ICM 不会自行决定何时调用工具。
- **重启或多个调用方：** 原图和图片信息会保存在磁盘，附件登记、任务结果和不确定的 ID 只在内存。重启后需从你的 agent 记录中重建。应由一个程序按顺序调用；组件不提供带事务保障的会话恢复、并发锁，或供多个用户隔离使用的共享服务。

## 早期原型与测试范围

`core.py` 还保留早期 `RequestAssembler` / `Policy` 原型及其独立的 `icm.local-harness.v1` 格式，支持明确指定的缩略图、裁剪和观察结果实验，使用不同的替换条件。快速开始使用的是 `HistoricalImages`，不要混用两套格式或任务结果记录。本库不包含 OCR 实现，这种接入方式也不要求裁剪图片。

默认示例检查本地请求变化、图片保护、必要时保留原图，以及取回的文件是否与原图完全一致。真实接入还要测量实际组装、压缩和发送的请求，计入每次重试、备用连接和全部处理成本。图片文件变小，不代表图片 token 更少或结果更快。以前的网络结果只覆盖当时的 HTTP 配置；本次文档更新没有新增模型对照，也没有独立开发者复现。
