import copy
import unittest
from hypercube.scoring import score_response, summarize
from tests.fixtures import fixture

G = fixture()
RAW = '{"path":["00","01","11"]}'
SCHEDULE = [{'slot_id':'model_a/q2-01/1','model':'model_a','instance_id':'q2-01','n':2,'trial':1,'prompt_sha256':'a'*64},
            {'slot_id':'model_a/q2-01/2','model':'model_a','instance_id':'q2-01','n':2,'trial':2,'prompt_sha256':'a'*64}]


def attempt(identifier='a1', status='received', replaces=None):
    return {'attempt_id':identifier, 'slot_id':SCHEDULE[0]['slot_id'], 'status':status,
            'raw':RAW if status=='received' else None,
            'error':None if status=='received' else 'connection interrupted',
            'provider':'test-provider','model_id':'test-model-001',
            'timestamp_utc':'2026-10-15T20:00:00Z','requested_settings':{},'returned_settings':None,
            'prompt_sha256':'a'*64,'tool_policy':'none','fresh_context':True,
            'replaces_attempt_id':replaces}


class ScoringTests(unittest.TestCase):
    def test_deeply_nested_response_is_invalid_not_an_analysis_crash(self):
        raw = '[' * 20000 + ']' * 20000
        self.assertFalse(score_response(G, raw)['valid_path'])
        self.assertFalse(score_response(G, '```json\n' + raw + '\n```')['valid_path'])

    def test_format_and_mathematics_are_distinct(self):
        self.assertEqual([score_response(G,RAW)[k] for k in ['json_only','schema_compliant','valid_path']], [True]*3)
        fenced = score_response(G,'```json\n'+RAW+'\n```')
        self.assertEqual([fenced[k] for k in ['json_only','schema_compliant','valid_path']], [False,True,True])
        extra = score_response(G,'{"path":["00","01","11"],"explanation":"x"}')
        self.assertEqual([extra[k] for k in ['json_only','schema_compliant','valid_path']], [True,False,True])
        for raw in ['prefix '+RAW, 'No solution', '', '{"path":[],"path":["00","01","11"]}',
                    '{"path":NaN}', '{"path":[true]}','[]','{"path":["00","11"]}']:
            with self.subTest(raw=raw):
                self.assertFalse(score_response(G,raw)['valid_path'])

    def test_empty_and_received_empty_denominators(self):
        row = summarize(SCHEDULE,[],{'q2-01':G})['groups'][0]
        self.assertEqual([row[k] for k in ['planned','received','never_attempted','transport_failed','correct']], [2,0,2,0,0])
        self.assertIsNone(row['valid_path_rate_observed'])
        a = attempt(); a['raw']=''
        row = summarize(SCHEDULE,[a],{'q2-01':G})['groups'][0]
        self.assertEqual([row[k] for k in ['received','never_attempted','correct']], [1,1,0])
        self.assertEqual(row['valid_path_rate_observed'],0)

    def test_transport_and_linked_replacement(self):
        error = attempt('a1','transport_error')
        row = summarize(SCHEDULE,[error],{'q2-01':G})['groups'][0]
        self.assertEqual([row[k] for k in ['never_attempted','transport_failed','transport_error_events']], [1,1,1])
        result = summarize(SCHEDULE,[error,attempt('a2',replaces='a1')],{'q2-01':G})
        row = result['groups'][0]
        self.assertEqual([row[k] for k in ['received','correct','transport_failed','transport_error_events']], [1,1,0,1])
        self.assertEqual(row['valid_path_rate_observed'],1)
        self.assertEqual(len(result['attempts']),2)

    def test_corrupt_attempts_rejected(self):
        a = attempt()
        for field, value in [('prompt_sha256','wrong'),('slot_id','missing'),('timestamp_utc','not time'),
                             ('fresh_context',False),('model_id',''),('requested_settings',[]),('tool_policy','browsing')]:
            b = copy.deepcopy(a); b[field]=value
            with self.subTest(field=field):
                with self.assertRaises(ValueError): summarize(SCHEDULE,[b],{'q2-01':G})
        for records in [[a,a], [a,attempt('a2')], [a,attempt('a2',replaces='a1')],
                        [attempt('a1','transport_error'),attempt('a2',replaces='a1'),attempt('a3',replaces='a1')]]:
            with self.assertRaises(ValueError): summarize(SCHEDULE,records,{'q2-01':G})
