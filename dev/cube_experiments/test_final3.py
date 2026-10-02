_SOLVED = {'U':'W','D':'Y','F':'G','B':'B','R':'R','L':'O'}

# FIXED cycles: only change U.B[2,1,0] and R.B[8,5,2]
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

print("FIXED cycles (U.B=[2,1,0], R.B=[8,5,2]):")
tests = [
    ("R U R' U' x6", "R U R' U'", 6),
    ("T-perm x2", "R U R' U' R' F R2 U' R' U' R U R' F'", 2),
    ("Sune x8", "R U R' U R U2 R'", 8),
    ("F-perm x2", "R' U' F' R U R' U' R' F R2 U' R' U' R U R' U R", 2),
]
for name, alg, exp in tests:
    order = find_order(_FIXED, alg)
    print(f"  {name}: {order} (exp {exp}) {'OK' if order==exp else 'FAIL'}")

for m in ['U','D','F','B','R','L']:
    ct = CubeTest(_FIXED)
    for _ in range(4): ct.apply(m)
    print(f"  {m}x4: {'OK' if ct.is_solved() else 'FAIL'}")
    ct2 = CubeTest(_FIXED)
    ct2.apply(m + " " + m + "'")
    print(f"  {m} {m}': {'OK' if ct2.is_solved() else 'FAIL'}")
