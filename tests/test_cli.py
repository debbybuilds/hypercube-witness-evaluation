import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def cli(*args):
    return subprocess.run([sys.executable,'-m','hypercube',*map(str,args)],cwd=ROOT,capture_output=True,text=True)


class CliTests(unittest.TestCase):
    def test_collected_settings_must_match_frozen_configuration(self):
        from tests.test_scoring import attempt
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); data = root/'data'
            self.assertEqual(cli('generate', '--output', data).returncode, 0)
            slot = json.loads((data/'schedule.json').read_text())[0]
            a = attempt()
            a.update(slot_id=slot['slot_id'], prompt_sha256=slot['prompt_sha256'],
                     requested_settings={'temperature': 1}, raw='refusal')
            attempts = root/'attempts.jsonl'
            attempts.write_text(json.dumps(a)+'\n')
            config = {slot['model']: {'provider': a['provider'], 'model_id': a['model_id'],
                                    'requested_settings': {'temperature': 0}}}
            other = 'model_b' if slot['model'] == 'model_a' else 'model_a'
            config[other] = {'provider': 'other-test-provider', 'model_id': 'other-test-model',
                             'requested_settings': None}
            models = root/'models.json'; models.write_text(json.dumps(config))
            run = cli('score','--dataset',data,'--attempts',attempts,'--models',models,
                      '--output',root/'out.json')
            self.assertNotEqual(run.returncode, 0)
            self.assertIn('settings', run.stderr)
            config[slot['model']]['requested_settings'] = {'temperature': 1}
            models.write_text(json.dumps(config))
            run = cli('score','--dataset',data,'--attempts',attempts,'--models',models,
                      '--output',root/'out.json')
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(sum(g['received'] for g in json.loads((root/'out.json').read_text())['groups']), 1)
            del config[other]
            models.write_text(json.dumps(config))
            run = cli('score','--dataset',data,'--attempts',attempts,'--models',models,
                      '--output',root/'out.json')
            self.assertNotEqual(run.returncode, 0)
            self.assertIn('both model slots', run.stderr)

    def test_generate_verify_empty_scoring_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); data = root/'data'
            run = cli('generate','--output',data)
            self.assertEqual(run.returncode,0,run.stderr)
            run = cli('verify','--dataset',data)
            self.assertEqual(run.returncode,0,run.stderr)
            summary = json.loads(run.stdout)
            self.assertEqual([summary[k] for k in ['instances','prompts','reference_paths','planned_responses']], [20,20,20,120])
            attempts = root/'attempts.jsonl'; attempts.write_text('')
            output = root/'summary.json'
            run = cli('score','--dataset',data,'--attempts',attempts,'--output',output)
            self.assertEqual(run.returncode,0,run.stderr)
            report = json.loads(output.read_text())
            self.assertEqual(sum(g['planned'] for g in report['groups']),120)
            self.assertEqual(sum(g['received'] for g in report['groups']),0)
            self.assertTrue(all(g['valid_path_rate_observed'] is None for g in report['groups']))
            target = data/'prompts/q3-01.txt'; target.write_text(target.read_text()+'hint')
            run = cli('verify','--dataset',data)
            self.assertNotEqual(run.returncode,0)
            self.assertIn('hash',run.stderr)

    def test_missing_files_and_bad_json_give_readable_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            self.assertNotEqual(cli('verify','--dataset',p).returncode,0)
            (p/'manifest.json').write_text('not JSON')
            run = cli('verify','--dataset',p)
            self.assertNotEqual(run.returncode,0)
            self.assertNotIn('Traceback',run.stderr)
