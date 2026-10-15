"""Offline commands. No provider SDKs, credentials or network requests."""
import argparse
from pathlib import Path
from .dataset import load_dataset
from .generation import build_dataset, json_bytes, digest
from .scoring import strict_json, summarize, model_identity
from .pilot_audit import audit_pilot, write_audit, DEFAULT_PILOT


def main():
    parser = argparse.ArgumentParser(description='Generate and verify the hypercube LLM pilot locally.')
    commands = parser.add_subparsers(dest='command', required=True)
    generate = commands.add_parser('generate')
    generate.add_argument('--output', type=Path, default=Path('data'))
    verify = commands.add_parser('verify')
    verify.add_argument('--dataset', type=Path, default=Path('data'))
    score = commands.add_parser('score')
    score.add_argument('--dataset', type=Path, default=Path('data'))
    score.add_argument('--attempts', type=Path, default=Path('responses/attempts.jsonl'))
    score.add_argument('--models', type=Path, default=Path('responses/model-config.json'))
    score.add_argument('--output', type=Path, default=Path('results/summary.json'))
    audit = commands.add_parser("audit-pilot")
    audit.add_argument("--dataset", type=Path, default=Path("data"))
    audit.add_argument("--pilot", type=Path, default=DEFAULT_PILOT)
    audit.add_argument("--output", type=Path, default=Path("results/pilot-20"))
    audit.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == 'audit-pilot':
            report = audit_pilot(args.dataset, args.pilot)
            write_audit(report, args.output, check=args.check)
            print(f"Audited {report['received']}/{report['planned']} responses; {report['missing']} missing.")
            return
        if args.command == 'generate':
            manifest = build_dataset(args.output)
            print(f'Generated {len(manifest["instances"])} instances; no model responses collected.')
            return
        manifest, instances, schedule = load_dataset(args.dataset)
        if args.command == 'verify':
            print(json_bytes({'instances':len(instances),'prompts':len(instances),
                              'reference_paths':len(instances),'planned_responses':len(schedule),
                              'status':'all artifacts checked; no model performance implied'}).decode(),end='')
            return
        attempts = [strict_json(line) for line in args.attempts.read_text(encoding='utf-8').splitlines() if line.strip()]
        models = strict_json(args.models.read_text(encoding='utf-8'))
        collection_mode = models.get('collection_mode','exact_model_id') if type(models) is dict else 'exact_model_id'
        if collection_mode not in ('exact_model_id','manual_app'):
            raise ValueError('unknown collection_mode')
        if attempts:
            for label in ('model_a', 'model_b'):
                config = models.get(label) if type(models) is dict else None
                if type(config) is not dict:
                    raise ValueError('configure both model slots before scoring')
                identity = model_identity(config)
                if identity[2] == 'display_label_only' and collection_mode != 'manual_app':
                    raise ValueError('display labels require explicit manual_app collection mode')
                if 'requested_settings' not in config or (config['requested_settings'] is not None
                                                          and type(config['requested_settings']) is not dict):
                    raise ValueError('configured requested_settings must be an object or null when unknown')
            slots = {s['slot_id']:s for s in schedule}
            for a in attempts:
                if type(a) is not dict or a.get('slot_id') not in slots:
                    raise ValueError('unknown or missing slot_id')
                config = models.get(slots[a['slot_id']]['model'])
                if model_identity(a) != model_identity(config):
                    raise ValueError('attempt identity differs from frozen model configuration')
                if a.get('requested_settings') != config['requested_settings']:
                    raise ValueError('attempt requested settings differ from frozen model configuration')
        result = summarize(schedule,attempts,instances)
        result['collection_mode'] = collection_mode
        result['identity_limitation'] = ('App display labels are user-reported; exact model versions and hidden app settings remain unverified.'
                                         if collection_mode == 'manual_app' else None)
        result['dataset_manifest_sha256'] = digest((args.dataset/'manifest.json').read_bytes())
        result['attempts_sha256'] = digest(args.attempts.read_bytes())
        result['model_config_sha256'] = digest(args.models.read_bytes())
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_bytes(json_bytes(result))
        print(f'{result["measurement_status"]}; summary saved to {args.output}')
    except (OSError,ValueError,KeyError,TypeError,AttributeError,RecursionError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
