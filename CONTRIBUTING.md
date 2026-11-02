# Contributing

[中文](CONTRIBUTING.zh-CN.md) · [README](README.md)

ICM has two entry points: [skills and local tools](docs/AGENT-SETUP.md) for Claude Code / Codex, and [Python request integration](docs/INTEGRATION.md) for applications that control outgoing requests. State which path a change affects. The skill cannot erase images already embedded in the host's conversation.

## Run local checks

Use Python 3.9+ in a virtual environment:

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

Use new output and project directories when repeating these commands; some checks refuse to overwrite existing files.

These check installed code, local image operations and skill installation. A native visual worker must also be checked inside the intended agent; generating a handoff is not proof that a worker ran. See the [validation record](docs/VALIDATION.md).

## Preserve information and report evidence

- Keep originals retrievable and bind results to the exact source, version and task stage. Test changes to crop coordinates, image encoding, task protection and conflicting results.
- Choose representations from task needs and verified results. Size pressure or instructions found inside an image cannot authorize discarding evidence.
- Keep English and Chinese explanations consistent. Use plain wording and runnable commands.
- Use synthetic fixtures. Do not commit real screenshots, request/response bodies, credentials, `.env` files, session logs, local paths, image workspaces, machine-specific `.runtime.json` files or compiled hosts.
- Separate functional checks, request bytes, visual tokens, latency and cost. Count retries, fallback connections, processing and original retrieval when reporting net benefit. Keep failed runs in the record.
- Performance acceptance requires complete matched multi-turn runs, correct task outcomes and measured net benefit. A passing local demo or smaller image files alone do not meet that requirement. Missing measurements remain unverified.

First-party contributions use [MIT](LICENSE). Experiment patches follow the applicable upstream license identified in [NOTICE](NOTICE).
