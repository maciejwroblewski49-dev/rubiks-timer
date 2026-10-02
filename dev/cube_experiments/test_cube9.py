# Let me think about this differently.
# The current code has ONE sticker index per face-cycle entry, used for both read and write.
# The algorithm: face[k][idx[j]] = face[k-1][idx[j]] -- using the SAME idx for both.
# This means: the sticker at position idx[j] on face[k-1] moves to position idx[j] on face[k].
#
# For this to work correctly, we need: for each pair of adjacent faces in the cycle,
# the "corresponding" sticker positions have the same index.
#
# Let me think about what "corresponding" means:
# For F CW cycle [U[6,7,8], R[0,3,6], D[2,1,0], L[8,5,2]]:
# Position 0 corresponds to: U[6], R[0], D[2], L[8].
# These should all be in the same physical location (same corner/edge piece).
# U[6] is the bottom-left of U (in U's view) = front-left corner = (x=-1, y=+1, z=+1).
# R[0] is the top-left of R = back-top corner = (x=+1, y=+1, z=-1).
# D[2] is the top-right of D = front-right-ish.
# L[8] is the bottom-right of L = ...
# These are ALL DIFFERENT 3D positions! That's wrong for a single move affecting a 2D slice.
#
# Wait, no. In a FACE move (like F), the stickers DON'T all move to the "same piece".
# The sticker at U[6] (bottom-left of U, at FUL corner) moves to R[0] (top-left of R, at BUR corner)?
# That can't be right for an F move. F move only affects the front slice (z=+1 layer in my convention).
# FUL corner = (x=-1, y=+1, z=+1). After F CW: piece at FUL goes to FUR.
# FUR on R face = R[2] = (y=+1, z=+1, x=+1). So U[6] should go to R[2], not R[0]!
#
# But the code has U[6] going to R[0]. That seems wrong!
# Let me check: position 0 in F cycle = U[6] and R[0].
# With right-shift: R[0] gets from U[6]. So U[6] moves to R[0]. But physically:
# U[6] = (x=-1, y=+1, z=+1) = FUL corner's U sticker.
# After F CW: FUL piece goes to FUR. FUR's R sticker = R[2] = (y=+1, z=+1).
# But code puts it at R[0] = (y=+1, z=-1) = BUR corner. WRONG.
#
# So the F cycle also has a bug? But F*4 = solved... hmm.
# Oh wait: IF the index is wrong, but the SAME wrong index is used consistently for all 4 faces,
# then F*4 would still be solved (because the 4 cyclic applications restore original state).
# And F' would also work. But F combined with U would reveal the mismatch.
#
# Let me trace F cycle more carefully:
# Position 0: U[6]->R[0], R[0]->D[2], D[2]->L[8], L[8]->U[6].
# Are U[6], R[0], D[2], L[8] all at the same physical location? They shouldn't be for a face move.
# For F CW (moving z=+1 slice): U[6] is at FUL (z=+1, front slice) ✓
# R[0] is at BUR (z=-1). NOT in front slice! WRONG.
# This confirms the F cycle is wrong.
#
# Let me find the CORRECT F cycle:
# F CW moves the z=+1 slice. Stickers that move:
# - F face itself (rotates CW)
# - Bottom row of U face: U[6,7,8] (y=+1, z=+1) ✓
# - Left column of R face: R[?] at (x=+1, z=+1) = R's right column (z=+1 side).
#   R face layout: R[0]=(y=+1,z=-1), R[2]=(y=+1,z=+1), R[8]=(y=-1,z=+1).
#   R's right column (z=+1) = R[2,5,8].
# - Top row of D face: D[?] at (y=-1, z=+1) = D's bottom row in D's view.
#   D[6]=(x=-1,z=+1), D[7]=(x=0,z=+1), D[8]=(x=+1,z=+1). D[6,7,8].
# - Right column of L face: L[?] at (x=-1, z=+1) = L's right column.
#   L[2]=(y=+1,z=+1), L[5]=(y=0,z=+1), L[8]=(y=-1,z=+1). L[2,5,8].
#
# F CW sticker flow (from above, +Z direction): stickers flow upward-CW:
# U bottom -> R right -> D top -> L right -> U bottom (which direction for each?)
#
# F CW (looking at F from front, +Z direction): CW means:
# (x,y) -> (y,-x) for the stickers at z=+1 level.
# - U[6]=(x=-1,z=+1): on U face (+Y). After F CW: (x=-1,y=+1)->(new_x=y=+1,new_y=-x=+1).
#   Actually F CW rotates: (+1,0) -> (0,-1) in x,y? Let me recompute.
#   F CW (viewed from +Z, looking -Z): CW = right->down->left->up.
#   Looking in -Z direction: right=+X, up=+Y.
#   Wait: looking in the direction of -Z (at F from front), your right = -X? No.
#   You stand outside the cube at +Z and look toward -Z direction.
#   Facing -Z, right = +X (your natural right). Wait:
#   facing = -Z = (0,0,-1). up = Y = (0,1,0).
#   right = up x forward = Y x (-Z) = (0,1,0)x(0,0,-1) = (1*(-1)-0*0, 0*0-0*(-1), 0*0-1*0) = (-1,0,0)=-X.
#   Hmm, right=-X again. That means right is -X. Left is +X.
#   CW in view: right(+X if standard, but right=-X here)...
#   OK I'll just say: looking at F from outside, the right side of the cube (+X) appears to your left, and -X appears to your right.
#   But by convention, F face left-to-right: F[0]=top-left in YOUR view from outside = top at +X side? Or top at -X?
#   Standard: F[0]=top-left as viewed from outside = +Y and the left side of the face.
#   The "left side of F from outside" = +X direction? Or -X?
#   In WCA standard, the scrambles are given from the solver's perspective (looking at F face).
#   F face left side = solver's right hand side = depends on conventions.
#   Actually: looking at the cube with F face toward you, R is to your RIGHT.
#   F face's right side = R side = +X direction.
#   So F face: right = +X, top = +Y. F[0]=top-left=(-X,+Y)=(x=-1,y=+1). F[2]=top-right=(+X,+Y)=(x=+1,y=+1).
#   And F CW (as solver sees it, looking at F): right->down->left->up:
#   +X -> -Y -> -X -> +Y -> +X. Transformation: (x,y)->(y,-x).
#   Check: +X=(1,0)->(0,-1)=-Y. +X goes down. CW ✓.
#
#   F CW transformation: (x,y) -> (y,-x) for pieces at z=+1.
#   U[6]=(x=-1,y=+1,z=+1). After F CW: (x=-1,y=+1)->(y=+1,-x=+1)=(new_x=+1,new_y=+1). Position:(x=+1,y=+1,z=+1)=FUR.
#   U-sticker (+Y) transforms: (x,y)=(0,1) for +Y direction -> (new_x=1, new_y=0) = +X = R face.
#   FUR on R face: R[2]=(y=+1,z=+1,x=+1).
#   U[6] -> R[2]. ✓
#
#   U[7]=(x=0,y=+1,z=+1). After CW: (0,1)->(1,0). Position:(1,1,+1)? x=1,y=1 is still +Y and +X: corner? No: y=1 and x=0 after transformation. (x=0,y=+1)->(y=+1,-x=0)=(1,0). Position: x=+1? That's (x=+1,y=0,z=+1)=FMR (front-middle-right). On R face: R[5]=(y=0,z=+1,x=+1). U[7]->R[5]. ✓
#
#   U[8]=(x=+1,y=+1,z=+1). After CW: (1,1)->(1,-1). Position:(x=+1,y=-1,z=+1)=FDR. On R face: R[8]=(y=-1,z=+1,x=+1). U[8]->R[8]? Wait: (x=+1,y=+1)->(y=+1,-x=-1)=(new_x=+1,new_y=-1). Position:(x=+1,y=-1,z=+1)=FDR. On R face: R[8]=(y=-1,z=+1). ✓. U[8]->R[8].
#
# So U[6,7,8]->R[2,5,8]. Code has U->R at the same positions, but mapped to R[0,3,6] instead of R[2,5,8].
# U[6]->R[0] (code) but U[6]->R[2] (correct). CONFIRMED BUG IN F CYCLE.
#
# Correct F cycle:
# U[6,7,8] -> R[2,5,8] (right column of R, top to bottom)
# R[2,5,8] -> D[?]:
#   R[2]=(y=+1,z=+1,x=+1)=FUR. After F CW: (+x=+1,+y=+1)->(+1,-1). (new_x=+1,new_y=-1)=FDR. On D face: D[8]=(x=+1,z=+1,y=-1). FDR=(x=+1,y=-1,z=+1)=D[8]. R[2]->D[8].
#   R[8]=(y=-1,z=+1,x=+1)=FDR. After CW: (-1,+1)->(+1,+1)? (x=+1,y=-1)->(y=-1,-x=-1). (new_x=-1,new_y=-1). Position:(x=-1,y=-1,z=+1)=FDL. +X direction ->(new_x=y=-1,new_y=-x=-1)?? Hmm.
#   +X direction = (1,0) in (x,y). After (y,-x): (0,-1) = -Y = D face. FDL on D face: D[6]=(x=-1,z=+1,y=-1). R[8]->D[6].
#   R[5]=(y=0,z=+1,x=+1). (x=+1,y=0)->(0,-1)=-Y. D face. Position: (x=0,y=-1,z=+1)=FDM. D[7]=(x=0,z=+1). R[5]->D[7].
# R[2,5,8]->D[8,7,6]=D[8,7,6]=reversed D bottom row.
# But D[6,7,8] is D's bottom row going D[6](FDL)-D[7](FDM)-D[8](FDR). Reversed = D[8,7,6].
#
# D[8,7,6] -> L[?]:
#   D[8]=(x=+1,y=-1,z=+1)=FDR. After F CW: (x=+1,y=-1)->(-1,-1). (new_x=-1,new_y=-1). Position:(x=-1,y=-1,z=+1)=FDL.
#   -Y direction: (0,-1) in (x,y) -> (-1,0)=-X = L face. FDL on L face: L[8]=(y=-1,z=+1,x=-1). D[8]->L[8].
#   D[6]=(x=-1,y=-1,z=+1)=FDL. (x=-1,y=-1)->(-1,+1). Position:(x=-1,y=+1,z=+1)=FUL. -Y direction->-X=L. FUL on L: L[2]=(y=+1,z=+1,x=-1). D[6]->L[2].
#   D[7]->L[5].
# D[8,7,6]->L[8,7,2]? D[8]->L[8], D[7]->L[7]? Let me check D[7]:
#   D[7]=(x=0,y=-1,z=+1). (0,-1)->(-1,0). Position:(x=-1,y=0,z=+1)=FML. -Y->-X=L. FML on L: L[5]=(y=0,z=+1,x=-1). D[7]->L[5].
# D[8,7,6]->L[8,5,2]. So same indices just different order: D[8]->L[8], D[7]->L[5], D[6]->L[2].
# = L[8,7?,2] but: D[8]->L[8], D[7]->L[5], D[6]->L[2]. So D[8,7,6]->L[8,5,2].
#
# L[8,5,2] -> U[?]:
#   L[8]=(y=-1,z=+1,x=-1)=FDL. After F CW: (x=-1,y=-1)->(-1,+1). Position: (x=-1,y=+1,z=+1)=FUL.
#   -X direction: (-1,0) in (x,y) -> (0,+1) = +Y = U face. FUL on U: U[6]=(x=-1,z=+1,y=+1). L[8]->U[6]. ✓
#   L[2]=(y=+1,z=+1,x=-1)=FUL. (x=-1,y=+1)->(+1,+1)? Hmm. (x=-1,y=+1)->(y=+1,-x=+1)=(+1,+1). Position:(x=+1,y=+1,z=+1)=FUR. -X direction -> +Y. FUR on U: U[8]=(x=+1,z=+1,y=+1). L[2]->U[8]. ✓
#   L[5]=(y=0,z=+1,x=-1). (x=-1,y=0)->(0,+1). Position:(x=0,y=+1,z=+1). U[7]=(x=0,z=+1). L[5]->U[7]. ✓
# L[8,5,2]->U[6,7,8]. ✓
#
# So CORRECT F cycle:
# U[6,7,8] -> R[2,5,8] -> D[8,7,6] -> L[8,5,2] -> U[6,7,8]
# Code has: U[6,7,8] -> R[0,3,6] -> D[2,1,0] -> L[8,5,2] -> U[6,7,8]
# DIFFERENCES:
# U->R: code uses R[0,3,6], correct is R[2,5,8]. R's LEFT column vs RIGHT column!
# R->D: code uses D[2,1,0], correct is D[8,7,6]. D's front-row REVERSED.
# Wait: D[8,7,6] vs D[2,1,0]: completely different indices, not just reversed!
# Actually: D[2]=(x=+1,z=-1), D[8]=(x=+1,z=+1). Very different. This is major bug.
# L->U: both use L[8,5,2] and U[6,7,8]. These match ✓. (code has this right!)
# D->L: code uses L[8,5,2]. Correct L indices = L[8,5,2] too? Let's check.
# D[8,7,6]->L[8,5,2]: same indices as code's D[2,1,0]->L[8,5,2]? No: the SOURCE face changes (D[8] vs D[2]).
# But with right-shift: L gets from D at same positions. L[8]=D[?].
# Code: L[8]=D[2]. Correct: L[8]=D[8].
# So the ONLY correct part is L[8,5,2]->U[6,7,8].
#
# MAJOR BUG FOUND IN F CYCLE:
# Code: [U[6,7,8], R[0,3,6], D[2,1,0], L[8,5,2]]
# Correct: [U[6,7,8], R[2,5,8], D[8,7,6], L[8,5,2]]  ???
# Wait let me re-derive using right-shift:
# For F CW, sticker flow: U->R->D->L->U.
# Right-shift means: face[k] gets from face[k-1]. So R gets from U, D gets from R, L gets from D, U gets from L.
# Cycle order is [U, R, D, L]. R gets from U, D gets from R, L gets from D, U gets from L.
# Sticker flow at position j: L[j]->U[j]->R[j]->D[j]->L[j].
#
# For correct mapping:
# U[6]->R[2]: R[2] gets U[6]. Position j in cycle: when k=R (k=1), face[1][idx[1][j]] = face[0][idx[0][j]].
# face[0]=U, face[1]=R: R[idx_R[j]] = U[idx_U[j]].
# R[2]=U[6]: idx_R[j]=2, idx_U[j]=6 for j=0. But idx_U=[6,7,8] so idx_U[0]=6 ✓. idx_R must have 2 as first element.
# U[7]->R[5]: idx_R[1]=5. U[8]->R[8]: idx_R[2]=8. So idx_R=[2,5,8].
# R[2]->D[8]: D[idx_D[0]] = R[idx_R[0]] = R[2]. But we need D[8]=R[2], so idx_D[0]=8.
# R[5]->D[7]: idx_D[1]=7. R[8]->D[6]: idx_D[2]=6. So idx_D=[8,7,6].
# D[8]->L[8]: L[idx_L[0]] = D[idx_D[0]] = D[8]. Need L[8]=D[8], so idx_L[0]=8. ✓ Same.
# D[7]->L[5]: idx_L[1]=5. D[6]->L[2]: idx_L[2]=2. idx_L=[8,5,2]. ✓ (same as code!)
# L[8]->U[6]: U[idx_U[j]] = L[idx_L[j]]. U[6]=L[8]: idx_U[0]=6 ✓ (matches idx_U=[6,7,8]).
# L[5]->U[7]: ✓. L[2]->U[8]: ✓.
#
# CORRECT F cycle: [('U',[6,7,8]), ('R',[2,5,8]), ('D',[8,7,6]), ('L',[8,5,2])]
# CODE cycle: [('U',[6,7,8]), ('R',[0,3,6]), ('D',[2,1,0]), ('L',[8,5,2])]
# DIFFERENCES: R uses [2,5,8] not [0,3,6], D uses [8,7,6] not [2,1,0]. L and U are correct.

print("CORRECT F cycle: [('U',[6,7,8]), ('R',[2,5,8]), ('D',[8,7,6]), ('L',[8,5,2])]")
print("CODE F cycle:    [('U',[6,7,8]), ('R',[0,3,6]), ('D',[2,1,0]), ('L',[8,5,2])]")

# Now let me derive correct U cycle (again):
# U CW: sticker flow... U face moves, and the top row of F->R->B->L.
# Top row of F: F[0,1,2] (as established).
# U[6,7,8] is adjacent to F's top row in 3D? No, U[6,7,8] is U's front row (adjacent to F).
# For U move, we need F's TOP ROW, not U's rows.
# F top row = F[0,1,2]. But F[0]=(x=-1,y=+1,z=+1)=FUL and this is in the U slice (y=+1).
# The U cycle affects the y=+1 layer (all face stickers at y=+1 level).
#
# For U CW, the TOP ROW of each side face:
# F top row: F[0,1,2] at y=+1.
# R top row: R[0,1,2] at y=+1.
# B top row: B[0,1,2] at y=+1.
# L top row: L[0,1,2] at y=+1.
#
# U CW sticker flow: F->R->B->L->F.
# F[0]=(x=-1,y=+1,z=+1)=FUL. After U CW transformation (x,z)->(z,-x): (-1,+1)->(+1,+1)=(x=+1,z=+1). This is on R face AND F face? It's FUR corner. It's on R face at R[2]=(y=+1,z=+1).
# +Z direction transforms: (0,+1) in (x,z) -> (+1,0) = +X = R face. F[0]->R[2]. ✓ (same as before)
#
# For U cycle with right-shift [F, R, B, L]: R gets from F, B gets from R, L gets from B, F gets from L.
# R[idx_R[j]] = F[idx_F[j]]. R[2]=F[0]: idx_R[0]=2, idx_F[0]=0. idx_F=[0,1,2], idx_R starts with 2.
# R[1]=F[1]: idx_R[1]=1. R[0]=F[2]: idx_R[2]=0. idx_R=[2,1,0].
# R[2]->B[?]: B[idx_B[j]] = R[idx_R[j]].
# R[2]=(y=+1,z=+1,x=+1)=FUR. U CW: (x=+1,z=+1)->(+1,-1). BUR=(x=+1,y=+1,z=-1).
# +X direction: (1,0) in (x,z) -> (0,-1) = -Z = B face. BUR on B face: B[2]=(y=+1,x=+1)?
# Wait: B face orientation: B[0]=top-left from outside (from behind). "behind" = from -Z direction? Or from +Z direction?
# Looking at B from outside = from -Z direction (looking toward +Z). Wait, B is the -Z face, so outside of B is at -Z.
# You stand at -Z looking toward +Z. right = ?
# facing = +Z = (0,0,1). up = +Y. right = up x forward = (0,1,0)x(0,0,1) = (1,0,0)=+X.
# So when looking at B from outside (-Z looking +Z): right = +X, top = +Y.
# B[0] = top-left in view = +Y and -X = (y=+1, x=-1, z=-1) = BUL.
# B[2] = top-right = +Y and +X = (y=+1, x=+1, z=-1) = BUR.
# B[6] = bottom-left = -Y and -X = (y=-1, x=-1, z=-1) = BDL.
# B[8] = bottom-right = -Y and +X = (y=-1, x=+1, z=-1) = BDR.
# So B[2]=BUR corner. ✓ R[2]->B[2]. idx_B[0]=2.
# R[1]->B[?]: R[1]=(y=+1,z=0,x=+1). U CW: (x=+1,z=0)->(0,-1)=(x=0,z=-1). +X->-Z.
# Position: (x=0,y=+1,z=-1). On B face: (y=+1,x=0)=B[1]. R[1]->B[1]. idx_B[1]=1.
# R[0]->B[?]: R[0]=(y=+1,z=-1,x=+1)=BUR. (x=+1,z=-1)->(-1,-1). Position:(x=-1,y=+1,z=-1)=BUL. B[0]=(y=+1,x=-1)=BUL. R[0]->B[0]. idx_B[2]=0. idx_B=[2,1,0].
#
# B[2,1,0]->L[?]: B[2]=(y=+1,x=+1,z=-1)=BUR. U CW: (x=+1,z=-1)->(-1,-1). BUL=(x=-1,y=+1,z=-1).
# -Z direction: (0,-1) in (x,z) -> (-1,0) = -X = L face. BUL on L: L[0]=(y=+1,z=-1)=BUL. B[2]->L[0].
# B[1]->L[1], B[0]->L[?]: B[0]=(y=+1,x=-1,z=-1)=BUL. (x=-1,z=-1)->(z=-1,x'=+1). new_x=z=-1,new_z=-x=+1. (x=-1,y=+1,z=+1)=FUL. -Z->-X=L. FUL on L: L[2]=(y=+1,z=+1)=FUL. B[0]->L[2]. So B[2,1,0]->L[0,1,2]. idx_L=[0,1,2].
#
# L[0,1,2]->F[?]: L[0]=(y=+1,z=-1,x=-1)=BUL. U CW: (x=-1,z=-1)->(-1,+1)=(new_x=-1,new_z=+1)=FUL. -X direction: (-1,0)->(0,+1)=+Z=F. FUL on F: F[0]=(y=+1,x=-1,z=+1)=FUL. L[0]->F[0]. ✓
# L[1]->F[1], L[2]->F[2]. idx_F=[0,1,2]. ✓ (matches our starting idx_F=[0,1,2])
#
# CORRECT U cycle: [('F',[0,1,2]), ('R',[2,1,0]), ('B',[2,1,0]), ('L',[0,1,2])]
# CODE U cycle: [('F',[0,1,2]), ('R',[0,1,2]), ('B',[0,1,2]), ('L',[0,1,2])]
# Differences: R and B use [2,1,0] not [0,1,2].

print("CORRECT U cycle: [('F',[0,1,2]), ('R',[2,1,0]), ('B',[2,1,0]), ('L',[0,1,2])]")
print()

# Let me now derive D cycle:
# D CW (viewed from below, looking +Y): transformation (x,z)->(-z,x) as computed earlier.
# Bottom row of each side face (y=-1 level):
# F bottom: F[6,7,8]: F[6]=(x=-1,y=-1,z=+1), F[8]=(x=+1,y=-1,z=+1).
# D CW sticker flow: looking at D from below, CW means stickers flow...
# From below looking +Y, right=+X, top=+Z (front of cube). CW: right->down->left->up = +X->-Z->-X->+Z.
# So stickers at D's +X region (right when viewed from below) go to -Z region.
# F bottom row is at z=+1 (front). After D CW, the +Z region goes to... +Z->-X? So F bottom goes to L.
# Wait: stickers on the F bottom (z=+1 face, y=-1 level). These are F-face stickers pointing +Z.
# After D CW: F[6] at (x=-1,z=+1): new_x=-z=-1, new_z=x=-1. Position:(x=-1,y=-1,z=-1)=BDL.
# +Z direction: (0,+1)->(0,... ) in (x,z): (x,z)->(-z,x): (0,+1)->(-1,0)=-X=L face.
# BDL on L: L[6]=(y=-1,z=-1)=BDL. F[6]->L[6]. (sticker goes from F bottom-left to L bottom-left)
# Sticker flow for D CW: F->L->B->R->F.
# So with right-shift on [F,L,B,R]: F gets from R, L gets from F, B gets from L, R gets from B.
# Sticker flow: F->L->B->R->F. ✓
#
# F[6]->L[6]: L[idx_L[0]]=F[idx_F[0]]. L[6]=F[6]: idx_L[0]=6, idx_F[0]=6.
# F[7]->L[7], F[8]->L[8]. idx_F=[6,7,8], idx_L=[6,7,8].
# L[6]->B[?]: L[6]=(y=-1,z=-1,x=-1)=BDL. D CW: (x=-1,z=-1)->(-(-1),-1)=(+1,-1)=BDR. -X->+Y? No:
# D CW: (x,z)->(-z,x). (x=-1,z=-1)->(-(-1),-1)=(+1,-1). Position:(x=+1,y=-1,z=-1)=BDR. Wait I made an error: new_x=-z=+1, new_z=x=-1. So (x=+1,y=-1,z=-1)=BDR.
# -X direction: (-1,0) in (x,z) -> (-z=0, x=-1) = (0,-1) = -Z = B face. BDR on B: B[8]=(y=-1,x=+1)=BDR. L[6]->B[8].
# L[8]=(y=-1,z=+1,x=-1)=FDL. (x=-1,z=+1)->(-1,-1). -X -> (0,-1)=-Z=B. Position (-1,-1) means (x=-1,y=-1,z=-1)? No: new_x=-z=-1, new_z=x=-1. (-1,-1). B face at z=-1: (y=-1,x=-1)=B[6]. FDL sticker is -X facing. Goes to (x=-1,y=-1,z=-1)=BDL. B[6]=(y=-1,x=-1)=BDL. L[8]->B[6].
# L[7]->B[7]. idx_B=[8,7,6] (reversed!). ✓ Same as I computed before.
#
# B[8,7,6]->R[?]: B[8]=(y=-1,x=+1,z=-1)=BDR. D CW: (x=+1,z=-1)->(+1,+1). Position:(x=+1,y=-1,z=+1)=FDR.
# -Z direction: (0,-1) in (x,z) -> (-(-1),0)=(+1,0)=+X=R. FDR on R: R[8]=(y=-1,z=+1)=FDR. B[8]->R[8].
# B[6]=(y=-1,x=-1,z=-1)=BDL. (x=-1,z=-1)->(+1,-1). FDL=(x=+1... wait: new_x=-z=+1, new_z=x=-1. So (x=+1,y=-1,z=-1)? That's BDR, not FDR. Wait: (x=-1,z=-1): new_x=-(-1)=+1, new_z=-1. (x=+1,y=-1,z=-1)=BDR? But that's wrong, BDR has x=+1,z=-1 ✓. R[6]=(y=-1,z=-1)=BDR. B[6]->R[6]. B[7]->R[7].
# idx_R=[8,7,6] (reversed!).
# R[8,7,6]->F[?]: R[8]=(y=-1,z=+1,x=+1)=FDR. D CW: (x=+1,z=+1)->(-1,+1). Position:(x=-1,y=-1,z=+1)=FDL. +X->+Z... wait: +X direction = (1,0) in (x,z): (x,z)->(-z,x): (1,0)->(-0,1)=(0,1)=+Z=F? But the piece went to x=-1 which is L face territory! Hmm.
# Actually: D CW moves pieces in the y=-1 plane. R[8] at (x=+1,y=-1,z=+1) moves to (-z=-1, x=+1)=(-1,+1)=(x=-1,z=+1). That's (x=-1,y=-1,z=+1)=FDL. The sticker direction +X: (1,0)->(0,1)=+Z=F face. FDL on F face: F[6]=(y=-1,x=-1)=FDL. R[8]->F[6].
# R[6]=(y=-1,z=-1,x=+1)=BDR. (x=+1,z=-1)->(+1,+1)=(x=+1... wait: new_x=-z=+1, new_z=x=+1. (x=+1,y=-1,z=+1)=FDR. +X direction -> +Z = F. FDR on F: F[8]=(y=-1,x=+1)=FDR. R[6]->F[8].
# idx_F=[6,7,8]. R[8,7,6]->F[6,7,8] ✓ (already verified L->B giving R the same result).
#
# CORRECT D cycle: [('F',[6,7,8]), ('L',[6,7,8]), ('B',[8,7,6]), ('R',[8,7,6])]
# CODE D cycle:    [('F',[6,7,8]), ('L',[6,7,8]), ('B',[6,7,8]), ('R',[6,7,8])]
# Differences: B and R use [8,7,6] not [6,7,8].

print("CORRECT D cycle: [('F',[6,7,8]), ('L',[6,7,8]), ('B',[8,7,6]), ('R',[8,7,6])]")
print()

# Now let me derive the correct R cycle:
# R CW (viewed from right, +X direction): looking -X direction. right=?
# facing=-X. up=+Y. right = up x forward... actually right = view_right.
# Using: right = up x facing_direction_inverted? Actually: right = forward x up = (-X) x (+Y)?
# forward = -X = (-1,0,0). right = forward x up = (-1,0,0)x(0,1,0) = (0*0-0*1, 0*(-1)-(-1)*0, (-1)*1-0*0) = (0,0,-1)=-Z.
# Hmm: right=-Z when looking -X. So left=+Z.
# Looking at R from outside: right=-Z (toward back of cube), left=+Z (toward front).
# R[0]=top-left=(y=+1,+Z)=(y=+1,z=+1,x=+1)=FUR. But earlier I computed R[0]=(y=+1,z=-1,x=+1)=BUR!
# There's a contradiction. Let me use the cross product formula more carefully.
#
# To look at R face from outside, you're at +X looking toward -X.
# In this scenario, let's say "up" in your view = +Y, and the cube's front face (+Z) appears on your left.
# Convention matters. WCA standard: when looking at R face from the right, the U face is on top, F face is to your left.
# So: top = +Y, left = +Z (front of cube is to your left when looking right).
# Therefore: right = -Z (toward back of cube), top = +Y.
# R[0] = top-left = (+Y, +Z) = (y=+1, z=+1, x=+1) = FUR.
# R[2] = top-right = (+Y, -Z) = (y=+1, z=-1, x=+1) = BUR.
# R[6] = bottom-left = (-Y, +Z) = (y=-1, z=+1, x=+1) = FDR.
# R[8] = bottom-right = (-Y, -Z) = (y=-1, z=-1, x=+1) = BDR.
#
# THIS CHANGES MY EARLIER ANALYSIS! R[0]=FUR, not BUR!
# So R[0,1,2] = top row of R = FUR, FUR_mid, BUR.
# R[0] = FUR = (x=+1,y=+1,z=+1).
#
# Now let me redo R move:
# R CW (viewed from right, right=+X): looking in -X direction with front (+Z) to your LEFT.
# CW rotation around +X axis: looking from +X, CW means (y,z) rotates CW.
# Looking in -X direction with right=-Z, up=+Y:
# CW: right->down->left->up = -Z->-Y->+Z->+Y->-Z.
# So: -Z->-Y, -Y->+Z, +Z->+Y, +Y->-Z.
# Transformation for R CW: in (y,z) plane: (y,z)->(-z,y)?
# Check: +Y=(0,1) for y: (y=0,z=1)=+Z -> (y=-1,z=0)=-Y? Wait let me use +Y=(1,0) in (y,z):
# +Y=(1,0) -> ? CW: +Y->-Z: (1,0)->? (0,-1) if -Z=(0,-1) in (y,z). So (y,z)->(z,-y)? Check: (1,0)->(0,-1). +Z=(0,1)->(1,0)=+Y. ✓. Transformation: new_y=z, new_z=-y.
#
# R CW: (y,z) -> (z,-y) (for pieces at x=+1 level).
# Verify with known result: F[2]=(x=+1,y=+1,z=+1)=FUR. R CW: (y=+1,z=+1)->(z=+1,-y=-1)=(new_y=+1,new_z=-1). Position:(x=+1,y=+1,z=-1)=BUR. +Z direction: (0,1) in (y,z) -> (1,0)=+Y=U. BUR on U: U[2]=(y=+1,z=-1,x=+1)? Wait, U[0,1,2] is U's back row (z=-1) and right column.
# U layout: U[0]=(x=-1,z=-1)=BUL, U[2]=(x=+1,z=-1)=BUR. ✓ F[2]->U[2].
# Earlier I computed: F right col F[2,5,8] -> U right col. And R right col U[2,5,8].
# Wait, with new R layout: R[0]=FUR=(y=+1,z=+1). F's right column at z=+1 level: F[2]=(y=+1,z=+1,x=+1). But that's at x=+1 which is R face. F face is at z=+1, so F[2]=(x=+1,y=+1,z=+1)=FUR corner. The sticker on F face is z=+1 facing.
# The R right move affects x=+1 layer. F[2] is in x=+1 layer (it's at FUR corner). After R CW: F[2]->U[2]. ✓ (F's right col, top = F[2])
# U[2]->B[?]: U[2]=(y=+1,z=-1,x=+1)=BUR. (y=+1,z=-1)->(-1,-1). (new_y=-1,new_z=-1). Position:(x=+1,y=-1,z=-1)=BDR. +Y direction: (1,0) in (y,z) -> (0,-1)=-Z=B face. BDR on B: B[8]=(y=-1,x=+1)=BDR. U[2]->B[8]? Wait but earlier it was B[6,3,0] for R cycle...
#
# Hmm, B[8]=(y=-1,x=+1,z=-1)=BDR. And U[2]=(y=+1,z=-1,x=+1)=BUR. After R CW: U[2]=(BUR) at (y=+1,z=-1): new_y=z=-1, new_z=-y=-1. Position:(x=+1,y=-1,z=-1)=BDR. That's B[8]. So U[2]->B[8].
# But code has U[2,5,8]->B[6,3,0]. Code: U[2]->B[6]. B[6]=(y=-1,x=-1)=BDL. But we need B[8]=BDR. WRONG!
#
# Wait: with the OLD R layout (R[0]=BUR), we had:
# F right col = F[2,5,8] and U right col = U[2,5,8], B[6,3,0] (going bottom to top of back column). Let me check with NEW layout.
# NEW R layout: R[0]=FUR, R[2]=BUR, R[6]=FDR, R[8]=BDR.
# F's right column (x=+1 face stickers on F, i.e., F stickers at y=+1...0...-1, z=+1):
# F face at z=+1: F[2]=(x=+1,y=+1), F[5]=(x=+1,y=0), F[8]=(x=+1,y=-1). These are F's right column.
# After R CW: F[2]->U[2], F[5]->U[5], F[8]->U[8]. (as established)
# U right column (x=+1 face stickers on U, i.e., U stickers at y=+1,z=-1...0...+1 but in U layout):
# Wait: U face at y=+1. U stickers in x=+1 column: U[2]=(x=+1,z=-1), U[5]=(x=+1,z=0), U[8]=(x=+1,z=+1). These go from back to front.
# After R CW: U[2,5,8]->B[?]:
# U[2]=(y=+1,z=-1,x=+1)->B[8]: ✓ (computed above)
# U[5]=(y=+1? Wait U is at y=+1 but sticker positions are on the U face. U[5]=(x=+1,z=0,y=+1). R CW: (y=+1,z=0)->(z=0,-y=-1). Position:(x=+1,y=-1,z=0)? Wait: x=+1 is still R face, but that's not right for U sticker. Hmm.
# Actually: U[5] is on U face (y=+1), at position x=+1, z=0. The sticker is at (x=+1, y=+1, z=0).
# R CW moves pieces at x=+1. The sticker on U[5] has y=+1, so it's on the boundary...
# No: the sticker position for U[5] is: it's the sticker at the center-right of the U face. In 3D, the piece center is at (x=+1, y=+1, z=0). This is indeed in the x=+1 slice (R layer). After R CW: (y=+1,z=0)->(z=0,-y=-1)=(new_y=0,new_z=-1). Position:(x=+1,y=0,z=-1). On B face (z=-1): B[5]=(y=0,x=+1,z=-1). +Y direction:(1,0)->new_y=z=0,new_z=-y=-1. -Z=B face. B at (y=0,x=+1)=B[5]. U[5]->B[5].
# U[8]=(x=+1,z=+1,y=+1). (y=+1,z=+1)->(+1,-1)=(new_y=+1,new_z=-1). Position:(x=+1,y=+1,z=-1)=BUR. Wait, that's back to BUR? No, new_y=z_old=+1, new_z=-y_old=-1. (x=+1,y=+1,z=-1)=BUR. On B: B[2]=(y=+1,x=+1)=BUR. U[8]->B[2].
# U[2,5,8]->B[8,5,2].
#
# B[8,5,2]->D[?]: B[8]=(y=-1,x=+1,z=-1)=BDR. R CW: (y=-1,z=-1)->(-(-1),-(-1))=(new_y=-1,new_z=+1). Wait: (y,z)->(z,-y): (-1,-1)->(-1,+1). new_y=-1, new_z=+1. Position:(x=+1,y=-1,z=+1)=FDR. -Z direction sticker: (0,-1) in (y,z) -> (-1,0)=-Y? Wait: (0,-1)->(-(-1),0)=(1,0)=+Y. No, transformation (y,z)->(z,-y): (0,-1)->(-1,0)? (y=0,z=-1)->(z=-1,-y=0)=(-1,0). -Y=(-1,0) in (y,z). Hmm that's D face. FDR on D face: D[8]=(x=+1,z=+1,y=-1). B[8]->D[8]? Let me just use consistent mapping.
# -Z sticker at (x=+1,y=-1,z=-1): direction is -Z = (0,0,-1). As a 2D direction in (y,z) plane: (0,-1).
# After R CW: (y,z)->(z,-y): (0,-1)->(-(-1),0)=(+1,0)? No: z=-1, y=0: new_y=z=-1, new_z=-y=0. So direction becomes (-1,0)=-Y=D face. FDR at -Y = D face: position is (x=+1,y=-1,z=+1)=FDR. D[8]=(x=+1,z=+1,y=-1)=FDR. B[8]->D[8]. ✓
# B[5]=(y=0,x=+1,z=-1). -Z sticker. R CW: (y=0,z=-1)->(z=-1,-y=0)=(-1,0)=-Y=D. Position:(x=+1,y=-1,z=0). D[7]=(x=0,...) wait D[7]? Actually D layout: D[6]=(x=-1,z=+1), D[7]=(x=0,z=+1), D[8]=(x=+1,z=+1). D[5] would be... D[6,7,8] is bottom row, D[3,4,5] is middle row. D[5]=(x=+1,z=0,y=-1). B[5]->D[5]. ✓
# B[2]=(y=+1,x=+1,z=-1)=BUR. -Z sticker. R CW: (y=+1,z=-1)->(-1,-1). new_y=-1, new_z=-1. Position:(x=+1,y=-1,z=-1)=BDR. D face... wait D[2]=(x=+1,z=-1,y=-1). D[2]=(x=+1,z=-1)? My D layout: D[0]=(x=-1,z=-1), D[2]=(x=+1,z=-1). So D[2]=(x=+1,z=-1,y=-1)=BDR on D. B[2]->D[2]. ✓
# B[8,5,2]->D[8,5,2]. Same indices!
#
# D[8,5,2]->F[?]: D[8]=(x=+1,z=+1,y=-1)=FDR. R CW: (y=-1,z=+1)->(+1,+1). new_y=+1,new_z=+1. Position:(x=+1,y=+1,z=+1)=FUR. +Y direction(-Y sticker): (-1,0) in (y,z) -> (0,-(-1))=(0,+1)=+Z=F. FUR on F: F[2]=(y=+1,x=+1,z=+1)=FUR. D[8]->F[2].
# D[5]=(x=+1,z=0,y=-1). (y=-1,z=0)->(0,+1). Position:(x=+1,y=0,z=+1). +Z=F. F[5]=(y=0,x=+1). D[5]->F[5].
# D[2]=(x=+1,z=-1,y=-1)=BDR. (y=-1,z=-1)->(-1,+1). Position:(x=+1,y=-1,z=+1)? No: new_y=z=-1, new_z=-y=+1. (x=+1,y=-1,z=+1)=FDR. Hmm: -Y sticker goes to +Z? Let me redo: D sticker is -Y facing. (-Y direction in (y,z) = (-1,0)). After R CW (y,z)->(z,-y): (-1,0)->(0,+1)=+Z=F. Position: (x=+1,y=-1? wait the piece moved to y=+1?) Actually: D[2] piece is at (x=+1,y=-1,z=-1). After R CW: (y=-1,z=-1)->(z=-1,-y=+1)=(-1,+1). Position:(x=+1,y=-1,z=+1)=FDR? No: new_y=z_old=-1, new_z=-y_old=+1. So position: (x=+1,y=-1,z=+1)=FDR. But FDR is F[8]=(y=-1,x=+1,z=+1). -Y direction -> +Z=F face. F[8]=(y=-1,x=+1)=FDR. D[2]->F[8]. ✓
# D[8,5,2]->F[2,5,8]. ✓
#
# CORRECT R cycle: [('F',[2,5,8]), ('U',[2,5,8]), ('B',[8,5,2]), ('D',[8,5,2])]
# CODE R cycle:    [('F',[2,5,8]), ('U',[2,5,8]), ('B',[6,3,0]), ('D',[2,5,8])]
# Differences: B uses [8,5,2] not [6,3,0], D uses [8,5,2] not [2,5,8].
# NOTE: Code's D[2,5,8] should be D[8,5,2] (reversed). And B[6,3,0] should be B[8,5,2] (completely different!).

print("CORRECT R cycle: [('F',[2,5,8]), ('U',[2,5,8]), ('B',[8,5,2]), ('D',[8,5,2])]")
print("CODE R cycle:    [('F',[2,5,8]), ('U',[2,5,8]), ('B',[6,3,0]), ('D',[2,5,8])]")
print()

# Summary so far:
# U: R and B should be [2,1,0] not [0,1,2]
# D: B and R should be [8,7,6] not [6,7,8]
# F: R should be [2,5,8] not [0,3,6], D should be [8,7,6] not [2,1,0]
# R: B should be [8,5,2] not [6,3,0], D should be [8,5,2] not [2,5,8]

# Let me derive L and B too to be complete, then test all together.
# By left-right symmetry with R, L cycle:
# L CW (viewed from left, -X direction):
# L face right column (x=-1): similar to R but mirrored.
# Correct L cycle should be: [('F',[0,3,6]), ('D',[0,3,6]), ('B',[2,5,8]), ('U',[2,5,8])]? Or different.
# Let me just test and see.

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

# Test with corrected F, U, D, R cycles (keep L, B original for now)
new_cycles = {
    'U': ('U', [('F',[0,1,2]),('R',[2,1,0]),('B',[2,1,0]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[8,7,6]),('R',[8,7,6])]),
    'F': ('F', [('U',[6,7,8]),('R',[2,5,8]),('D',[8,7,6]),('L',[8,5,2])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[8,5,2]),('D',[8,5,2])]),
    'B': ('B', [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]),  # original
    'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',[8,5,2]),('U',[0,3,6])]),  # original
}

print("Testing with corrected U, D, F, R:")
print("R U R' U' x6:", find_order(new_cycles, "R U R' U'"), "(expected 6)")
print("T-perm x2:", find_order(new_cycles, "R U R' U' R' F R2 U' R' U' R U R' F'"), "(expected 2)")
print("Sune x8:", find_order(new_cycles, "R U R' U R U2 R'"), "(expected 8)")
print("F-perm x2:", find_order(new_cycles, "R' U' F' R U R' U' R' F R2 U' R' U' R U R' U R"), "(expected 2)")
