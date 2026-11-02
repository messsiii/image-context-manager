# Diagram attribution

The `paths-*` and `architecture-*` SVGs adapt the MIT-licensed diagrams from [Browser Use](https://github.com/browser-use/browser-use/tree/b49a68e4060acb226da8f784194fef301c53a6d7), by Gregor Zunic (copyright 2024). The complete license is preserved in [UPSTREAM_LICENSE](UPSTREAM_LICENSE).

Original files: `static/readme/which-product-{light,dark}{,-mobile}.svg` and `examples/integrations/toolsets-for-claude/architecture-{light,dark}{,-mobile}.svg`.

Modifications: project-specific labels, descriptions, routing and ICM marks. Geometry, light/dark palettes, typography, source dimensions, responsive variants and reduced-motion animations follow the upstream source. They depict ICM local artifacts and host-owned request processing, not Browser Use products or supported model integrations.

The `tool-workflow-*` SVGs use the same visual conventions (palette, dot grid, typography, isometric icons, animated orange connectors and separate mobile layouts). Their workflow, labels and layout are specific to the current ICM skill and tools. They are workflow schematics, not session recordings. Rebuild these diagrams with `python3 tools/render_workflow.py`.

Wordmark, badge artwork, synthetic demo visualization, and benchmark plotting are original project documentation assets. The canyon hero and office still-life are original AI-generated illustrative artwork; the latter does not depict the project author or a real project office. Neither contains upstream branding or founder photography.
