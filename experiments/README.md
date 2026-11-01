# Experiments: historical evidence, not the default install path

The Python package/demo is independent of Codex and has no model client. These files document earlier synthetic experiments. They do not make installing the library change an installed agent. No model experiments were rerun for the public release.

## Native HTTP: historical fourth round

- Workflow: seven synthetic image tasks, five independent A/B pairs, ten threads, 70 total attempts. A replayed original history; B used host-declared lifecycle and actual completed-task receipts. The harness, not this library, supplied lifecycle events and sufficiency assumptions.
- Host: public Codex `rust-v0.162.1`, isolated debug-source adapter, existing login, native HTTP and compression, macOS aarch64. Not a direct model API substitute.
- Strict correctness: A 35/35, B 35/35. Attempts/failures were not selectively discarded.
- B/A: cumulative process socket sends **0.30950354**; median per-turn TTFT **0.68809493**; median complete-workflow E2E **0.72914439**. No measured billing/cost conclusion (`actual_cost` is null).
- [Original aggregate report](http-results.json), [provenance and source hashes](http-provenance.json). Aggregates include five workflow durations and byte totals per arm; prompt/response bodies, raw sessions, private material and credentials are excluded. The original aggregate report hash is retained for integrity; the underlying private delivery archive is not published.

Socket counters were macOS nettop process-lifetime bytes_out for an isolated app-server PID, including startup/control/TLS/retries/fallback. This is not JSON request size, visual tokens, physical link traffic, billing, or guaranteed server receipt. TTFT and end-to-end elapsed time are separate. The five-pair synthetic result is not independent external reproduction or evidence for default Codex, real App Store operations, other models or arbitrary task semantics.

## WebSocket diagnosis: unresolved size-related rejection

[Metadata-only summary](websocket-results.json) retains all six case directories' outcomes, including the invalid setup trial. Seven valid diagnostic turns had correct answers; only five met protocol checks. An answer after HTTP fallback does not count as WS success.

- Small image: three correct native WS turns, later turns using incremental continuation.
- Four large synthetic images: WS succeeded, no retries; JSON 14,147,876 B, compressed frame 10,597,259 B.
- Five images: two fresh first-turn trials each sent six large requests, each receiving close **1009**, then fell back to HTTP. First-turn TTFT 57.439 / 57.024 s; process sends 92,876,128 / 92,896,154 B. Failed sends and retries remain included.
- Same five images forced to isolated HTTP: correct, no retries; 10.372 s TTFT and 13,243,020 B process sends. This single diagnostic control is not a performance benchmark.
- Initial small trial was invalid: relative image paths prevented image loading. Its three records are retained as `invalid-setup` and excluded from valid-image correctness.

[1009 means a message too big for the receiving endpoint](https://www.rfc-editor.org/rfc/rfc6455#section-7.4.1). We narrowed the phenomenon to size-related remote rejection; the exact threshold and rejecting layer remain unknown and no underlying fix is claimed. Five-image uncompressed JSON was about 17.65 MB but compressed frames about 13.24 MB: do not describe this as a confirmed 16 MiB frame limit. No direct-vs-proxy comparison was performed.

Frame lengths were measured after deflate/masking/header construction; above-TLS writes accepted locally do not prove remote receipt. HTTP zstd body size is not total process socket traffic. Measurements in this diagnostic set are not randomized benefit acceptance data.

Unmodified small-image history can continue incrementally. Source inspection suggests replacing old images changes the request prefix and forces a full input instead of a previous-response delta; actual WS image-retirement behavior remains **unverified**. No desktop transport or long-lived connection stability claim is made.

## Optional source patches

[Codex adapter](codex/README.md) and [diagnostic patch notes](websocket-diagnostics/README.md) are explicitly research-only. They are not stable extension APIs. Build metadata identifies upstream tags/revisions and hashes; no toolchain, dependency cache, compiled host, credentials or raw request bodies are published. Directory-specific licensing is explained in [NOTICE](../NOTICE).

The default path for a later real-workflow pilot is the isolated native HTTP profile, with consistent settings across arms and complete retry/quality accounting. That pilot and any new formal A/B are outside this release.
