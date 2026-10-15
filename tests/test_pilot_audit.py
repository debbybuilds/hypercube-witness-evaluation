import json
from pathlib import Path
import shutil
import tempfile
import unittest
from hypercube.pilot_audit import audit_pilot, write_audit

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT/'responses/cohorts/gpt-6-1-sol-light/pilot-20'


class PilotAuditTests(unittest.TestCase):
    def test_complete_pilot_resolves_correction_and_retained_records(self):
        report = audit_pilot(ROOT/'data',PILOT)
        self.assertEqual((report['planned'],report['received'],report['missing']),(20,20,0))
        self.assertEqual([(g['received'],g['displayed_paths_valid'],g['json_only_passed'],g['formal_path_passed']) for g in report['groups']],[(10,10,10,10),(10,10,6,6)])
        corrected=next(r for r in report['rows'] if r['slot_id']=='model_b/q3-04/1')
        self.assertFalse(corrected['json_only'])
        self.assertIn('correction-1',corrected['record_file'])
        retained=next(r for r in report['rows'] if r['slot_id']=='model_a/q3-03/1')
        self.assertEqual(retained['original_slot_id'],'model_a/q3-03/2')
        self.assertEqual(len({r['slot_id'] for r in report['rows']}),20)

    def test_output_is_byte_identical_and_check_detects_tampering(self):
        report = audit_pilot(ROOT/'data',PILOT)
        with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
            write_audit(report,Path(a));write_audit(report,Path(b))
            for f in ('audit.json','audit.csv'):
                self.assertEqual((Path(a)/f).read_bytes(),(Path(b)/f).read_bytes())
            write_audit(report,Path(a),check=True)
            (Path(a)/'audit.csv').write_text('corrupted')
            with self.assertRaisesRegex(ValueError,'differs'):write_audit(report,Path(a),check=True)

    def test_changed_retained_record_and_extra_record_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            cohort=Path(d)/'cohort';shutil.copytree(PILOT.parent,cohort)
            p=cohort/'intake/model_a-q3-03-trial-2.json'
            p.write_text(p.read_text()+' ')
            with self.assertRaisesRegex(ValueError,'hash'):audit_pilot(ROOT/'data',cohort/'pilot-20')
        with tempfile.TemporaryDirectory() as d:
            cohort=Path(d)/'cohort';shutil.copytree(PILOT.parent,cohort)
            intake=cohort/'pilot-20/intake'
            shutil.copy(intake/'model_a-q3-02-trial-1.json',intake/'duplicate.json')
            with self.assertRaisesRegex(ValueError,'duplicate'):audit_pilot(ROOT/'data',cohort/'pilot-20')

    def test_diagnostic_displayed_path_must_match_raw_reply(self):
        with tempfile.TemporaryDirectory() as d:
            cohort=Path(d)/'cohort';shutil.copytree(PILOT.parent,cohort)
            p=cohort/'pilot-20/intake/model_b-q3-01-trial-1.json'
            r=json.loads(p.read_text());r['displayed_path']=['100','000','001','011']
            p.write_text(json.dumps(r))
            with self.assertRaisesRegex(ValueError,'displayed path'):audit_pilot(ROOT/'data',cohort/'pilot-20')
