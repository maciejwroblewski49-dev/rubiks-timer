_MOVE_CYCLES = {
    'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',[0,1,2]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[2,1,0]),('L',[8,5,2])]),
    'B': ('B', [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[6,3,0]),('D',[2,5,8])]),
    'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',[8,5,2]),('U',[0,3,6])]),
}

_SOLVED = {'U':'W','D':'Y','F':'G','B':'B','R':'R','L':'O'}

class CubeState:
    def __init__(self):
        self.faces = {f: [_SOLVED[f]] * 9 for f in 'UDFBRL'}

    def _rotate_cw(self, f):
        c = self.faces[f][:]
        self.faces[f] = [c[6],c[3],c[0], c[7],c[4],c[1], c[8],c[5],c[2]]

    def _apply_cw(self, base):
        if base not in _MOVE_CYCLES: return
        face, cycle = _MOVE_CYCLES[base]
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

# Test R U R' U' cycle (order 6)
cs = CubeState()
for i in range(6):
    cs.apply("R U R' U'")
print("R U R' U' repeated 6 times:", "SOLVED" if cs.is_solved() else "NOT SOLVED")

# Test T-perm (order 2)
cs2 = CubeState()
tperm = "R U R' U' R' F R2 U' R' U' R U R' F'"
cs2.apply(tperm)
cs2.apply(tperm)
print("T-perm twice:", "SOLVED" if cs2.is_solved() else "NOT SOLVED")

# Test F-perm (order 2)
cs3 = CubeState()
fperm = "R' U' F' R U R' U' R' F R2 U' R' U' R U R' U R"
cs3.apply(fperm)
cs3.apply(fperm)
print("F-perm twice:", "SOLVED" if cs3.is_solved() else "NOT SOLVED")

# Test U move: After U CW, check that top rows are correct
cs4 = CubeState()
cs4.apply("U")
print("\nAfter U CW:")
print("  F top row (should be Orange/L):", cs4.faces['F'][0:3])
print("  R top row (should be Green/F):", cs4.faces['R'][0:3])
print("  B top row (should be Red/R):", cs4.faces['B'][0:3])
print("  L top row (should be Blue/B):", cs4.faces['L'][0:3])

# In the net, let's think about what the B top row MEANS visually.
# After U CW: B[0,1,2] = R (Red) -- B's top row is Red
# This is the row of B that is adjacent to U's back row.
# In the NET DRAWING, B's top row (B[0,1,2]) is drawn at the top of the B area.
# B is to the right of R in the net.
# B's top in the net is physically adjacent to U's top in the 3D cube.
# After U CW, U's back row = U[0,1,2] should still be White (U face rotated, all same color).
# B's top row = Red (from R).
# These are different pieces/colors as expected after U CW.

# Now, what about the net adjacency? In the net:
#     U(col3-5, row0-2)
# L(col0-2) F(col3-5) R(col6-8) B(col9-11)   <- row 3-5
#     D(col3-5, row6-8)
#
# F and U share an edge: F top = F[0,1,2] adjacent to U bottom = U[6,7,8]
# R and U share an edge: R top = R[0,1,2] adjacent to U right = U[2,5,8] -- NO! R is not directly below U.
# Actually in this net, only F is directly below U. R, L, B are not directly above/below U.
#
# The edges in this net that should match:
# - F top (F[0,1,2]) adj U bottom (U[6,7,8])
# - F bottom (F[6,7,8]) adj D top (D[0,1,2])
# - F left (F[0,3,6]) adj R right (R[2,5,8])? No: F left adj L right.
#   F left = F[0,3,6], L right = L[2,5,8]
# - F right (F[2,5,8]) adj R left (R[0,3,6])
# - R right (R[2,5,8]) adj B left (B[0,3,6]) -- THIS IS THE KEY ONE
# - L left (L[0,3,6]) adj B right ... wait
# - D adj L, D adj R, D adj B... but in this net these aren't directly adjacent.
#
# The key physical edge: R's right edge meets B's ??? edge.
# In 3D: R is +X face, B is -Z face.
# R's right edge = the edge where +X meets -Z = the right column of R when viewed from +X
# = R[2,5,8] in code (right column).
# B's adjacent edge = the edge where -Z meets +X = the right column of B when viewed from -Z (from behind)
# = B[2,5,8] in code (right column, since B[0]=top-left from behind).
#
# In the net: R's right column (R[2,5,8]) should be adjacent to B's left column (B[0,3,6]) as drawn.
# But physically R[2] and B[2] are on the same edge (same 3D position for adjacent stickers).
# So for the net to be correct: B[2] should appear at the top-left of the B area in the net
# (adjacent to R[2] at the top-right of the R area).
# But draw_net draws B[0] at the top-left of the B area.
#
# CONCLUSION: B needs to be drawn rotated 180 degrees so that B[8] appears at top-left,
# B[2] appears at top-right... wait that's still wrong.
#
# Let me reconsider. If B[0]=top-left from behind:
# For the net, B needs its RIGHT column (from behind) adjacent to R's right edge.
# B's right column (from behind) = B[2,5,8].
# In the net (unfolded to right of R), B's LEFT column in net should equal B's right column from behind.
# That means B needs to be drawn with LEFT-RIGHT mirrored.
# B drawn mirrored: net(row,col) = B_original[row*3 + (2-col)]
# net position (0,0) = B[2], (0,1) = B[1], (0,2) = B[0]
# net position (1,0) = B[5], (1,1) = B[4], (1,2) = B[3]
# net position (2,0) = B[8], (2,1) = B[7], (2,2) = B[6]
# So the left column of B in net = B[2], B[5], B[8] = B's RIGHT column from behind.
# And R[2] (top of R's right col) is adjacent to B[2] (top of B's right col from behind = top of B's left in net).
# This makes physical sense! B[2] and R[2] share the top-right-back corner of the cube (both are stickers on that corner from their respective faces).
#
# So the fix is: mirror B LEFT-RIGHT, not rotate 180 degrees.
#
# Alternatively expressed: iterate B's columns in reverse order.
# Instead of r, c = divmod(i, 3), draw with c = (2 - c_original)

print("\n\nConclusion: B face needs LEFT-RIGHT mirror in draw_net")
print("Fix: when drawing B, iterate columns right-to-left instead of left-to-right")
print("i.e., x1 = fx + (2-c) * cell instead of fx + c * cell")
print("OR equivalently, use B[2,1,0, 5,4,3, 8,7,6] instead of B[0,1,2,3,4,5,6,7,8]")

# But wait - let me also check the top/bottom orientation.
# After the mirroring, is top/bottom correct?
# After U CW: B[0,1,2] = Red. Mirrored B top row in net = B[2,1,0] = [R,R,R].
# Still Red. Top row stays the same color (in this symmetric case).
# Let's check with a distinguishable scramble.

cs5 = CubeState()
cs5.apply("U")
print("\nAfter U CW, B face internal state:", cs5.faces['B'])
# B[0,1,2] = Red (from R's top row R[0,1,2])
# B[3,4,5] = Blue (unchanged middle)
# B[6,7,8] = Blue (unchanged bottom)
#
# Mirrored B (for net):
# top: B[2],B[1],B[0] = R,R,R
# middle: B[5],B[4],B[3] = B,B,B
# bottom: B[8],B[7],B[6] = B,B,B
#
# In 3D: after U CW, B's top row (adjacent to U) should be Red (from R).
# U's back row = White (rotated, all same).
# In net: B top in net is adjacent to U top in net (physically in 3D).
# B's top in mirrored net = [R,R,R]. U's back row = U[0,1,2] = [W,W,W].
# These are the stickers at the U-B interface. Different pieces = different colors. Looks correct.
