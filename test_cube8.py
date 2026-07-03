# Let me test with the ORIGINAL cycles and just check if R U R' U' x6 works
# If original cycles give R U R' U' x6 = solved but T-perm order > 2, maybe the issue
# is specifically in the D or B cycles (not U).

_MOVE_CYCLES_ORIG = {
    'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',[0,1,2]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[2,1,0]),('L',[8,5,2])]),
    'B': ('B', [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[6,3,0]),('D',[2,5,8])]),
    'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',[8,5,2]),('U',[0,3,6])]),
}

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

def find_order(cycles, alg, max_n=50):
    ct = CubeTest(cycles)
    for i in range(1, max_n+1):
        ct.apply(alg)
        if ct.is_solved():
            return i
    return None

print("=== ORIGINAL cycles ===")
print("R U R' U' x6:", find_order(_MOVE_CYCLES_ORIG, "R U R' U'"), "(expected 6)")
print("T-perm x2:", find_order(_MOVE_CYCLES_ORIG, "R U R' U' R' F R2 U' R' U' R U R' F'"), "(expected 2)")
print("Sune x8:", find_order(_MOVE_CYCLES_ORIG, "R U R' U R U2 R'"), "(expected 8)")
print("F-perm x2:", find_order(_MOVE_CYCLES_ORIG, "R' U' F' R U R' U' R' F R2 U' R' U' R U R' U R"), "(expected 2)")
print()

# The fact that R U R' U' x6 works with original means U and R cycles are consistent.
# The T-perm failure with order 24 suggests D or B is wrong.
# T-perm doesn't use D or B directly! T-perm = R U R' U' R' F R2 U' R' U' R U R' F'
# Moves used: R, U, F. No D or B!
# So the bug is in R, U, or F cycles!

# But R U R' U' x6 = solved means R and U are internally consistent.
# F cycle must be the issue!

# Let's test F alone:
print("Testing F cycle:")
print("F x4:", find_order(_MOVE_CYCLES_ORIG, "F"), "(expected 4)")
print("U F U' F' order:", find_order(_MOVE_CYCLES_ORIG, "U F U' F'"), "(expected... depends)")
print("F U F' U' x?:", find_order(_MOVE_CYCLES_ORIG, "F U F' U'"))

# If U and F are both wrong in a consistent way that makes U*4=ok and F*4=ok but U F U' F' != solved,
# then the issue is in how U and F interact.

# What does T-perm do? It's an OLL/PLL that permutes pieces in the top layer.
# It uses U, R, F moves. Let me trace what it does step by step.
ct = CubeTest(_MOVE_CYCLES_ORIG)
alg = "R U R' U' R' F R2 U' R' U' R U R' F'"
ct.apply(alg)
print("\nAfter T-perm:")
for f in 'UDFBRL':
    print(f"  {f}: {ct.faces[f]}")

# Count how many stickers are in the wrong place
from collections import Counter
all_pos = []
for f in 'UDFBRL':
    for i, col in enumerate(ct.faces[f]):
        if col != _SOLVED[f]:
            all_pos.append((f, i, col))
print(f"\n{len(all_pos)} stickers in wrong position:")
for f, i, col in all_pos[:10]:
    print(f"  {f}[{i}] = {col} (expected {_SOLVED[f]})")
