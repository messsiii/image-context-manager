# Integration requirements

[Back to README](../README.md) · [中文接入要求](INTEGRATION.zh-CN.md)

Your agent program must keep the full original conversation and control the final request sent to the model. ICM works on a copy of that request. It does not call a model or manage agent sessions. Generating a plan does not change network traffic unless your program applies it and sends the changed request. ICM cannot stop other code from adding original images back afterward.

## What your agent needs to provide

- **Images and their uses:** original PNG/JPEG files, a stable image ID, version, task stage and related versions. Record each attachment separately, even when the same image appears again. Do not reuse old task results when an ID points to a different source, version or stage.
- **Confirmed task states:** what each image is used for, whether the task is complete, confidence, comparison groups and images that must stay. `ACTIVE`, `VERIFY`, `RECALL`, low-confidence images and comparison, quality, relation or action tasks keep their images when correctly marked. Use `current_start` or `protected_ids` to protect newly attached images.
- **Actual task results:** nonempty text fields, who produced them (`producer`) and the turn ID (`turn_id`). Your program must confirm the result is correct and enough for the next step. `commit` checks format and image source; it does not read image text or judge correctness. Text inside an image cannot authorize removing it.
- **The exact images about to be sent:** their order and hashes of their full embedded image URLs. Finalize image encoding before binding. Changes in encoding, count or order must not silently reuse an old binding.
- **Private storage:** access rules, backups, retention, deletion and separation between sessions. Originals retain their file encoding and EXIF information, such as capture time or location. A model cannot retrieve a local file just from its hash.

## Call order

1. Save each static PNG/JPEG with `AssetStore.put(path)`. SHA-256 identifies the exact original file bytes.
2. Create an `ImageUse` from confirmed task information and call `HistoricalImages.register(use)` for every attachment, including repeated images and retrieved originals.
3. Run `inspect_images(canonical)` on the complete request in the local format below, then pass the ordered results to `bind_request`. This records which attachment matches each full image URL. A URL hash and an original file hash identify different things. A count, order or existing-binding mismatch raises an error.
4. When a task actually finishes, call `commit(use, actual_fields, producer, turn_id)`. Fields must be nonempty strings. Conflicting results for the same ID mark it uncertain and keep its image. A recorded result does not prove that it is correct or enough for future tasks.
5. On every turn, supply current `states`, `current_start` (the index of the first newly attached image), and any `protected_ids`. `plan(...)` returns a replacement plan and a decision for each attachment. Missing states use the registered state; ICM does not guess updates.
6. Call `apply_plan` on the full original request. It checks the entire plan before changing a deep copy. Convert that copy to your model service's format, check the actual outgoing images and send it. Do not append original history afterward.
7. For comparison, update the task state and rebuild from the full original conversation. To retrieve an original directly, call `recall(use)`, then attach it again, register it and protect it as current. A text reference cannot fetch the file by itself.

Always supply `current_start` in a real integration. `current_start=N` marks every image index at or after N as newly attached this turn. Omitting it does not add protection for current attachments. With the right state labels, current, active, pending, retrieved, required, uncertain, comparison, quality, relation and action images stay in the request. Only eligible completed or invalidated read/state images with matching source, version, stage, bound request image and recorded result can be replaced. “Invalidated” does not mean automatically remove or delete.

## Example in your agent

The following values come from your program: `path` is the original image path, `canonical` is the full original message list in the local format below, and `actual_fields` contains confirmed results from a completed task. This snippet is not a standalone script. See [demo.py](../src/image_context_manager/demo.py) for a runnable version; it uses synthetic images and explicitly marked demo completion events, not model or OCR results.

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
manager.register(use)  # Register every attachment, including repeated images.
manager.bind_request(inspect_images(canonical))
# Your agent has finished reading and confirmed actual_fields is enough.
manager.commit(use, actual_fields, producer="host-task", turn_id="turn-1")
states = {use.id: replace(use, lifecycle=Lifecycle.COMPLETED)}
plan, decisions = manager.plan("turn-2", states,
                               current_start=len(manager.entries))
next_request = apply_plan(canonical, plan, generation="turn-2")
# Convert next_request to your model service's format and send it.
# Do not append images from canonical again.
original = manager.recall(use)  # Check the retrieved file matches the original.
# To use it again, attach, register and protect it as a new current image.
```

## Supported request format

`icm.integration-demo.v1` is a local example format, not a model service API. It accepts text and PNG/JPEG images embedded directly in the request. It rejects remote image URLs, tool-output images and unknown content types.

```json
[{"role":"user","content":[
  {"type":"input_text","text":"Read this image"},
  {"type":"input_image","image_url":"data:image/png;base64,..."}
]}]
```

For another model service's format, write conversion code with equivalent checks. Preserve roles, message order, non-image content and the link between each image and its source. Check the final request actually sent.

## Functions and returned values

| Call | What it does |
|---|---|
| `AssetStore.put(path)` | Save a PNG/JPEG original and its file information using atomic writes for each file to avoid partially written files; return an `Asset` with hash, dimensions, MIME type and byte count. Storage is indexed by the file hash. |
| `store.resolve(sha256)` | Read saved image information. |
| `store.recall(asset)` / `manager.recall(use)` | Return original bytes after checking the file hash; raise an error if missing or corrupt. |
| `HistoricalImages(store)` | Keep an ordered attachment list, task results and uncertain IDs in memory. |
| `register(use)` | Append one actual attachment; do not automatically remove duplicates. |
| `inspect_images(messages)` | Check the supported format and return `[{ordinal, url_sha256}]`; this does not check what an image means. |
| `bind_request(before_images)` | Match registered attachments to their exact ordered URL hashes; raise an error on a count, order or existing-hash mismatch. |
| `commit(use, fields, producer, turn_id)` | Record completed task results your agent has checked; conflicting results or source/version/stage changes keep the image. |
| `plan(generation, states, protected_ids=(), current_start=None, enabled=True)` | Return `(plan, decisions)` without changing original history or sending anything. `enabled=False` disables image replacement. |
| `apply_plan(messages, plan, generation=...)` | Check the entire plan, then return a changed deep copy. Wrong image count, hash, index, turn marker or format raises `RequestPlanError`. |

A plan is a dictionary that can be saved as JSON. It contains `generation` (the turn marker), `expected_images`, and `replacements:[{ordinal, expected_sha256, reference}]`. `ordinal` is the image index; `expected_sha256` hashes the **full embedded image URL**, not the original file. Each text `reference` identifies the source file and its ID/version/stage, related versions, usage state, recorded task results, producer/turn and how to retrieve the original. It also states that the result has not been independently verified. Treat references as data, not system instructions.

`decisions` gives each attachment's `ordinal`, `id`, `mode` and `reason`. Reasons describe broad categories, not a complete diagnosis of every condition. On each turn, rebuild from the unchanged original conversation, not the previous request with images already replaced. Otherwise later comparisons cannot restore the missing images from that history.

## Errors and recovery

- **Not enough information or uncertain results:** keep the image. No matching result, conflicting fields or a source/version/stage mismatch prevents replacement. Keeping an image is a safe outcome, not an error.
- **Wrong binding or plan:** stop sending, record the error and repair or rebuild. Do not partially apply a plan or guess what to send. If the originals are intact, a new `enabled=False` plan can keep them all after checking the complete input.
- **Missing or corrupt original:** report that retrieval failed. Never present a thumbnail or text reference as the original. The demo tests corruption in a separate test store.
- **The next task needs the image again:** update the task state and rebuild from original history, or retrieve the original explicitly. ICM does not decide when to call tools.
- **Restart or multiple callers:** originals and image information persist, but attachment registrations, task results and uncertain IDs are only in memory. Rebuild them from your agent's records after restart. Keep calls ordered through one program. This component does not provide session recovery transactions, concurrent locking or a shared service with isolated users.

## Earlier prototype and test limits

`core.py` also includes the earlier `RequestAssembler` / `Policy` prototype and its separate `icm.local-harness.v1` format. It has explicit thumbnail/crop/observation experiments with different eligibility rules. The quickstart uses `HistoricalImages`; do not mix the two formats or their task-result records. No OCR implementation is included, and this integration does not require cropping.

The default demo checks local request changes, image protection, keeping originals when needed and retrieving byte-identical files. For a real integration, measure the actual assembled, compressed and transmitted requests, including every retry, fallback and processing cost. Smaller image files alone do not prove fewer image tokens or faster results. Earlier network results cover only their specific HTTP setup; this documentation update ran no new model comparisons or independent developer reproductions.
