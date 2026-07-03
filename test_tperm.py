"""
Let me verify T-perm by looking at what PIECES it should move.
T-perm = R U R' U' R' F R2 U' R' U' R U R' F'

The T-perm permutes:
- 2 corners: UFR and UBL (they swap)
- 2 edges: UR and UF (they swap)

After T-perm on a solved cube, only these 4 pieces should be in wrong positions.
Let me check what our simulation gives.
"""
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
    def wrong(self):
        return [(f, i, self.faces[f][i]) for f in 'UDFBRL' for i in range(9) if self.faces[f][i] != _SOLVED[f]]

ct = CubeTest(_FIXED)
ct.apply("R U R' U' R' F R2 U' R' U' R U R' F'")
wrong = ct.wrong()
print(f"After T-perm: {len(wrong)} stickers wrong")
print("Wrong stickers:")
for f, i, v in wrong:
    print(f"  {f}[{i}] = {v} (expected {_SOLVED[f]})")
print()
print("For T-perm: should only affect UFR corner (U[2],F[2],R[0]), UBL corner (U[0],B[0],L[0]),")
print("UR edge (U[5],R[1]), and UF edge (U[7],F[1])")
print("= 8 stickers total, but positions should be swapped between UFR/UBL and UR/UF")
