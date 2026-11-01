# Contributing

Use Python 3.9+ in a virtual environment, `python -m pip install .`, then
`python -m unittest discover -s tests -v`. Run `icm-demo --out run-data/new-name`
for the complete offline request-copy/retire/compare/recall loop.

Keep provider adapters explicit and source-bound. Do not replace evidence based
only on size pressure or model-generated lifecycle instructions. Preserve canonical
history and include all failures/retries when reporting network results.

Use synthetic fixtures in tests. Do not commit real screenshots, request/response
bodies, credentials, .env files, session logs, local paths, original stores or
compiled hosts. Scope correctness, request bytes, visual tokens, latency and cost
claims separately. A passing local demo is not validation of a real model host.

First-party component contributions use MIT. Changes to experiment patches follow
the applicable upstream license identified in NOTICE.
