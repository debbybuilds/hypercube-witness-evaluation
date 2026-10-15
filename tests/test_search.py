import unittest
from hypercube.search import find_path
from hypercube.validation import check_path
from tests.fixtures import fixture


def exhaustive_exists(g):
    """Independent depth-first simple-path enumeration on tiny fixtures."""
    vertices = sorted({u for u,v,c in g['edges']} | {v for u,v,c in g['edges']})
    for start in vertices:
        target = ''.join(str(1-int(b)) for b in start)
        for color in (0,1):
            def explore(path):
                if path[-1] == target:
                    return True
                for u,v,c in g['edges']:
                    if c != color:
                        continue
                    w = v if u == path[-1] else u if v == path[-1] else None
                    if w is not None and w not in path and explore(path+[w]):
                        return True
                return False
            if explore([start]):
                return True
    return False


class SearchTests(unittest.TestCase):
    def test_bfs_agrees_with_exhaustive_small_fixtures(self):
        for g in [fixture(2),fixture(3),fixture(3,['000','001','011','111'])]:
            path = find_path(g)
            self.assertEqual(path is not None,exhaustive_exists(g))
            self.assertTrue(check_path(g,path)['valid'])
