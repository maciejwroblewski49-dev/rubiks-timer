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

def find_order(cycles, alg, max_n=50):
    ct = CubeTest(cycles)
    for i in range(1, max_n+1):
        ct.apply(alg)
        if ct.is_solved():
            return i
    return None

# Derive L cycle:
# L CW (viewed from left, -X direction): right = -Z (when looking +X direction, right = ?).
# Actually: looking at L from outside means looking in +X direction.
# facing = +X = (1,0,0). up = +Y. right = up x facing = (0,1,0)x(1,0,0) = (0*0-1*0, 1*1-0*0, 0*0-0*1) = (0,1,0)?? That's up itself.
# Let me use: right = forward x up = (1,0,0)x(0,1,0) = (0*0-0*1, 0*0-1*0, 1*1-0*0) = (0,0,1) = +Z.
# Hmm, right = +Z when looking at L from outside (+X direction).
# So: looking at L from outside (+X): right = +Z (front of cube is to your right!).
# Wait that means the F face of the cube is to YOUR RIGHT when looking at L. That means you're looking from the L side toward R.
# Actually: if you stand to the LEFT of the cube (at x=-inf) and look RIGHT (toward +X), then:
# - The front of the cube (+Z) is to YOUR RIGHT (you face +X, cube's front is at +Z which is... to your right if you're looking in +X direction).
# Actually, facing +X: your right hand points in the direction given by right-hand rule.
# right = up x forward? Let me use the standard camera convention:
# view_right = normalize(view_forward cross view_up) = (+X) cross (+Y) = (0,0,-1)? No: (1,0,0)x(0,1,0) = (0*0-0*1, 0*0-1*0, 1*1-0*0) = (0,0,1)=+Z. So right=+Z. OK.
# So looking at L from outside: right=+Z. This means cube's front (+Z) is to YOUR RIGHT.
# L[0] = top-left = (y=+1, -Z) = (y=+1, z=-1, x=-1) = BUL.
# L[2] = top-right = (y=+1, +Z) = (y=+1, z=+1, x=-1) = FUL.
# L[6] = bottom-left = (y=-1, -Z) = (y=-1, z=-1, x=-1) = BDL.
# L[8] = bottom-right = (y=-1, +Z) = (y=-1, z=+1, x=-1) = FDL.
#
# Compare with code's L cycle expectations:
# Code: [F[0,3,6], D[0,3,6], B[8,5,2], U[0,3,6]]
# Right-shift: F gets from U, D gets from F, B gets from D, U gets from B.
# Sticker flow: B->U->F->D->B.
# For L CW (from left, +X direction, with right=+Z):
# CW transformation: right->down->left->up = +Z->-Y->-Z->+Y->+Z.
# So for pieces at x=-1: +Z -> -Y, -Y -> -Z, -Z -> +Y, +Y -> +Z.
# (y,z) plane with +Y and +Z: CW from +X: (y,z) -> ?
# +Y=(1,0) -> -Z? No: +Z -> -Y means (0,1) -> (-1,0). So: (y,z) -> (-z, y)? Check: (0,1)=+Z -> (-1,0)=-Y ✓. (1,0)=+Y -> (0,1)=+Z ✓. Transformation: (y,z)->(-z,y).
# Hmm: but wait. CW when viewed from +X: +Z -> -Y. Let me re-examine.
# Looking from +X (at L face), with right=+Z, up=+Y. CW rotation:
# right -> down -> left -> up: +Z -> -Y -> -Z -> +Y -> +Z.
# So: (y=0,z=+1)=+Z -> (y=-1,z=0)=-Y. (y=0,z=+1)->(-1,0): new_y=-z=-1,new_z=y=0. Transformation: new_y=-z,new_z=y.
# (y,z)->(-z,y). ✓ (as I had).
# L CW: (y,z)->(-z,y) for pieces at x=-1.
#
# F left column: F[0]=(y=+1,x=-1,z=+1), F[3]=(y=0,x=-1,z=+1), F[6]=(y=-1,x=-1,z=+1).
# Wait: F layout: F[0]=top-left=(y=+1,x=-1,z=+1), F[6]=bottom-left=(y=-1,x=-1,z=+1).
# F left column = F[0,3,6] (left column of F from front = x=-1 side of F).
# After L CW: F[0]=(y=+1,z=+1): new_y=-z=-1, new_z=y=+1. Position:(x=-1,y=-1,z=+1)=FDL. On D face: D[6]=(x=-1,z=+1,y=-1)=FDL. +Z direction (-Z sticker): (0,1) in (y,z): new_y=-1, new_z=0 = (−1,0) = −Y = D face. F[0]->D[6]. ✓
# F[6]=(y=-1,z=+1): new_y=-1, new_z=-1. (x=-1,y=-1,z=-1)=BDL. D[0]=(x=-1,z=-1,y=-1)=BDL. F[6]->D[0]. REVERSED (F[0]->D[6], F[6]->D[0]).
# F[3]=(y=0,z=+1): new_y=-1, new_z=0. (x=-1,y=-1,z=0). D[3]=(x=-1,z=0,y=-1). F[3]->D[3].
# F[0,3,6]->D[6,3,0]. ✓ Reversed!
#
# D left column: D[0]=(x=-1,z=-1,y=-1)=BDL, D[3]=(x=-1,z=0,y=-1), D[6]=(x=-1,z=+1,y=-1)=FDL.
# Wait, actually for D face: I established D[0]=(x=-1,z=-1), D[6]=(x=-1,z=+1). So D's left column = D[0,3,6].
# After L CW: D[0]=(y=-1,z=-1): new_y=-(-1)=+1, new_z=-1. (x=-1,y=+1,z=-1)=BUL. -Y direction: (-1,0) -> (0,-1)=-Z=B face. BUL on B: B[0]=(y=+1,x=-1,z=-1)=BUL. D[0]->B[0].
# D[6]=(y=-1,z=+1): new_y=-1, new_z=-1. Position:(x=-1,y=-1,z=-1)=BDL. -Y -> -Z = B. B[6]=(y=-1,x=-1)=BDL. D[6]->B[6]. ✓ same order.
# D[0,3,6]->B[0,3,6]. ✓ Same.
#
# But wait: with right-shift cycle [F,D,B,U]: D gets from F (at position j: D[idx_D[j]]=F[idx_F[j]]).
# F[0,3,6] -> D[6,3,0]: D[6]=F[0], D[3]=F[3], D[0]=F[6]. So D gets from F[j] at idx_F=[0,3,6] but D stores at idx_D=[6,3,0].
# For algorithm: D[idx_D[j]] = F[idx_F[j]]. If idx_F=[0,3,6], then idx_D=[6,3,0] for D to get F[0]->D[6], F[3]->D[3], F[6]->D[0].
# But code uses idx_D=[0,3,6] (same as F). So code gives D[0]=F[0], D[3]=F[3], D[6]=F[6]. WRONG (should be D[6]=F[0]).
#
# D[0,3,6]->B[0,3,6]: idx_D=[0,3,6] for source, idx_B=[0,3,6] for dest. ✓
# B[0,3,6]->U[?]: B[0]=(y=+1,x=-1,z=-1)=BUL. L CW: (y=+1,z=-1): new_y=-(-1)=+1, new_z=+1. (x=-1,y=+1,z=+1)=FUL. -Z direction: (0,-1)->(+1,0)=+Y=U. FUL on U: U[6]=(x=-1,z=+1)=FUL. B[0]->U[6]. Reversed (B[0]->U[6]).
# B[6]=(y=-1,x=-1,z=-1)=BDL. (y=-1,z=-1)->(+1,-1). (x=-1,y=+1,z=-1)=BUL. +Y->U. U[0]=(x=-1,z=-1)=BUL. B[6]->U[0]. Reversed.
# B[0,3,6]->U[6,3,0]. ✓ Reversed.
# U[6,3,0]->F[?]: U[6]=(x=-1,z=+1,y=+1)=FUL. L CW: (y=+1,z=+1): new_y=-1, new_z=+1. (x=-1,y=-1,z=+1)=FDL. +Y direction: (1,0)->(-0,1)=(0,1)=+Z=F. FDL on F: F[6]=(y=-1,x=-1)=FDL. U[6]->F[6]. Reversed order of U giving to F.
# U[0]=(x=-1,z=-1,y=+1)=BUL. (y=+1,z=-1)->(+1,+1). (x=-1,y=+1,z=+1)=FUL. +Y->+Z=F. FUL on F: F[0]=(y=+1,x=-1)=FUL. U[0]->F[0]. ✓
# U[6,3,0]->F[6,3,0]? U[6]->F[6], U[0]->F[0]. Wait that's same indices! But if U[6,3,0] is the reversed left column, then source and dest have same indices.
# Actually: B[0,3,6]->U[6,3,0] means U gets from B at same position: B[j]->U[6-6j]? No: B[idx_B[j]]->U[idx_U[j]].
# idx_B=[0,3,6], idx_U=[6,3,0]: U[6]=B[0], U[3]=B[3], U[0]=B[6]. U gets B stickers in reversed column order.
# Then U[6,3,0] as source for F: U[idx_U[j]]->F[idx_F[j]]. With idx_U=[6,3,0]: U[6]->F[0]? Or U[6]->F[6]?
# We computed U[6]->F[6] and U[0]->F[0]. So F[idx_F[j]]=U[idx_U[j]].
# F[0]=U[0], F[3]=U[3], F[6]=U[6]. idx_F=[0,3,6]. Same as U's source indices. Consistent!
#
# So for L CW with cycle [F[0,3,6], D[0,3,6], B[0,3,6], U[0,3,6]]:
# Wait that's the CODE. Let me re-examine.
# Actually: let me reconsider. The RIGHT-SHIFT algorithm means face[k][idx_k[j]] = face[k-1][idx_{k-1}[j]].
# Cycle [F, D, B, U]: F gets from U (k=0, prev=k-1=3=U), D gets from F, B gets from D, U gets from B.
# Sticker flow: U->F->D->B->U.
# For L CW: sticker flow should be F->D->B->U->F.
# With right-shift on [F, D, B, U]: sticker flow U->F->D->B->U. That's the REVERSE of F->D->B->U!
# So cycle [F, D, B, U] with right-shift gives L CCW (opposite direction).
# For L CW, we need cycle [U, B, D, F] (reversed list)? OR use the same list but in a different way?
# Actually, with [F, D, B, U] reversed = [U, B, D, F]. Right-shift: U gets from F, B gets from U, D gets from B, F gets from D. Flow: F->U->B->D->F. Still not right.
# For L CW (F->D->B->U->F), we need right-shift cycle order where each face gets from the one that feeds it.
# F gets from U: cycle has F at position k with U at k-1. So: if list is [U, F, D, B], F gets from U, D gets from F, B gets from D, U gets from B. Flow: U->F->D->B->U. Still backwards.
#
# Hmm. Let me just figure out: what list order gives L CW flow?
# For right-shift: face[k] gets from face[k-1]. Sticker at face[k-1] moves to face[k].
# So stickers FLOW from lower k to higher k (cyclically).
# L CW flow: F->D->B->U->F. This means: F should appear BEFORE D, D before B, B before U, U before F.
# List: [F, D, B, U] gives flow F->D->B->U->F. ✓ With right-shift!
# Wait, I said earlier that it's U->F->D->B->U. Let me recheck.
# Right-shift: face[k] gets from face[k-1 mod n].
# For list [F(0), D(1), B(2), U(3)]:
# F(0) gets from U(3): U->F.
# D(1) gets from F(0): F->D.
# B(2) gets from D(1): D->B.
# U(3) gets from B(2): B->U.
# So sticker that was at U moves to F, sticker at F moves to D, etc. Flow: U->F->D->B->U.
# This is L CW? L CW from left: F->D->B->U->F? Or U->F->D->B->U?
#
# L CW means the left face rotates CW when viewed from left. From left (looking +X direction, right=+Z):
# The stickers in the x=-1 slice rotate. F stickers (z=+1 side) go DOWN (F->D direction).
# CW: right(+Z) -> down(-Y) -> left(-Z) -> up(+Y) -> right(+Z).
# +Z->-Y: F stickers (z=+1=front) go to D (y=-1=down). F->D. ✓
# -Y->-Z: D stickers (y=-1) go to B (z=-1=back). D->B. ✓
# -Z->+Y: B stickers (z=-1) go to U (y=+1=up). B->U. ✓
# +Y->+Z: U stickers (y=+1) go to F (z=+1=front). U->F. ✓
# Flow: F->D->B->U->F. ✓ But with [F,D,B,U] cycle and right-shift: flow is U->F->D->B->U.
# U->F is the opposite! With [F,D,B,U] and right-shift: U sticker goes to F (not F->D). WRONG.
# So the list should be [U,F,D,B] for flow U->F->D->B->U. But L CW needs F->D->B->U flow.
# No wait: L CW flow F->D->B->U->F means F stickers end up at D, D at B, B at U, U at F.
# "F moves to D" means D GETS from F. So D[j] = F[j]. Right-shift: when D is at k and F at k-1, D gets from F. List [F,D,...] has D at k=1 getting from F at k=0. ✓
# So right-shift on [F,D,B,U] gives D gets from F ✓, B gets from D ✓, U gets from B ✓, F gets from U ✓.
# The sticker that was at F goes to D: F->D. The sticker at D goes to B: D->B. B->U. U->F. Flow F->D->B->U->F. ✓
# Wait I was wrong earlier. Let me redo: face[k] gets from face[k-1]. The sticker AT face[k-1] MOVES to face[k].
# List [F(k=0), D(k=1), B(k=2), U(k=3)]:
# D(k=1) gets from F(k=0): F sticker moves to D. F->D. ✓
# B(k=2) gets from D(k=1): D->B. ✓
# U(k=3) gets from B(k=2): B->U. ✓
# F(k=0) gets from U(k=3): U->F. ✓ (cyclic)
# Flow: F->D->B->U->F. ✓ This IS L CW! So code's list order [F,D,B,U] = correct!
# I was confusing myself. The code's cycle ORDER for L is [F,D,B,U]... but wait code has:
# 'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',[8,5,2]),('U',[0,3,6])])
# That's [F,D,B,U]. ✓ Correct order for L CW.
#
# Now verify the INDEX LISTS:
# We need: F[0,3,6]->D[6,3,0] (reversed), D[0,3,6]->B[0,3,6] (same), B[0,3,6]->U[6,3,0] (reversed), U[6,3,0]->F[0,3,6] (same).
# With right-shift [F,D,B,U]: D[idx_D[j]] = F[idx_F[j]].
# Need D[6]=F[0], D[3]=F[3], D[0]=F[6]: idx_D=[6,3,0], idx_F=[0,3,6].
# Code has idx_D=[0,3,6] WRONG (should be [6,3,0]).
# And idx_F=[0,3,6] ✓.
#
# B[idx_B[j]] = D[idx_D[j]]: B[0]=D[6], B[3]=D[3], B[6]=D[0] (since D src idx=[6,3,0]).
# Wait: after the fix, D's stored stickers are at positions idx_D=[6,3,0] in cycle order.
# Then B reads from D at the SAME cycle positions: B[idx_B[j]] = D[idx_D[j]].
# If D source is [6,3,0] (meaning D[6] flows, then D[3], then D[0]):
# B[idx_B[0]] = D[6]: need B[0]=D[6] for D[6]->B[0]. idx_B[0]=0.
# B[idx_B[1]] = D[3]: B[3]=D[3]. idx_B[1]=3.
# B[idx_B[2]] = D[0]: B[6]=D[0]. idx_B[2]=6. So idx_B=[0,3,6]. But we need D[0,3,6]->B[0,3,6] (same). Yes! ✓
#
# Actually wait, I computed D[0,3,6]->B[0,3,6] (same order). With idx_D=[6,3,0] and idx_B=[0,3,6]:
# D[6]->B[0], D[3]->B[3], D[0]->B[6]. That's D[6,3,0]->B[0,3,6] (D reversed -> B forward). But I computed D[0]->B[0] etc. There's a discrepancy.
# Let me recompute: D[0]=(x=-1,z=-1,y=-1)=BDL. L CW: (y=-1,z=-1): new_y=-(-1)=+1, new_z=-1. (y=+1,z=-1). Position:(x=-1,y=+1,z=-1)=BUL. -Y direction: (-1,0) in (y,z) -> (0,-1)=-Z=B. BUL on B: B[0]=(y=+1,x=-1)=BUL. D[0]->B[0]. ✓
# D[6]=(x=-1,z=+1,y=-1)=FDL. (y=-1,z=+1): new_y=-1, new_z=-1. (x=-1,y=-1,z=-1)=BDL. -Y->-Z=B. BDL on B: B[6]=(y=-1,x=-1)=BDL. D[6]->B[6].
# D[0,3,6]->B[0,3,6]. Same. ✓
# So in the cycle with idx_D=[6,3,0] as destination (D reads from F at these positions), the D stickers stored at D[6], D[3], D[0] (in that order) then flow to B.
# B[idx_B[j]] = D[idx_D[j]] (the SAME list). So B[6]=D[6], B[3]=D[3], B[0]=D[0]. That means B gets D's values at same positions. B[0]=D[0], B[6]=D[6]. ✓ consistent with D[0]->B[0].
# So idx_B should match the SINK indices of D, which are the same as D's idx_D=[6,3,0]? NO!
# The algorithm: B[idx_B[j]] = D[idx_D[j]]. The "source" values are D[idx_D[j]] = D's stickers at positions idx_D[j].
# If idx_D=[6,3,0]: B[idx_B[0]]=D[6], B[idx_B[1]]=D[3], B[idx_B[2]]=D[0].
# We need D[6]->B[6]: B[idx_B[0]]=D[6] means idx_B[0]=6. B[6]=D[6]. ✓
# idx_B[1]=3. idx_B[2]=0. idx_B=[6,3,0]. Same as idx_D!
# So B also uses [6,3,0]? But we need D[0,3,6]->B[0,3,6] (same order, same indices):
# D[0]->B[0]: D[idx_D[j]]=D[0] at j=2 (since idx_D=[6,3,0], position 2 has value 0). B[idx_B[2]]=D[0]: idx_B[2]=0. ✓
# So it all works out: idx_D=[6,3,0] and idx_B=[6,3,0].
# But code has idx_D=[0,3,6] and idx_B=[8,5,2] (a completely different set!).
# Something is very wrong with the code's L cycle.

# Let me just compute the correct L cycle from scratch using the mapping I derived:
# F[0,3,6] -> D[6,3,0] -> B[6,3,0] -> U[?] -> F[0,3,6]
# B[6]->U[?]: B[6]=(y=-1,x=-1,z=-1)=BDL. L CW: (y=-1,z=-1)->(+1,-1). (x=-1,y=+1,z=-1)=BUL. -Z direction: (0,-1)->(+1,0)=+Y=U. BUL on U: U[0]=(x=-1,z=-1)=BUL. B[6]->U[0].
# B[0]=(y=+1,x=-1,z=-1)=BUL. (y=+1,z=-1)->(-(-1),+1)=(+1,+1). (x=-1,y=+1,z=+1)=FUL. -Z->+Y=U. U[6]=(x=-1,z=+1)=FUL. B[0]->U[6].
# B[6,3,0]->U[0,3,6]. So B gives to U at indices [0,3,6].
# U[0,3,6]->F[?]: U[0]=(x=-1,z=-1,y=+1)=BUL. L CW: (y=+1,z=-1)->(+1,+1). (x=-1,y=+1,z=+1)=FUL. +Y->+Z=F. F[0]=(y=+1,x=-1)=FUL. U[0]->F[0]. ✓
# U[6]=(x=-1,z=+1,y=+1)=FUL. (y=+1,z=+1)->(-1,+1). (x=-1,y=-1,z=+1)=FDL. +Y->+Z=F. F[6]=(y=-1,x=-1)=FDL. U[6]->F[6].
# U[0,3,6]->F[0,3,6]. Same.
#
# Complete mapping:
# Cycle [F,D,B,U] right-shift: F[j]->D, D->B, B->U, U->F.
# idx_F=[0,3,6]: F stickers at 0,3,6 flow.
# idx_D=[6,3,0]: F[0]->D[6], F[3]->D[3], F[6]->D[0]. (D receives at [6,3,0])
# idx_B=[6,3,0]: D[6]->B[6], D[3]->B[3], D[0]->B[0]. Wait, D reads from D[idx_D[j]]=D[6,3,0], so B[idx_B[j]]=D[6,3,0]. B[6]=D[6], B[3]=D[3], B[0]=D[0]. ✓
# idx_U=[0,3,6]: B[6]->U[0], B[3]->U[3], B[0]->U[6]. (U receives at [0,3,6])
# B sends B[idx_B[j]]=B[6,3,0] to U[idx_U[j]]=U[0,3,6]. B[6]->U[0], B[0]->U[6]. ✓
# U sends U[idx_U[j]]=U[0,3,6] to F[idx_F[j]]=F[0,3,6]. U[0]->F[0], U[6]->F[6]. ✓
#
# CORRECT L cycle: [('F',[0,3,6]), ('D',[6,3,0]), ('B',[6,3,0]), ('U',[0,3,6])]
# CODE L cycle: [('F',[0,3,6]), ('D',[0,3,6]), ('B',[8,5,2]), ('U',[0,3,6])]
# Differences: D should be [6,3,0] not [0,3,6], B should be [6,3,0] not [8,5,2].

print("CORRECT L cycle: [('F',[0,3,6]), ('D',[6,3,0]), ('B',[6,3,0]), ('U',[0,3,6])]")
print()

# Now derive B cycle:
# B CW (viewed from behind, looking in +Z direction): right=+X, up=+Y (standard).
# Looking in +Z direction (you face away from cube, toward B face):
# Actually: when you look at B from OUTSIDE the cube, you look in +Z direction (from z=-inf toward z=0).
# Right = +X. CW rotation: +X->-Y->-X->+Y->+X.
# (x,y) plane: +X=(1,0)->(0,-1)=-Y. Transformation: (x,y)->(y,-x)? Wait: (1,0)->(0,-1). new_x=y=0,new_y=-x=-1. Hmm: new_x=0=y_old, new_y=-1=-x_old. But y_old=0, so new_x=y=0. But we need new_x=0 for +X sticker. Actually for direction (1,0): new_x=new direction_x=y=0, new_y=-x=-1. This gives (0,-1)=-Y. ✓ For direction (0,1)=+Y: new_x=y=1, new_y=-x=0. (+X)=+X. ✓ Transformation: direction (x,y) -> (y,-x). Wait: (y,-x): for (1,0): (0,-1). ✓
# B CW pieces at z=-1: (x,y) -> (y,-x).
#
# B's adjacent faces and edges:
# B is adjacent to U (U's back row = U[0,1,2] at z=-1,y=+1), L (L's left col = L[0,3,6] at z=-1,x=-1), D (D's back row = D[0,1,2] at z=-1,y=-1), R (R's right col... wait).
# R's right column as stored: R[2]=(y=+1,z=+1), R[5]=(y=0,z=+1), R[8]=(y=-1,z=+1). These are z=+1, NOT z=-1. R's LEFT column = R[0]=(y=+1,z=-1), R[3]=(y=0,z=-1), R[6]=(y=-1,z=-1). These are z=-1 = adjacent to B. So B is adjacent to R's LEFT column [R[0,3,6]].
# Similarly: L's right column = L[2]=(y=+1,z=+1), etc. L[2] is z=+1, not adjacent to B. L's left column = L[0]=(y=+1,z=-1), L[3]=(y=0,z=-1), L[6]=(y=-1,z=-1). Adjacent to B = L[0,3,6].
# Wait that's the same as U-adjacent L column? For U, L[0,3,6] was the BACK column...
# Actually L[0]=(y=+1,z=-1)=BUL: both adjacent to U and adjacent to B. It's a corner piece.
#
# B CW sticker flow: U back row -> ? Let's compute.
# U[0]=(x=-1,z=-1,y=+1)=BUL. B CW: (x=-1,y=+1)->(y=+1,-x=+1)=(new_x=+1,new_y=+1). Position:(x=+1,y=+1,z=-1)=BUR. +Y direction (U sticker): (0,1) in (x,y) -> (1,0)=+X=R face. BUR on R: R[0]=(y=+1,z=-1,x=+1)=BUR. U[0]->R[0]. Wait with new R layout R[0]=FUR? I said R[0]=(y=+1,z=+1). But BUR=(y=+1,z=-1). These are DIFFERENT!
# I'm confused about R layout again. Let me recheck.
# I established: looking at R from outside (+X direction, with front cube at your left): left=+Z (front), right=-Z (back). R[0]=top-left=(y=+1,+Z)=(y=+1,z=+1)=FUR. R[2]=top-right=(y=+1,-Z)=(y=+1,z=-1)=BUR.
# So R[0]=FUR and R[2]=BUR. BUR = R[2].
# U[0]->R[2] (not R[0]).
#
# U[0,1,2] -> R[2,1,0] (top row of U, going L to R = BUL,BUM,BUR, going to R face, BUR=R[2], BUM=R[1]?, BUL=R[0]?).
# U[2]=(x=+1,z=-1,y=+1)=BUR. B CW: (x=+1,y=+1)->(+1,-1). (new_x=+1,new_y=-1). Position:(x=+1,y=-1,z=-1)=BDR. +Y direction:(0,1)->(1,0)=+X=R. BDR on R: R[8]=(y=-1,z=-1,x=+1)? R[6]=(y=-1,z=+1)=FDR, R[8]=(y=-1,z=-1)=BDR. R[8]=BDR. U[2]->R[8]. Reversed again (U[0]->R[2], U[2]->R[8]).
# U[0,1,2]->R[2,1,8]? U[1]=(x=0,z=-1,y=+1)=BUM. (x=0,y=+1)->(1,0)=(new_x=1,new_y=0). (x=+1,y=0,z=-1). R[5]=(y=0,z=-1)? R[3]=(y=0,z=+1)=FMR, R[5]=(y=0,z=-1)=BMR. U[1]->R[5].
# U[0,1,2]->R[2,5,8]. Same indices as I computed for the R cycle! ✓
# So U's back row [0,1,2] goes to R's right column [2,5,8]... wait R[2]=BUR, R[5]=BMR, R[8]=BDR: these are the BACK column of R face (z=-1 side). But earlier for R cycle I said the sticker indices were [2,5,8] for F->U->B->D. Let me re-examine.
#
# For R cycle: F[2,5,8] (F right col at z=+1, i.e., F[2]=(x=+1,y=+1,z=+1)=FUR).
# F[2]->U[2] (we established). U[2]=(x=+1,z=-1,y=+1)=BUR.
# U[2]->B[8]. B[8]=(y=-1,x=+1)=BDR. After R CW: U[2]=(y=+1,z=-1). (y,z)->(z,-y): (-1,-1). (x=+1,y=-1,z=-1)=BDR. ✓
# So U[2,5,8]->B[8,5,2]. (I verified this before.)
#
# Now back to B CW. B's adjacent R edge = R[0,3,6]? Or R[2,5,8]?
# B is adjacent to R at z=-1. R stickers at z=-1: R[2]=(y=+1,z=-1)=BUR, R[5]=(y=0,z=-1)=BMR, R[8]... wait R[8]=(y=-1,z=-1)? Let me recheck: I said R[6]=(y=-1,z=+1)=FDR, R[8]=(y=-1,z=-1)=BDR? Let me reverify.
# R face layout (looking +X direction, with right=+Z): R[0]=top-left=(y=+1,z=+1)=FUR... WAIT.
# Earlier I just derived R[0]=FUR=(y=+1,z=+1) vs my old derivation of R[0]=(y=+1,z=-1)=BUR.
# I used two contradictory conventions for R. Let me settle this once and for all.
# "Looking at R face from outside" = standing at +X, looking toward -X. The F face of the cube (+Z) appears where?
# If you're at +X looking toward -X (toward the cube), the front of the cube (+Z) is to your LEFT (if you have standard orientation with up=+Y). Actually: facing -X direction, with +Y up:
# Your LEFT is +Z (front of cube), your RIGHT is -Z (back of cube).
# So: left = +Z, right = -Z. R[0]=top-left=(+Y,+Z)=(y=+1,z=+1)=FUR? Or (y=+1,-Z)=(y=+1,z=-1)=BUR?
# Top-left: top=+Y ✓, left=+Z. So top-left=(+Y,+Z)=(y=+1,z=+1,x=+1)=FUR.
# WAIT but when looking in -X direction, is your left +Z or -Z?
# If you face -X (toward the cube from the right side), your right arm would point toward -Z (back of cube) naturally if you're in WCA solving position.
# Actually in WCA, when looking at R face, R face's top is U, and R face's left is F side (front of cube). So R[0]=top-left is adjacent to both U and F = FUR corner.
# So R[0]=FUR=(x=+1,y=+1,z=+1). ✓ My recent derivation.
# Therefore: R[2]=(y=+1,z=-1,x=+1)=BUR, R[6]=(y=-1,z=+1,x=+1)=FDR, R[8]=(y=-1,z=-1,x=+1)=BDR.
# R stickers at z=-1 (adjacent to B): R[2]=BUR, R[5]=BMR, R[8]=BDR = R[2,5,8].
# But wait, these are the SAME indices I got for the R cycle (U->B->D mappings all use 2,5,8 for R). Consistent!

# Now the B CW cycle:
# U[0,1,2] -> R[2,1,8]? No: U[0]->R[2], U[1]->R[5]?, U[2]->R[8]. So U[0,1,2]->R[2,5,8]. (just with different j ordering)
# Wait: U[0]->R[2], U[1]->R[5], U[2]->R[8]. In the right-shift for [U,R,D,L] or whatever B cycle order:
# If cycle for B is [U,R,D,L] with right-shift: U gets from L, R gets from U, D gets from R, L gets from D. Flow: L->U->R->D->L. For B CW, need U->R->D->L->U? Let me compute all:
# After U: U[0,1,2] goes to R. U[0]->R[2]: sticker at U[0] moves to R[2].
# R[2,5,8] (z=-1 col of R) goes to D: R[2]=(y=+1,z=-1,x=+1)=BUR. B CW: (x=+1,y=+1)->(1,-1). (x=+1... wait B CW is (x,y)->(y,-x) at z=-1 plane. (x=+1,y=+1)->(new_x=y=+1,new_y=-x=-1)=(new_x=+1,new_y=-1). Position:(x=+1,y=-1,z=-1)=BDR. +X direction:(1,0)->(0,-1)=-Y=D. BDR on D: D[2]=(x=+1,z=-1)=BDR. R[2]->D[2].
# R[8]=(y=-1,z=-1,x=+1)=BDR. (x=+1,y=-1)->(-1,-1). (x=-1,y=-1,z=-1)=BDL. +X->-Y=D. BDL on D: D[0]=(x=-1,z=-1)=BDL. R[8]->D[0].
# R[5]=(y=0,z=-1,x=+1). (x=+1,y=0)->(0,-1). D. (x=-1? Let me recompute: new_x=y=0, new_y=-x=-1). (x=0,y=-1,z=-1). D[1]=(x=0,z=-1)? Let me check D layout: D[0]=(x=-1,z=-1), D[1]=(x=0,z=-1), D[2]=(x=+1,z=-1). So D[1]=(x=0,z=-1,y=-1). R[5]->D[1].
# R[2,5,8]->D[2,1,0]. Reversed.
# D[2,1,0]->L: D[2]=(x=+1,z=-1,y=-1)=BDR. (x=+1,y=-1)->(-1,-1). (x=-1,y=-1,z=-1)=BDL. -Y direction:(-1,0)->(0,+1)=+Y? Wait: (x,y)->direction transform: -Y direction=(0,-1) in (x,y): new_x=y=-1, new_y=-x=0. (new_x=-1,new_y=0). -X=-X direction=L face. BDL on L: L[6]=(y=-1,z=-1)=BDL. D[2]->L[6]. (L[6]=(y=-1,z=-1)?)
# Wait: L face layout. I established L[0]=(y=+1,z=-1)=BUL, L[2]=(y=+1,z=+1)=FUL, L[6]=(y=-1,z=-1)=BDL, L[8]=(y=-1,z=+1)=FDL.
# D[2]=(x=+1,z=-1,y=-1)=BDR. After B CW, it goes to (x=-1,y=-1,z=-1)=BDL. -Y direction -> -X=L face. BDL on L: L[6]=(y=-1,z=-1)=BDL. D[2]->L[6].
# D[0]=(x=-1,z=-1,y=-1)=BDL. (x=-1,y=-1)->(-1,+1). (x=-1,y=+1,z=-1)=BUL. -Y->-X=L. BUL on L: L[0]=(y=+1,z=-1)=BUL. D[0]->L[0].
# D[1]->L[3]. D[2,1,0]->L[6,3,0]. Hmm: D[2]->L[6], D[1]->L[3], D[0]->L[0]. So D[2,1,0]->L[6,3,0]. = same reversed indices.
# L[6,3,0]->U: L[6]=(y=-1,z=-1,x=-1)=BDL. (x=-1,y=-1)->(new_x=-1,new_y=+1). (x=-1,y=+1,z=-1)=BUL. -X direction:(-1,0)->(0,+1)=+Y=U. BUL on U: U[0]=(x=-1,z=-1)=BUL. L[6]->U[0].
# L[0]=(y=+1,z=-1,x=-1)=BUL. (x=-1,y=+1)->(+1,+1). (x=+1,y=+1,z=-1)=BUR. -X->+Y=U. BUR on U: U[2]=(x=+1,z=-1)=BUR. L[0]->U[2].
# L[3]->U[1]. L[6,3,0]->U[0,1,2] (reversed: L[6]->U[0], L[0]->U[2]). Wait: L[6,3,0] means L[6] then L[3] then L[0]. They go to U[0],U[1],U[2]. So L[6]->U[0], L[3]->U[1], L[0]->U[2]. This is L[6,3,0]->U[0,1,2]. Reversed (L's indices are reversed but they map to U in order).
#
# Summary for B CW:
# U[0,1,2] -> R[2,5,8] (U's back row goes to R's back column, but reversed in index: U[0]->R[2], U[2]->R[8] = same index direction)
# R[2,5,8] -> D[2,1,0] (R's back col goes to D's back row, reversed: R[2]->D[2], R[8]->D[0])
# D[2,1,0] -> L[6,3,0] (D's back row reversed goes to L's... wait: D[2]->L[6], D[0]->L[0]... these are different!)
# Actually: D[2,1,0] means D[2] first, D[1] second, D[0] third. They go to L[6],L[3],L[0] respectively.
# So in flow order: D[2]->L[6], D[1]->L[3], D[0]->L[0]. The D indices decrease, L indices decrease too: both reversed. Effectively same index mapping in reverse order.
# L[6,3,0] -> U[0,1,2] (L's back col reversed goes to U's back row in order).
#
# For B cycle right-shift on list [?, ?, ?, ?]:
# Sticker flow: U->R->D->L->U.
# Right-shift: face[k] gets from face[k-1].
# For flow U->R: R gets from U. Order in list: U before R. [U, R, ...]
# For R->D: D gets from R. R before D. [U, R, D, ...]
# For D->L: L gets from D. D before L. [U, R, D, L]. ✓
# And L->U: U gets from L. Cyclic: U is at k=0, L is at k-1=3. ✓
# So B CW cycle list order: [U, R, D, L].
#
# Index lists (right-shift: R[idx_R[j]] = U[idx_U[j]]):
# U[0]->R[2]: idx_R[0]=2, idx_U[0]=0. U[1]->R[5]: idx_R[1]=5. U[2]->R[8]: idx_R[2]=8. idx_U=[0,1,2], idx_R=[2,5,8].
# R[2]->D[2]: D[idx_D[j]]=R[idx_R[j]]. R[2]=D[?]: D[idx_D[0]]=R[2]. R[idx_R[0]]=R[2] (idx_R[0]=2). So idx_D[0]=2. R[5]->D[1]: idx_D[1]=1. R[8]->D[0]: idx_D[2]=0. idx_D=[2,1,0].
# D[2]->L[6]: L[idx_L[j]]=D[idx_D[j]]. D[idx_D[0]]=D[2] -> L[idx_L[0]]=L[6]: idx_L[0]=6. D[1]->L[3]: idx_L[1]=3. D[0]->L[0]: idx_L[2]=0. idx_L=[6,3,0].
# L[6]->U[0]: U[idx_U[j]]=L[idx_L[j]]. L[idx_L[0]]=L[6] -> U[idx_U[0]]: idx_U[0]=0 ✓. L[3]->U[1] ✓. L[0]->U[2] ✓.
#
# CORRECT B cycle: [('U',[0,1,2]), ('R',[2,5,8]), ('D',[2,1,0]), ('L',[6,3,0])]
# CODE B cycle:    [('D',[6,7,8]), ('R',[8,5,2]), ('U',[2,1,0]), ('L',[0,3,6])]
# COMPLETELY DIFFERENT order and indices!
print("CORRECT B cycle: [('U',[0,1,2]), ('R',[2,5,8]), ('D',[2,1,0]), ('L',[6,3,0])]")
print()

# Now test ALL correct cycles:
new_cycles = {
    'U': ('U', [('F',[0,1,2]),('R',[2,1,0]),('B',[2,1,0]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[8,7,6]),('R',[8,7,6])]),
    'F': ('F', [('U',[6,7,8]),('R',[2,5,8]),('D',[8,7,6]),('L',[8,5,2])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[8,5,2]),('D',[8,5,2])]),
    'B': ('B', [('U',[0,1,2]),('R',[2,5,8]),('D',[2,1,0]),('L',[6,3,0])]),
    'L': ('L', [('F',[0,3,6]),('D',[6,3,0]),('B',[6,3,0]),('U',[0,3,6])]),
}

print("Testing ALL corrected cycles:")
print("R U R' U' x6:", find_order(new_cycles, "R U R' U'"), "(expected 6)")
print("T-perm x2:", find_order(new_cycles, "R U R' U' R' F R2 U' R' U' R U R' F'"), "(expected 2)")
print("Sune x8:", find_order(new_cycles, "R U R' U R U2 R'"), "(expected 8)")
print("F-perm x2:", find_order(new_cycles, "R' U' F' R U R' U' R' F R2 U' R' U' R U R' U R"), "(expected 2)")

# Also test single moves are still correct
for m in ['U','D','F','B','R','L']:
    ct = CubeTest(new_cycles)
    for _ in range(4): ct.apply(m)
    print(f"{m}x4: {'OK' if ct.is_solved() else 'FAIL'}")
    ct2 = CubeTest(new_cycles)
    ct2.apply(m + " " + m + "'")
    print(f"{m} {m}': {'OK' if ct2.is_solved() else 'FAIL'}")
