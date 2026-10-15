"""Independent hand-defined fixtures; never import the production generator."""
import itertools


def fixture(n=2, zero_path=None):
    if zero_path is None and n == 2:
        zero_path = ['00', '01', '11']
    vertices = [''.join(v) for v in itertools.product('01', repeat=n)]
    complement = lambda v: ''.join('1' if b == '0' else '0' for b in v)
    chosen = {tuple(sorted(e)) for e in zip(zero_path or [], (zero_path or [])[1:])}
    edges = []
    for u, v in itertools.combinations(vertices, 2):
        if sum(a != b for a, b in zip(u, v)) != 1:
            continue
        e = (u, v)
        opposite = tuple(sorted((complement(u), complement(v))))
        if e in chosen:
            color = 0
        elif opposite in chosen:
            color = 1
        else:
            color = int(e > opposite)
        edges.append([u, v, color])
    return {'id': f'fixture-q{n}', 'n': n, 'edges': edges}
