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

    def print_state(self, label=""):
        if label: print(label)
        for f in 'UDFBRL':
            print(f"  {f}: {self.faces[f]}")

# Test U F U' F' step by step with labeled cube
class CubeStateLabeled:
    def __init__(self):
        self.faces = {f: [f+str(i) for i in range(9)] for f in 'UDFBRL'}

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

# The key question: when U is applied, what happens to U face?
# U CW cycle: [F[0,1,2], R[0,1,2], B[0,1,2], L[0,1,2]]
# Right-shift: F<-L, R<-F, B<-R, L<-B
# So sticker flow: F->R->B->L->F (each goes to next)
# F[0,1,2] -> R[0,1,2]: F's top row goes to R's top row
# R[0,1,2] -> B[0,1,2]: R's top row goes to B's top row
# B[0,1,2] -> L[0,1,2]: B's top row goes to L's top row
# L[0,1,2] -> F[0,1,2]: L's top row goes to F's top row
# QUESTION: Is this correct for U CW?

# Standard U CW (viewed from above, White face):
# F top -> L top? No! F top -> R top for CW from above.
# Looking down at U face, CW means:
# Front -> Right -> Back -> Left -> Front
# So: F top row goes to R top row (CORRECT per code)
# R top row goes to B top row
# B top row goes to L top row
# L top row goes to F top row
# This seems correct.

# But wait - for B: when you look from above, does B[0,1,2] correspond to the back of the cube?
# We established: U[0,1,2] is adjacent to B (back row of U face).
# B[0,1,2] goes to L[0,1,2] after U CW.
# After U CW, B's top row now appears on L's top row.
# L is to the LEFT. After U CW, B stickers should go to L, and the index order matters.
#
# B's top row (B[0,1,2]) viewed from behind = [B[0]=top-left, B[1]=top-mid, B[2]=top-right]
# After U CW (viewed from above), these stickers go to L's top row.
# B's top row FROM BEHIND corresponds to:
#   B[0] = top-left from behind = top-RIGHT from front perspective = appears on the left of L after CW
#   Actually:
#   From above, going CW: the sticker at top-left of B (when viewed from behind)
#   moves to... which position on L?
#
# Let me use actual coordinates:
# B[0] is at the top-back-left corner (from global perspective, if left=negative x, back=negative z)
# Wait, in standard orientation (White=U, Green=F):
# B is at -Z. Looking at B from outside (-Z direction, i.e., from behind):
#   B[0] = top-left from this view = actual position: top, +X side (right side of cube)
#   B[1] = top-center
#   B[2] = top-right from this view = actual position: top, -X side (left side of cube)
#
# After U CW (viewed from +Y), the top stickers rotate.
# B[0] is at top, +X side. After CW, it moves to... bottom, +X (which is R's top+Z side?).
# No wait, CW from +Y rotates: +X->+Z (actually +X->-Z for the stickers on the top layer).
#
# Hmm. Let me think in terms of R/L/F/B positions.
# Standard: R=+X, L=-X, F=+Z (or F=-Z?), B=opposite of F.
# In WCA: Green=F, Blue=B, Red=R, Orange=L, White=U, Yellow=D.
# Let's say F=+Z, B=-Z, R=+X, L=-X, U=+Y, D=-Y.
#
# B face is at z=-1 (back of cube). When viewed from outside (from z=-inf),
# x increases to the RIGHT in the view, but in global coords, right in the view = -x direction.
# So B[0]=top-left-from-behind = (+y, +x in global) = this is the corner shared with U and R.
# B[2]=top-right-from-behind = (+y, -x in global) = corner shared with U and L.
# B[6]=bottom-left-from-behind = (-y, +x) = corner shared with D and R.
# B[8]=bottom-right-from-behind = (-y, -x) = corner shared with D and L.
#
# U CW (viewed from +y, clockwise): +x -> -z -> -x -> +z -> +x?
# No: CW from above (+y): +x -> +z, +z -> -x, -x -> -z, -z -> +x.
# Wait: CW rotation around +y axis: (x,z) -> (z,-x).
# So: (1,0) -> (0,-1), (0,1) -> (1,0), (-1,0) -> (0,1), (0,-1) -> (-1,0).
# +x -> -z, -z -> -x, -x -> +z, +z -> +x.
#
# So the sticker at B[0] = (+y,+x) moves to... (+y,-z) which is on the R face (+x)?
# No wait: (+y,+x) means the sticker is on U face (at +y) at the +x,-z corner (back-right).
# But B[0] is on the B FACE, not U face. B face stickers are at z=-1.
# B[0] is at (+y,+x,z=-1). After U CW: the z=-1 layer stickers on top row:
# B[0] is at (x=+1, y=+1, z=-1). After CW around y: x->-z, so new position: (x=-1+1... hmm)
# Let me use actual grid positions: stickers are at x in {-1,0,1}, y=+1 (top layer), z in {-1,0,1}.
#
# B face stickers are at z=-1:
# B[0]: (x=+1, y=+1, z=-1) [top-right in global, top-LEFT from behind]
# B[1]: (x=0, y=+1, z=-1)
# B[2]: (x=-1, y=+1, z=-1) [top-left in global, top-RIGHT from behind]
#
# After U CW (rotate around +y, CW from above): (x,z) -> (z,-x) wait let me redo.
# CW from +y looking down: think of a compass. North=+z is "up" on map.
# CW: N->E->S->W->N, i.e., +z->+x->-z->-x->+z.
# So: z=+1 goes to x=+1, x=+1 goes to z=-1, z=-1 goes to x=-1, x=-1 goes to z=+1.
# Transformation: (x,z) -> (-z, x)? Let's check: (+1,0) -> (0,+1)? That's +x -> +z, no.
# CW from above: N(+z)->E(+x): so +z becomes +x. Means z maps to +x: new_x = z, new_z = -x?
# Check: (0,+1)=North -> (+1,0)=East: new_x=z=+1, new_z=-x=0. Yes!
# So transformation: new_x=z, new_z=-x.
#
# B[0] is at (x=+1, z=-1). After CW: new_x=-1, new_z=-1.
# Position (-1, +1, -1) = on L face (x=-1), at y=+1, z=-1.
# L face: L[0] is at? L is at x=-1. Looking at L from outside (-x direction):
# L[0]=top-left-from-L's outside. From outside L (from -x direction), right in view = +z.
# L[0] = (+y, +z, x=-1). So L[0] = (x=-1, y=+1, z=+1).
# But B[0] moved to (x=-1, y=+1, z=-1). That's L face but at z=-1, which is L[2] (top-right from L's perspective from outside, since from -x perspective z=-1 is to the right? Let me reconsider.
# From outside L face (-x direction, looking toward +x):
#   In this view, +z is to the LEFT (because we're looking in the +x direction and +z would be to our left).
#   Wait - when looking from -x toward +x:
#   Your "right" = -z direction (standard right-hand rule)?
#   Actually: if you're looking in the +x direction, your right hand points in -z, left hand in +z.
#   So L face from outside: left=+z, right=-z, top=+y, bottom=-y.
#   L[0]=top-left = (+y, +z, x=-1).
#   L[2]=top-right = (+y, -z, x=-1).
#   L[6]=bottom-left = (-y, +z, x=-1).
#   L[8]=bottom-right = (-y, -z, x=-1).
#
# B[0] moved to (x=-1, y=+1, z=-1). This is L[2] (top-right from L's outside).
#
# So after U CW: B[0] -> L[2].
# But the code says B[0,1,2] -> L[0,1,2] (top row maps to top row, same order).
# B[0] should go to L[2], but code maps B[0] -> L[0]. THIS IS THE BUG!
#
# The U cycle for B->L should be reversed!
# Correct: B[0,1,2] -> L[2,1,0] (reversed)

# Let me verify: B[2] at (x=-1, y=+1, z=-1)? No:
# B[2] = top-right-from-behind = (x=-1, y=+1, z=-1). After CW: new_x=z=-1, new_z=-x=+1.
# Position: (x=-1, y=+1, z=+1) = L[0] (top-left from outside L).
# So B[2] -> L[0]. And B[0] -> L[2]. Confirmed: B[0,1,2] -> L[2,1,0].
# The code has B[0,1,2] -> L[0,1,2], which is WRONG.

print("=== BUG FOUND IN U MOVE ===")
print("U cycle has B[0,1,2] -> L[0,1,2]")
print("But physically B[0] -> L[2], B[1] -> L[1], B[2] -> L[0]")
print("So the cycle should be: B[0,1,2] -> L[2,1,0] (or equivalently, B[2,1,0] -> L[0,1,2])")
print()

# Now let's figure out ALL the issues.
# The U cycle in code: [('F',[0,1,2]),('R',[0,1,2]),('B',[0,1,2]),('L',[0,1,2])]
# Right-shift means: F<-L, R<-F, B<-R, L<-B
# Sticker flow: F->R->B->L->F
#
# Let's verify each:
# F[0,1,2] -> R[0,1,2]:
# F[0] = (x=-1, y=+1, z=+1) [top-left-from-front of F]
# After U CW: new_x=z=+1, new_z=-x=+1. Position: (x=+1, y=+1, z=+1) = R[0] (top-left from R's outside).
# R from outside (+x direction, looking toward -x): right in view = +z, top=+y.
# R[0]=top-left = (+y, -z, x=+1)? Wait, if looking in -x direction, your right = -z?
# Looking in -x direction: right = -z (by right-hand rule: looking in -x, right = -(x cross y) = z... hmm).
# Let me just use: R[0]=top-left from outside means top-front (y=+1, z=+1). Hmm.
# Actually for R face (x=+1), looking from outside (+x direction, looking toward -x):
# In this view, you see the cube from the right.
# Top is +y, bottom is -y. What's left/right?
# If you're standing to the right of the cube looking left (-x direction):
# Your right hand points toward +z (front of cube), your left hand toward -z (back).
# Wait: if facing -x direction, right is +z? Let me use cross product.
# facing direction = -x = (-1,0,0). up = y = (0,1,0). right = up x facing = y x (-x) = (0,1,0) x (-1,0,0)
# = (1*0-0*0, 0*(-1)-0*0, 0*0-1*(-1)) = (0, 0, 1) = +z.
# So looking in -x direction: right = +z.
# R[0] = top-left = top, left = +y, -z = (x=+1, y=+1, z=-1).
# R[2] = top-right = +y, +z = (x=+1, y=+1, z=+1).
#
# So F[0] = (x=-1, y=+1, z=+1)? Wait, for F face (z=+1), looking from outside (+z direction, toward -z):
# facing = -z. right = up x facing_dir = y x (-z) = (0,1,0) x (0,0,-1) = (1*(-1)-0*0, 0*0-0*(-1), 0*0-1*0) = (-1,0,0) = -x.
# So looking at F from outside: right = -x.
# F[0] = top-left = +y, +x (since right=-x means left=+x... wait).
# If right=-x, then left=+x. So F[0] = top-left = (+y, +x, z=+1) = (x=+1, y=+1, z=+1)?
# Hmm that doesn't feel right. Let me try differently.
#
# For F face: imagine standing in front of the cube. You see the F face.
# F[0] = top-left as you see it. Standing facing the cube (facing -z direction):
# right = +x (your right hand), left = -x.
# F[0] = top-left = (+y, -x, z=+1) = (x=-1, y=+1, z=+1).
# F[2] = top-right = (+y, +x, z=+1) = (x=+1, y=+1, z=+1).
# F[6] = bottom-left = (-y, -x, z=+1) = (x=-1, y=-1, z=+1).
# F[8] = bottom-right = (-y, +x, z=+1) = (x=+1, y=-1, z=+1).
#
# Now F[0] = (x=-1, y=+1, z=+1). After U CW: new_x=z=+1, new_z=-x=-(-1)=+1.
# New position: (x=+1, y=+1, z=+1) = R face (x=+1).
# R face: looking from +x direction toward -x: right=+z.
# R[0] = top-left = (+y, -z, x=+1) = (x=+1, y=+1, z=-1). But we got (x=+1, y=+1, z=+1).
# That's R[2] = top-right = (+y, +z, x=+1) = (x=+1, y=+1, z=+1).
# So F[0] -> R[2], NOT R[0]!
#
# And F[2] = (x=+1, y=+1, z=+1). After U CW: new_x=z=+1, new_z=-x=-1.
# New position: (x=+1, y=+1, z=-1) = R[0].
# So F[2] -> R[0].
#
# This means F[0,1,2] -> R[2,1,0] (reversed order)!
# But the code has F[0,1,2] -> R[0,1,2]. THIS IS ALSO WRONG.
#
# So BOTH F->R and B->L (and presumably R->B and L->F) have the wrong sticker order.
# But wait - the simple test "U U' = solved" still works. How?
# Because if F->R and R->B and B->L and L->F each use the SAME wrong mapping (just reversed),
# applying U 4 times still gives identity, and U U' still gives identity.
# But U combined with F or other moves would reveal the bug.

print("=== DEEPER ANALYSIS ===")
print("F[0] should go to R[2] after U CW, but code maps F[0]->R[0]")
print("F[2] should go to R[0] after U CW, but code maps F[2]->R[2]")
print()
print("The U cycle should have reversed index order for all faces")
print("Current: [('F',[0,1,2]),('R',[0,1,2]),('B',[0,1,2]),('L',[0,1,2])]")
print("Correct: [('F',[0,1,2]),('R',[2,1,0]),('B',[0,1,2]),('L',[2,1,0])]")
print("OR maybe the direction of sticker flow needs to be reversed?")
print()
print("Actually - wait. Let me reconsider the right-shift direction.")
print("The code says 'stickers travel in list order [0]->[1]->[2]->[3]->[0]'")
print("For U: [F,R,B,L] with right-shift: F<-L, R<-F, B<-R, L<-B")
print("This means: L->F->R->B->L (sticker from L goes to F, then to R, etc.)")
print("For U CW, should it be F->R->B->L->F or L->F->R->B->L?")
print()
print("U CW (from above): stickers flow Front->Right->Back->Left->Front")
print("So F->R->B->L->F is the CORRECT direction for sticker flow.")
print("Code has right-shift = F gets from L = L->F direction. This means stickers go L->F->R->B->L.")
print("That's WRONG! Stickers should go F->R, but code makes stickers go L->F.")
print()
print("Wait, let me recheck...")

# With right-shift: face[k] gets from face[k-1]
# List order: [F(0), R(1), B(2), L(3)]
# F gets from L (k=0, src=k-1=3=L): F <- L
# R gets from F (k=1, src=0=F): R <- F
# B gets from R (k=2, src=1=R): B <- R
# L gets from B (k=3, src=2=B): L <- B
# So: F<-L, R<-F, B<-R, L<-B
# Sticker "origin" chain: L->F->R->B->L (where does L's sticker end up? F. F ends up at R. R ends up at B. B ends up at L.)
# Wait: if F gets FROM L, that means L's sticker is now at F. So L's sticker moved to F.
# L->F->R->B->L is correct for the sticker travel direction? NO:
# F gets from L: means L's old value goes to F. So sticker at L moves to F. L->F.
# R gets from F: F's old value goes to R. F->R.
# B gets from R: R's old value goes to B. R->B.
# L gets from B: B's old value goes to L. B->L.
# So sticker travel: L->F->R->B->L.
# For U CW from above: stickers at Front top go to Right top (F->R), Right top go to Back top (R->B), etc.
# Correct direction: F->R->B->L->F.
# But code gives: L->F->R->B->L.
# These are OPPOSITE directions! L->F->R->B->L is actually U' (counterclockwise)!
#
# Wait, no. F->R->B->L->F: F goes to R. L->F->R->B->L: L goes to F. These are the same cycle,
# just starting at different points! L->F->R->B->L IS the same as F->R->B->L->F.
# They're cyclic permutations of the same cycle. Both describe: sticker at L -> F, F -> R, R -> B, B -> L.
#
# Actually: F->R->B->L->F means F's sticker ends up at R.
# L->F->R->B->L means L's sticker ends up at F, F's ends up at R.
# These ARE THE SAME CYCLE. I was confused.
#
# The question isn't the direction of the cycle, but whether the INDEX ORDER within each face is correct.
# For U CW: F[0,1,2] -> R[0,1,2] vs F[0,1,2] -> R[2,1,0]?
# We showed: F[0]=(x=-1,y=+1,z=+1) -> R[2]=(x=+1,y=+1,z=+1) after U CW.
# So the mapping is F[0]->R[2], F[2]->R[0]. Reversed.
# The code has F[0]->R[0] (same indices). This IS the bug.

print("CONFIRMED BUG: In U cycle, when F's top row goes to R's top row,")
print("the index order should be reversed (F[0]->R[2], not F[0]->R[0]).")
print()
print("But wait - since all faces have the same [0,1,2] indices in the U cycle,")
print("the reversal applies uniformly: the whole cycle should use [2,1,0] instead.")
print("Or, equivalently, the LIST ORDER of faces in the cycle should be reversed.")
