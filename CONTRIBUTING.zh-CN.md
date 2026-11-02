# 参与贡献

[English](CONTRIBUTING.md) · [README](README.zh-CN.md)

ICM 有两种入口：供 Claude Code / Codex 使用的 [skill 和本地工具](docs/AGENT-SETUP.zh-CN.md)，以及供能控制发送请求的程序使用的 [Python 接入](docs/INTEGRATION.zh-CN.md)。提交改动时，请说明影响哪一种。skill 无法删除已经进入宿主会话历史的图片。

## 运行本地检查

使用 Python 3.9+ 和虚拟环境：

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
python -I tools/verify_install.py --tests tests --out run-data/contribution-check
python examples/agent_tools.py --out run-data/agent-tools-example
icm-demo --out run-data/request-example
icm install --agent both --project run-data/agent-project
python run-data/agent-project/.agents/skills/image-context-manager/scripts/icm.py --workspace run-data/agent-workspace list
```

重复执行时，请换用新的输出目录和项目目录；部分检查会拒绝覆盖已有文件。

这些检查覆盖安装后的代码、本地图片处理和 skill 安装。原生视觉子 agent 还需要在对应的 agent 中验证；生成交接文件不代表子 agent 已运行。详见[验证记录](docs/VALIDATION.md)。

## 保留信息，如实记录结果

- 保留可取回的原图，将结果绑定到准确的来源、版本和任务阶段。修改裁剪坐标、图片编码、任务保护或结果冲突处理时，补充相关测试。
- 根据任务需要和已核对的结果选择图片形式。不能仅因体积压力或图片中的指令就丢弃依据。
- 中英文说明保持一致，使用平实的表述和可运行的命令。
- 测试使用合成素材。不要提交真实截图、请求或响应内容、凭据、`.env` 文件、会话日志、本地路径、图片工作目录、机器专用的 `.runtime.json` 文件或编译后的宿主程序。
- 分开说明功能检查、请求字节、视觉 token、耗时和费用。报告净收益时，计入重试、备用连接、图片处理和原图取回的开销；保留失败记录。
- 性能验收要求完整且条件一致的多轮对照、任务结果正确，以及测得净收益。本地示例通过或图片文件变小，都不能单独满足这一要求。缺少数据的项目仍标为未验证。

本项目自行编写的内容采用 [MIT](LICENSE)。实验补丁遵循 [NOTICE](NOTICE) 中标明的上游许可。
