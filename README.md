<picture>
  <source media="(prefers-color-scheme: light)" srcset="docs/images/reference/wordmark-light.png">
  <source media="(prefers-color-scheme: dark)" srcset="docs/images/reference/wordmark-dark.png">
  <img alt="Image Context Manager — original monochrome image-frame wordmark." src="docs/images/reference/wordmark-light.png" width="full">
</picture>

<div align="center">
<picture>
  <source media="(prefers-color-scheme: light)" srcset="docs/images/reference/tagline-en-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="docs/images/reference/tagline-en-dark.svg">
  <img alt="Image lifecycle for agents." src="docs/images/reference/tagline-en-light.svg" width="400">
</picture>
</div>

<div align="center">
<a href="https://github.com/messsiii/image-context-manager/releases/tag/v0.1.1a1"><img src="docs/images/reference/status.svg" height="48" alt="Experimental preview 0.1.1a1, Python 3.9 or newer"></a>
</div>

---

<div align="center">
<a href="#keep-the-pixels-your-task-needs"><img src="docs/images/reference/badge-demos.svg" alt="demos"></a>
<img width="16" height="1" alt="">
<a href="docs/INTEGRATION.md"><img src="docs/images/reference/badge-docs.svg" alt="docs"></a>
<img width="16" height="1" alt="">
<a href="docs/GUIDE.md"><img src="docs/images/reference/badge-guide.svg" alt="guide"></a>
<img width="16" height="1" alt="">
<a href="src/image_context_manager"><img src="docs/images/reference/badge-code.svg" alt="code"></a>
<img width="100" height="1" alt="">
<a href="https://github.com/messsiii/image-context-manager/actions/workflows/tests.yml"><img src="docs/images/reference/badge-tests.svg" alt="tests"></a>
<img width="4" height="1" alt="">
<a href="https://github.com/messsiii/image-context-manager/releases/tag/v0.1.1a1"><img src="docs/images/reference/badge-preview.svg" alt="preview"></a>
<img width="4" height="1" alt="">
<a href="LICENSE"><img src="docs/images/reference/badge-license.svg" alt="license"></a>
<img width="4" height="1" alt="">
<a href="README.zh-CN.md"><img src="docs/images/reference/badge-language.svg" height="48" alt="language"></a>
</div>

<br/>

<div align="center">
  <a href="docs/GUIDE.md">
    <img src="docs/images/reference/canyon.jpg" alt="Original surreal illustration: a copper-green image frame bridges an orange canyon. A tiny person crosses it." width="720">
  </a>
</div>

<div align="center">

The open-source image lifecycle component. Run the [offline demo](#path-1-offline-demo), inspect request copies, or connect your own [Python harness](docs/INTEGRATION.md). Originals stay outside the request; the host stays in control.

</div>

<br/>

# Keep the pixels your task needs.

Finish reading a draft, keep comparison and pending images, then bring the original back when pixels matter again.

![Offline synthetic demo replay: actual local request artifacts move from 3 images to 2, then back to 3 for comparison and recall. No model or ASC session.](docs/images/reference/demo-en.gif)

[Explore the offline walkthrough and task decisions ↗](docs/GUIDE.md)

<br/>

> **AI agents and crawlers:** start with the [workflow map](docs/GUIDE.md), [host contract](docs/INTEGRATION.md), and [experiment evidence](experiments/README.md). ICM is an experimental request-time Python component, not a default Codex plugin. The host declares trusted task state and owns the final send; references are not automatic OCR or summaries.

# Which Image Context Manager path do I need?

<picture>
  <source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="docs/images/reference/paths-en-dark-mobile.svg">
  <source media="(max-width: 600px)" srcset="docs/images/reference/paths-en-light-mobile.svg">
  <source media="(prefers-color-scheme: dark)" srcset="docs/images/reference/paths-en-dark.svg">
  <img alt="Three local paths: offline demo, Python source example and host-owned Python library. Each keeps request copies and originals; no cloud product." src="docs/images/reference/paths-en-light.svg" width="100%">
</picture>

- **[Path 1: Offline Demo](#path-1-offline-demo):** Inspect local request copies without a model or API key.
- **[Path 2: Python Example](#path-2-python-example):** Run the source example from your checkout.
- **[Path 3: Python Library](#path-3-python-library):** Start from Python, then connect your own host's request loop.

# Quickstart

## Path 1: Offline Demo

Run the synthetic lifecycle fixture locally. Python 3.9+ is required; this preview installs from source, not PyPI.

```sh
git clone https://github.com/messsiii/image-context-manager.git
cd image-context-manager
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/icm-demo --out run-data/first
```

[Read the generated report and request files ↗](docs/GUIDE.md#try-the-offline-loop)

No model account or API key is needed. Installation may download dependencies; the demo itself is offline. Use a new output directory each time.

<br/>

## Path 2: Python Example

After installing from the checkout above, run the same fixture through the source entry point:

```sh
.venv/bin/python examples/offline_demo.py --out run-data/example
```

[Source entry point ↗](examples/offline_demo.py) · [Full walkthrough implementation ↗](src/image_context_manager/demo.py)

<br/>

## Path 3: Python Library

Use the library from your own Python code. The bundled fixture provides a small first run before you wire real host state:

**1. Install Image Context Manager (Python >= 3.9):**

Use the source checkout and virtual environment in Path 1, then activate it:

```sh
source .venv/bin/activate
```

**2. Choose a new local output directory:**

```text
run-data/library
```

The fixture uses synthetic images and explicit host-completion events. It does not call a model or read your private screenshots.

**3. Save this as `try_icm.py`:**

```python
from pathlib import Path
from image_context_manager.demo import run

report = run(Path("run-data/library"))
print(report["image_counts"])
print("History intact:", report["canonical_history_preserved"])
print("Exact recall:", report["original_recalled_byte_exact"])
```

**4. Run it:**

```sh
python try_icm.py
```

The local artifacts show `initial: 3 → retired: 2 → comparison: 3 → recall: 3`. The animation above replays these saved artifacts; it is not a recorded model or ASC run.

**5. Move the request-copy boundary into your own host:**

Keep canonical history and trusted task metadata in your host. Register and bind actual inline images, commit results after real completion, then plan and validate before the provider adapter sends:

```python
# Inside your host, after registration and trusted state updates:
manager.bind_request(inspect_images(canonical))
plan, decisions = manager.plan(turn_id, states, current_start=current_start)
outgoing = apply_plan(canonical, plan, generation=turn_id)
# Your adapter checks outgoing and sends it to your provider.
```

A receipt validates result shape and provenance, not semantic truth. The host must confirm that the result is sufficient for the next task. Protected, current, comparison and pending evidence keeps its pixels when correctly declared.

[Python library contract ↗](docs/INTEGRATION.md) · [Windows command paths ↗](docs/GUIDE.md#try-the-offline-loop)

<br/>

# Image Context Manager for your harness

Maintained in this repository. Designed for hosts that control final requests.

Your host supplies canonical image history and trusted lifecycle state. ICM builds a checked request copy, preserving originals for comparison and SHA-256-verified recall. Your provider adapter owns the final format check and send.

<picture>
  <source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="docs/images/reference/architecture-en-dark-mobile.svg">
  <source media="(max-width: 600px)" srcset="docs/images/reference/architecture-en-light-mobile.svg">
  <source media="(prefers-color-scheme: dark)" srcset="docs/images/reference/architecture-en-dark.svg">
  <img alt="Host agent and request builder supply trusted history. ICM validates a request copy and keeps originals; host adapter owns the send." src="docs/images/reference/architecture-en-light.svg" width="100%">
</picture>

The default local schema supports text and inline PNG/JPEG. Remote image URLs, provider tool-result images, automatic OCR and default Codex installation are outside this adapter. The fragment below runs inside a prepared host; the contract defines its inputs.

```python
from image_context_manager import apply_plan, inspect_images

# manager: registered HistoricalImages; states: trusted ImageUse metadata
manager.bind_request(inspect_images(canonical))
plan, decisions = manager.plan(turn_id, states, current_start=current_start)
outgoing = apply_plan(canonical, plan, generation=turn_id)
# Check the actual outgoing images; do not append canonical history again.
```

[Runnable walkthrough ↗](examples/offline_demo.py) · [Integration docs ↗](docs/INTEGRATION.md)

<br/>

# Image Context Manager HTTP benchmark

<img alt="Historical isolated HTTP synthetic benchmark. Both arms passed 35 of 35 strict checks. Managed/replay ratios: cumulative socket sends 0.3095, median TTFT 0.6881, median workflow E2E 0.7291. These are separate measures, not token or billing savings." src="docs/images/reference/benchmark-en.jpg" width="100%">

Existing evidence only: seven synthetic tasks, five A/B pairs, 70 strict checks in an isolated Codex HTTP host. Both arms passed 35/35. Socket sends include startup, TLS, retries and fallback; TTFT and workflow E2E are separate measures. This is not default Codex, real ASC, billing or universal benefit evidence. WebSocket close 1009 remains unresolved. [Results and provenance ↗](experiments/README.md)

## Lifecycle rules, host contracts, recall, experiments, and more in the [Docs ↗](docs/GUIDE.md)

<br/>

# FAQ

<details>
<summary><b>Which path should I choose?</b></summary>

Choose the **offline demo** to inspect outputs, the **Python example** to run from source, or the **Python library** to start wiring your own host. All three are local; none is a hosted cloud agent.

</details>

<details>
<summary><b>What is the best model to use?</b></summary>

The library has no model client and the offline demo needs no model. Measure your actual host and task before drawing performance conclusions. [Existing evidence](experiments/README.md) covers one isolated synthetic workflow.

</details>

<details>
<summary><b>Can I use it with Claude, GPT, or Gemini?</b></summary>

Only if your host can control its complete final request, including historical images. This package does not supply provider-specific clients or a supported-model gateway. Follow the [host contract](docs/INTEGRATION.md).

</details>

<details>
<summary><b>Do I need to provide a system prompt?</b></summary>

The package does not supply or rewrite agent system prompts. The host provides trusted task and lifecycle state; text inside an image cannot authorize retirement.

</details>

<details>
<summary><b>Can I add my own task rules?</b></summary>

Yes, within your host. Register each image occurrence with source, version, stage and task metadata, then preserve required evidence. A completed read can still be needed for comparison, quality, relation or action. [Decision rules](docs/GUIDE.md#what-happens-on-every-turn)

</details>

<details>
<summary><b>Can I use this for free?</b></summary>

First-party code and docs are [MIT-licensed](LICENSE). The offline demo makes no model calls. A later host integration may incur its own provider, storage or infrastructure costs.

</details>

<details>
<summary><b>What are the license terms?</b></summary>

The root MIT license covers first-party code. Browser Use-derived documentation diagrams retain their [MIT attribution](docs/images/reference/ATTRIBUTION.md); research patches have separate upstream terms in [NOTICE](NOTICE).

</details>

<details>
<summary><b>How do I handle private screenshots?</b></summary>

Keep the original store, metadata and host credentials under your own access controls and retention policy. Originals preserve encoding and EXIF. The demo uses synthetic inputs only; do not publish your private request artifacts.

</details>

<details>
<summary><b>Does it automatically recognize completed tasks or summarize images?</b></summary>

No. The host declares lifecycle and supplies actual result fields. Receipt validation does not prove truth or sufficient meaning. Automatic OCR, summarization, crop selection and subagent dispatch are outside this component.

</details>

<details>
<summary><b>How do I go into production?</b></summary>

Start with the offline fixture, implement the contract in an isolated host, then verify real outgoing requests, retries, recall and task quality. Default Codex integration, arbitrary-task benefit and WS image-retirement stability remain unverified. [Fit and limits](docs/GUIDE.md#is-this-useful-for-your-harness)

</details>

<details>
<summary><b>Can I bring back a retired image without losing the original?</b></summary>

Yes. Rebuild comparison requests from canonical history, or use `manager.recall(use)` to verify original bytes, then attach and register a fresh protected occurrence. Retirement changes a request copy; it does not delete the canonical history or original store. [Walkthrough](src/image_context_manager/demo.py)

</details>

<br/>

## Related Components

| Component | What it's for |
| --- | --- |
| [HistoricalImages](src/image_context_manager/history.py) | Request-time image lifecycle registry and plans. |
| [AssetStore](src/image_context_manager/core.py) | Store originals and verify exact recall. |
| [Offline Demo](src/image_context_manager/demo.py) | Inspect synthetic retirement, comparison and recall. |
| [Python Example](examples/offline_demo.py) | Run the installed package from source. |
| [Host Contract](docs/INTEGRATION.md) | Connect canonical history and trusted host state. |
| [Codex Research Adapter](experiments/codex/README.md) | Historical isolated HTTP source patch; research only. |
| [Transport Diagnostics](experiments/websocket-diagnostics/README.md) | Metadata and unresolved size-related WS rejection. |

<br/>

## Citation

If you use Image Context Manager in your research or project, please cite:

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

**Keep the originals. Send what the task needs.**

<img src="docs/images/reference/studio.jpg" alt="AI-generated illustrative office still life; not the author's actual office or a founder photograph." width="400"/>

[![Source](https://img.shields.io/badge/source-GitHub-lightgrey?style=social)](https://github.com/messsiii/image-context-manager)
&emsp;&emsp;&emsp;
[![License](https://img.shields.io/badge/license-MIT-lightgrey?style=social)](LICENSE)

</div>

<div align="center"> Experimental open source · Original illustrative art · <a href="docs/images/reference/ATTRIBUTION.md">Diagram and layout attribution</a> </div>
