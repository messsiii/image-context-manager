"""Offline file-operation walkthrough, not a model or speed benchmark."""
import argparse
import json
from pathlib import Path
from PIL import Image
from image_context_manager.agent import Workspace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error('Choose a new output directory')
    args.out.mkdir(parents=True)
    source = args.out / 'synthetic.png'
    Image.effect_noise((1200, 800), 60).convert('RGB').save(source)
    workspace = Workspace(args.out / 'workspace')
    with workspace.transaction() as state:
        item = workspace.add(state, 'draft', source, ['read_content'], 'v1', 'draft')
        original = workspace.prepare(item)
        compressed = workspace.prepare(item, 'compress', edge=600, allow_lossy=True)
        crop = workspace.prepare(item, 'crop', roi=[0, 0, 300, 200], region_verified=True)
        # Explicit synthetic completion event, NOT a real OCR or agent result.
        workspace.record(state, 'draft', dict(id=item['id'], source_sha256=item['source_sha256'],
            version='v1', stage='draft', producer='synthetic-demo',
            fields={'fixture': 'Synthetic noise; no OCR claim'}, verified=True, sufficient=True))
        item['lifecycle'] = 'completed'
        text = workspace.prepare(item)
        recall = workspace.prepare(item, 'original')
    report = dict(scope=__doc__, original=original, compressed=compressed, crop=crop,
                  text=text, recall_byte_exact=Path(recall['path']).read_bytes() == source.read_bytes())
    (args.out / 'report.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
