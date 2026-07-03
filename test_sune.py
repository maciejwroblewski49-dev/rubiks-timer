_SOLVED = {'U':'W','D':'Y','F':'G','B':'B','R':'R','L':'O'}

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

cycles_ru = {
    'U': ('U', [('F',[0,1,2]),('R',[2,1,0]),('B',[2,1,0]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[2,1,0]),('L',[8,5,2])]),
    'B': ('B', [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[8,5,2]),('D',[8,5,2])]),
    'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',[8,5,2]),('U',[0,3,6])]),
}

ct = CubeTest(cycles_ru)
ct.apply("R U R' U R U2 R'")
print("After Sune (corrected R and U):")
wrong = [(f, i, ct.faces[f][i]) for f in 'UDFBRL' for i in range(9) if ct.faces[f][i] != f+str(i)]
print(f"{len(wrong)} stickers wrong:")
for item in wrong:
    print(f"  {item[0]}[{item[1]}] = {item[2]}")

# The Sune should affect 3 corners of the U face only (orient them in place).
# After Sune: the pieces at FUL, FUR, BUR should be in same positions but with different orientations.
# Specifically Sune is an OLL algorithm that twists 3 corner pieces:
# FUL: F[0]+U[6]+L[2] -> R[0]+F[2]+U[8] etc. (corner piece cycle)
# Actually: Sune is a 2-cycle + twist. Let me check what the CORRECT output should be.
# Sune on solved = the 3 corners at FUL, FUR, BUR get rotated.
# FUL corner stickers: U[6]=UFL, F[0]=FUL, L[2]=LUF.
# After Sune:
# Physical result: FUL stays at FUL but twisted CW (F sticker goes to U position, U to L, L to F).
# FUR stays at FUR but twisted CW.
# BUL stays at BUL but twisted CW.
# Actually I need to look this up... Sune is Anti-Sune in different conventions.
# The correct piece movements depend on orientation conventions.

# Let me check: do the wrong stickers form a valid orientation-only change?
print("\nChecked positions:")
print("U[0]=", ct.faces['U'][0], "(expected U0)")
print("U[2]=", ct.faces['U'][2])
print("U[6]=", ct.faces['U'][6])
print("U[8]=", ct.faces['U'][8])
# Check if wrong stickers are only on U face (corner twists only affect U, F, R stickers)

# What's the sticker distribution wrong?
wrong_faces = {}
for f, i, val in wrong:
    wrong_faces[f] = wrong_faces.get(f, 0) + 1
print("\nWrong stickers per face:", wrong_faces)

# If only U, F, R stickers are wrong, this is consistent with corner twists.
# But if D or B stickers are wrong, there's a deeper bug.
print("\nFull state:")
for f in 'UDFBRL':
    print(f"  {f}: {ct.faces[f]}")
