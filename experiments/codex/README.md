# 可选：隔离 Codex 源码适配

**本节不是 quickstart 前置条件，也不会在 pip install 时执行。** 通用包不依赖 Codex，安装不会获得默认 Codex 内部历史控制权。没有找到受支持的选择性历史图替换接口；`thread/resume.history` 在该版本标为 FOR CODEX CLOUD - DO NOT USE，不能据此承诺稳定适配。

现有实验仅在公开上游 `rust-v0.162.1` 的独立 `dev-small` 调试构建中验证，macOS aarch64 / Rust 1.95.0。它在 `Prompt::get_formatted_input_for_request` 克隆后的真实请求 input 上变换图片，随后走原生压缩/HTTP 发送；canonical 会话保留。默认 WebSocket 故障未修复。没有修改认证、端点或已安装应用。

## 重建（可选，大体积）

使用独立 scratch 目录，不覆盖本机安装；需要已有可用 Rust 1.95.0 或在 scratch 自行安装工具链。以下 `CARGO_HOME`/`RUSTUP_HOME` 是该独立工具链位置；不要把它们指向用户全局目录。若没有准备好的工具链，先按 Rust 官方工具链安装方式仅装到这两个目录，再执行 cargo；这里不自动安装。

```sh
mkdir -p scratch
cd scratch
curl -L https://codeload.github.com/openai/codex/tar.gz/refs/tags/rust-v0.162.1 -o codex.tar.gz
shasum -a 256 codex.tar.gz
# 必须得到 e709bda93494c000a69d4c07a85a1975ce433f5541e737d1a5feddd399c97c60
 tar -xzf codex.tar.gz
cd codex-rust-v0.162.1
patch -p1 < /absolute/path/to/image-context-manager/experiments/codex/history-host.patch
CARGO_HOME=/absolute/scratch/cargo-home RUSTUP_HOME=/absolute/scratch/rustup-home RUSTUP_TOOLCHAIN=1.95.0 /absolute/scratch/cargo-home/bin/cargo build --manifest-path codex-rs/Cargo.toml -p codex-app-server --bin codex-app-server --profile dev-small
```

上游源包 Cargo.lock 中 161 个工作区包仍为 0.0.0，需要与源码的 0.162.1 对齐；补丁另增加已存在的 `sha2 0.10.9` 到 codex-core 的依赖边。不应全量重生成 lock 或升级第三方包。首次构建后检查差异：只有这两类变化；随后可加 `--locked`。上次实际构建的版本、源包/补丁/二进制 hash 见 [metadata](history-build-metadata.json)，跨路径重建不保证二进制 hash 一致。未把工具链、依赖缓存或约 293 MB 二进制打入本包。

补丁包含：忽略用户配置的隐藏入口参数 `--icm-ignore-user-config`、首请求原生 HTTP 选择开关、真实 input 副本的历史图变换。只在 debug assertions 开启且进程显式设置 `ICM_EXPERIMENT_HISTORY_PLAN` 时启用历史变换；release 或不设置变量时跳过。HTTP 通过 `ICM_EXPERIMENT_HTTP_ONLY=1` 选择，沿用原生鉴权、服务路由、压缩与重试。上游 LICENSE/NOTICE 原文一并保留；这些派生补丁（含其中新增代码）按 Apache-2.0 分发，见根目录 NOTICE；Python 组件另按 MIT。

## 调用方计划协议

已有 stdio app-server driver 可启动上述独立二进制（不要启动已安装 Codex 来假定获得此能力），以进程环境指向自己拥有的计划文件。示例启动形态：

```sh
ICM_EXPERIMENT_HTTP_ONLY=1 ICM_EXPERIMENT_HISTORY_PLAN=/absolute/experiment/history-plan.json /absolute/isolated/codex-app-server --icm-ignore-user-config
```

这不是一个自动完成登录/会话/模型调用的脚本。调用方仍须通过该版本 app-server 的 initialize/thread/turn 协议管理自己的实验会话，复用现有本地登录，不提供新 key、端点或云服务。本最小包不附带会自动发模型请求的 driver；默认示例不执行本节。

宿主开始第一轮前写 `{"generation":"t0","expected_images":N,"replacements":[]}`，其中 N 为该次最终消息 input 的图片总数。每轮在无 in-flight turn 时原子更新计划。正常模型任务完成后，读取同目录 `history-plan.audit.jsonl` 新增的 `before_images` 交给 `HistoricalImages.bind_request`；使用实际回答 commit。下一轮由 `HistoricalImages.plan` 产生同格式计划并原子写入，再发送该轮 turn。不要把本地 demo schema 当 app-server turn 参数。

补丁先验证整个计划的 count、唯一 ordinal、完整 inline URL SHA-256 和非空 reference，再替换指定图片；不匹配时当前 turn 在模型请求压缩/发送前失败。启动/控制通信仍可能发生。generation 用于审计关联，由 driver 校对，不是宿主自行识别轮次；可信 driver 还必须保护当前附件、比较图和未决证据，补丁本身不推断生命周期。

审计记录 generation、图片数、保留/替换 ordinal、URL hash/长度、transform_duration_us 和 request_copy_only，不保存 base64、凭据或完整请求。调用方须核对新增审计与当前计划及 turn 的关联。原图 hash 与宿主归一化后的 URL hash 可能不同，先绑定真实组装值，不能从源文件大小猜测。

当前只处理 `ResponseItem::Message` 中的 inline `InputImage`；非 inline 图片拒绝，工具输出图片未适配。该补丁是隔离实验接口，不是生产失败恢复方案，也不承诺兼容其他 tag、模型或默认 WebSocket。新宿主部署与网络验证均不包含在这次最小包验收中；第四轮既有边界见根目录能力表与证据摘要。
