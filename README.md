<picture>
  <source media="(prefers-color-scheme: light)" srcset="docs/images/reference/wordmark-light.png">
  <source media="(prefers-color-scheme: dark)" srcset="docs/images/reference/wordmark-dark.png">
  <img alt="Image Context Manager — original monochrome image-frame wordmark." src="docs/images/reference/wordmark-light.png" width="100%">
</picture>

<div align="center">
<picture>
  <source media="(prefers-color-scheme: light)" srcset="docs/images/reference/tagline-en-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="docs/images/reference/tagline-en-dark.svg">
  <img alt="Manage images for your agent." src="docs/images/reference/tagline-en-light.svg" width="400">
</picture>
</div>

<div align="center">
<a href="https://github.com/messsiii/image-context-manager/releases/tag/v0.2.0a1"><img src="docs/images/reference/status.svg" height="48" alt="Experimental preview 0.2.0a1, Python 3.9 or newer"></a>
</div>

---

<div align="center">
<a href="#install"><img src="docs/images/reference/badge-install.svg" alt="Install"></a>
<img width="16" height="1" alt="">
<a href="#use-it"><img src="docs/images/reference/badge-use.svg" alt="Use"></a>
<img width="16" height="1" alt="">
<a href="#how-it-chooses-what-to-keep"><img src="docs/images/reference/badge-workflow.svg" alt="Workflow"></a>
<img width="16" height="1" alt="">
<a href="src/image_context_manager"><img src="docs/images/reference/badge-code.svg" alt="code"></a>
<img width="100" height="1" alt="">
<a href="https://github.com/messsiii/image-context-manager/actions/workflows/tests.yml"><img src="docs/images/reference/badge-tests.svg" alt="tests"></a>
<img width="4" height="1" alt="">
<a href="https://github.com/messsiii/image-context-manager/releases/tag/v0.2.0a1"><img src="docs/images/reference/badge-preview.svg" alt="preview"></a>
<img width="4" height="1" alt="">
<a href="LICENSE"><img src="docs/images/reference/badge-license.svg" alt="license"></a>
<img width="4" height="1" alt="">
<a href="README.zh-CN.md"><img src="docs/images/reference/badge-language.svg" height="48" alt="language"></a>
</div>

<br/>

<div align="center">
  <img src="docs/images/reference/canyon.jpg" alt="Illustration: an image frame bridges a canyon." width="720">
</div>

<div align="center">

Give Claude Code or Codex a **skill and local tools to choose between originals, crops, compressed images and text findings** for each screenshot or visual asset. Image Context Manager (ICM) also supports a separate visual worker and keeps originals for later checks.

</div>

# Quickstart

## Install

Requires Python 3.9+ and Claude Code or Codex:

```sh
git clone https://github.com/messsiii/image-context-manager.git
cd image-context-manager
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/icm install --agent both --project /absolute/path/to/your-project
```

Replace `/absolute/path/to/your-project` with your project's absolute path. To install for one agent, change `both` to `codex` or `claude`.

Keep this repository and `.venv` at the same location after installation; the tools use that Python environment.

## Use it

Start a **new Claude Code or Codex session in your project**, then ask:

> Use image-context-manager to manage screenshots and visual assets for this task.

For example: check two versions of App Store screenshots, compare their headlines and layouts, recheck after edits, and retrieve an older version when needed.

## How it chooses what to keep

<picture>
  <source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="docs/images/reference/tool-workflow-en-dark-mobile.svg">
  <source media="(max-width: 600px)" srcset="docs/images/reference/tool-workflow-en-light-mobile.svg">
  <source media="(prefers-color-scheme: dark)" srcset="docs/images/reference/tool-workflow-en-dark.svg">
  <img alt="Image workflow: identify the task, prepare an image, inspect it, save findings and recall originals." src="docs/images/reference/tool-workflow-en-light.svg" width="720">
</picture>

Choose by purpose. A caption may need only a crop; judging the layout needs the full view. A visual worker can return text findings. Keep the detail needed for active work, pending checks and comparisons; reuse text once findings are checked and sufficient, and retrieve originals for another inspection.

## Where images become a problem

| Complete workflow | Tasks within an image | What can go wrong |
| --- | --- | --- |
| Development and acceptance checks | Find controls, inspect layout, compare changes | Screenshots accumulate; an old interface can be mistaken for the current state |
| Software operation and business tasks | Read forms, locate action areas, verify state | Screenshots and coordinates become stale; uploaded and submitted states can be confused |
| Visual asset creation and iteration | Read copy, judge quality, compare versions | Drafts and candidates recur; compressing everything can hide review details |
| Reading materials and preparing outputs | Extract text, understand charts and spatial relationships | Repeated reading; text or crops can omit headers, units and context |
| Model testing and evaluation | Read, locate, infer relationships, compare outputs | Different inputs or histories can make a material difference look like a strategy benefit |

App Store Connect (ASC) submission combines **asset creation** and **backend operation** in one conversation: distinguish drafts, candidates and final assets, then verify upload and submission states. Images are reused across these tasks.

Our initial image-task categories are **reading content, locating targets, recognizing state, understanding relationships, judging quality, comparing changes and extracting action information**. One image can serve several tasks: finishing a text read does not finish its comparison or verification. Even small images still need rules for repeated inspection, versions and reuse of findings.

## Measured results

### Accumulating image history: five A/B pairs, 70 turns

**This was a synthetic-task experiment in an isolated Codex HTTP setup, not a real ASC speedup from installing the skill.** A kept original-image history; B replaced eligible old images in later requests with results from completed tasks. The experiment driver supplied task stages.

Each pair used two independent conversations, each running seven turns: draft reading → version comparison → upload state → version selection → submission state → recall comparison → final check. All five pairs completed.

| Metric | A: original-image history | B: task-based history handling | Change |
| --- | --- | --- | --- |
| Cumulative process sends, all five pairs | 305.26 MB | 94.48 MB | 69.0% less |
| Median complete seven-turn workflow | 57.32 s | 41.79 s | 27.1% less |
| Answer checks passed | 35 / 35 | 35 / 35 | All checks passed in this set |

Median per-turn time to first token fell by 31.2%. Workflow time includes preparation and processing, excluding fixed observation waits. Send totals are process network counters including startup, control traffic, TLS, retries and fallback. MB means 1,000,000 bytes; these are not image-file sizes or token counts. Cost savings were not measured. [Original aggregate](experiments/http-results.json) · [Setup and provenance](experiments/README.md)

### Large image requests: retries can multiply the overhead

A separate WebSocket diagnostic recorded:

| Request | Compressed frame | Result | First token |
| --- | --- | --- | --- |
| 4 large images | 10.60 MB | WS success, no retries | 11.47 s |
| 5 large images, 2 trials | About 13.24 MB | 1009 → HTTP fallback | 57.02 s / 57.44 s |

Each five-image trial received 1009 on all six sends before HTTP fallback. The two trials sent 92.88 MB and 92.90 MB at process level. The same five images in an isolated HTTP control sent 13.24 MB, with 10.37 s to first token. File compression alone does not capture this overhead: failures, retries and full elapsed time also matter. These samples do not establish a universal size limit, and ICM does not fix this WebSocket issue. [Diagnostic data](experiments/websocket-results.json)

## Integration scope

The skill and local tools prepare future image inputs, save findings and retrieve originals. **They cannot remove images already embedded in Claude Code or Codex conversation history.** If your own agent controls every complete request, the Python library can manage historical images: [integration requirements](docs/INTEGRATION.md).

This is an experimental release. The 27 local tests pass; a Codex functional session verified tool calls, visual-worker inspection, saved findings and original recall. Speedups in real workflows still need a separate controlled comparison. [Validation record](docs/VALIDATION.md)

[Commands, updates and uninstalling](docs/AGENT-SETUP.md) · [Contributing](CONTRIBUTING.md) · [Changelog](CHANGELOG.md) · [License](NOTICE) · [Artwork attribution](docs/images/reference/ATTRIBUTION.md)

<br/>

<div align="center">
<p>README layout and visual style inspired by <a href="https://github.com/browser-use/browser-use">Browser Use</a>.</p>

[![Source](docs/images/reference/footer-source.svg)](https://github.com/messsiii/image-context-manager)
&emsp;
[![License](docs/images/reference/footer-license.svg)](LICENSE)
</div>
