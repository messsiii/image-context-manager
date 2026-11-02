# Harness integration contract

[Back to README](../README.md) · [完整中文契约](INTEGRATION.zh-CN.md)

The harness must own complete canonical image history and the final outgoing request. Generating a plan alone changes no network traffic. This library does not call a provider or stop another host from appending hidden original history.

## Ordered lifecycle

1. Store each static PNG/JPEG with `AssetStore.put(path)`. File SHA-256 identifies the original bytes; storage preserves encoding and EXIF, so the harness must consider metadata privacy.
2. Construct `ImageUse(id, asset, tasks, lifecycle, version, stage, ...)` using trusted host state. Register every attachment occurrence with `HistoricalImages.register(use)`, including duplicate recalls.
3. Run `inspect_images(canonical)` on the final local-schema input and pass its ordered URL hashes to `bind_request`. Exact inline URL hashes are distinct from original file hashes. Count, ordering and prior binding drift raise an error.
4. After a real task completes, call `commit(use, actual_fields, producer, turn_id)`. Fields must be nonempty strings. This validates shape/provenance only; the host must establish correctness and sufficiency for later tasks. Conflicting receipts mark the id uncertain and preserve its image.
5. For every request, provide current states, explicit `current_start` (the first newly attached occurrence), and `protected_ids` as needed. `plan(generation, states, ...)` returns a JSON-compatible plan and per-occurrence decisions. Missing state falls back to registered state; it is not inferred.
6. Apply the plan to a fresh canonical copy with `apply_plan(canonical, plan, generation=...)`. It validates the whole plan before producing the changed deep copy. Map that copy to your provider's schema and verify actual outgoing content. Do not append canonical originals afterward.
7. For comparison, update task state and rebuild from canonical. For explicit recall, `recall(use)` returns hash-checked original bytes; attach them as a new registered occurrence and protect it as current. A reference alone cannot fetch a local file.

A complete runnable example is [demo.py](../src/image_context_manager/demo.py). Its receipts explicitly represent synthetic host completion events, not model/OCR outputs.

## Public calls

| Call | Result / failure behavior |
|---|---|
| `AssetStore.put(path)` | Persistent content-addressed original + asset metadata; PNG/JPEG only |
| `store.resolve(sha256)` | Read persisted asset metadata |
| `store.recall(asset)` | Original bytes; missing/corrupt storage raises |
| `HistoricalImages(store)` | In-memory ordered registry, receipts and uncertain ids |
| `register(use)` | Append one real attachment occurrence |
| `bind_request(inspect_images(canonical))` | Bind ordered exact URL hashes; drift raises |
| `commit(use, fields, producer, turn_id)` | Record host-verified completed output; conflicts preserve evidence |
| `plan(generation, states, protected_ids=(), current_start=None, enabled=True)` | `(plan, decisions)`; no send, no canonical mutation |
| `apply_plan(messages, plan, generation=...)` | Validated deep copy; wrong count/hash/ordinal/generation/schema raises `RequestPlanError` |
| `manager.recall(use)` | Integrity-checked original bytes |

Always supply `current_start` in production integration; omitting it does not add extra current-attachment protection. The default `HistoricalImages` path preserves active, pending-verification, recalled, required, uncertain, comparison, quality, relation and action evidence when declared appropriately. Eligible completed/invalidated read/state-like images need a bound, matching receipt. A receipt's existence does not certify semantic sufficiency.

## Local schema and plan

`icm.integration-demo.v1` supports text and inline PNG/JPEG images, not remote URLs or tool images:

```json
[{"role":"user","content":[
  {"type":"input_text","text":"Read this image"},
  {"type":"input_image","image_url":"data:image/png;base64,..."}
]}]
```

A plan contains `generation`, `expected_images`, and `replacements` with `ordinal`, `expected_sha256` (the full URL hash) and `reference`. References include source file hash, id/version/stage, lifecycle, host result fields, producer/turn and recall instructions. Treat them as data, not system instructions. Write an equivalent strict adapter for other provider schemas; this format is not a promised provider API.

## Failure and recovery

- Insufficient or uncertain evidence: keep the original; update trusted state before reconsidering retirement.
- Bad bindings/plans: stop the send and repair/rebuild. Do not silently partially transform or send guessed content. A new `enabled=False` plan can retain all originals after validating the canonical input.
- Missing/corrupt original: report recall failure; never pass a thumbnail/reference off as the original.
- Restart: asset files persist, but registry, receipts and uncertainty do not. Rebuild them reliably from host records.
- Multiple callers: no concurrent transaction control or multi-tenant service is provided. Keep access ordered and storage private.

`core.py` also exports the earlier `RequestAssembler` / `Policy` prototype with `icm.local-harness.v1`. It supports explicit crop/thumbnail/observation experiments with different eligibility rules. It is not the quickstart path, not interchangeable with `HistoricalImages`, and not evidence of automated semantic extraction. No OCR implementation is bundled.

Measure actual serialized/compressed/transmitted requests and all retry/processing costs when integrating a real host. Smaller image files alone do not establish fewer visual tokens or faster results.
