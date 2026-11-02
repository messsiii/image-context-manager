"""JSON CLI for local agents."""
import argparse
import json
from pathlib import Path
from .agent import Workspace, install
from .core import Task, Lifecycle


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', default='.icm')
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('install')
    p.add_argument('--agent', choices=['codex', 'claude', 'both'], required=True)
    p.add_argument('--project', required=True)
    p = sub.add_parser('add')
    p.add_argument('path'); p.add_argument('--id', required=True)
    p.add_argument('--task', action='append', choices=[t.value for t in Task], required=True)
    p.add_argument('--version', required=True); p.add_argument('--stage', required=True)
    sub.add_parser('list')
    p = sub.add_parser('state')
    p.add_argument('id'); p.add_argument('state', choices=[s.value for s in Lifecycle])
    p.add_argument('--task', action='append', choices=[t.value for t in Task])
    p = sub.add_parser('record')
    p.add_argument('id'); p.add_argument('--file', required=True)
    p = sub.add_parser('prepare')
    p.add_argument('id'); p.add_argument('--mode', choices=['auto', 'original', 'compress', 'crop', 'text'], default='auto')
    p.add_argument('--edge', type=int, default=1280); p.add_argument('--quality', type=int, default=85)
    p.add_argument('--max-bytes', type=int)
    p.add_argument('--roi', nargs=4, type=int); p.add_argument('--region-verified', action='store_true')
    p.add_argument('--allow-lossy', action='store_true')
    p = sub.add_parser('recall'); p.add_argument('id')
    p = sub.add_parser('delegate')
    p.add_argument('ids', nargs='+'); p.add_argument('--goal', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'install':
            output = install(args.project, args.agent)
        else:
            ws = Workspace(args.workspace)
            with ws.transaction() as state:
                if args.command == 'add':
                    output = ws.add(state, args.id, args.path, args.task, args.version, args.stage)
                elif args.command == 'list':
                    output = list(state.values())
                elif args.command == 'state':
                    item = state[args.id]
                    if args.task and set(args.task) != set(item['tasks']):
                        item['tasks'] = args.task
                        item['result'] = None
                    item['lifecycle'] = args.state
                    output = item
                elif args.command == 'record':
                    output = ws.record(state, args.id, json.loads(Path(args.file).read_text()))
                elif args.command == 'prepare':
                    output = ws.prepare(state[args.id], args.mode, args.edge, args.quality, args.roi,
                                        args.region_verified, args.allow_lossy, args.max_bytes)
                elif args.command == 'recall':
                    output = ws.prepare(state[args.id], 'original')
                    state[args.id]['lifecycle'] = 'recalled'
                else:
                    images = []
                    for key in args.ids:
                        item = state[key]
                        images.append(dict(item, original=ws.prepare(item, 'original')['path']))
                    output = dict(goal=args.goal, images=images,
                        instruction='Invoke icm-visual-worker using the host native subagent tool. Return text only. This command does not start an agent.')
                    path = ws.root / 'handoff.json'
                    from .core import AssetStore
                    AssetStore._atomic(path, json.dumps(output, ensure_ascii=False).encode())
                    output = dict(handoff=str(path), **output)
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, KeyError, OSError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
