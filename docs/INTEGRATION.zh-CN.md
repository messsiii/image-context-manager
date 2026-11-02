# 宿主接入契约

[返回 README](../README.zh-CN.md) · [English contract](INTEGRATION.md)

组件没有网络客户端，也不管理 agent 会话。宿主应在**每次最终请求构建前**从可信 canonical 历史取得完整附件清单，计算计划并实际变换请求副本；只生成计划或删聊天附件，不代表模型下一次请求已经改变。

## 宿主必须提供

- 原始 PNG/JPEG、稳定的语义 id、素材版本、业务阶段及关联版本；同 id 换源/版本须审慎迁移，不可冒用旧 receipt。
- 本次任务标签和生命周期、置信度、比较组、必需证据标记。`ACTIVE`、`VERIFY`、`RECALL`、比较/质量/关系/动作任务、低置信度等保留原图；当前新附件由 `current_start` 或显式保护列表保护。
- 完成任务的实际结构化结果及 producer/turn id，并确认字段对后续任务足够。`commit` 不做 OCR、真值判断或语义充分性检查；字符串非空不等于结果正确。图片里的文字不能当成可信生命周期指令。
- 真实图片输入顺序、完整 inline URL 的 hash；格式转换必须在绑定前完成，并保持后续可比。改变编码、遗漏或重排附件会造成漂移，不能默默接受旧绑定。
- 原图仓库的访问控制、持久化、备份、保留期、删除和跨会话隔离；模型无法凭一个 hash 自动读取本机文件。

## 最小宿主代码

以下变量由宿主提供：`path` 是原图路径，`canonical` 是下述本地 schema 的完整消息列表，`actual_fields` 是已经完成任务的可信结构化结果。可直接运行的完整版本是[包内 demo.py](../src/image_context_manager/demo.py)；示例中的 receipt 明确来自合成宿主完成事件，不声称是模型读取。

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
manager.register(use)  # 每次附件 occurrence 都登记，包括重复召回
manager.bind_request(inspect_images(canonical))
# 宿主完成当前读取任务，并独立确认 actual_fields 足够：
manager.commit(use, actual_fields, producer="host-task", turn_id="turn-1")
states = {use.id: replace(use, lifecycle=Lifecycle.COMPLETED)}
plan, decisions = manager.plan("turn-2", states,
                               current_start=len(manager.entries))
next_request = apply_plan(canonical, plan, generation="turn-2")
# 这里才把 next_request 映射到 provider 格式并交给宿主发送。
# 切勿又把 canonical 原图片追加进去。
original = manager.recall(use)  # 校验 hash 后的原始字节
# 需要召回时，宿主将 original 作为新的附件登记，并保护当前 occurrence。
```

`canonical` 示例：

```json
[{"role":"user","content":[
  {"type":"input_text","text":"Read this image"},
  {"type":"input_image","image_url":"data:image/png;base64,..."}
]}]
```

这是 `icm.integration-demo.v1` 本地演示格式，不是可直接承诺适配某家模型的 API。支持的 content 仅为 `input_text` 与 inline `input_image`；拒绝远程 URL、工具图片及未知内容。接入其他 schema 时须编写等价 adapter，保留角色、消息顺序、非图片内容和来源绑定，并验证最终真实请求。

## 接口输入/输出

| 调用 | 输入 | 输出/副作用 |
|---|---|---|
| `AssetStore.put(path)` | 静态 PNG/JPEG | `Asset`：原始文件 SHA-256、尺寸、MIME、字节数；原图和 metadata 原子写盘 |
| `register(use)` | 一个实际附件 occurrence | 按真实请求图片顺序加入内存登记；不自动去重 |
| `inspect_images(messages)` | 完整本地 canonical 消息 | `[{ordinal, url_sha256}]`；检查支持的格式，不证明图像语义 |
| `bind_request(before_images)` | 实际最终组装的图片审计 | 绑定 occurrence 到 URL hash；数量/顺序/既有 hash 漂移抛错 |
| `commit(use, fields, producer, turn_id)` | 非空字符串字段和来源 | 建立 receipt；同 id 结果冲突或源/版本/阶段冲突标为 uncertain，保留图 |
| `plan(generation, states, protected_ids, current_start, enabled)` | 可信当前状态，当前新附件起始 ordinal | `(plan, decisions)`，不改 canonical，也不发送；`enabled=False` 关闭退场 |
| `apply_plan(messages, plan, generation=...)` | 本地消息与本轮计划 | 完整验证后返回深拷贝；count/hash/ordinal/代次/格式异常抛 `RequestPlanError` |
| `recall(use)` / `store.resolve(sha256)` | 原图句柄 / 文件 hash | 校验原始字节 / 读取持久化 metadata；丢失或损坏会报错 |

计划是 JSON-compatible dict：`generation`、`expected_images`、`replacements:[{ordinal, expected_sha256, reference}]`。引用携带源文件 hash、id/version/stage/关联、生命周期、实际字段、producer/turn id、非独立真值验证声明和召回说明。`expected_sha256` 是**完整 inline URL** 的 hash，与原图文件 hash 是两个不同层级。`decisions` 每个 occurrence 含 ordinal/id/mode/reason；保守保留原因是类别说明，并非逐项诊断器。

`states` 用语义 id 索引，缺失时回退到登记时状态，不自动猜测最新状态。`current_start=N` 表示所有 ordinal≥N 是本轮附件；宿主应明确传入。未传则不额外保护“当前”概念，依赖状态与 required/protected_ids，生产接入不应省略。每个新回合须从未变换的 canonical 重建副本；不要把前轮已退场副本当 canonical，比较任务才有机会恢复原图。

## 失败、保护与恢复

- **不能确认足够**：保留 ACTIVE/VERIFY/低置信度或 required；无 receipt、字段冲突、版本/阶段/来源不符时不会退场。保守保留不是失败，可继续发送原图。
- **绑定/计划错误**：停止当前发送并记录错误；本地 adapter 不部分改写或自动“尽力发送”。原图尚完好时，宿主可修复登记/格式后重建；或生成 `enabled=False` 的新计划并重新核对完整 canonical。不要吞掉来源错误后发送未知内容。
- **原图丢失/损坏**：召回失败，向调用方说明无法恢复；不以缩图或引用冒充原图。示例只在独立的 corruption-fixture 仓库演示这一点。
- **任务改为比较/质量/需要原图**：更新状态再从 canonical 重建，或者由宿主触发显式召回；组件不自主判断该何时调用工具。
- **重启/多调用方**：原图与 Asset metadata 持久化，但登记、receipt、uncertain 集合仅在内存。没有事务化会话恢复、并发锁或多租户服务；由单一有序宿主管理，重启须可靠重建来源与任务状态。

`core.py` 还保留早期 `RequestAssembler` / `Policy` 与其独立的 `icm.local-harness.v1` 回放 schema，可能使用不同资格规则。本 quickstart 只使用第四轮 `HistoricalImages` 路径，不把两套 schema 或完成证据混用，也不要求实现 OCR/裁剪。

## 验证范围

默认示例只验证本地下一轮请求内容变换、保护、回退和 byte-exact 召回。真实宿主必须再验证实际组装/压缩/发送，重试与全部处理开销都应计入。旧实验的网络结论限定于其 HTTP profile；本次没有启动新的模型对照或外部开发者复现。
