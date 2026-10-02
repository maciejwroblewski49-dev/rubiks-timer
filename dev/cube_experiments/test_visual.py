# Let me examine the actual visual display for a known scramble and check if it matches
# what the scramble SHOULD look like.
# Apply U move and see what the net looks like.
# After U CW: top row of each side face rotates.
# F top gets L top (Orange), R top gets F top (Green), B top gets R top (Red), L top gets B top (Blue).

_SOLVED = {'U':'W','D':'Y','F':'G','B':'B','R':'R','L':'O'}
_MOVE_CYCLES_ORIG = {
    'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',[0,1,2]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[2,1,0]),('L',[8,5,2])]),
    'B': ('B', [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[6,3,0]),('D',[2,5,8])]),
    'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',[8,5,2]),('U',[0,3,6])]),
}

class CubeState:
    _SOLVED = {'U':'W','D':'Y','F':'G','B':'B','R':'R','L':'O'}
    def __init__(self):
        self.faces = {f: [self._SOLVED[f]] * 9 for f in 'UDFBRL'}
    def _rotate_cw(self, f):
        c = self.faces[f][:]
        self.faces[f] = [c[6],c[3],c[0], c[7],c[4],c[1], c[8],c[5],c[2]]
    def _apply_cw(self, base):
        if base not in _MOVE_CYCLES_ORIG: return
        face, cycle = _MOVE_CYCLES_ORIG[base]
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
    def print_net(self):
        def row(face, r):
            abbrev = {'W':'W','Y':'Y','G':'G','B':'B','R':'R','O':'O'}
            return ''.join(abbrev.get(self.faces[face][r*3+c], '?') for c in range(3))
        print("   [U]")
        for r in range(3):
            print("   " + row('U', r))
        print("[L][F][R][B]")
        for r in range(3):
            print(row('L', r) + row('F', r) + row('R', r) + row('B', r))
        print("   [D]")
        for r in range(3):
            print("   " + row('D', r))

cs = CubeState()
cs.apply("U")
print("=== After U CW ===")
cs.print_net()
print()
print("Expected:")
print("   WWW  (U face, all white)")
print("   WWW")
print("   WWW")
print("BBB OOO GGG RRR  (L top=Blue, F top=Orange, R top=Green, B top=Red)")
print("OOO GGG RRR BBB  (middle rows unchanged)")
print("OOO GGG RRR BBB")
print("   YYY  (D unchanged)")
print()

# The net shows B top row. B's top row is B[0,1,2].
# After U CW: B[0,1,2] = Red (from R's original top row R[0,1,2]).
# When drawn in net, B[0,1,2] are the TOP ROW of the B area.
# If B is correct: B[0,1,2] = R,R,R (Red). Displayed at TOP-LEFT of B area.
# Expected in net: B top row = Red. Is Red correct at top of B in the net?
# In the net, B is to the right of R. When you fold B back into position:
# B's top in the net (B[0,1,2]) is the edge that connects to U's top (U[0,1,2]).
# After U CW: U[0,1,2] is still White (U face rotated but all white).
# The adjacent edge in 3D: U's back row (U[0,1,2]) and B's top row (B[0,1,2]).
# After U CW: B[0,1,2]=Red. These are the pieces of the top-back row. They moved from R.
# The net correctly shows B top = Red. ✓
# CONCLUSION: For U moves, the B display seems visually correct.
print()
print("=== After R CW ===")
cs2 = CubeState()
cs2.apply("R")
cs2.print_net()
print()
print("Expected after R CW:")
print("U right col gets F right col = Green")
print("B affected col gets U right col = White (reversed)")
print("D right col gets B affected col = Blue")
print("F right col gets D right col = Yellow")
print()
print("Key check: B's left column in net = ??? ")
print("Code R cycle puts B[6]=U2, B[3]=U5, B[0]=U8 (from labeled test)")
print("This means B's LEFT COLUMN (B[0,3,6]) has: B[0]=White(U8), B[3]=White(U5), B[6]=White(U2)")
print("Visually: B shows White on its left column in the net.")
print("But physically: after R CW, R's right edge (=B's RIGHT edge from behind) should get White.")
print("B's RIGHT column from behind = B[2,5,8]. Those should be White.")
print("B's LEFT column from behind = B[0,3,6]. Those should remain Blue.")
print()
print("Code shows B[0,3,6]=White in the net (WRONG). Should show B[2,5,8]=White.")
print("In the net: B[0,3,6] is B's LEFT column as drawn = adjacent to R's right in the net.")
print("But physically: the stickers adjacent to R in the net should be B's RIGHT column from behind.")
print("So the display IS wrong for R moves affecting B face stickers.")
print()
print("Actual net after R:")
for r in range(3):
    l_row = ''.join(cs2.faces['L'][r*3+c][0] for c in range(3))
    f_row = ''.join(cs2.faces['F'][r*3+c][0] for c in range(3))
    r_row = ''.join(cs2.faces['R'][r*3+c][0] for c in range(3))
    b_row = ''.join(cs2.faces['B'][r*3+c][0] for c in range(3))
    print(l_row + f_row + r_row + b_row)
print()
print("B face stickers after R:")
print("B[0]=", cs2.faces['B'][0], "B[1]=", cs2.faces['B'][1], "B[2]=", cs2.faces['B'][2])
print("B[3]=", cs2.faces['B'][3], "B[4]=", cs2.faces['B'][4], "B[5]=", cs2.faces['B'][5])
print("B[6]=", cs2.faces['B'][6], "B[7]=", cs2.faces['B'][7], "B[8]=", cs2.faces['B'][8])
print("(B[0,3,6] = left col from behind = should be Blue. B[2,5,8] = right col = should be White)")
