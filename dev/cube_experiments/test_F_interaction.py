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

# Test F alone
ct = CubeTest(_FIXED)
ct.apply("F")
print("After F: wrong stickers:", len(ct.wrong()))
ct2 = CubeTest(_FIXED)
ct2.apply("F F'")
print("F F': solved =", ct2.is_solved())

# Test: R' F R (a conjugation of F by R)
ct3 = CubeTest(_FIXED)
ct3.apply("R' F R")
wrong3 = ct3.wrong()
print(f"After R' F R: {len(wrong3)} wrong stickers")
print("Expected: A rotation of F by R' should affect different faces")
# R' F R is like applying F in R's coordinate frame

# Test that F x4 = solved
ct4 = CubeTest(_FIXED)
for _ in range(4): ct4.apply("F")
print("F x4: solved =", ct4.is_solved())

# Test F directly - trace which stickers move
ct5 = CubeTest(_FIXED)
ct5.faces = {f: [f+str(i) for i in range(9)] for f in 'UDFBRL'}
ct5.apply("F")
wrong5 = [(f, i, ct5.faces[f][i]) for f in 'UDFBRL' for i in range(9) if ct5.faces[f][i] != f+str(i)]
print(f"\nAfter F (labeled): {len(wrong5)} moved:")
for f, i, v in wrong5:
    print(f"  {f}[{i}] = {v}")
print("\nExpected after F CW:")
print("  U[6,7,8] = L[8,5,2] (L right col reversed)")
print("  R[0,3,6] = U[6,7,8] (U bottom)")
print("  D[2,1,0] = R[0,3,6] (R left col)")
print("  L[8,5,2] = D[2,1,0] (D top reversed)")
