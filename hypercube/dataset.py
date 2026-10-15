"""Verify saved artifacts before analysis, including canonical reproducibility."""
from pathlib import Path
import tempfile
from .generation import build_dataset, digest, make_prompt
from .scoring import strict_json
from .validation import validate_instance, check_path


def load_dataset(root):
    root = Path(root).resolve()
    manifest = strict_json((root/'manifest.json').read_text(encoding='utf-8'))
    if type(manifest) is not dict or type(manifest.get('files')) is not dict or type(manifest.get('instances')) is not list:
        raise ValueError('invalid dataset manifest')
    for relative, expected in manifest['files'].items():
        path = (root/relative).resolve()
        if not path.is_relative_to(root):
            raise ValueError('manifest path escapes dataset directory')
        if digest(path.read_bytes()) != expected:
            raise ValueError(f'file hash mismatch: {relative}')
    instances = {}
    for row in manifest['instances']:
        if type(row) is not dict:
            raise ValueError('manifest instance row must be object')
        for key in ('instance_file','reference_file','prompt_file'):
            if row.get(key) not in manifest['files']:
                raise ValueError('manifest instance file missing from fingerprint inventory')
        g = strict_json((root/row['instance_file']).read_text(encoding='utf-8'))
        validate_instance(g)
        if g.get('id') != row.get('id') or g['id'] in instances:
            raise ValueError('invalid or duplicate instance identifier')
        reference = strict_json((root/row['reference_file']).read_text(encoding='utf-8'))
        if reference.get('instance_id') != g['id'] or not check_path(g,reference.get('path'))['valid']:
            raise ValueError('invalid reference certificate')
        prompt = (root/row['prompt_file']).read_text(encoding='utf-8')
        if prompt != make_prompt(g) or digest(prompt.encode('utf-8')) != row['prompt_sha256']:
            raise ValueError('prompt differs from fixed template or prompt hash')
        instances[g['id']] = g
    # Independent mathematical checks above precede canonical byte comparison.
    with tempfile.TemporaryDirectory() as temporary:
        expected_root = Path(temporary)
        expected_manifest = build_dataset(expected_root)
        if manifest != expected_manifest:
            raise ValueError('manifest differs from the frozen pilot protocol')
        expected_files = set(expected_manifest['files']) | {'manifest.json'}
        actual_files = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
        if actual_files != expected_files:
            raise ValueError('dataset contains missing or unexpected files')
        for relative in sorted(expected_files):
            if (root/relative).read_bytes() != (expected_root/relative).read_bytes():
                raise ValueError(f'non-reproducible dataset bytes: {relative}')
    schedule = strict_json((root/'schedule.json').read_text(encoding='utf-8'))
    return manifest, instances, schedule
