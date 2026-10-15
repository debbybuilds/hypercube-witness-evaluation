"""Versioned deterministic generation from mathematical definitions."""
import hashlib
import json
from pathlib import Path
from .validation import validate_instance
from .search import find_path

SEED = 'hypercube-pilot-v1'
VERSION = 'sha256-antipodal-pairs-v1'


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode('utf-8')


def digest(value):
    return hashlib.sha256(value).hexdigest()


def _key(parts):
    return json.dumps(parts, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def make_instance(n, candidate, seed):
    if type(n) is not int or n not in (3, 4):
        raise ValueError('generation supports dimensions 3 and 4')
    if type(candidate) is not int or candidate < 0 or type(seed) is not str:
        raise ValueError('candidate must be nonnegative integer and seed must be string')
    mask = (1 << n) - 1
    edge_pairs = set()
    for u in range(1 << n):
        for bit in range(n):
            v = u ^ (1 << bit)
            edge_pairs.add(tuple(sorted((f'{u:0{n}b}', f'{v:0{n}b}'))))
    assigned = {}
    for edge in sorted(edge_pairs):
        if edge in assigned:
            continue
        opposite = tuple(sorted(f'{int(v,2)^mask:0{n}b}' for v in edge))
        pair_label = min(edge, opposite)
        color = hashlib.sha256(_key([seed, n, candidate, list(pair_label)])).digest()[0] & 1
        assigned[pair_label] = color
        assigned[max(edge, opposite)] = 1 - color
    result = {'n': n, 'edges': [[u, v, assigned[(u,v)]] for u,v in sorted(edge_pairs)],
              'generation': {'seed': seed, 'candidate': candidate, 'version': VERSION}}
    validate_instance(result)
    return result


def make_prompt(instance):
    validate_instance(instance)
    edges = '\n'.join(f'{u} {v} {c}' for u,v,c in instance['edges'])
    return (
        f'Consider the {instance["n"]}-dimensional hypercube. Vertices are binary strings of length '
        f'{instance["n"]}; adjacent vertices differ in exactly one bit. '
        'The antipode of a vertex complements every bit. Edges are undirected. '
        'Each edge has color 0 or 1; antipodal edges have opposite colors.\n\n'
        'Find a simple path joining ANY vertex to its antipode, with all path edges having '
        'the same color. Every consecutive pair must be an edge in the list below. '
        'Do not repeat vertices. The path need not be shortest.\n\n'
        'Complete edge list (vertex vertex color):\n' + edges + '\n\n'
        'Return only a JSON object with one key, "path", containing the vertex sequence '
        'as fixed-width binary strings. Schematic format: {"path":["<vertex>","..."]}. '
        'Replace the placeholders with your path. Do not include explanations or Markdown.\n'
    )


def build_dataset(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    manifest = {'protocol_version': 1, 'seed': SEED, 'generator_version': VERSION,
                'instances': [], 'exclusions': [], 'files': {}}
    def write(relative, content):
        path = output / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        manifest['files'][relative] = digest(content)
    for n in (3, 4):
        seen, candidate = set(), 0
        for number in range(1, 11):
            while True:
                if candidate >= 10000:
                    raise ValueError('candidate safety limit reached; investigate generation')
                instance = make_instance(n, candidate, SEED)
                colors = _key(instance['edges'])
                if colors not in seen:
                    break
                manifest['exclusions'].append({'n': n, 'candidate': candidate, 'reason': 'duplicate coloring'})
                candidate += 1
            instance['id'] = f'q{n}-{number:02d}'
            path = find_path(instance)
            if path is None:
                manifest['exclusions'].append({'n': n, 'candidate': candidate, 'reason': 'no antipodal path'})
                (output/'generation-failure.json').write_bytes(json_bytes(manifest))
                raise ValueError('candidate has no antipodal path; generation stopped for investigation')
            seen.add(colors)
            row = {'id': instance['id'], 'n': n, 'candidate': candidate,
                   'instance_file': f'instances/{instance["id"]}.json',
                   'prompt_file': f'prompts/{instance["id"]}.txt',
                   'reference_file': f'reference/{instance["id"]}.json'}
            write(row['instance_file'], json_bytes(instance))
            write(row['prompt_file'], make_prompt(instance).encode('utf-8'))
            write(row['reference_file'], json_bytes({'instance_id': instance['id'], 'path': path}))
            row['instance_sha256'] = manifest['files'][row['instance_file']]
            row['prompt_sha256'] = manifest['files'][row['prompt_file']]
            manifest['instances'].append(row)
            candidate += 1
    schedule = [{'slot_id': f'{model}/{r["id"]}/{trial}', 'model': model,
                 'instance_id': r['id'], 'n': r['n'], 'trial': trial,
                 'prompt_sha256': r['prompt_sha256']}
                for r in manifest['instances'] for model in ('model_a','model_b') for trial in (1,2,3)]
    schedule.sort(key=lambda s: digest(_key([SEED, s['slot_id']])))
    write('schedule.json', json_bytes(schedule))
    (output/'manifest.json').write_bytes(json_bytes(manifest))
    return manifest
