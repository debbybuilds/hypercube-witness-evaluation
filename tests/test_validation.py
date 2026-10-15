import copy
import unittest
from hypercube.validation import validate_instance, check_path
from tests.fixtures import fixture


class ValidationTests(unittest.TestCase):
    def test_complete_topology_and_valid_path(self):
        for n, count in [(2, 4), (3, 12), (4, 32)]:
            g = fixture(n)
            self.assertEqual(len(g['edges']), count)
            validate_instance(g)
        self.assertTrue(check_path(fixture(), ['00','01','11'])['valid'])

    def test_invalid_paths(self):
        cases = [(['01','00','10'], 'monochromatic'),
                 (['00','11'], 'adjacent'),
                 (['00','01'], 'antipodal'),
                 (['00','01','00','10','11'], 'repeated'),
                 (['00', True, '11'], 'vertex'),
                 (['00','1','11'], 'vertex'),
                 (['00','02','11'], 'vertex'),
                 ([], 'two'), (None, 'list')]
        for path, reason in cases:
            with self.subTest(path=path):
                result = check_path(fixture(), path)
                self.assertFalse(result['valid'])
                self.assertIn(reason, result['reason'])

    def test_non_geodesic_simple_path_accepted(self):
        path = ['0000','0001','0011','0010','0110','0111','1111']
        self.assertTrue(check_path(fixture(4, path), path)['valid'])

    def test_invalid_instances(self):
        base = fixture()
        cases = []
        g = copy.deepcopy(base); g['edges'].pop(); cases.append(g)
        g = copy.deepcopy(base); g['edges'].append(g['edges'][0]); cases.append(g)
        g = copy.deepcopy(base); g['edges'].append(list(reversed(g['edges'][0][:2])) + [0]); cases.append(g)
        g = copy.deepcopy(base); g['edges'][0] = ['00','00',0]; cases.append(g)
        for field, value in [('n', True), ('n', 0), ('n', 5), ('edges', None)]:
            g = copy.deepcopy(base); g[field] = value; cases.append(g)
        for color in [True, 2, -1, '0']:
            g = copy.deepcopy(base); g['edges'][0][2] = color; cases.append(g)
        g = copy.deepcopy(base); g['edges'][0][2] ^= 1; cases.append(g)
        for g in cases:
            with self.subTest(g=g):
                with self.assertRaises(ValueError):
                    validate_instance(g)
