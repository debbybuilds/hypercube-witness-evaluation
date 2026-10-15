"""Direct mathematical checks, independent of generation and reference search."""
from itertools import combinations, product


def validate_instance(instance):
    """Raise ValueError for malformed or non-antipodal complete cube colorings."""
    if type(instance) is not dict:
        raise ValueError('instance must be an object')
    n = instance.get('n')
    if type(n) is not int or not 2 <= n <= 4:
        raise ValueError('n must be an integer from 2 through 4 for this pilot')
    vertices = {''.join(v) for v in product('01', repeat=n)}
    expected = {tuple(sorted((u, v))) for u, v in combinations(vertices, 2)
                if sum(a != b for a, b in zip(u, v)) == 1}
    if type(instance.get('edges')) is not list:
        raise ValueError('edges must be a list')
    colors = {}
    for edge in instance['edges']:
        if type(edge) is not list or len(edge) != 3:
            raise ValueError('edge must be [u, v, color]')
        u, v, c = edge
        if type(u) is not str or type(v) is not str or u not in vertices or v not in vertices:
            raise ValueError('invalid edge vertex')
        key = tuple(sorted((u, v)))
        if key not in expected:
            raise ValueError('edge must join distinct adjacent cube vertices')
        if key in colors:
            raise ValueError('duplicate undirected edge')
        if type(c) is not int or c not in (0, 1):
            raise ValueError('edge color must be integer 0 or 1')
        colors[key] = c
    if set(colors) != expected:
        raise ValueError('edge list does not cover the complete hypercube')
    for (u, v), c in colors.items():
        anti = tuple(sorted(''.join('1' if b == '0' else '0' for b in w) for w in (u, v)))
        if colors[anti] != 1 - c:
            raise ValueError('antipodal edges must have opposite colors')


def check_path(instance, path):
    """Validate a simple monochromatic antipodal path; length need not be n."""
    validate_instance(instance)
    def reject(reason):
        return {'valid': False, 'reason': reason}
    if type(path) is not list:
        return reject('path must be a list')
    if len(path) < 2:
        return reject('path needs at least two vertices')
    n = instance['n']
    if any(type(v) is not str or len(v) != n or set(v) - {'0', '1'} for v in path):
        return reject('invalid vertex: use fixed-width binary strings')
    if len(set(path)) != len(path):
        return reject('repeated vertex: path must be simple')
    colors = {tuple(sorted((u, v))): c for u, v, c in instance['edges']}
    traversed = []
    for u, v in zip(path, path[1:]):
        e = tuple(sorted((u, v)))
        if e not in colors:
            return reject('consecutive vertices must be adjacent')
        traversed.append(colors[e])
    if len(set(traversed)) != 1:
        return reject('path is not monochromatic')
    if any(a == b for a, b in zip(path[0], path[-1])):
        return reject('endpoints are not antipodal')
    return {'valid': True, 'reason': None, 'color': traversed[0], 'length': len(path) - 1}
