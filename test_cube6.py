# Let me derive correct cycles from scratch using coordinate geometry
# Face layout:
# U face is +Y plane. Viewed from above (+Y, looking down -Y):
#   Looking in -Y direction. right = +X. top = -Z (toward back).
#   U[0] = row 0, col 0 = top-left = (-Z, -X) position = (x=-1, z=-1)?
#   Actually: if right=+X and up/top in the view = -Z:
#   U[0] = top-left-in-view = (x=-1, z=-1) [back-left]
#   U[2] = top-right-in-view = (x=+1, z=-1) [back-right]
#   U[6] = bottom-left-in-view = (x=-1, z=+1) [front-left]
#   U[8] = bottom-right-in-view = (x=+1, z=+1) [front-right]
#
# So U face layout (with x increasing right, z increasing down = toward front in view):
#   0(x=-1,z=-1) 1(x=0,z=-1) 2(x=+1,z=-1)   <- back row
#   3(x=-1,z=0)  4(x=0,z=0)  5(x=+1,z=0)
#   6(x=-1,z=+1) 7(x=0,z=+1) 8(x=+1,z=+1)   <- front row
#
# F face is +Z plane. Viewed from front (+Z, looking in -Z direction):
#   Looking in -Z direction. right = -X (as established before). top = +Y.
#   F[0] = top-left = (+Y, +X) position = wait, right=-X means left=+X...
#   Actually when looking in -Z with right=-X:
#   left = +X, right = -X, top = +Y, bottom = -Y.
#   F[0] = top-left = (x=+1, y=+1) [top-right when facing cube from front? That's confusing]
#   No wait. When YOU look at the F face:
#   You're looking in -Z direction. Your right hand points in -X (toward the left of the cube).
#   F[0] = top-left-AS-SEEN = top, on the left as you see it = top, on the +X side.
#   F[0] = (x=+1, y=+1, z=+1)
#   F[2] = top-right-as-seen = top, -X side = (x=-1, y=+1, z=+1)
#   F[6] = bottom-left-as-seen = (x=+1, y=-1, z=+1)
#   F[8] = bottom-right-as-seen = (x=-1, y=-1, z=+1)
#
# Wait, this contradicts my earlier analysis. Let me restart cleanly.
# Standard convention: face stickers are indexed 0-8 in reading order (left-to-right, top-to-bottom)
# WHEN YOU LOOK AT THE FACE FROM OUTSIDE.
#
# F face (z=+1), looking in from front (-Z direction, as if you're standing in front):
# What's to your left and right?
# You face the cube. Cube's right = +X. Your right = +X (same orientation).
# F[0] = top-left = (x=-1, y=+1, z=+1)
# F[2] = top-right = (x=+1, y=+1, z=+1)
# F[6] = bottom-left = (x=-1, y=-1, z=+1)
# F[8] = bottom-right = (x=+1, y=-1, z=+1)
#
# Hmm, but earlier I concluded F[0]=(x=+1,y=+1,z=+1). Let me be more careful.
# You're standing in front of the cube, facing the F face (+Z face).
# You face in the +Z direction (toward the cube).
# Your right = +X direction.
# F[0] = what you see at top-left = cube's top (y=+1) and to your LEFT = cube's -X side.
# F[0] = (x=-1, y=+1, z=+1). OK so F[0]=(x=-1,y=+1,z=+1).
#
# Now redo U face:
# U face (y=+1), looking down from above (-Y direction).
# You're above the cube, looking down. You face in -Y direction.
# What's to your right? If you're above looking down, typically you're still facing the front of the cube,
# so your right = cube's right = +X, and up/north (away from you) = cube's front = +Z.
# Wait: if you're standing above the cube looking down, your "up" (away from you in your view)
# could be +Z (front of cube) or -Z (back of cube), depending on how you're oriented.
# WCA standard: when looking down at U face from above, the front of U (adjacent to F) is at the bottom of your view.
# So your "up" in the view = -Z (back of cube).
# U[0] = top-left-in-view = back-left = (x=-1, y=+1, z=-1)
# U[2] = top-right = back-right = (x=+1, y=+1, z=-1)
# U[6] = bottom-left = front-left = (x=-1, y=+1, z=+1)
# U[8] = bottom-right = front-right = (x=+1, y=+1, z=+1)
# (Same as what I had before.)
#
# Now: U CW rotation (from above, -Y direction): CW =
# If you look down and rotate CW: +X -> +Z -> -X -> -Z -> +X (standard CW in XZ plane, viewed from +Y).
# Wait: CW from +Y perspective (looking down from +Y, so your view is the XZ plane):
# CW as you see it: right -> down -> left -> up = +X -> +Z -> -X -> -Z -> +X.
# (because you see the XZ plane, with +X to the right and you've set +Z as down in view)
# So: +X -> +Z under CW.
#
# F[0] = (x=-1, y=+1, z=+1). This is on the top face (y=+1), at the F-face's top-left position.
# Wait, F[0] has y=+1 and z=+1. Under U CW: x -> z direction... actually F[0] is NOT on the top layer.
# F[0] is at z=+1 which is the F face (front). It's at the top-left of F face. y=+1 means top layer.
# So F[0] IS in the top layer (y=+1).
#
# Under U CW: (x,z) -> (+z, -x) [CW from above: +X->+Z means new_z=... hmm let me redo]
# CW rotation around +Y axis (from above): standard definition.
# Rotation matrix for CW around Y (looking from +Y down):
# [+cos, 0, +sin]   but CW from ABOVE is CW in the XZ plane when viewed from +Y
# For CW in XZ plane (viewed from +Y): +X rotates toward -Z.
# +X -> -Z, +Z -> +X, -X -> +Z, -Z -> -X.
# So: new_x = z (since +Z->+X means if old=+Z, new_x=+1, new_z=? (not -X means new_z=... ))
# Let me just compute: CW in XZ plane viewed from +Y:
# Rotation matrix: (x,z) -> (z, -x)
# Check: (+1,0) -> (0,-1): +X maps to (0,-1) in (x,z) = new position is (x=0, z=-1) = -Z.
# So +X -> -Z. And +Z maps to: (0,1) -> (1, 0) = +X. +Z -> +X. Correct for CW from above.
# Transformation: new_x = old_z, new_z = -old_x.
# (Using CW from +Y downward view: +X -> -Z -> -X -> +Z -> +X)
# Hmm: (+1,0) -> new_x=0, new_z=-1 = (0,-1). That's -Z. So +X -> -Z. OK.
# (0,+1) -> new_x=+1, new_z=0 = (+1,0). That's +X. So +Z -> +X. OK.
# Transformation: new_x = +old_z, new_z = -old_x.
#
# F[0] = (x=-1, z=+1). After U CW: new_x = z = +1, new_z = -x = +1.
# New position: (x=+1, y=+1, z=+1).
# This is on the R face (x=+1) AND F face (z=+1)...
# Wait, a sticker is only on ONE face. F[0] is on the F face (z=+1) at (x=-1, y=+1).
# After U CW, the sticker at F[0]=(x=-1, y=+1, z=+1) moves to (x=+1, y=+1, z=+1).
# New face: this point is on both R face (x=+1) and F face (z=+1)... no, it's a corner.
# The sticker's new face: F[0] was on the F face, so after rotation it's still tracking the same physical piece.
# The piece moved. The piece was at (x=-1, z=+1) top layer. After CW: goes to (x=+1, z=+1) top layer.
# This new position (x=+1, z=+1) is the front-right top corner.
# Stickers at this corner: on R face, F face, U face.
# The sticker being tracked was on the F face (z=+1), so it's still on the F face? No, wait.
# The sticker was ON F FACE = it's the F-face sticker of the front-left-top corner piece.
# After U CW: this piece moves. The piece moves to the front-right-top position.
# At front-right-top, the sticker we're tracking IS STILL ON THE F FACE (because U move only moves top-layer edge stickers, and the F face sticker of a corner piece in the top layer stays on F face? NO.)
#
# U CW moves the top layer. The piece at front-left-top (corner piece) moves to... which corner?
# Top layer CW rotation: corners go: FUL -> FUR -> BUR -> BUL -> FUL.
# Front-top-left -> Front-top-right -> Back-top-right -> Back-top-left.
# F[0] = front-top-LEFT corner's F sticker.
# After U CW: this corner piece moves to front-top-RIGHT.
# At front-top-RIGHT, this piece's stickers: originally the F face sticker of FUL corner was on the F face.
# After U CW, at FUR position, the sticker that was facing F now faces... RIGHT (R face)!
# (Because the piece rotated around the Y axis, and F-facing becomes R-facing.)
# More precisely: the piece at FUL has stickers in directions: +Z (F), +Y (U), -X (L).
# After U CW, at FUR position: same piece but rotated. CW from above:
# +Z becomes... under CW (x,z)->(z,-x): the sticker facing +Z was at the piece's +Z face.
# After rotation, +Z direction maps to: new facing = rotate the direction. +Z = (x=0,z=+1) -> (new_x=z=+1, new_z=-x=0) = (+X).
# So the sticker that was facing +Z now faces +X = R face!
# F[0] (F face sticker of FUL corner) after U CW becomes an R face sticker at FUR position.
# In R face sticker indices: FUR = front-top-right of R face.
# R face (x=+1), viewed from outside (+X direction, looking -X):
# right in view = +Z (as I calculated before).
# R[0] = top-left = (+Y, -Z, x=+1) = (y=+1, z=-1, x=+1).
# R[2] = top-right = (+Y, +Z, x=+1) = (y=+1, z=+1, x=+1).
# FUR corner on R face: (y=+1, z=+1, x=+1) = R[2].
# So F[0] (FUL corner, F sticker) moves to R[2] (FUR corner, R sticker)!
# Confirmed: F[0] -> R[2].
#
# Similarly: F[1] = top-center of F face = (x=0, y=+1, z=+1). This is on top edge F-U.
# After U CW: (x=0,z=+1) -> (new_x=+1, new_z=0) = (x=+1, y=+1, z=0).
# This is on R face (x=+1) at (y=+1, z=0) = R[1] (top-center of R face).
# Wait: R face, top-center = (y=+1, z=0, x=+1). Looking at R from outside:
# R[0]=top-left=(y=+1,z=-1), R[1]=top-mid=(y=+1,z=0), R[2]=top-right=(y=+1,z=+1).
# (y=+1,z=0,x=+1) = R[1]. So F[1] -> R[1]. Same index!
#
# And F[2] = (x=+1, y=+1, z=+1) = FUR corner, F sticker.
# After U CW: (x=+1,z=+1) -> (new_x=+1, new_z=-1). Position: (x=+1, y=+1, z=-1) = BUR corner on R face.
# R face: (y=+1, z=-1, x=+1) = R[0].
# So F[2] -> R[0].
#
# Summary: F[0]->R[2], F[1]->R[1], F[2]->R[0]. The mapping is F[i] -> R[2-i].
# But code has F[0,1,2] -> R[0,1,2]. CODE IS WRONG for F->R.

# Now verify R->B:
# R[0] = (y=+1, z=-1, x=+1). After U CW: (x=+1,z=-1) -> (new_x=-1, new_z=-1). Position: (x=-1, y=+1, z=-1).
# This is on the L face? No: x=-1 is L face. But wait:
# We need to find which FACE this sticker is on after rotation.
# The sticker was on R face (x=+1), specifically at the BUR corner (back-top-right), facing +X direction.
# Under U CW, the +X direction sticker at BUR corner:
# BUR corner is at (x=+1, y=+1, z=-1). After CW: (x=+1,z=-1) -> (new_x=-1, new_z=-1) = (-1,y=+1,-1).
# That's the BUL corner (back-top-left). At BUL corner, the sticker that was facing +X now faces...
# +X direction under CW becomes: (1,0,0) in x,z -> (new_x=0, new_z=-1) = -Z direction = B face.
# So the R-face sticker at BUR corner becomes a B-face sticker at BUL corner.
# BUL corner on B face: B face is z=-1, viewed from behind (-Z direction, looking +Z):
# When looking in +Z direction: right = +X, top = +Y.
# B[0] = top-left = (y=+1, x=-1, z=-1)? Wait: looking in +Z with right=+X:
# left = -X, right = +X. B[0] = top-left = (y=+1, x=-1).
# B[2] = top-right = (y=+1, x=+1).
# BUL corner = (x=-1, y=+1, z=-1). On B face this is B[0].
# So R[0] -> B[0].
#
# R[1] = (y=+1, z=0, x=+1). After CW: (x=+1,z=0) -> (new_x=0, new_z=-1). Position: (x=0, y=+1, z=-1).
# This is on B face (z=-1) at (y=+1, x=0) = B[1]. R[1] -> B[1].
#
# R[2] = (y=+1, z=+1, x=+1). After CW: (x=+1,z=+1) -> (new_x=+1, new_z=-1). Position: (x=+1,y=+1,z=-1).
# On B face: (y=+1, x=+1) = B[2]. R[2] -> B[2].
# So R[0,1,2] -> B[0,1,2]. Same indices! Code has R[0,1,2] -> B[0,1,2]. CORRECT!

# But wait, F->R was REVERSED (F[0]->R[2]), but R->B is same order (R[0]->B[0]).
# That's inconsistent... let me double-check F->R again.
# F[2] = (x=+1, y=+1, z=+1). Under CW: (x=+1,z=+1) -> (new_x=+1, new_z=-1) = (x=+1,y=+1,z=-1).
# This is at BUR corner... but which face?
# F[2] was on the F face (z=+1), facing +Z direction.
# Under CW, the +Z direction sticker at FUR corner:
# The FUR corner piece moves to BUR corner (F->top-CW rotation: F-right moves to B-right? No...)
# Top layer CW: FUL->FUR->BUR->BUL? Let me recompute.
# CW from above: (x,z) -> (z,-x). Actually I said new_x=z, new_z=-x.
# FUR = (x=+1,z=+1). After CW: (new_x=+1, new_z=-1) = BUR (x=+1,z=-1). So FUR -> BUR.
# Corner moves from FUR to BUR. The sticker that was facing +Z (F face) at FUR...
# Under CW rotation, the direction +Z rotates: (x=0,z=+1) -> (new_x=+1, new_z=0) = +X direction.
# So the F-facing sticker becomes an R-facing sticker!
# At BUR position, on R face: BUR on R face = (y=+1, z=-1, x=+1). That's R[0].
# So F[2] -> R[0]. Confirmed.
#
# Now F[0] = FUL corner. After CW: (x=-1,z=+1) -> (new_x=+1, new_z=+1) = FUR.
# +Z direction sticker (F face) at FUL -> rotates to +X direction (R face) at FUR position.
# FUR on R face: (y=+1, z=+1, x=+1) = R[2]. So F[0] -> R[2]. Confirmed reversed.
#
# So F[0,1,2] -> R[2,1,0]. Reversed. But R[0,1,2] -> B[0,1,2]. Not reversed.
# Why the inconsistency?
#
# Let me check B->L:
# B[0] = (y=+1, x=-1, z=-1). After CW: (x=-1,z=-1) -> (new_x=-1, new_z=+1). Position: (x=-1, y=+1, z=+1).
# B-face sticker at B[0] (BUL corner) facing -Z direction.
# Under CW: -Z direction = (0,-1) in (x,z). After CW: (new_x=-1, new_z=0) = -X direction.
# -X = L face.
# BUL -> new position: (x=-1, y=+1, z=+1) = FUL corner. On L face at FUL: (y=+1, z=+1, x=-1).
# L face viewed from outside (-X direction, looking +X): right = -Z (as I calculated).
# Wait: looking in +X direction: right = -Z (by right-hand rule... let's compute).
# L face is at x=-1. Looking from outside (-X direction, toward +X):
# You face the +X direction. right = +Z (as I computed before with right-hand rule: facing +X, up=+Y, right = up cross facing = y cross x = (0,1,0)x(1,0,0) = (0*0-0*0, 0*1-1*0, 1*0-0*1) = (0,0,-1) = -Z. Wait, that gives -Z.)
# Let me redo: facing direction = +X = (1,0,0), up = +Y = (0,1,0).
# right = up x (-facing) = up x (-x-hat) = (0,1,0) x (-1,0,0) = (0*0-0*0, 0*(-1)-1*0, 1*0-0*(-1)) = (0,0,1) = +Z.
# Hmm, I need to be more careful. Standard formula: right = forward x up? Or up x forward?
# Actually for a camera: right = normalize(forward x up) where forward is the look direction.
# forward = +X (looking at L from outside), up = +Y.
# right = +X x +Y = (0,0,-1) = -Z.
# Hmm, so looking at L from outside (+X direction): right = -Z.
# That means: L[0] = top-left = (+Y, +Z, x=-1) (because left = +Z in this view).
# L[2] = top-right = (+Y, -Z, x=-1) (right = -Z).
#
# FUL corner on L face: FUL = (x=-1, y=+1, z=+1). On L face: (y=+1, z=+1, x=-1) = L[0] (top-left in view, since left=+Z).
# So B[0] -> L[0].
#
# B[2] = (y=+1, x=+1, z=-1) = BUR corner on B face. After CW: (x=+1,z=-1) -> (new_x=-1, new_z=-1). Position: (x=-1,y=+1,z=-1) = BUL.
# -Z direction sticker (B face) under CW: (0,-1) in (x,z) -> (new_x=-1, new_z=0) = -X = L face.
# BUL corner on L face: (y=+1, z=-1, x=-1). On L face: (y=+1, z=-1) = L[2] (top-right in view since right=-Z).
# So B[2] -> L[2].
#
# B[0]->L[0], B[2]->L[2]. Same order! So B->L is NOT reversed.

# Now L->F:
# L[0] = (y=+1, z=+1, x=-1) = FUL. After CW: (x=-1,z=+1) -> (new_x=+1, new_z=+1). FUR = (x=+1,y=+1,z=+1).
# -X direction sticker under CW: (-1,0) in (x,z) -> (new_x=0, new_z=+1) = +Z direction = F face.
# FUR on F face: (y=+1, z=+1, x=+1)... wait FUR is the FRONT-UP-RIGHT corner. On F face: (y=+1, x=+1) = F[2] (top-right).
# So L[0] -> F[2].
#
# L[2] = (y=+1, z=-1, x=-1) = BUL. After CW: (x=-1,z=-1) -> (new_x=-1, new_z=+1). FUL=(x=-1,y=+1,z=+1).
# -X direction under CW: (-1,0) -> (0,+1) = +Z = F face.
# FUL on F face: (y=+1, z=+1, x=-1) = F[0] (top-left since left=+X for F face... wait)
# F face viewed from front (-Z direction, you facing +Z):
# right = +X (as I computed? Let me recheck).
# facing = -Z direction? No: you stand in front of cube, facing the cube = facing +Z direction.
# forward = +Z = (0,0,1). up = +Y = (0,1,0).
# right = forward x up = +Z x +Y = (0,0,1)x(0,1,0) = (0*0-1*1, 1*0-0*0, 0*1-0*0) = (-1,0,0) = -X.
# Hmm, that gives right=-X again. But intuitively if you face a wall (+Z direction) and extend your right arm, it goes to... +X or -X?
# If you face +Z (north), your right arm points +X (east). So right = +X.
# right = up x forward = +Y x +Z = (0,1,0)x(0,0,1) = (1*1-0*0, 0*0-0*1, 0*0-1*0) = (1,0,0) = +X. Yes!
# So F face: right = +X. F[0] = top-left = (+Y, -X) = (y=+1, x=-1, z=+1). That's FUL corner. F[0]=(y=+1,x=-1,z=+1).
# F[2] = top-right = (+Y, +X) = (y=+1, x=+1, z=+1). FUR corner.
#
# L[0] -> FUR = F[2]. L[0] -> F[2]. Reversed!
# L[2] -> FUL = F[0]. L[2] -> F[0]. Reversed!
# So L[0,1,2] -> F[2,1,0]. Reversed.
#
# Summary for U CW:
# F[0,1,2] -> R[2,1,0]: REVERSED
# R[0,1,2] -> B[0,1,2]: SAME
# B[0,1,2] -> L[0,1,2]: SAME
# L[0,1,2] -> F[2,1,0]: REVERSED
#
# This is the bug! Every other pair has reversed indices.
# The code has ALL of them as [0,1,2] -> [0,1,2], but it should be:
# F[0,1,2] -> R[2,1,0]  (or equivalently: F goes to R but reversed)
# R[0,1,2] -> B[0,1,2]  (same, correct)
# B[0,1,2] -> L[0,1,2]  (same, correct)
# L[0,1,2] -> F[2,1,0]  (reversed)
#
# But wait, the right-shift algorithm:
# saved = snapshot of current stickers
# for k in range(n):
#   face[k] gets from saved[k-1]
#
# So face[0]=F gets from saved[3]=L. That's L -> F.
# For L[0]->F[2]: we need F[0] to get L[2], F[1] to get L[1], F[2] to get L[0].
# Currently: F[0,1,2] gets L[0,1,2]. Should get L[2,1,0].
# Fix: L's indices in the cycle should be [2,1,0] not [0,1,2].
# OR: use different target indices for F.
#
# Actually, the cycle format is (face_name, [list of indices]).
# The sticker flow: face[k] at idx[j] gets from face[k-1] at its idx[j].
# So F[idx[j]] = L[idx[j]]. Currently idx=[0,1,2] for both.
# For correct L->F: F[0] = L[2], F[1] = L[1], F[2] = L[0].
# Option: keep cycle as [F,R,B,L] but with DIFFERENT indices per face.
# This would complicate things. The current algorithm assumes all faces use the SAME indices.
#
# Alternative interpretation: maybe the cycle DIRECTION is wrong for U.
# What if instead of [F,R,B,L] we use [F,L,B,R] (reversed)?
# Right-shift on [F,L,B,R]: F gets from R, L gets from F, B gets from L, R gets from B.
# F->L->B->R->F: stickers go F->L->B->R.
# For U CW we need F->R->B->L. So [F,L,B,R] with right-shift = L gets from F = F->L. That's U CCW direction.
#
# Actually, let me think about it differently.
# We need: F[idx_F] -> R[idx_R] -> B[idx_B] -> L[idx_L] -> F[idx_F].
# With right-shift on [F,R,B,L]: stickers go L->F->R->B->L (equivalent).
# So L's sticker goes to F (at same idx), F's to R (at same idx), R's to B (at same idx), B's to L (at same idx).
# But we need: F[0]->R[2], F[1]->R[1], F[2]->R[0] (F->R reversed),
#              R[0]->B[0], R[1]->B[1], R[2]->B[2] (R->B same),
#              B[0]->L[0], B[1]->L[1], B[2]->L[2] (B->L same),
#              L[0]->F[2], L[1]->F[1], L[2]->F[0] (L->F reversed).
#
# With the current algorithm (same indices for all faces), we can't represent a mix of reversed/same.
# BUT: we can express the reversed mappings differently.
# L[0]->F[2]: this means F[2] gets L[0]. In the cycle, if F comes after L:
# F[i] gets L[idx_L[i]]. If idx_L = [2,1,0], then F[0] gets L[2], F[1] gets L[1], F[2] gets L[0].
# That gives: L[2]->F[0], L[1]->F[1], L[0]->F[2]. But we need L[0]->F[2]. Correct!
# So: set L's indices to [2,1,0] in the cycle.
# Similarly: R's indices should be [2,1,0] because F[0]->R[2], meaning R[2] gets F[0] = R[i] gets F[2-i].
# If R's indices are [2,1,0]: R[2,1,0] = R[2] gets from F[0], R[1] gets from F[1], R[0] gets from F[2].
# That gives: F[0]->R[2], F[1]->R[1], F[2]->R[0]. Correct!
# And B's indices [0,1,2]: B[0] gets from R[0], B[1] from R[1], B[2] from R[2]. R[i]->B[i]. Correct!
# And L's indices [2,1,0]: L[2] gets from B[0], L[1] from B[1], L[0] from B[2]. B[i]->L[2-i]. Correct!
# Wait, B->L: B[0]->L[0], B[1]->L[1], B[2]->L[2] (same). But L[2,1,0] means L[2]=B[0], L[1]=B[1], L[0]=B[2].
# That gives B[0]->L[2] which is WRONG. We need B[0]->L[0].
#
# Hmm. So we need:
# F's indices: [0,1,2] (destination: F[0]=from_L[2], F[1]=from_L[1], F[2]=from_L[0])
# R's indices: [2,1,0] (destination: R[2]=from_F[0], R[1]=from_F[1], R[0]=from_F[2])
# B's indices: [0,1,2] (destination: B[0]=from_R[0], B[1]=from_R[1], B[2]=from_R[2])
# L's indices: ??? (destination: L[0]=from_B[0], L[1]=from_B[1], L[2]=from_B[2])
# L[0]=B[0], L[1]=B[1], L[2]=B[2]. L's indices = [0,1,2].
# But with algorithm: L gets from B[idx_B] where B's idx = [0,1,2]. So L[idx_L[j]] = B[idx_B[j]].
# L[0]=B[0]: idx_L[0]=0, idx_B[0]=0. ✓
# L[1]=B[1]: idx_L[1]=1, idx_B[1]=1. ✓
# L[2]=B[2]: idx_L[2]=2, idx_B[2]=2. ✓
# And L->F (L[0]->F[2]): F gets from L[idx_L[j]]. F[idx_F[j]] = L[idx_L[j]].
# F[0]=L[2]: idx_F[0]=0, idx_L[0]=2. But idx_L[0]=0 from above. Contradiction!
#
# The issue is that the SAME L index list is used both for "L as source" and "L as destination".
# The current algorithm: face[k][idx[k][j]] = face[k-1][idx[k-1][j]].
# Each face has ONE index list used for BOTH reading and writing.
#
# For U CW to work correctly, we need DIFFERENT read/write indices.
# F writes to R[2,1,0] (reversed), but B reads from R[0,1,2] (same).
# This can't be represented with one index list per face.
#
# HOWEVER: there's another way to express this. The cycle can be written so that
# the "sending" face and "receiving" face agree on index order.
#
# The fix for U: use cycle [F[0,1,2], R[2,1,0], B[2,1,0], L[0,1,2]]?
# No, wait. Let me think again.
# The algorithm: for k in [0..3]:
#   face[k][idx[k][j]] = face[k-1][idx[k-1][j]]   (for j in range)
#
# To achieve F[0]->R[2]:
# R[2] = F[0]. In the loop: when k=R(=1), j=0: face[1][idx[1][0]] = face[0][idx[0][0]].
# face[1]=R, face[0]=F, so R[idx_R[0]] = F[idx_F[0]].
# Want R[2] = F[0]: idx_R[0]=2, idx_F[0]=0. R's index list starts with 2.
#
# To achieve R[0]->B[0]:
# B[0] = R[0]. When k=B(=2), j=0: B[idx_B[0]] = R[idx_R[0]].
# Want B[0]=R[0]: idx_B[0]=0, idx_R[0]=0. But we just said idx_R[0]=2. Contradiction!
#
# So with this algorithm, it's impossible to simultaneously have F[0]->R[2] and R[0]->B[0]
# using a single index list per face. The algorithm fundamentally requires consistent index order.
#
# ALTERNATIVE: Express the cycle with reversed index order for the "odd" faces.
# F[0,1,2] -> R[2,1,0] -> B[0,1,2] -> L[2,1,0] -> F[0,1,2]
# With right-shift on [F[0,1,2], R[2,1,0], B[0,1,2], L[2,1,0]]:
# F[0] = prev(L)[2], F[1]=prev(L)[1], F[2]=prev(L)[0]
# R[2] = prev(F)[0], R[1]=prev(F)[1], R[0]=prev(F)[2]
# B[0] = prev(R)[2], B[1]=prev(R)[1], B[2]=prev(R)[0]
# L[2] = prev(B)[0], L[1]=prev(B)[1], L[0]=prev(B)[2]
#
# This gives: L[2]->F[0], F[0]->R[2], R[2]->B[0]? Let's trace:
# From F[0]=L[2] -> F[0] holds L[2]'s old value. Sticker L[2] moved to F[0]. ✓ (L[2]->F[0])
# R[2]=F[0] -> R[2] holds F[0]'s old value. F[0] moved to R[2]. ✓ (F[0]->R[2])
# B[0]=R[2] -> B[0] holds R[2]'s old value. R[2] moved to B[0]. ✓
# But we need R[0]->B[0], not R[2]->B[0].
# So [F[0,1,2], R[2,1,0], B[0,1,2], L[2,1,0]] gives F[0,1,2]->R[2,1,0]->B[0,1,2]->L[2,1,0]->F[0,1,2].
# Which means: F[0]->R[2], F[1]->R[1], F[2]->R[0], R[2]->B[0], R[1]->B[1], R[0]->B[2], etc.
# But we need R[0]->B[0], R[1]->B[1], R[2]->B[2]. Not matching.
#
# Actually let me reconsider. Perhaps I made an error in the R->B calculation.
# Let me redo: R[0] = (y=+1, z=-1, x=+1) = BUR corner, R face sticker.
# After U CW: (x=+1, z=-1) -> (new_x=-1, new_z=-1). Position: (x=-1, y=+1, z=-1) = BUL corner.
# R-face sticker (+X facing) under CW rotation: +X direction = (1,0,0) in x,z = (x=1,z=0).
# After CW: (new_x=0, new_z=-1) = -Z direction = B face.
# So R[0] becomes a B-face sticker at BUL corner.
# BUL on B face (viewed from behind, looking +Z direction): left in view = -X.
# Wait: looking in +Z direction. right = +X (you face away from cube, looking at B from outside means you walk around the back).
# Hmm: looking at B from OUTSIDE (from behind the cube) means looking in the +Z direction.
# When looking in +Z: right = +X (standard), top = +Y.
# B[0] = top-left = (+Y, -X) = (y=+1, x=-1, z=-1). That's BUL.
# B[2] = top-right = (+Y, +X) = (y=+1, x=+1, z=-1). That's BUR.
#
# BUL on B face = B[0]. So R[0] -> B[0]. Correct!
# My earlier computation was correct. R[0]->B[0], R[1]->B[1], R[2]->B[2]. R->B same order.
#
# So the ACTUAL correct U cycle is:
# F[0,1,2] -> R[2,1,0]  (REVERSED going F->R)
# R[0,1,2] -> B[0,1,2]  (SAME going R->B)
# B[0,1,2] -> L[0,1,2]  (SAME going B->L)
# L[0,1,2] -> F[2,1,0]  (REVERSED going L->F)
#
# This pattern: alternate reversed/same. With the current algorithm structure,
# we can express this by flipping every other face's index list.
# Cycle: [F[0,1,2], R[2,1,0], B[0,1,2], L[2,1,0]]
# Right-shift: F gets from L, R gets from F, B gets from R, L gets from B.
# F[0]=L[2], F[1]=L[1], F[2]=L[0]. So L[2]->F[0], L[1]->F[1], L[0]->F[2]. i.e., L[i]->F[2-i]. WRONG (need L[0]->F[2] = L[i]->F[2-i] = same thing). Actually L[0]->F[2] IS L[i]->F[2-i] for i=0. ✓
# R[2]=F[0], R[1]=F[1], R[0]=F[2]. So F[0]->R[2], F[1]->R[1], F[2]->R[0]. ✓
# B[0]=R[2], B[1]=R[1], B[2]=R[0]. So R[2]->B[0], R[1]->B[1], R[0]->B[2]. WRONG (need R[0]->B[0]).
#
# Doesn't work. The alternating pattern can't be expressed simply.
#
# ALTERNATIVE: Use a DIFFERENT cycle direction.
# What if U CW uses cycle [L,B,R,F] instead of [F,R,B,L]?
# Right-shift on [L,B,R,F]: L gets from F, B gets from L, R gets from B, F gets from R.
# Sticker flow: F->L->B->R->F. For U CW we need F->R->B->L->F. That's the opposite direction!
# [L,B,R,F] = reversed [F,R,B,L]. Would give U CCW.
#
# SIMPLEST FIX: Change the index order for F and L in the U cycle.
# Current: [F[0,1,2], R[0,1,2], B[0,1,2], L[0,1,2]]
# Correct:  ???
#
# The algorithm assigns: face[k][idx_k[j]] = face[k-1][idx_{k-1}[j]]
# For F->R: F[0]->R[2] means R[2] = F[0]. At step k=R: R[idx_R[j]] = F[idx_F[j]].
# R[2]=F[0]: idx_R[0]=2. R[1]=F[1]: idx_R[1]=1. R[0]=F[2]: idx_R[2]=0. So idx_R=[2,1,0].
# For R->B: R[0]->B[0]. At k=B: B[idx_B[j]] = R[idx_R[j]].
# B[idx_B[0]]=R[idx_R[0]]=R[2]. We need B[0]=R[0]. Contradiction (R[2] is assigned to B[something], not R[0]).
#
# This can't work with one index list per face. The only solution is to either:
# 1. Use different source and destination index lists.
# 2. Change the direction of sticker flow (reverse the cycle).
#
# Let me think about option 2 more carefully.
# The TRUE physical cycle for U CW (by sticker destination):
# What position gets F[0]? We know F[0] goes to R[2]. So R[2] gets F[0].
# What position gets F[1]? F[1] goes to R[1]. R[1] gets F[1].
# What position gets F[2]? F[2] goes to R[0]. R[0] gets F[2].
# What gets R[0]? R[0] goes to B[0]. B[0] gets R[0].
# What gets R[1]? R[1] goes to B[1]. B[1] gets R[1].
# What gets R[2]? R[2] goes to B[2]. B[2] gets R[2].
# What gets B[0]? B[0] goes to L[0]. L[0] gets B[0].
# What gets B[2]? B[2] goes to L[2]. L[2] gets B[2].
# What gets L[0]? L[0] goes to F[2]. F[2] gets L[0].
# What gets L[2]? L[2] goes to F[0]. F[0] gets L[2].
#
# So: F[i_F] gets L[idx_F(i_F)] where:
# F[0] = L[2], F[1] = L[1], F[2] = L[0]. So L source index = [2,1,0] for F.
# R[0]=F[2], R[1]=F[1], R[2]=F[0]. So F source index = [2,1,0] for R.
# B[0]=R[0], B[1]=R[1], B[2]=R[2]. So R source index = [0,1,2] for B.
# L[0]=B[0], L[1]=B[1], L[2]=B[2]. So B source index = [0,1,2] for L.
#
# This means the cycle should be:
# F with dest-indices [0,1,2] reading from L with source-indices [2,1,0]
# R with dest-indices [0,1,2] reading from F with source-indices [2,1,0]
# B with dest-indices [0,1,2] reading from R with source-indices [0,1,2]
# L with dest-indices [0,1,2] reading from B with source-indices [0,1,2]
#
# In the current algorithm: face[k][idx_k[j]] = face[k-1][idx_{k-1}[j]].
# Destination is face[k] at idx_k[j], source is face[k-1] at idx_{k-1}[j].
# Same index list for both source and destination role.
#
# For F: dest [0,1,2], source from L = [2,1,0]. Need L's index to be [2,1,0].
# For R: dest [0,1,2], source from F = [2,1,0]. Need F's index to be [2,1,0].
# For B: dest [0,1,2], source from R = [0,1,2]. Need R's index to be [0,1,2].
# For L: dest [0,1,2], source from B = [0,1,2]. Need B's index to be [0,1,2].
#
# F needs source index [2,1,0] (when used as source for R), but dest index [0,1,2] (when F is written).
# But F's source role and dest role use THE SAME index list. Conflict!
# (F as source for R needs [2,1,0], but F as destination from L needs [0,1,2].)
#
# The ONLY way to make this work with the current algorithm is to combine the reversed indices:
# If we use F's index list as [0,1,2] and make F->R mapping work by REVERSING R's list too:
# R's list = [2,1,0]. Then F[0] reads into R[2], F[1] into R[1], F[2] into R[0]. ✓ (F[i]->R[2-i])
# But then R->B: B[0] gets R[2] (since R's list=[2,1,0] and B's list=[0,1,2], B[0]=R[2]). WRONG.
#
# FUNDAMENTAL ISSUE: The current algorithm is WRONG for this cube orientation/index convention.
# The algorithm assumes "same index position" = "same relative position on the face",
# but that's only true when adjacent faces have compatible orientation conventions.
# Here, L->F is orientation-reversed because when L unfolds to the left and F faces you,
# the index ordering goes in opposite directions.
#
# THE REAL FIX:
# Use the correct index lists per face in the cycle. The cycle format (face, [indices])
# needs DIFFERENT indices for each face to account for orientation changes.
#
# CURRENT BUG: For the U move (and likely others), the index lists for adjacent faces are wrong.
# They use [0,1,2] everywhere but some faces need [2,1,0].
#
# Specifically for U: The indices F[0,1,2] are the TOP ROW of F face = adjacent to U's BOTTOM row.
# The indices R[0,1,2] are the TOP ROW of R face = adjacent to U's RIGHT col.
#
# The key insight: in the current code, U[0,1,2] is U's BACK ROW (adjacent to B) and U[6,7,8] is FRONT ROW (adjacent to F).
# This is because U face is stored with row 0 at the BACK (index 0 = top-left when viewed from ABOVE with front = down in view).
#
# For F face, row 0 (F[0,1,2]) is the TOP ROW when viewing F from front.
# In 3D, F's top row is adjacent to U's FRONT ROW = U[6,7,8].
# In the net, F is placed below U, and F's top row should match U's bottom row (U[6,7,8]). ✓
#
# The F move cycle correctly uses U[6,7,8] for the F-U connection. So those indices are fine.
# The issue is with the U cycle where SAME top-row indices [0,1,2] are used for ALL four faces.
# But the faces have different orientations, so going around the top layer, the index direction reverses.
#
# Let me now derive the CORRECT U cycle:
# Top row of F (adjacent to U bottom): F[0,1,2], going LEFT to RIGHT as seen from front.
# Top row of R (adjacent to U right): R[0,1,2], going LEFT to RIGHT as seen from right.
#   LEFT of R (from the right face perspective) = FRONT direction = +Z.
#   So R[0]=front-top, R[2]=back-top.
# Top row of B (adjacent to U top): B[0,1,2], going LEFT to RIGHT as seen from behind.
#   LEFT of B (from behind) = +X direction = same as R's right side.
#   So B[0]=right-top (from global), B[2]=left-top.
# Top row of L (adjacent to U left): L[0,1,2], going LEFT to RIGHT as seen from left.
#   LEFT of L = BACK direction = -Z.
#   L[0]=back-top, L[2]=front-top.
#
# U CW rotation (F->R->B->L->F for sticker travel):
# F[0] (front-top-left corner in global: x=-1,z=+1) -> R[?]:
#   In R's coordinate: x=-1,z=+1 is the FRONT of R face (R[2] since R[0]=front-top, wait).
#   R[0]=front-top means R row 0 starts at front. R[0]=(y=+1,z=+1) and R[2]=(y=+1,z=-1)?
#   Hmm, when viewing R from outside: left = +Z (front direction). R[0]=top-left=front.
#   But R[0,1,2] goes left to right = front to back. R[0]=front, R[2]=back.
#   After U CW: F[0]=(x=-1,z=+1) top goes to? CW: (x,z)->(new_x=z,new_z=-x)=(+1,+1).
#   New position: x=+1,z=+1 = front-right. On R face: front = R[0] side. R[0]=(y=+1,z=+1).
#   But x=+1,z=+1 = (x=+1,y=+1,z=+1) = FUR corner. On R face: left (+Z) side = R[0]=front.
#   R[0]=(y=+1,z=+1,x=+1) ✓. So F[0]->R[0].
#
# Wait! That contradicts my earlier coordinate analysis where F[0]=(x=-1,y=+1,z=+1) and R[0]=(y=+1,z=-1,x=+1)!
# I'm getting confused between different index conventions for R[0].
#
# I need to carefully establish: looking at R from outside (standing to the right of the cube, looking LEFT = looking in -X direction):
# right = -Z (I computed this earlier via cross product: forward=-X, up=+Y, right = forward x up = (-X) x (+Y) = -(X x Y) = -Z).
# Wait: right = up x forward = (+Y) x (-X) = (0,1,0) x (-1,0,0) = (1*0-0*0, 0*(-1)-0*0, 0*0-1*(-1)) = (0,0,1) = +Z.
# OK so looking in -X direction: right = +Z. Not -Z.
# So R[0]=top-left in view (looking -X): left=-Z, right=+Z. Top-left=(y=+1,z=-1). R[0]=(y=+1,z=-1,x=+1).
# R[2]=top-right=(y=+1,z=+1,x=+1).
#
# OK so my ORIGINAL calculation was right: R[0]=(y=+1,z=-1) and R[2]=(y=+1,z=+1).
# R[0]=back-top (z=-1=back), R[2]=front-top (z=+1=front).
#
# F[0]=(x=-1,y=+1,z=+1)=FUL. After U CW: (x=-1,z=+1)->(new_x=+1,new_z=+1). (x=+1,y=+1,z=+1)=FUR.
# On R face: FUR=(y=+1,z=+1,x=+1). R[2]=(y=+1,z=+1,x=+1). So F[0]->R[2]. Confirmed.
#
# I had it right. My error above was confusing "left in R view" with front/back directions.
# R[0]=(y=+1,z=-1) = BACK-top of R face. R[2]=(y=+1,z=+1) = FRONT-top of R face.
# F[0] (FUL, front-top-left) goes to R[2] (front-top of R face). Makes sense physically!
#
# So the correct U cycle (as established) is:
# F[0,1,2] -> R[2,1,0]
# R[0,1,2] -> B[0,1,2]
# B[0,1,2] -> L[0,1,2]
# L[0,1,2] -> F[2,1,0]
#
# With the right-shift algorithm, we can express this as:
# [('F',[0,1,2]), ('R',[2,1,0]), ('B',[2,1,0]), ('L',[0,1,2])]?
# Let's verify: F gets from L, R gets from F, B gets from R, L gets from B.
# F[0] = L[0], F[1]=L[1], F[2]=L[2]. Source L indices [0,1,2], dest F indices [0,1,2].
# But we need F[0] = L[2], not L[0]. So F[0,1,2] getting from L with L-index [0,1,2] = F[j]=L[j]. WRONG.
#
# I'm going in circles. Let me just try all possible combinations and test.

# What if U cycle uses [('F',[2,1,0]),('R',[0,1,2]),('B',[2,1,0]),('L',[0,1,2])]?
# Right-shift: F[2,1,0] gets from L[0,1,2], R[0,1,2] gets from F[2,1,0], B[2,1,0] gets from R[0,1,2], L[0,1,2] gets from B[2,1,0].
# F[2]=L[0], F[1]=L[1], F[0]=L[2]. So L[0]->F[2], L[1]->F[1], L[2]->F[0]. ✓
# R[0]=F[2], R[1]=F[1], R[2]=F[0]. So F[2]->R[0]. But we need F[0]->R[2]. WRONG direction in R.

# Hmm. What if it's [('F',[0,1,2]),('R',[0,1,2]),('B',[2,1,0]),('L',[2,1,0])]?
# F gets from L: F[0]=L[2], F[1]=L[1], F[2]=L[0]. L[2]->F[0], L[0]->F[2]. Need L[0]->F[2]. ✓
# R gets from F: R[0]=F[0], R[1]=F[1], R[2]=F[2]. F[0]->R[0]. Need F[0]->R[2]. WRONG.

# [('F',[0,1,2]),('R',[2,1,0]),('B',[0,1,2]),('L',[2,1,0])]?
# F gets from L: F[0]=L[2], F[1]=L[1], F[2]=L[0]. L[2]->F[0], L[0]->F[2]. ✓
# R gets from F: R[2]=F[0], R[1]=F[1], R[0]=F[2]. F[0]->R[2]. ✓
# B gets from R: B[0]=R[2], B[1]=R[1], B[2]=R[0]. R[2]->B[0]. Need R[0]->B[0]. WRONG.

# Seems like we can't get it with this simple algorithm...
# Unless... the correct answer is to swap the face ordering.
# What if we reverse the LIST ORDER: [L,B,R,F] instead of [F,R,B,L]?
# Right-shift on [L,B,R,F]: L gets from F, B gets from L, R gets from B, F gets from R.
# L[0]=F[0], etc. But we need L[0]=B[0] for U CW. Wrong direction.
#
# What if we use [F,L,B,R] with some index reversal?
# [F,L,B,R]: F gets from R, L gets from F, B gets from L, R gets from B.
# Sticker flow: F->L->B->R->F = U CCW.
# With reversed indices for some: [F[2,1,0],L[0,1,2],B[2,1,0],R[0,1,2]]?
# F[2]=R[0], F[1]=R[1], F[0]=R[2]. R[0]->F[2], R[2]->F[0]. These are U CCW.
# Not what we want.
#
# I think the simplest correct representation is to use the "standard" Rubik's cube cycle representation
# where each edge is specified as pairs:
# F_row0 -> R_col0 -> B_row2_reversed -> L_col2_reversed -> F_row0
# But the current data structure can't express this without per-pair index lists.
#
# THE REAL FIX: The algorithm needs to be changed, OR the cycles need to be specified differently.
#
# Actually, looking at this again: many Rubik's cube simulators use a simpler representation
# where the U cycle is just [F[0,1,2], L[0,1,2], B[0,1,2], R[0,1,2]] (reverse order).
# Wait - maybe the KEY is the DIRECTION of the cycle list.
# Let me try: if the cycle list is reversed (F before L in original, now F before R in reversed):
# Original: [F,R,B,L] -> reversed -> [L,B,R,F]
# That gives U CCW (already checked).
#
# I think the root issue is with HOW B and other faces are indexed.
# Different simulators use different B face indexing conventions.
# Let me just empirically find the correct cycles by brute-force testing.

print("Let me try different U cycle configurations...")

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

# Standard correct cycles (from a known-good implementation like kociemba or similar)
# Reference: https://ruwix.com/the-rubiks-cube/notation/
# U CW: F top row -> R top row -> B top row -> L top row (in sticker order preserving direction)
# But B's "top row" from behind goes right-to-left in global coords, opposite to F.
# A common correct implementation uses:
# U: [F[0,1,2], R[0,1,2], B[0,1,2], L[0,1,2]] -- but this is what's buggy!
# OR uses: F,L,B,R order (to account for B orientation flip)
#
# Let me look at what happens with the cycle [('F',[0,1,2]),('L',[0,1,2]),('B',[0,1,2]),('R',[0,1,2])]:
# Right-shift: F gets from R, L gets from F, B gets from L, R gets from B.
# F[0]=R[0], L[0]=F[0], B[0]=L[0], R[0]=B[0]. Cycle: R->F->L->B->R = U CCW.

# For U CW with correct orientation, the standard approach used in many cubers' simulators:
# Actually I've seen implementations use:
# U: F_top, R_top, B_top, L_top where B_top is [2,1,0] (reversed)
# OR use the cycle direction [F,L,B,R] with B reversed.

correct_cycles = {
    'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',[2,1,0]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[8,7,6]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[2,1,0]),('L',[8,5,2])]),
    'B': ('B', [('D',[8,7,6]),('R',[2,5,8]),('U',[0,1,2]),('L',[6,3,0])]),  # Need to figure out
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[6,3,0]),('D',[2,5,8])]),
    'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',[8,5,2]),('U',[0,3,6])]),
}

# Test: T-perm order should be 2
tperm = "R U R' U' R' F R2 U' R' U' R U R' F'"
ct = CubeTest(correct_cycles)
for i in range(1, 10):
    ct.apply(tperm)
    if ct.is_solved():
        print(f"With B fixed U: T-perm order = {i}")
        break
else:
    print("T-perm order > 9 with modified B-related U fix")
