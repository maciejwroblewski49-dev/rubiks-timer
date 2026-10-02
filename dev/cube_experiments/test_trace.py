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
        self.faces = {f: [f+str(i) for i in range(9)] for f in 'UDFBRL'}
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
        return all(self.faces[f] == [f+str(i) for i in range(9)] for f in 'UDFBRL')

# After Sune: which stickers moved?
ct = CubeTest(cycles_test2)
ct.apply("R U R' U R U2 R'")
wrong = [(f, i, ct.faces[f][i]) for f in 'UDFBRL' for i in range(9) if ct.faces[f][i] != f+str(i)]
print(f"After Sune: {len(wrong)} wrong stickers:")
for item in wrong:
    print(f"  {item[0]}[{item[1]}] = {item[2]}")

# For Sune to be correct, only 3 corners should be twisted (9 sticker positions).
# Corners: FUL: F[0],U[6],L[2] | FUR: F[2],U[8],R[0] | BUR: B[2],U[2],R[2] | BUL: B[0],U[0],L[0]
print()
print("U face stickers:", ct.faces['U'])
print("F face stickers:", ct.faces['F'])
print("R face stickers:", ct.faces['R'])
print("B face stickers:", ct.faces['B'])
print("L face stickers:", ct.faces['L'])

# Let me trace R U step by step:
print()
print("=== TRACING STEP BY STEP ===")
ct2 = CubeTest(cycles_test2)
ct2.apply("R")
print("After R:")
print("  U:", ct2.faces['U'])
print("  F:", ct2.faces['F'])
print("  B:", ct2.faces['B'])
print("  D:", ct2.faces['D'])

print()
print("Expected after R CW:")
print("  F[2,5,8] -> U[2,5,8]: U2=F2, U5=F5, U8=F8")
print("  U[2,5,8] -> B[8,5,2]: B8=U2, B5=U5, B2=U8")
print("  B[8,5,2] -> D[8,5,2]: D8=B8, D5=B5, D2=B2")
print("  D[8,5,2] -> F[2,5,8]: F2=D8, F5=D5, F8=D2")
print()
print("Actual U[2,5,8]:", ct2.faces['U'][2], ct2.faces['U'][5], ct2.faces['U'][8])
print("Expected: F2, F5, F8")
print("Actual B[8,5,2]:", ct2.faces['B'][8], ct2.faces['B'][5], ct2.faces['B'][2])
print("Expected: U2(original)=U2, U5, U8")
print("Actual D[8,5,2]:", ct2.faces['D'][8], ct2.faces['D'][5], ct2.faces['D'][2])
print("Expected: B8(original)=B8, B5, B2")
print("Actual F[2,5,8]:", ct2.faces['F'][2], ct2.faces['F'][5], ct2.faces['F'][8])
print("Expected: D8(original)=D8, D5, D2")
