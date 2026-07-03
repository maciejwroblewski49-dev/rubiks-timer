_SOLVED = {'U':'W','D':'Y','F':'G','B':'B','R':'R','L':'O'}

cycles_test2 = {
    'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',[2,1,0]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[8,7,6]),('L',[8,5,2])]),
    'B': ('B', [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[8,5,2]),('D',[8,5,2])]),
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

# Let me look up the true orders of these algorithms:
# T-perm: The T-perm is a 2-cycle of edges + 2-cycle of corners. Order should be 2.
# If our T-perm gives 24 or 12, something is wrong.
# Sune: R U R' U R U2 R' - this is an OLL algorithm (orientation of last layer).
# Sune affects 3 corners. Its order depends on what it does to the full cube:
# On a full cube (not just last layer), Sune has a specific permutation+orientation pattern.
# Let me look at what algorithms give order 6 (=2*3) to narrow down.
#
# Actually - what if the R cycle is correct but the U cycle is CW/CCW swapped?
# Let me test the ANTI-Sune: R U2 R' U' R U' R' (which should also have some order).

print("Orders with corrected U(B=2,1,0) + F(D=8,7,6) + R(B=8,5,2,D=8,5,2):")
algorithms = [
    ("Sune", "R U R' U R U2 R'"),
    ("Anti-Sune", "R U2 R' U' R U' R'"),
    ("R U R' U' x1", "R U R' U'"),
    ("R U", "R U"),
    ("T-perm", "R U R' U' R' F R2 U' R' U' R U R' F'"),
    ("Y-perm", "F R U' R' U' R U R' F' R U R' U' R' F R F'"),
    ("J-perm", "R U R' F' R U R' U' R' F R2 U' R'"),
    ("U' F' R' F R", "U' F' R' F R"),
    ("F R U R' U' F'", "F R U R' U' F'"),
]
for name, alg in algorithms:
    order = find_order(cycles_test2, alg)
    print(f"  {name} ({alg}): order={order}")
