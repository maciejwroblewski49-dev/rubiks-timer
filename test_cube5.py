# Final analysis: Is the net drawing correct or does it need B mirrored?
# Let's use a distinguishable scramble and check if the NET is physically correct.
#
# Test: Apply R' then check the right edge of R and left edge of B in the net.
# After R': the stickers that were on D's right col should appear on B.
# Specifically, D[2,5,8] should go to B (after R CW: D<-B. So after R': D's values go to B).
# Wait, let's be careful.
# R CW cycle: [F[2,5,8], U[2,5,8], B[6,3,0], D[2,5,8]] with sticker flow F->U->B->D->F.
# R CW: F[2,5,8]->U[2,5,8], U[2,5,8]->B[6,3,0], B[6,3,0]->D[2,5,8], D[2,5,8]->F[2,5,8].
# R' (= R applied 3 times): reverse flow. F->D, D->B, B->U, U->F? No:
# R' = the inverse of R CW. In the inverse:
# F gets from U, U gets from B, B gets from D, D gets from F.
# But index mapping: R CW maps U[2,5,8] -> B[6,3,0]. So R' maps B[6,3,0] -> U[2,5,8]
# i.e., R': U[2,5,8] <- B[6,3,0], B[6,3,0] <- D[2,5,8], D[2,5,8] <- F[2,5,8], F[2,5,8] <- U[2,5,8].

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

    def print_net(self):
        def row(face, r):
            return ''.join(self.faces[face][r*3+c][0] for c in range(3))
        for r in range(3):
            print('   ' + row('U', r))
        for r in range(3):
            print(row('L', r) + row('F', r) + row('R', r) + row('B', r))
        for r in range(3):
            print('   ' + row('D', r))

    def print_net_b_mirrored(self):
        """Draw with B mirrored left-right to show the alternative rendering."""
        def row(face, r):
            return ''.join(self.faces[face][r*3+c][0] for c in range(3))
        def row_b_mirrored(r):
            return ''.join(self.faces['B'][r*3+(2-c)][0] for c in range(3))
        for r in range(3):
            print('   ' + row('U', r))
        for r in range(3):
            print(row('L', r) + row('F', r) + row('R', r) + row_b_mirrored(r))
        for r in range(3):
            print('   ' + row('D', r))

# The physical test:
# For R' move:
# After R': B[6,3,0] = D[2,5,8] = [Y,Y,Y] (Yellow from D's right col)
# So B[0]=Y, B[3]=Y, B[6]=Y? No: B[6,3,0] = [Y,Y,Y] means B[6]=Y, B[3]=Y, B[0]=Y.
# So B's LEFT column (as stored internally, from behind perspective) = Yellow.
# Also: R[2,5,8] right col in net = ? After R': R face rotated CCW.

print("=== After R' ===")
cs = CubeState()
cs.apply("R'")
print("B face:", cs.faces['B'])
print("B[0,3,6] (B's left col from behind):", cs.faces['B'][0], cs.faces['B'][3], cs.faces['B'][6])
print("B[2,5,8] (B's right col from behind):", cs.faces['B'][2], cs.faces['B'][5], cs.faces['B'][8])
print("R face right col R[2,5,8]:", cs.faces['R'][2], cs.faces['R'][5], cs.faces['R'][8])
print()
print("Net (current rendering, B drawn as-is):")
cs.print_net()
print()
print("Net (B drawn left-right mirrored):")
cs.print_net_b_mirrored()
print()

# Physical analysis for R' net:
# After R': D's right column moved to B.
# In a physical cube after R':
# Looking at the net, R's right edge and B's adjacent edge should be from the same piece.
# After R': The edge between R and B (physically = between +x face and -z face at the +x,-z seam):
# This edge contains 3 sticker pairs. On a solved cube: R has Red, B has Blue at this seam.
# After R': R's right col (R[2,5,8] in net) should contain what?
# R' moves: U[2,5,8] -> F[2,5,8], B[6,3,0] -> U[2,5,8], D[2,5,8] -> B[6,3,0], F[2,5,8] -> D[2,5,8]
# So R[2,5,8] face... R face after R' is rotated CCW (3 CW = 1 CCW).

print("R face after R' (should be CCW rotation of solved R):")
print("  Solved R: [R,R,R,R,R,R,R,R,R]")
print("  After R': ", cs.faces['R'])
print("  CCW rotation: [c[2],c[5],c[8], c[1],c[4],c[7], c[0],c[3],c[6]]")
solved_r = ['R']*9
print("  Expected:", [solved_r[2],solved_r[5],solved_r[8], solved_r[1],solved_r[4],solved_r[7], solved_r[0],solved_r[3],solved_r[6]])
print()

# For the net to be correct, we need to know: what stickers are physically adjacent
# at the R-B seam after R'?
# The R-B seam in 3D: x=+1 face meets z=-1 face.
# On R face: the right edge (when viewed from right, with right=+z) = R[2,5,8].
# After R', R[2,5,8] from the R CCW rotation... R CCW: [c[2],c[5],c[8], c[1],c[4],c[7], c[0],c[3],c[6]]
# From solved R: R[2]=R, R[5]=R, R[8]=R (still Red after CCW since all same).
# So R's right edge in net (R[2,5,8]) = [R, R, R].
#
# On B face: the stickers adjacent to R are on B's right column (from behind) = B[2,5,8].
# After R': B[6,3,0] = [Y,Y,Y] (from D right col). B[2,5,8] = unchanged = [B,B,B].
# So B's right col from behind = Blue.
#
# In the net:
# If B drawn as-is: B right col in net = B[2,5,8] = [B,B,B].
# If B drawn mirrored: B left col in net (showing B's right col from behind) = B[2,5,8] = [B,B,B].
# Hmm. Both give same result here since B right col = Blue either way on a solved cube.
# After R', B[2,5,8] = still Blue. So we can't distinguish with this test.

# Let me use a test with B MOVE instead.
print("=== After B CW ===")
cs2 = CubeState()
cs2.apply("B")
print("After B CW:")
print("B face:", cs2.faces['B'])
print("R face right col R[2,5,8]:", cs2.faces['R'][2], cs2.faces['R'][5], cs2.faces['R'][8])
print("L face left col L[0,3,6]:", cs2.faces['L'][0], cs2.faces['L'][3], cs2.faces['L'][6])
print()
print("Physical analysis of B CW:")
print("B CW (from behind): U back row -> L left col, L left col -> D bottom row, D bottom row -> R right col, R right col -> U back row")
print("After B CW:")
print("  R[8,5,2] (right col, bottom-to-top) gets D[6,7,8] = [Y,Y,Y]")
print("  So R[8]=Y, R[5]=Y, R[2]=Y")
print("  Actual R[2,5,8]:", cs2.faces['R'][2], cs2.faces['R'][5], cs2.faces['R'][8])
print()

# After B CW: R[8,5,2] = D[6,7,8] = [Y,Y,Y]. So R[2]=Y, R[5]=Y, R[8]=Y.
# In the net, R's right column = R[2,5,8] = [Y,Y,Y].
#
# Physically, R's right column IS adjacent to B in the 3D cube.
# After B CW, the pieces at the R-B seam:
#   On R face: right edge = Yellow (just moved from D).
#   On B face: left edge (from behind) = B[0,3,6] = ? (B rotated CW, face stays Blue).
# B face after CW rotation: still all Blue (since solved B is all Blue).
# So B[0,3,6] = Blue, B[2,5,8] = Blue.
#
# In the net:
# - R right col = [Y,Y,Y] (correct, matches physical right edge of R)
# - B adjacent to R: in the net, B's LEFT column (net position) is adjacent to R's RIGHT column.
#
# What should B's left col (net) show?
# After B CW: the physical stickers at the R-B seam from B's side: these are B's right edge (from behind = B[2,5,8]).
# These are STILL BLUE (B face unchanged color since all same).
# But wait: after B CW, the actual PIECES at the R-B seam moved!
# The R right edge got pieces from D (Yellow). Those D pieces now have their R-side facing R = Yellow.
# The corresponding B-side of those same pieces... are they part of B face or D face?
# A corner piece at top-right-back: has stickers on R, U, and B faces.
# After B CW, the top-right-back corner:
# R[2] = Yellow (from D[6] = bottom-right-front corner's D sticker).
# Wait, that piece (D[6]) was originally at bottom-right-front. Its stickers: D[6]=Yellow, F[6]=Green, R[6]=Red.
# After B CW: D[6] -> R[2]? Let me check the R cycle vs B cycle.
# B CW: R[8,5,2] gets D[6,7,8]. So R[2] gets D[8] = Yellow (D[8]=bottom-right-back corner's D face sticker).
#
# The piece at D[8] (bottom-right-back) has stickers: D[8]=Yellow, R[8]=Red, B[6]=Blue.
# After B CW: D[8] -> R[2]. The piece MOVES. Where does the whole piece go?
# The piece was at corner (x=+1, y=-1, z=-1). After B CW (rotation around z=-1 plane, CW from -z):
# Rotation: (x,y) -> (y,-x). So (x=+1, y=-1) -> (y=-1, -x=-1) = new (x=-1, y=-1)?
# That would put it at the bottom-left-back corner. Hmm.
#
# Actually, a B CW move (as viewed from outside = from -z, looking toward +z) rotates the -z slice.
# CW from -z direction: using right-hand rule for rotation around -z axis, CW = standard.
# Wait: B CW "from behind" means CW when you look at the B face from outside (-z direction).
# When looking in the +z direction (from behind at -z, looking toward +z):
# CW rotation: right-hand rule with thumb in +z direction gives CCW when you flip = CW in our view.
# (x,y) rotation CW (in our view, looking in +z): (x,y) -> (y,-x).
#
# Piece at (1,-1,-1): after B CW: x_new=y=-1, y_new=-x=-1 -> (-1,-1,-1).
# So it moved to bottom-left-back. That piece now occupies corner (-1,-1,-1) which is D[6] (bottom-left-back)?
# D[6] = (x=-1, y=-1, z=+1)? No that's front. Hmm.
# D face is y=-1. D[6] = row 2, col 0 of D face. Row goes from z=-1 (back) to z=+1 (front)?
# Actually: F move cycle uses D[2,1,0] for D top = adjacent to F. And F is +z.
# So D[0,1,2] is adjacent to...
# F cycle: D[2,1,0]. D's top row = adjacent to F's bottom = D[2,1,0]?
# If D[2,1,0] is adjacent to F(+z), then D[2] is at (x=+1, y=-1, z=+1)? That's D's right-front corner.
# D layout:
#   D[0] is adjacent to F(+z) and... from the F cycle D[2,1,0] reversed means D[0]=D's top-right(from above)?
# Ugh, getting complicated. Let me just trust the move tests and focus on the NET RENDERING.

print()
print("=== Key question: Is the net rendering correct? ===")
print("Net after U CW:")
cs3 = CubeState()
cs3.apply("U")
cs3.print_net()
print()
print("Physical expectation for U CW net:")
print("Looking at the net with L[F][R][B] unfolded:")
print("U top row in net = U[0,1,2] = back row of U. Should be White (unchanged).")
print("U bottom row in net = U[6,7,8] = front row of U. Should be White (unchanged).")
print("F top row in net = F[0,1,2]. After U CW, F[0,1,2] = Orange (from L). CORRECT.")
print("R top row in net = R[0,1,2]. After U CW, R[0,1,2] = Green (from F). CORRECT.")
print("B top row in net = B[0,1,2]. After U CW, B[0,1,2] = Red (from R). Shows in net correctly IF B is not mirrored.")
print("L top row in net = L[0,1,2]. After U CW, L[0,1,2] = Blue (from B). CORRECT.")
print()
print("The net top rows (row 0 of middle band): L=B(blue), F=O(orange), R=G(green), B=R(red)")
print("Physical top row adjacency with U:")
print("- F[0,1,2] is adjacent to U[6,7,8] (bottom of U). U[6,7,8]=White, F[0,1,2]=Orange. Makes sense.")
print("- L[0,1,2] is adjacent to U[0,3,6] (left col of U). U[0,3,6]=White, L[0,1,2]=Blue. Makes sense.")
print("- R[0,1,2] is adjacent to U[2,5,8] (right col of U). U[2,5,8]=White, R[0,1,2]=Green. Makes sense.")
print("- B[0,1,2] is NOT directly adjacent to U in the net!")
print("  B is at columns 9-11, U is at columns 3-5. They're not touching in the net.")
print("  B's top row connects to U's top row ONLY when folded 3D.")
print("  B[0,1,2]=Red is the back row of B (adjacent to U back row).")
print("  When the net is folded: B's top goes against U's top (U[0,1,2]).")
print("  U[0,1,2]=White, B[0,1,2]=Red. These are adjacent PIECES in 3D.")
print()
print("  But the VISUAL DISPLAY of B in the net: is B[0,1,2] at the top correct?")
print("  YES if B face is stored as viewed from behind (outside).")
print("  In a standard net diagram, B is drawn as seen from outside.")
print("  The code stores B with indices 0=top-left WHEN VIEWED FROM BEHIND.")
print("  So drawing B[0,1,2] at the top is CORRECT.")
print()
print("CONCLUSION: The net rendering of B appears to be CORRECT.")
print("The 'bug' might be something else...")
print()

# Maybe the issue is the D face orientation? Or maybe the MOVE SIMULATION is truly wrong
# and the display happens to be correct?

# Let me check: is T-perm truly order > 19? Maybe it has order much larger.
_MOVE_CYCLES_TEST = _MOVE_CYCLES
class CubeStateTest:
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

print("=== T-perm order search (up to 100) ===")
tperm = "R U R' U' R' F R2 U' R' U' R U R' F'"
cs_t = CubeStateTest()
for i in range(1, 101):
    cs_t.apply(tperm)
    if cs_t.is_solved():
        print(f"T-perm order: {i}")
        break
else:
    print("T-perm order > 100 - DEFINITELY A BUG IN MOVE SIMULATION")
