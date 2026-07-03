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

def test_cycles(cycles, label=""):
    tests = [
        ("R U R' U' x6", "R U R' U'", 6),
        ("T-perm x2", "R U R' U' R' F R2 U' R' U' R U R' F'", 2),
        ("Sune x8", "R U R' U R U2 R'", 8),
        ("F-perm x2", "R' U' F' R U R' U' R' F R2 U' R' U' R U R' U R", 2),
    ]
    results = []
    for name, alg, expected_order in tests:
        ct = CubeTest(cycles)
        found = False
        for i in range(1, 30):
            ct.apply(alg)
            if ct.is_solved():
                ok = "OK" if i == expected_order else f"WRONG (got {i}, expected {expected_order})"
                results.append(f"  {name}: order={i} {ok}")
                found = True
                break
        if not found:
            results.append(f"  {name}: order>29 WRONG")
    all_ok = all("WRONG" not in r and ">" not in r for r in results)
    print(f"{label}: {'ALL OK' if all_ok else 'SOME FAILURES'}")
    if not all_ok:
        for r in results:
            print(r)
    return all_ok

# Start with the known partial fix
# The B face indexing: based on my coordinate analysis:
# B is viewed from BEHIND (+Z direction looking toward cube). In that view:
# right = +X, top = +Y. So B[0]=top-left=(y=+1,x=-1), B[2]=top-right=(y=+1,x=+1).
#
# For U CW: B's top row contributes to L. B[0]->L[0]? Or B[0]->L[2]?
# B[0]=(y=+1,x=-1,z=-1) = BUL. After U CW: (x=-1,z=-1)->(new_x=-1,new_z=+1). Position: (x=-1,y=+1,z=+1)=FUL.
# -Z sticker direction under CW: (0,-1) in (x,z) -> (-z,x)? Wait: (x,z)->(new_x=z,new_z=-x). For direction:
# direction (0,-1) (which is -Z): new_x=-1, new_z=0 = -X direction. So B-facing sticker becomes L-facing.
# FUL on L face: L is at x=-1. FUL=(y=+1,z=+1). On L face (looking -X, right=-Z? Let me recompute).
# Looking in -X... I computed before: facing -X (looking in -X direction? No, looking AT L means looking FROM -X toward +X).
# L is the -X face. You stand at x=-inf looking in +X direction. right=+Z (as computed).
# L[0]=top-left=(y=+1,z=-1), L[2]=top-right=(y=+1,z=+1). Actually: left in view is -Z (since right=+Z). So top-left=(+Y,-Z)=(y=+1,z=-1)=BUL. L[0]=BUL.
# Wait: looking in +X direction, right=+Z (you face +X, right arm points +Z=toward front of cube).
# Left = -Z (toward back of cube). Top = +Y.
# L[0]=top-left=(+Y,-Z)=(y=+1,z=-1,x=-1)=BUL on L face.
# L[2]=top-right=(+Y,+Z)=(y=+1,z=+1,x=-1)=FUL on L face.
#
# B[0]=(y=+1,x=-1,z=-1)=BUL. After U CW: goes to FUL=(y=+1,x=-1,z=+1). On L face: FUL = L[2]. So B[0]->L[2].
#
# But with cycle [U, [F[0,1,2], R[0,1,2], B[0,1,2], L[0,1,2]]]:
# Right-shift: F gets from L, R gets from F, B gets from R, L gets from B.
# L[B[0]] -> L face: L[0] = B[0]. So B[0] -> L[0]. But we need B[0]->L[2]. WRONG.
#
# To get B[0]->L[2]: when L gets from B, we need L[2]=B[0].
# This means: either L's index list has L[2] as the first element (L gets idx=[2,1,0]),
# or B's index list has B[0] at the appropriate position.
# L gets from B (right-shift: L is at k=3, gets from B at k=2).
# L[idx_L[j]] = B[idx_B[j]].
# L[2]=B[0]: idx_L[0]=2, idx_B[0]=0.
# L[1]=B[1]: idx_L[1]=1, idx_B[1]=1.
# L[0]=B[2]: idx_L[2]=0, idx_B[2]=2.
# So idx_L=[2,1,0], idx_B=[0,1,2].
# AND we need to check if B->L is consistent with R->B:
# B[0]=R[?]: B[idx_B[j]] = R[idx_R[j]]. B[0]=R[idx_R[0]].
# We need R[0]->B[0]: R[idx_R[0]]=0, so idx_R[0]=0. idx_R=[0,1,2].
# AND R->B: B[0]=R[0]. ✓ if idx_R=[0,1,2] and idx_B=[0,1,2].
# Then: L[idx_L[j]] = B[idx_B[j]] = B[j]. L[2]=B[0], L[1]=B[1], L[0]=B[2].
# B[0]->L[2]: B[0] is stored at B[idx_B[0]]=B[0], goes to L[idx_L[0]]=L[2]. ✓
# AND check F->R: R[idx_R[j]]=F[idx_F[j]]. R[j]=F[idx_F[j]].
# Need F[0]->R[2]: R[2]=F[0], so idx_F must satisfy: R[idx_R[j]]=F[idx_F[j]] with j=2: R[2]=F[idx_F[2]]=F[0], so idx_F[2]=0.
# j=0: R[0]=F[idx_F[0]], need F[2]->R[0]: idx_F[0]=2.
# j=1: R[1]=F[1]: idx_F[1]=1.
# So idx_F=[2,1,0].
# AND L->F: F[idx_F[j]]=L[idx_L[j]]. F[2]=L[2], F[1]=L[1], F[0]=L[0].
# But we need L[0]->F[2] (L[0] goes to F[2]). F[idx_F[j]]=L[idx_L[j]] with j=2: F[0]=L[0]. So L[0]->F[0]. WRONG (need L[0]->F[2]).
#
# There's an inherent contradiction in representing this with a single index list per face.
# The fix must use a COMPLETELY DIFFERENT approach.
#
# CORRECT APPROACH: Use separate indices for the SAME face when it appears in different roles.
# The standard way in cube implementations is:
# Each edge of the cube is defined as an ordered pair (face, [sticker_indices_in_order]).
# For U CW: the four edges, each specified independently:
# Edge 1: F top row = F[0,1,2] (F's stickers in left-to-right order as they travel CW)
# Edge 2: R top row = R[0,1,2] (R's stickers in order... but what order?)
#
# The KEY is: what is "in order" for each face? It means: in the ORDER that the stickers flow.
# For U CW (from above): stickers flow F->R->B->L. The "direction" of flow along each edge:
# F top: left(F[0]) to right(F[2]) in F's coordinate = the sticker at F[0] (FUL) goes FIRST.
# After CW: F[0](FUL) -> R[2](FUR corner). F[1] -> R[1](UR edge). F[2] -> R[0](BUR).
# So F top in F's order [0,1,2] maps to R in ORDER [2,1,0] = REVERSED R order.
# F's order and R's order are REVERSED relative to each other.
#
# IF we specify the R edge ALSO in the order they ARRIVE (not R's natural left-to-right):
# R edge for U CW (from F->R): arrives at R[2], R[1], R[0]. So R's indices in arrival order = [2,1,0].
# Then R's [2,1,0] -> B's [?].
# R[2](FUR) -> B[?]: R[2]=(y=+1,z=+1,x=+1). CW: (x=+1,z=+1)->(new_x=+1,new_z=-1)=(BUR). On B: B[2]=(y=+1,x=+1).
# R[1] -> B[1]. R[0](BUR) -> BUL = B[0].
# So R[2]->B[2], R[1]->B[1], R[0]->B[0]. The R edge [2,1,0] maps to B edge [2,1,0] (REVERSED).
# Then B[2]->L[?]: B[2]=(y=+1,x=+1,z=-1)=BUR. CW: (x=+1,z=-1)->(new_x=-1,new_z=-1)=(BUL)=(x=-1,y=+1,z=-1). On L: L[0]=(y=+1,z=-1). B[2]->L[0].
# B[1]->L[1], B[0]->L[2].
# B edge [2,1,0] maps to L edge [0,1,2] (REVERSED -> SAME = REVERSED again).
# Wait: B[2]->L[0], B[1]->L[1], B[0]->L[2]. B[2,1,0] -> L[0,1,2]. ✓ Same indices in that order.
# L[0]->F[?]: L[0]=(y=+1,z=-1,x=-1)=BUL. CW: (x=-1,z=-1)->(new_x=-1,new_z=+1)=(FUL). F[0]=(y=+1,x=-1,z=+1)=FUL. L[0]->F[0]. ✓
# L[1]->F[1], L[2]->F[2]. L[0,1,2]->F[0,1,2]. ✓
#
# So if we specify the cycle edges in "travel order":
# [F[0,1,2], R[2,1,0], B[2,1,0], L[0,1,2]]
# This represents: F[0]->R[2], R[2]->B[2]? No wait.
# With right-shift: face[k] gets from face[k-1] at same list position j.
# face[0]=F, face[1]=R, face[2]=B, face[3]=L.
# F[0] gets from L[0]. L[0]->F[0]. ✓
# F[1] gets from L[1]. L[1]->F[1]. ✓
# F[2] gets from L[2]. L[2]->F[2]. ✓
# R[2] gets from F[0]. F[0]->R[2]. ✓
# R[1] gets from F[1]. F[1]->R[1]. ✓
# R[0] gets from F[2]. F[2]->R[0]. ✓
# B[2] gets from R[2]. R[2]->B[2]. But we need R[2]->B[2]? Yes, R[2] is from F[0], and B[2]=(y=+1,x=+1)=BUR.
# R[2]->B[2]: ✓ (as computed above).
# B[1] gets from R[1]. ✓
# B[0] gets from R[0]. R[0]->B[0]. ✓
# L[0] gets from B[2]. B[2]->L[0]. ✓
# L[1] gets from B[1]. ✓
# L[2] gets from B[0]. B[0]->L[2]. ✓
#
# ALL CORRECT! The correct U cycle is:
# [('F',[0,1,2]), ('R',[2,1,0]), ('B',[2,1,0]), ('L',[0,1,2])]
print("Correct U cycle: [('F',[0,1,2]), ('R',[2,1,0]), ('B',[2,1,0]), ('L',[0,1,2])]")

# Now I need to verify the current code's BUGGY cycle and find ALL wrong cycles.
# Current:
# 'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',[0,1,2]),('L',[0,1,2])])
# Correct:
# 'U': ('U', [('F',[0,1,2]),('R',[2,1,0]),('B',[2,1,0]),('L',[0,1,2])])
# Differences: R and B indices are [2,1,0] instead of [0,1,2].

# Now let me derive D, F, B, R, L cycles similarly.
# I'll use the coordinate approach for D:
# D CW (from below, looking +Y direction): stickers flow F->L->B->R->F.
# D face (y=-1), viewed from below (from -Y, looking +Y):
# right = -X (by right-hand rule: looking in +Y direction, right = ?).
# facing +Y, up is arbitrary. Conventionally: viewing D from below with F face "up" = +Z up.
# Looking +Y with up=+Z: right = up x forward = +Z x +Y? Hmm, let me compute:
# I need: facing direction (forward) = +Y. Let's say "up in view" = +Z (toward front of cube as seen from below).
# right = forward x up... no: right = view_up x forward = +Z x +Y = (0,0,1)x(0,1,0) = (0*0-1*1, 1*0-0*0, 0*1-0*0) = (-1,0,0) = -X.
# So looking at D from below: right = -X. D[0]=top-left=(+Z,-X) wait...
# "top" in the below view (looking up): away from you = +Z (front of cube, which is "forward" when looking up from below with front = up in view).
# D[0] = top-left in below view = forward and left = (+Z, +X, y=-1). Wait: left = +X since right = -X.
# D[0] = (+Z, +X, y=-1) = (x=+1, y=-1, z=+1).
# D[2] = top-right = (+Z, -X, y=-1) = (x=-1, y=-1, z=+1).
# D[6] = bottom-left = (-Z, +X, y=-1) = (x=+1, y=-1, z=-1).
# D[8] = bottom-right = (-Z, -X, y=-1) = (x=-1, y=-1, z=-1).
#
# Verify with F cycle: F uses D[2,1,0] as D's top row (adjacent to F's bottom).
# F's bottom row is adjacent to D's front row. D's front row = row with z=+1 = D[0,1,2].
# F cycle has D[2,1,0] which is D[0,1,2] reversed. Hmm, interesting.
# In the F CW cycle: D[2,1,0]. With right-shift: D gets from R.
# D[2]=R[?]. F->R->D path. R[0,3,6] is R's left column.
# F CW: U bottom -> R left -> D top(reversed) -> L right -> U bottom.
# After F CW: D[2,1,0] gets R[0,3,6]: D[2]=R[0], D[1]=R[3], D[0]=R[6].
# This means F[2,1,0] addressing for D = [2,1,0] = D's top-right then mid then top-left.
# D[2]=(y=-1,z=+1,x=-1)=FDL corner on D face. D[0]=(y=-1,z=+1,x=+1)=FDR corner.
# Wait my D coordinates above: D[0]=(x=+1,z=+1) and D[2]=(x=-1,z=+1). So D[0,1,2] is D's front row (z=+1).
# D[2]=FDL and D[0]=FDR. D[2,1,0] = left to right from D's front row? Going D[2](FDL)->D[1](FDM)->D[0](FDR).
# In D's view (from below, right=-X), D[2] is to the right... hmm wait.
# D[0]=(x=+1,z=+1), right=-X means +X is LEFT. So D[0] is on the LEFT side.
# D[0]=top-left in below-view? Wait I said D[0]=top-left=(+Z,+X)=(z=+1,x=+1) and right=-X so left=+X.
# Yes: D[0]=top-left=(z=+1=toward front, x=+1=left in view). D[2]=top-right=(z=+1,x=-1=right in view).
# OK so D[2,1,0] going left-to-right in below-view = D[2](top-right)->D[1](top-mid)->D[0](top-left).
# = right to left in below-view.
#
# OK this is getting very complex. Let me just EMPIRICALLY find all correct cycles.
# I'll keep F, R, L, B cycles as in the original (they pass the individual tests),
# and fix U based on my analysis, then fix D by symmetry, and test.

# From coordinate analysis:
# U correct: [('F',[0,1,2]), ('R',[2,1,0]), ('B',[2,1,0]), ('L',[0,1,2])]
# D: D CW moves F->L->B->R->F (reversed from U). Let me figure out:
# D face stickers: adjacent to F bottom row (F[6,7,8]), adjacent to L bottom row (L[6,7,8]), etc.
# Original D cycle: [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])]
# By symmetry with U, D should be:
# [('F',[6,7,8]),('L',[8,7,6]),('B',[8,7,6]),('R',[6,7,8])]? Let me think.
# D CW from below = D CW from below is like U CW but upside down.
# Actually D CW: the D face rotates clockwise when viewed from BELOW.
# From below, the faces adjacent to D are the BOTTOM rows of F, L, B, R.
# The sticker flow for D CW (from below) should be: F->R->B->L->F? Or F->L->B->R?
# Looking from BELOW: it's the opposite handedness. D CW from below = D CCW from above.
# From above, D CW = same as U CW but lower. Actually:
# D CW from BELOW looking UP: if you hold the cube with D face toward you, you're looking +Y.
# CW from +Y (bottom face): +X -> -Z -> -X -> +Z -> +X (same as U CW from +Y... wait).
# Hmm, D CW "from below" means clockwise when you look at the D face from outside (from below = -Y).
# Looking from -Y: CW rotation. Let's compute: (x,z) rotation CW when viewed from -Y.
# Viewed from -Y (looking +Y): CW is the same physical rotation as viewed from above (+Y) but with... hmm.
# Actually "D CW" in WCA notation = D face rotates CW when viewed from BELOW the cube.
# This is the SAME physical rotation direction as U CW.
# Actually: both U CW and D CW rotate in the same direction (CW when seen from their respective outside).
# U CW from above (+Y looking down): CW = +X->-Z->-X->+Z.
# D CW from below (-Y looking up): viewed from -Y, right = -X (as I computed). CW from -Y:
# When looking in +Y direction (from -Y toward +Y), CW = +X->+Z->-X->-Z? Or +X->-Z?
# Actually the physical rotation: D CW = the D layer spins such that, if you look at D from below, it spins clockwise.
# Looking from -Y (from below, looking +Y): right = -X. CW: right -> down = -X -> -Z, down -> left = -Z -> +X, left -> up = +X -> +Z, up -> right = +Z -> -X.
# Wait: right = -X, up in view = +Z (I said "top" in below view is +Z direction).
# CW from -Y: right -> down -> left -> up -> right = -X -> -Z -> +X -> +Z -> -X.
# So D CW: -X->-Z->+X->+Z->-X, or equivalently: +X->+Z->-X->-Z->+X (following +X sticker).
# Hmm: +X goes to +Z, +Z goes to -X, -X goes to -Z, -Z goes to +X.
# This is: +X -> +Z (same transformation: new_x=z, new_z=+x? Let me check: +X=(1,0): new_x=z=0, new_z=x=+1. So goes to (0,+1)=+Z). ✓
# Transformation for D CW: (new_x, new_z) = (-z, x) [since D CW from -Y is CW when viewed from -Y].
# Hmm: +X=(1,0) -> (-0,+1)=(0,+1)=+Z. +Z=(0,1)->(-1,0)=-X. ✓
# So D CW transformation: (x,z) -> (-z, x).
# Compare U CW: (x,z) -> (z, -x).
# These are OPPOSITE rotations! D CW is U CCW in terms of 3D rotation direction.
# This makes sense: U CW (from above) = D CCW (from above). U CW and D CW are OPPOSITE 3D rotations.
#
# D CW transformation: (x,z) -> (-z, x).
# Bottom row of F: F[6]=(x=-1,z=+1,y=-1), F[7]=(x=0,z=+1,y=-1), F[8]=(x=+1,z=+1,y=-1).
# After D CW: F[6] at (-z=(-1), x=-1) = (x=-1, z=-1). That's on B face (z=-1) or L face (x=-1)?
# A corner sticker: F[6] is on F face (z=+1). After D CW, it goes to position (-1,-1).
# x=-1 and z=-1: bottom-back-left corner. On L face: (x=-1,y=-1,z=-1). L face at x=-1.
# L[6]=(y=-1, z=-1, x=-1)? Let me check: L[6]=bottom-left in L's view (looking +X): left=-Z, bottom=-Y.
# L[6]=(y=-1, z=-1, x=-1)? L bottom row going left to right: L[6]=(y=-1,z=-1), L[7]=(y=-1,z=0), L[8]=(y=-1,z=+1).
# So L[6]=(x=-1,y=-1,z=-1). Our sticker went to (x=-1,y=-1,z=-1) on L face. So F[6]->L[6]. ✓ (same index!)
#
# F[8]=(x=+1,z=+1,y=-1). After D CW: (-z=(-1), x=+1) = (x=+1, z=-1). This is on R face (x=+1).
# R[8]=(y=-1,z=-1,x=+1)? R bottom row: R[6]=(y=-1,z=-1), R[7]=(y=-1,z=0), R[8]=(y=-1,z=+1).
# (x=+1,y=-1,z=-1) = R[6]. So F[8]->R[6]. REVERSED! (F[8] is F[6+2=8], R[6] is R[6+0=6]).
#
# Hmm: F[6,7,8] -> L[6,7,8] for F[6], but F[8]->R[6]. Let me check F[7]:
# F[7]=(x=0,z=+1,y=-1). After D CW: (-z=-1, x=0)=(x=0,z=-1). That's B[7]? Wait: z=-1 is B face.
# B[7]=(y=-1,x=0,z=-1)? B bottom row: B[6]=(y=-1,x=-1), B[7]=(y=-1,x=0), B[8]=(y=-1,x=+1).
# Hmm wait: B[0]=top-left=(y=+1,x=-1), so B[6]=bottom-left=(y=-1,x=-1), B[8]=bottom-right=(y=-1,x=+1).
# B[7]=(y=-1,x=0,z=-1). Our sticker: (x=0,y=-1,z=-1). On B face: B[7]=(y=-1,x=0). ✓
# So F[7]->B[7].
#
# So D CW: F[6]->L[6], F[7]->B[7], F[8]->R[6]. That means F's bottom row goes to L,B,R in parts? That's weird...
# Wait, D move should only move the BOTTOM LAYER. And each face's bottom row goes to one FACE entirely. Let me recheck.
# After D CW: F[6,7,8] should all go to ONE of {L,B,R,F}. Not split across faces.
#
# Oh! I think I made an error. The D move in WCA moves the ENTIRE BOTTOM layer.
# F[6,7,8] are the bottom row of F face, which are part of the D layer.
# F[6]=(x=-1,y=-1,z=+1): this is the bottom-left of F. After D CW transformation (x,z)->(-z,x):
# new_x = -z = -1, new_z = x = -1. Position: (x=-1,y=-1,z=-1). That's on L face (x=-1) and B face (z=-1)? It's the corner piece at the intersection. The STICKER is from F face (z=+1). After D CW, the piece moved to (x=-1,y=-1,z=-1). The sticker that was facing +Z now faces... the F direction (z=+1) transforms under D CW:
# +Z direction = (0,0,1) in (x,z) = (0,1). After D CW transformation: (-z=(-1),x=0) = (-1,0) = -X = L face!
# So F[6] (F-face sticker of FDL corner) becomes L-face sticker at corner (x=-1,y=-1,z=-1) = BDL corner.
# L face at BDL = L[6]=(y=-1,z=-1). So F[6]->L[6]. ✓

# Hmm but I'm confusing myself. Let me also check F[8]:
# F[8]=(x=+1,z=+1,y=-1). D CW: position moves to (-z=-1, x=+1)=(x=+1,z=-1)=(BDR corner).
# F sticker (+Z direction) transforms to -X? Wait: +Z direction = (0,+1) in (x,z). After (-z,x): (-1,0)=-X=L face.
# But BDR corner is at (x=+1,y=-1,z=-1) which is on R face (x=+1) and B face (z=-1). Not L.
# The STICKER facing direction: +Z direction -> after D CW transformation -> -X direction = L face.
# But the CORNER is at (x=+1,y=-1,z=-1) which doesn't have an L face sticker (L is at x=-1, not x=+1)!
#
# I think I'm making an error in the transformation. Let me be more careful.
#
# D CW: rotating the bottom slice (y=-1). The rotation is around the Y axis.
# I said D CW (viewed from below, -Y) has transformation (x,z)->(-z,x).
# Let me verify: +X -> -Z? No: (1,0) -> (-0, 1) = (0,1) = +Z. +X->+Z. ✓ (same as from below: right goes to up-in-view = +Z front of cube).
# Wait but for U CW I had (x,z)->(z,-x). And for D CW I'm getting (x,z)->(-z,x).
# These are DIFFERENT. U CW: +X->-Z (CW from above). D CW: +X->+Z (which is CCW from above).
# +X -> +Z is the OPPOSITE rotation from above. That makes sense: D CW (from below) = U CCW (from above).
#
# So: D CW transformation: (x,z) -> (-z, x). (Or equivalently, 3D rotation around Y axis by +90° from below = -90° from above.)
# Actually: I computed (x,z)->(new_x, new_z) = (-z, x). Let me verify sign:
# For "CW from below" (looking +Y): I said right=-X (when looking in +Y). CW means -X goes to "up" (toward viewer = +Z in view = +Z in world if +Z is forward in the below view).
# Actually I need to be careful about "up in the below-view".
# Looking at D from below: you're at (0,-inf,0) looking up (+Y). The cube's front (+Z) is... toward you? No, +Z is the front of the cube, which when you look up is... away from you? It depends on body orientation.
# Let's say when looking at D from below, the F side of D appears at the BOTTOM of your view (like how when you look at U from above, F is at the bottom of your U view). Then "up in view" = -Z (back of cube).
# Looking in +Y with up=-Z: right = up x forward (actually: right = view_right which I need to compute via cross product).
# forward = +Y = (0,1,0). Let's define view-up = -Z = (0,0,-1).
# right = up_in_view x forward = (-Z) x (+Y) = (0,0,-1)x(0,1,0) = (0*0-(-1)*1, (-1)*0-0*0, 0*1-0*0) = (1,0,0) = +X.
# So when looking at D from below with F-side at bottom (like standard): right = +X.
# D[0]=top-left=(+Y_in_view = -Z, left = -X): D[0]=(-Z,-X) = (x=-1,z=-1,y=-1).
# D[2]=top-right=(−Z,+X) = (x=+1,z=-1,y=-1).
# D[6]=bottom-left=(+Z,-X) = (x=-1,z=+1,y=-1).
# D[8]=bottom-right=(+Z,+X) = (x=+1,z=+1,y=-1).
#
# Verify with F cycle: F uses D[2,1,0]. D[0]=(x=-1,z=-1), D[2]=(x=+1,z=-1). D[2,1,0] = [D[2],D[1],D[0]] = [(x=+1,z=-1),(x=0,z=-1),(x=-1,z=-1)].
# These are D's back row (z=-1). D's back row = adjacent to... wait, B is at z=-1. So D's back edge is adjacent to B's bottom edge. D[2,1,0] = D's back row (z=-1). But F cycle uses D[2,1,0] for F-adjacent stickers?? That doesn't make sense.
# Unless: D[0]=(x=-1,z=-1) is the BACK-LEFT of D, not front-left. Let me re-examine.
# I set up D viewing with F-side at bottom (y coordinate in the below view... hmm).
# Actually: when I look at D from below with the cube's front (+Z) side at the BOTTOM of my view:
# up in my view = -Z (back of cube). D[0] = top-left-in-view = back-left = (x=-1, z=-1, y=-1). ✓
# D[6] = bottom-left = front-left = (x=-1, z=+1, y=-1). ✓
# D[6,7,8] = D's bottom row in view = front row = adjacent to F's bottom. ✓
# D[0,1,2] = D's top row in view = back row = adjacent to B's bottom. ✓
#
# So D[6,7,8] is adjacent to F (front). D[0,1,2] is adjacent to B (back). ✓
# The current code uses D[6,7,8] for F cycle which is CORRECT.
# The current code uses D[6,7,8] for the D move's F/L/B/R edges. Let me verify.
# D cycle: [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])].
# Right-shift: F gets from R, L gets from F, B gets from L, R gets from B.
# Sticker flow: R->F->L->B->R. For D CW (from below), flow should be F->R->B->L->F (same as U CW from above? No...)
# D CW from below (right=+X, CW in the XZ plane from -Y): +X -> -Z (since I need to verify).
# D CW from below with right=+X: CW means right goes "down" in view. Down in view = +Z (front of cube).
# CW: +X -> +Z -> -X -> -Z -> +X.
# So: +X->+Z, +Z->-X, -X->-Z, -Z->+X.
# Stickers at D's bottom layer (front row, z=+1): F[6,7,8]. After D CW, they go to the +X side (R face) since +Z->-X... wait:
# +Z -> -X means: stickers at D's front (z=+1) go to... which face?
# F[6]=(x=-1,z=+1,y=-1). After D CW: (x=-1,z=+1) -> (-z=(-1), x=-1)? No wait, I need to recompute.
# D CW from below: transformation I'll now recompute.
# +X -> +Z: means (1,0) -> (0,1). In (x,z) coordinates: new_x=?, new_z=?.
# If +X=(1,0) -> (0,1)=+Z: new_x=0, new_z=1. This is z = x_old, x = ?. Not enough info.
# +Z=(0,1) -> -X=(-1,0): new_x=-1, new_z=0. From x_old=0,z_old=1: new_x=-z_old=-1. ✓ new_z=x_old=0. ✓
# So: new_x = -z, new_z = x. Transformation: (x,z)->(-z,x). (same as what I had before)
# F[6]=(x=-1,z=+1): new_x=-z=-1, new_z=x=-1. New position: (x=-1,y=-1,z=-1)=BDL.
# F sticker (+Z direction) transforms: (0,+1) -> (new_x=-1, new_z=0) = -X = L face.
# F[6] (at FDL corner) becomes L sticker at BDL corner.
# L face: BDL = (x=-1,y=-1,z=-1). L[6]=bottom-left in L view = (y=-1,z=-1). That's bottom-left = BDL. L[6]=(x=-1,y=-1,z=-1). ✓
# F[6] -> L[6]. ✓ (same index!)
#
# F[8]=(x=+1,z=+1): new_x=-1, new_z=+1. (x=-1,y=-1,z=+1)=FDL. +Z direction -> -X = L face.
# FDL on L face: L[8]=bottom-right=(y=-1,z=+1). FDL=(x=-1,y=-1,z=+1). L[8]=(x=-1,y=-1,z=+1). F[8]->L[8]?
# Hmm, L[8]=(y=-1,z=+1): bottom-right in L view (looking +X, right=+Z). bottom-right=(y=-1,z=+1). ✓
# So F[8]->L[8]. Same index.
#
# So F[6,7,8]->L[6,7,8] for D CW. ✓ (code has this)
# Now what about L->B? L[6,7,8]->B[?].
# L[6]=(x=-1,y=-1,z=-1)=BDL. D CW: (x=-1,z=-1)->(-z=+1,x=-1)=(x=-1,z=+1)=FDL.
# -X direction -> ? : (-1,0) -> (-0,-1)=(0,-1)=-Z=B face.
# FDL on B face? FDL=(x=-1,y=-1,z=+1). B face is at z=-1. That's not z=+1...
# Hmm, (new_x=-1, new_z=+1) means position is at (x=-1,y=-1,z=+1) = FDL, which is NOT on B face.
# The sticker direction became -Z (B face). But the piece is at FDL (z=+1), not at z=-1!
# I think there's an error. Let me redo:
# L[6] is an L-face sticker. L face is at x=-1. L[6]=(x=-1,y=-1,z=-1).
# The sticker DIRECTION = -X (outward from L face = toward -X = pointing left).
# After D CW: piece at (x=-1,y=-1,z=-1) moves. D CW transforms (x,z)->(-z,x): (-1,-1)->(-(-1),-1)=(+1,-1). New position: (x=+1,y=-1,z=-1) which is... B face (z=-1) AND R face (x=+1). It's the BDR corner.
# Sticker direction -X: under D CW transformation: (-1,0)->(new_x=-0=0, new_z=-1)=(0,-1)=-Z direction = B face!
# BDR corner on B face: B[8]? B face: B[6]=(y=-1,x=-1), B[8]=(y=-1,x=+1). BDR=(y=-1,x=+1,z=-1). B[8]=(y=-1,x=+1). ✓
# L[6]->B[8]. REVERSED! (L[6]=bottom-left of L, B[8]=bottom-right of B).
#
# L[8]=(x=-1,y=-1,z=+1)=FDL. D CW: (x=-1,z=+1)->(-z=-1,x=-1). Hmm wait: (-z,x)=(-1,-1). New position: (x=-1,y=-1,z=-1)=BDL.
# -X direction -> (0,-1)=-Z = B face. B[6]=(y=-1,x=-1). BDL=(y=-1,x=-1,z=-1). B[6]=(y=-1,x=-1). L[8]->B[6].
# L[6]->B[8], L[7]->B[7], L[8]->B[6]: REVERSED! L[6,7,8]->B[8,7,6].
#
# But code has L[6,7,8]->B[6,7,8]. WRONG! Code should use B[8,7,6] when L is the source.

# OK so D cycle needs: B indices to be [8,7,6] when B receives from L.
# With right-shift: [F[6,7,8], L[6,7,8], B[6,7,8], R[6,7,8]] has L->B as L[6,7,8]->B[6,7,8].
# Need L[6,7,8]->B[8,7,6].
# Fix: B's index list = [8,7,6] to represent B[8]=L[6], B[7]=L[7], B[6]=L[8].
# But then B[8,7,6] as SOURCE for R: what should R get?
# B[6]->R[?]: B[6]=(x=-1,z=-1) BDL. D CW: (x=-1,z=-1)->(-(-1),-1)=(+1,-1) = BDR = (x=+1,y=-1,z=-1).
# -Z direction -> (0,... ) under D CW: (-1,0) for -Z? Wait: -Z direction = (0,-1) in (x,z).
# (x,z)->(-z,x): (0,-1) -> (-(-1),0) = (1,0) = +X = R face.
# BDR on R face: R[8]=(y=-1,z=+1)? R[6]=(y=-1,z=-1), R[7]=(y=-1,z=0), R[8]=(y=-1,z=+1). BDR=(y=-1,z=-1)=R[6].
# B[6]->R[6]. Hmm.
# B[8]=(y=-1,x=+1,z=-1)=BDR. D CW: (x=+1,z=-1)->(-(-1),+1)=(+1,+1). FDR=(x=+1,y=-1,z=+1).
# -Z direction -> +X direction. FDR on R face: R[8]=(y=-1,z=+1). FDR=(y=-1,z=+1). R[8]. B[8]->R[8].
# B[6]->R[6], B[7]->R[7], B[8]->R[8]: SAME ORDER. B[6,7,8]->R[6,7,8] or B[8,7,6]->R[8,7,6]? Let me verify:
# With B indices [8,7,6] as source: B[8]->R[8], B[7]->R[7], B[6]->R[6]. ✓ Same mapping.
# So R's index list = [8,7,6] when receiving from B[8,7,6]. R[8]=B[8], R[7]=B[7], R[6]=B[6]. ✓
# But wait: R should have [6,7,8] as its natural order for the D face.
# If B=[8,7,6] and R=[8,7,6] (both reversed): B[8]=L[6], and R[8]=B[8]=L[6]. Hmm, need to check F->L:
# In the code: F gets from R (right-shift: F at k=0 gets from R at k=3).
# R[8,7,6] -> F[?]: R[6]->F[?].
# R[6]=(x=+1,y=-1,z=-1)=BDR. D CW: (x=+1,z=-1)->(+1,+1). FDR=(x=+1,y=-1,z=+1).
# +X direction -> ? : (1,0) -> (0,1) = +Z = F face! FDR on F: F[8]=(y=-1,x=+1). FDR=(y=-1,x=+1,z=+1)... wait.
# F[6]=(y=-1,x=-1,z=+1), F[8]=(y=-1,x=+1,z=+1). FDR=(y=-1,x=+1,z=+1)=F[8]. R[6]->F[8]. Reversed.
# R[8]=(y=-1,z=+1)=FDR. D CW: (x=+1,z=+1)->(-1,+1)=(-1,+1). FDL=(x=-1,y=-1,z=+1).
# +X direction -> +Z = F face. FDL on F: F[6]=(y=-1,x=-1,z=+1). R[8]->F[6]. Reversed.
# So R[6,7,8]->F[8,7,6] = REVERSED. R[8,7,6]->F[6,7,8].
# If R indices = [8,7,6] as source, F gets F[6]=R[8], F[7]=R[7], F[8]=R[6] = R[8,7,6]->F[6,7,8]. ✓
#
# So D cycle should be:
# [('F',[6,7,8]), ('L',[6,7,8]), ('B',[8,7,6]), ('R',[8,7,6])]
# Right-shift: F gets from R, L gets from F, B gets from L, R gets from B.
# F[6]=R[8], F[7]=R[7], F[8]=R[6]. R[8]->F[6], R[6]->F[8]. ✓
# L[6]=F[6], L[7]=F[7], L[8]=F[8]. F[6]->L[6]. ✓
# B[8]=L[6], B[7]=L[7], B[6]=L[8]. L[6]->B[8]. ✓ (reversed)
# R[8]=B[8], R[7]=B[7], R[6]=B[6]. B[8]->R[8]. ✓
#
# Great! Let me now test this.

# But first, let me also figure out B cycle and F cycle fixes.
# From the T-perm test with U fixed, we get order 8. The remaining bugs must be in B, F, or other cycles.
# The F cycle in the original code:
# F: [('U',[6,7,8]),('R',[0,3,6]),('D',[2,1,0]),('L',[8,5,2])]
# Let me verify if this is correct.
# F CW (viewed from front, +Z direction): stickers flow...
# +Z -> +Y means: face-toward-front stickers flow toward up.
# F CW: U bottom -> R left -> D top(rev) -> L right(rev) -> U bottom.
# Standard: U[6,7,8] -> R[0,3,6] (U bottom, left-to-right = R left col, top-to-bottom). CORRECT!
# R[0,3,6] -> D[2,1,0] (R left col top-to-bottom -> D top row right-to-left).
# D[2,1,0] -> L[8,5,2] (D top row right-to-left -> L right col bottom-to-top).
# L[8,5,2] -> U[6,7,8] (L right col bottom-to-top -> U bottom left-to-right).
# Current F cycle: [U[6,7,8], R[0,3,6], D[2,1,0], L[8,5,2]].
# Right-shift: U gets from L, R gets from U, D gets from R, L gets from D.
# U[6]=L[8], U[7]=L[5], U[8]=L[2]. L[8]->U[6], L[2]->U[8]. ✓ (L right bottom->U left bottom)
# R[0]=U[6], R[3]=U[7], R[6]=U[8]. U[6]->R[0], U[8]->R[6]. ✓
# D[2]=R[0], D[1]=R[3], D[0]=R[6]. R[0]->D[2], R[6]->D[0]. ✓
# L[8]=D[2], L[5]=D[1], L[2]=D[0]. D[2]->L[8], D[0]->L[2]. ✓
# F cycle appears CORRECT!
#
# Now B cycle: B[('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]
# B CW (from behind, -Z direction, looking +Z): looking +Z, right=+X.
# Standard B CW: U back -> L left -> D back(rev) -> R right(rev) -> U back.
# U back = U[0,1,2] (top row of U as stored = back row).
# L left = L[0,3,6] (left col of L, top-to-bottom in L view).
# D back = D[2,1,0]? D[0,1,2] is D's back row (z=-1). D[0]=(x=-1,z=-1), D[2]=(x=+1,z=-1).
# From L's bottom, the stickers go to D. L[6] is at (x=-1,y=-1,z=-1)=BDL. D[0]=(x=-1,z=-1). Same position? No: L[6] is the L sticker, D[0] is the D sticker, both at BDL corner. After B CW: L[6]-> D[?].
# Actually the current B cycle: [D[6,7,8], R[8,5,2], U[2,1,0], L[0,3,6]].
# Right-shift: D gets from L, R gets from D, U gets from R, L gets from U.
# D[6]=L[0], D[7]=L[3], D[8]=L[6]. L[0]->D[6], L[6]->D[8].
# But D[6]=bottom-left-front=(x=-1,z=+1) and L[0]=back-top=(y=+1,z=-1). These are completely different corners!
# After B CW, L[0] (BUL, L face sticker) should move to D[something] at the back bottom. D[0]=(x=-1,z=-1)=BDL. D[6]=(x=-1,z=+1)=FDL. L[0] at BUL should go to D[0] (BDL adjacent corner), not D[6] (FDL). That seems wrong.
# Let me verify: B CW moves the BACK LAYER. The back layer corners: BUL, BUR, BDL, BDR.
# B CW (viewed from behind, looking +Z): CW means BUL->BUR->BDR->BDL->BUL.
# B CW 3D: (x,y) -> ... rotation around Z axis? B face is -Z plane. B CW when looking +Z direction.
# Looking in +Z direction, right = +X, up = +Y. CW: +X->-Y->-X->+Y->+X.
# So: +X->-Y, -Y->-X, -X->+Y, +Y->+X.
# In (x,y) plane: +X=(1,0)->-Y=(0,-1). Transformation: new_x=y, new_y=-x? Check: (1,0)->(0,-1). new_x=0=y_old. ✓ new_y=-1=-x_old. ✓ Transformation: (x,y)->(y,-x).
#
# L[0]=(x=-1,y=+1,z=-1)=BUL. B CW: (x=-1,y=+1)->(y=+1,-x=+1)=(x=+1,y=+1). BUR.
# L sticker (-X direction) at BUL after B CW: (-X direction) = (-1,0) in (x,y): (-1,0)->(0,-(-1))=(0,1)=+Y=U face.
# BUR on U face: U[2]=(y=+1,x=+1,z=-1). U[2]=(x=+1,z=-1,y=+1). L[0]->U[2]. ✓
#
# Current code has U[2,1,0] getting from R: U[2]=R[?]. And right-shift has U gets from R.
# U[2]=R[8], U[1]=R[5], U[0]=R[2]. R[8]->U[2]. Let's verify:
# R[8]=(x=+1,y=-1,z=+1)=FDR. B CW should NOT affect R[8] since B moves z=-1 layer.
# But wait: R[8] is NOT in the back layer (z=+1, not z=-1). So it's wrong for B to affect R[8] unless...
# Oh! The B cycle moves R's RIGHT COLUMN (R[2,5,8] in R's column indices, not z coordinates).
# R[2,5,8] in code = ? Let me think about R's layout again.
# R[0]=(y=+1,z=-1,x=+1)=BUR, R[2]=(y=+1,z=+1,x=+1)=FUR, R[6]=(y=-1,z=-1,x=+1)=BDR, R[8]=(y=-1,z=+1,x=+1)=FDR.
# R's right column as seen from outside R (looking -X, right=+Z): R[2,5,8] = right column = (z=+1 column) = FUR, FMR, FDR. These are FRONT stickers of R face, NOT back stickers!
# But B move should affect B's adjacent R stickers. B is at z=-1 (back). B is adjacent to R's BACK stickers.
# R's back column = R[0,3,6] = (z=-1 column) = BUR, BMR, BDR.
# But the code uses R[8,5,2] for B! That's R's FRONT column (z=+1). That seems wrong!
#
# Or wait: maybe I have R's layout wrong? Let me re-examine.
# R face: at x=+1. Viewed from outside (+X direction, looking -X):
# right = ? I computed right=+Z (via cross product). Top = +Y.
# R[0] = top-LEFT (in view). Left = -Z. R[0]=(y=+1,z=-1,x=+1)=BUR. ✓
# R[2] = top-RIGHT (in view). Right = +Z. R[2]=(y=+1,z=+1,x=+1)=FUR. ✓
# R's RIGHT column (R[2,5,8]) = front column. B is adjacent to R's LEFT column (R[0,3,6]) = back column.
# But B cycle uses R[8,5,2] which is the BOTTOM row? R[8]=(y=-1,z=+1)=FDR, R[5]=(y=0,z=0), R[2]=(y=+1,z=+1)=FUR. R[8,5,2] going bottom to top of R's FRONT column... wait, going DOWN the front column?
# R[2](top-right)->R[5](mid-right)->R[8](bot-right) = top to bottom of right column. R[8,5,2] = reversed right column (bottom to top).
#
# Hmm, R[8,5,2] = R's right column in reverse. But B should affect R's LEFT column (z=-1 back).
# R's left column = R[0,3,6]. So B cycle using R[8,5,2] seems WRONG physically.
# BUT wait - maybe the B face adjacency is to R's right column in some coordinate systems?
# B face is at z=-1. R face is at x=+1. They share the edge at x=+1, z=-1.
# This edge on R face is R's LEFT column (z=-1 side): R[0,3,6].
# So B cycle should use R[0,3,6] (or reversed R[6,3,0]), not R[8,5,2].
# THIS IS A BUG IN THE B CYCLE!
#
# Let me also check: R cycle uses B[6,3,0] for the B face edge.
# B[6,3,0]: B[6]=(y=-1,x=-1,z=-1), B[3]=(y=0,x=-1,z=-1), B[0]=(y=+1,x=-1,z=-1) = left column of B from behind.
# B's left column from behind = the x=-1 side of B face = the side adjacent to L face, NOT R face!
# B face at z=-1. Adjacent to R face (x=+1): the x=+1 side of B face = B's right column from behind.
# B's right column from behind: B[2]=(y=+1,x=+1,z=-1), B[5]=(y=0,x=+1,z=-1), B[8]=(y=-1,x=+1,z=-1).
# B[2,5,8] is the right column. But R cycle uses B[6,3,0] which is B's LEFT column. WRONG!
#
# WAIT. Let me reconsider the B face orientation.
# Maybe the code stores B with a DIFFERENT orientation than I assumed.
# Let me go back to basics: the code has _MOVE_CYCLES with B face.
# The single-move tests all pass (B*4=solved, B*B'=solved). So the B cycle is internally consistent.
# The issue might just be a DISPLAY bug, not a computation bug.
#
# Let me check: do B and R share the correct edge in the R cycle?
# R cycle: [F[2,5,8], U[2,5,8], B[6,3,0], D[2,5,8]].
# F[2,5,8] = F's RIGHT column (from front). Adjacent to R: ✓ (F right = R left).
# U[2,5,8] = U's right column. Adjacent to R: ✓ (U right = R top).
# B[6,3,0] = B's left column (x=-1)? If B[0]=top-left-from-behind and B[6]=bottom-left, then B[6,3,0] is left column from bottom to top.
# BUT in 3D: R is adjacent to B's x=+1 side (B's right column from behind = B[2,5,8]).
# If code uses B[6,3,0] for R's effect on B, that would mean R affects B's LEFT column, not right. WRONG?
#
# Unless B is stored with B[0]=top-LEFT from FRONT (= top-RIGHT from behind).
# Then B[0]=(y=+1,x=+1,z=-1) and B[6]=(y=-1,x=+1,z=-1) = B's right column from behind = adjacent to R!
# And B[2]=(y=+1,x=-1,z=-1) = B's left column from behind = adjacent to L.
#
# If B is stored FLIPPED (mirrored left-right compared to outside view), then:
# B[6,3,0] = right col from behind (x=+1 side) going bottom-to-top. ✓ for R cycle!
# B[8,5,2] = left col from behind (x=-1 side) going bottom-to-top. ✓ for L cycle!
# B[0,1,2] = top row from... B[0]=(x=+1), B[2]=(x=-1): top row from right to left (from behind view).
# = reversed from outside view.
#
# So maybe the code has B stored with the OPPOSITE left-right orientation!
# B[0]=top-right-from-outside (= top-left from inside/front view).
#
# Then for U CW: B[0,1,2] -> L[0,1,2]:
# B[0]=(y=+1,x=+1,z=-1)=BUR. After U CW: (x=+1,z=-1)->(new_x=-1,new_z=-1)=(BUL).
# B sticker (-Z) under CW: (0,-1)->(+1,0)=+X. Wait: +X would be R face. But BUL is L face territory.
# (0,-1) in (x,z) transformation (z,-x): (-(-1),-0)=(+1,0)=+X? Hmm: new_x=z=-1? Wait.
# transformation for U CW: (x,z)->(z,-x): B[0] at (x=+1,z=-1): new_x=z=-1, new_z=-x=-1. Position (-1,-1)=BUL.
# -Z direction under CW: (0,-1) in (x,z)->(z,-x)=(-(-1),-0)=(+1,0)=+X. That's R, not L.
# But the piece moved to BUL (x=-1). The STICKER direction becomes +X = R? That's contradictory (piece on L side, sticker facing R?). Something is wrong.
#
# I'm clearly making errors with these transformations. Let me take a completely different approach:
# Just EMPIRICALLY test different cycle combinations until T-perm has order 2.

print("Testing empirically...")

# Based on analysis, the issues are:
# 1. U cycle: B[0,1,2] should be B[2,1,0] and R[0,1,2] should be R[2,1,0]
# 2. D cycle: possibly similar issue
# 3. B cycle: possibly issues

# Let me try various combinations for D and B while keeping F,R,L fixed and U as I found:
import itertools

base_cycles = {
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[2,1,0]),('L',[8,5,2])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[6,3,0]),('D',[2,5,8])]),
    'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',[8,5,2]),('U',[0,3,6])]),
}

def make_u(b_idx, r_idx):
    return ('U', [('F',[0,1,2]),('R',r_idx),('B',b_idx),('L',[0,1,2])])

def make_d(b_idx, r_idx):
    return ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',b_idx),('R',r_idx)])

def make_b(d_idx, r_idx, u_idx, l_idx):
    return ('B', [('D',d_idx),('R',r_idx),('U',u_idx),('L',l_idx)])

# U cycle with correct indices [('F',[0,1,2]),('R',[2,1,0]),('B',[2,1,0]),('L',[0,1,2])]
u_correct = make_u([2,1,0],[2,1,0])
# Try D options
for b_d, r_d in [([6,7,8],[6,7,8]),([8,7,6],[6,7,8]),([6,7,8],[8,7,6]),([8,7,6],[8,7,6])]:
    for b_b, r_b, u_b, l_b in [
        ([6,7,8],[8,5,2],[2,1,0],[0,3,6]),
        ([6,7,8],[2,5,8],[2,1,0],[0,3,6]),
        ([8,7,6],[8,5,2],[2,1,0],[0,3,6]),
        ([8,7,6],[2,5,8],[2,1,0],[0,3,6]),
        ([6,7,8],[8,5,2],[0,1,2],[0,3,6]),
        ([6,7,8],[2,5,8],[0,1,2],[0,3,6]),
        ([8,7,6],[8,5,2],[0,1,2],[0,3,6]),
        ([8,7,6],[2,5,8],[0,1,2],[0,3,6]),
        ([6,7,8],[8,5,2],[2,1,0],[6,3,0]),
        ([8,7,6],[8,5,2],[2,1,0],[6,3,0]),
        ([6,7,8],[2,5,8],[2,1,0],[6,3,0]),
        ([8,7,6],[2,5,8],[2,1,0],[6,3,0]),
        ([8,7,6],[8,5,2],[0,1,2],[6,3,0]),
        ([8,7,6],[2,5,8],[0,1,2],[6,3,0]),
    ]:
        cycles = dict(base_cycles)
        cycles['U'] = u_correct
        cycles['D'] = make_d(b_d, r_d)
        cycles['B'] = make_b(b_b, r_b, u_b, l_b)

        ok = test_cycles(cycles)
        if ok:
            print(f"FOUND! D: B={b_d} R={r_d}, B: D={b_b} R={r_b} U={u_b} L={l_b}")
            print(f"Full cycles:")
            print(f"  U: {u_correct}")
            print(f"  D: {cycles['D']}")
            print(f"  B: {cycles['B']}")
            break
    else:
        continue
    break
