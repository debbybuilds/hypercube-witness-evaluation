import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from hypercube.generation import make_instance, make_prompt, build_dataset
from hypercube.validation import validate_instance, check_path


class GenerationTests(unittest.TestCase):
    def test_generated_topology_and_reproducibility(self):
        for n, count in [(3,12),(4,32)]:
            g = make_instance(n, 0, 'hypercube-pilot-v1')
            validate_instance(g)
            self.assertEqual(len(g['edges']), count)
            self.assertEqual(g, make_instance(n, 0, 'hypercube-pilot-v1'))

    def test_complete_dataset_and_byte_identical_rebuild(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            manifest = build_dataset(Path(a))
            build_dataset(Path(b))
            contents = lambda root: {str(p.relative_to(root)):p.read_bytes() for p in Path(root).rglob('*') if p.is_file()}
            self.assertEqual(contents(a), contents(b))
            self.assertEqual(len(manifest['instances']),20)
            schedule = json.loads((Path(a)/'schedule.json').read_text())
            self.assertEqual(len(schedule),120)
            self.assertEqual(len({s['slot_id'] for s in schedule}),120)
            colorings = {3:set(),4:set()}
            for row in manifest['instances']:
                g = json.loads((Path(a)/row['instance_file']).read_text())
                ref = json.loads((Path(a)/row['reference_file']).read_text())
                self.assertTrue(check_path(g,ref['path'])['valid'])
                colorings[g['n']].add(json.dumps(g['edges']))
                prompt = (Path(a)/row['prompt_file']).read_text()
                self.assertEqual(make_prompt(g),prompt)
                (Path(a)/row['reference_file']).unlink()
                self.assertEqual(make_prompt(g),prompt)
                self.assertEqual(hashlib.sha256(prompt.encode()).hexdigest(),row['prompt_sha256'])
            self.assertEqual([len(colorings[n]) for n in (3,4)],[10,10])

    def test_duplicate_candidates_recorded(self):
        original = make_instance
        def repeat_second(n,candidate,seed):
            return original(n, 0 if candidate == 1 else candidate, seed)
        with tempfile.TemporaryDirectory() as d, patch('hypercube.generation.make_instance',side_effect=repeat_second):
            m = build_dataset(Path(d))
            self.assertEqual(len(m['instances']),20)
            self.assertGreaterEqual(len(m['exclusions']),2)
            self.assertEqual({r['n'] for r in m['exclusions'] if r['candidate']==1}, {3,4})
            self.assertTrue(all(r['reason']=='duplicate coloring' for r in m['exclusions']))

    def test_no_path_stops_instead_of_resampling(self):
        with tempfile.TemporaryDirectory() as d, patch('hypercube.generation.find_path',return_value=None):
            with self.assertRaisesRegex(ValueError,'no antipodal path'):
                build_dataset(Path(d))
