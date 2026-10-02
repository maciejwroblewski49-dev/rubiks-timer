"""Test alternative algorithms that should have known orders."""
_SOLVED = {'U':'W','D':'Y','F':'G','B':'B','R':'R','L':'O'}
_FIXED = {
    'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',[2,1,0]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[2,1,0]),('L',[8,5,2])]),
    'B': ('B', [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[8,5,2]),('D',[2,5,8])]),
    'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',[8,5,2]),('U',[0,3,6])]),
}

class CubeTest:
    def __init__(self, cycles):
        self.cycles = cycles
        self.faces = {f: [_SOLVED[f]] * 9 for f in 'UDFBRL'}
    def _rotate_cw(self, f):
        c = self.faces[f][:]
        self.faces[f] = [c[6],c[3],c[0], c[7],c[4],c[1], c[8],c[5],c[2]]
    def _apply_cw(self, base):
        if base not in self.cycles: return
        face, cycle = self.cycles[base]
        self._rotate_cw(face)
        n = len(cycle)
        saved = [[self.faces[fn][i] for i in idx] for fn, idx in cycle]
        for k in range(n):
            fn, idx = cycle[k]
            src = saved[(k - 1) % n]
            for j, i in enumerate(idx):
                self.faces[fn][i] = src[j]
    def apply(self, move_str):
        for tok in move_str.split():
            if not tok: continue
            if tok.endswith("'"):
                for _ in range(3): self._apply_cw(tok[:-1])
            elif tok.endswith('2'):
                for _ in range(2): self._apply_cw(tok[:-1])
            else:
                self._apply_cw(tok)
    def is_solved(self):
        return all(self.faces[f] == [_SOLVED[f]]*9 for f in 'UDFBRL')

def find_order(cycles, alg, max_n=100):
    ct = CubeTest(cycles)
    for i in range(1, max_n+1):
        ct.apply(alg)
        if ct.is_solved():
            return i
    return None

# Test basic moves and combinations
tests = [
    # Single moves (order 4)
    ("U", "U", 4),
    ("D", "D", 4),
    ("F", "F", 4),
    ("B", "B", 4),
    ("R", "R", 4),
    ("L", "L", 4),
    # Opposite face commutators (order 2 or some small number)
    ("U D U' D'", "U D U' D'", 1),  # U and D commute, so this = identity
    ("R L R' L'", "R L R' L'", 1),  # R and L commute
    ("F B F' B'", "F B F' B'", 1),  # F and B commute
    # Sexy move (order 6)
    ("R U R' U'", "R U R' U'", 6),
    # Corner 3-cycle (order 3)
    ("R U R' D' R U' R' D", "R U R' D' R U' R' D", 3),
    # Simple 2-cycle? Like A-perm: R' F R' B2 R F' R' B2 R2
    ("A-perm", "R' F R' B2 R F' R' B2 R2", 3),
    # U-perm a: R U' R U R U R U' R' U' R2
    ("U-perm a", "R U' R U R U R U' R' U' R2", 2),  # Actually it might be order 2
]

for name, alg, expected_order in tests:
    order = find_order(_FIXED, alg)
    ok = order == expected_order
    print(f"  {name}: {order} (exp {expected_order}) {'OK' if ok else 'FAIL'}")
