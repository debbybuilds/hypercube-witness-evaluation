"""Reference search using monochromatic connectivity, not a SAT solver."""
from collections import deque
from .validation import validate_instance, check_path


def find_path(instance):
    validate_instance(instance)
    vertices = sorted({v for e in instance['edges'] for v in e[:2]})
    for color in (0, 1):
        adjacency = {v: [] for v in vertices}
        for u, v, c in instance['edges']:
            if c == color:
                adjacency[u].append(v)
                adjacency[v].append(u)
        for start in vertices:
            target = ''.join('1' if b == '0' else '0' for b in start)
            previous = {start: None}
            queue = deque([start])
            while queue and target not in previous:
                u = queue.popleft()
                for v in sorted(adjacency[u]):
                    if v not in previous:
                        previous[v] = u
                        queue.append(v)
            if target in previous:
                path, vertex = [], target
                while vertex is not None:
                    path.append(vertex)
                    vertex = previous[vertex]
                path.reverse()
                if not check_path(instance, path)['valid']:
                    raise ValueError('reference search returned an invalid certificate')
                return path
    return None
