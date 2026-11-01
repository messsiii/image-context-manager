# Optional metadata instrumentation

`codex-diagnostic.patch` is incremental on `../codex/history-host.patch` for
Codex rust-v0.162.1. `tungstenite-diagnostic.patch` applies at the root of the
isolated Cargo checkout identified in build-metadata.json. These are research
patches, not a supported installed-Codex plugin or a fix for close 1009.

Only debug builds with `ICM_WS_DIAGNOSTIC=1` log metadata: handshake status,
request full/delta mode, serialized JSON length, final compressed frame length,
above-TLS accepted writes, close code, and timing. They do not log credentials,
headers, URLs or request bodies. The library's default demo does not enable or
require these patches, and this release does not include a model-call driver.

Use a separate source/toolchain/CARGO_HOME/RUSTUP_HOME and target directory;
never modify the installed client or a global dependency cache. Force rebuild
of the modified tungstenite dependency: edits inside a Cargo git checkout may
not invalidate previously compiled artifacts automatically. Build the isolated
host with Rust 1.95.0, dev-small profile and the checked isolated lock. Existing
endpoint tests were 12/12 passing during diagnosis; source and prior host binary
were restored afterward. Cross-path builds need not reproduce binary hashes.

The source patch base is Apache-2.0, with Codex license/NOTICE in ../codex.
The tungstenite patch is MIT OR Apache-2.0, with both upstream license texts
in this directory. See the root NOTICE for modification attribution.
