"""
Exhaustive sweep: try combinations of B in U, R, B, L cycles.
For each combination, test key algorithms.
"""
_SOLVED = {'U':'W','D':'Y','F':'G','B':'B','R':'R','L':'O'}

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

def find_order(cycles, alg, max_n=60):
    ct = CubeTest(cycles)
    for i in range(1, max_n+1):
        ct.apply(alg)
        if ct.is_solved():
            return i
    return None

def test_quick(cycles):
    """Quick test: return True if all basic tests pass."""
    # Commutators
    for alg in ["R L R' L'", "U D U' D'", "F B F' B'"]:
        if find_order(cycles, alg, 5) != 1:
            return False, f"Commutator fail: {alg}"
    if find_order(cycles, "R U R' U'", 10) != 6:
        return False, "Sexy order not 6"
    tperm = find_order(cycles, "R U R' U' R' F R2 U' R' U' R U R' F'", 30)
    sune = find_order(cycles, "R U R' U R U2 R'", 20)
    return True, f"T-perm={tperm}, Sune={sune}"

# The key insight: the B face has a different convention.
# Let's try B[0,1,2] vs B[2,1,0] for EACH of U,R,L moves (2^3=8 combinations)
# And B[0,1,2] vs B[2,1,0] for D (B row direction)
# And B cycle list order variation (U,R,D,L vs D,R,U,L etc.)

b_options_row = [[0,1,2], [2,1,0]]
b_options_col_r = [[8,5,2], [6,3,0], [2,5,8], [0,3,6]]  # for R and L cycles (column)
b_options_col_d = [[8,7,6], [6,7,8]]  # for D cycle (row)

# Also B cycle itself:
# Original: [D[6,7,8], R[8,5,2], U[2,1,0], L[0,3,6]]
# My derived: [U[2,1,0], R[2,5,8], D[8,7,6], L[0,3,6]]
# Try various combinations

b_cycles_to_try = [
    ('D_orig', [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]),
    ('U_fwd', [('U',[0,1,2]),('R',[2,5,8]),('D',[8,7,6]),('L',[0,3,6])]),
    ('U_rev', [('U',[2,1,0]),('R',[2,5,8]),('D',[8,7,6]),('L',[0,3,6])]),
    ('D_new', [('D',[8,7,6]),('R',[2,5,8]),('U',[0,1,2]),('L',[0,3,6])]),
    ('D_new_rev', [('D',[8,7,6]),('R',[2,5,8]),('U',[2,1,0]),('L',[0,3,6])]),
    ('U_fwd_rrev', [('U',[0,1,2]),('R',[8,5,2]),('D',[2,1,0]),('L',[0,3,6])]),
    ('U_rev_rrev', [('U',[2,1,0]),('R',[8,5,2]),('D',[2,1,0]),('L',[0,3,6])]),
    ('U_fwd_lrev', [('U',[0,1,2]),('R',[2,5,8]),('D',[8,7,6]),('L',[6,3,0])]),
    ('U_rev_lrev', [('U',[2,1,0]),('R',[2,5,8]),('D',[8,7,6]),('L',[6,3,0])]),
]

for u_b in [[0,1,2], [2,1,0]]:
    for r_b in [[8,5,2], [6,3,0]]:
        for l_b in [[6,3,0], [8,5,2]]:
            for d_b in [[8,7,6], [6,7,8]]:
                for b_label, b_cycle in b_cycles_to_try:
                    cycles = {
                        'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',u_b),('L',[0,1,2])]),
                        'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',d_b),('R',[6,7,8])]),
                        'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[2,1,0]),('L',[8,5,2])]),
                        'B': ('B', b_cycle),
                        'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',r_b),('D',[2,5,8])]),
                        'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',l_b),('U',[0,3,6])]),
                    }
                    ok, msg = test_quick(cycles)
                    if ok and 'T-perm=2' in msg and 'Sune=8' in msg:
                        print(f"FOUND! U.B={u_b} R.B={r_b} L.B={l_b} D.B={d_b} B={b_label}")
                        print(f"  Msg: {msg}")
                        print(f"  Full cycles:")
                        for k,v in cycles.items():
                            print(f"    {k}: {v}")
                        raise SystemExit(0)
                    elif ok:
                        print(f"Partial: U.B={u_b} R.B={r_b} L.B={l_b} D.B={d_b} B={b_label} -> {msg}")

print("No perfect solution found in sweep")
