"""Trace Sune = R U R' U R U2 R' step by step using labeled stickers."""
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
    def wrong(self):
        return [(f, i, self.faces[f][i]) for f in 'UDFBRL' for i in range(9) if self.faces[f][i] != f+str(i)]

ct = CubeTest(_FIXED)

# Key positions to track: corner pieces FUL, FUR, BUR, BUL and their sticker cycles.
# FUL corner stickers: F[0]=FUL-F, U[6]=FUL-U, L[2]=FUL-L
# FUR corner stickers: F[2]=FUR-F, U[8]=FUR-U, R[0]=FUR-R
# BUR corner stickers: B[2]=BUR-B, U[2]=BUR-U, R[2]=BUR-R
# BUL corner stickers: B[0]=BUL-B, U[0]=BUL-U, L[0]=BUL-L

def show_corner(faces, corner, stickers):
    vals = {s: faces[s[0]][int(s[1:])] for s in stickers}
    return f"{corner}: " + ", ".join(f"{s}={v}" for s, v in vals.items())

def check_corners(faces, label):
    print(f"  After {label}:")
    print("   ", show_corner(faces, "FUL", ["F0", "U6", "L2"]))
    print("   ", show_corner(faces, "FUR", ["F2", "U8", "R0"]))
    print("   ", show_corner(faces, "BUR", ["B2", "U2", "R2"]))
    print("   ", show_corner(faces, "BUL", ["B0", "U0", "L0"]))

check_corners(ct.faces, "start")

for move in ["R", "U", "R'", "U", "R", "U", "U", "R'"]:
    ct.apply(move)
    check_corners(ct.faces, move)

print()
print(f"After Sune: {len(ct.wrong())} stickers wrong")
wrong = ct.wrong()
for f, i, v in wrong[:12]:
    print(f"  {f}[{i}]={v}")
