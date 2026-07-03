"""
Derive correct F cycle with D[0]=FDL and R[0]=FUR conventions.

F CW (viewed from front, looking in -Z direction):
+Z -> +X (R CW from front means: stickers at +Z face move: +Z->+X->-Z->-X->+Z)
Wait: F CW means: looking at F face from outside (+Z direction... no, F is the +Z face,
so looking at F from OUTSIDE means looking in -Z direction (toward -Z).

CW rotation when looking in -Z direction (standard):
right = +X. Up = +Y.
CW: right->down->left->up = +X->-Y->-X->+Y->+X.

For pieces at z=+1 (front slice):
Direction transformations under F CW: +X->-Y->-X->+Y (from the CW description).
In (x,y) plane with the transformation: (x,y)->(y,-x)?
Check: +X=(1,0)->(0,-1)=-Y ✓. +Y=(0,1)->(1,0)=+X ✓. So F CW: (x,y)->(y,-x).

Now let's derive correct F cycle:

U bottom row: U[6]=(x=-1,z=+1,y=+1)=FUL. F CW: (x=-1,y=+1)->(+1,+1). FUR=(x=+1,y=+1). +Y(U sticker): (0,1)->(1,0)=+X=R. FUR on R: R[0]=(y=+1,z=+1)=FUR. U[6]->R[0]. ✓
U[8]=(x=+1,z=+1,y=+1)=FUR. F CW: (x=+1,y=+1)->(+1,-1). FDR=(x=+1,y=-1). +Y->+X. R[6]=(y=-1,z=+1)=FDR. U[8]->R[6].
U[6,7,8]->R[0,3,6]. Same indices. Code has U[6,7,8]->R[0,3,6]. ✓ CORRECT.

R left col: R[0]=(y=+1,z=+1)=FUR. F CW: (x=+1,y=+1)->(+1,-1). FDR=(x=+1,y=-1). +X (R sticker): (1,0)->(0,-1)=-Y=D. FDR on D: D[2]=(x=+1,z=+1)=FDR. R[0]->D[2].
R[6]=(y=-1,z=+1)=FDR. F CW: (x=+1,y=-1)->(-1,-1)? (y=-1,x=+1): new_x=y=-1, new_y=-x=-1. (-1,-1)=FDL=(x=-1,y=-1). +X->-Y=D. FDL on D: D[0]=(x=-1,z=+1)=FDL. R[6]->D[0].
R[0,3,6]->D[2,1,0]. Reversed. Code has D[2,1,0]. ✓ CORRECT.

D top row: D[0]=(x=-1,z=+1)=FDL. F CW: (x=-1,y=-1): new_x=-1, new_y=+1. FUL=(x=-1,y=+1). -Y(D sticker): (-1,0) in (x,y): new_x=y=-1?? Hmm: -Y direction = (0,-1) in (x,y). Under (x,y)->(y,-x): (0,-1)->(-(-1),0)=(+1,0)=+X? No that's R. But D sticker is -Y facing.
Actually: D sticker faces -Y (outward from D face). Direction vector (0,-1) in (x,y):
Under F CW transform (x,y)->(y,-x): (x=0,y=-1)->(y=-1,-x=0)=(-1,0)=-X=L.
FUL on L: L[2]=(y=+1,z=+1)=FUL. D[0]->L[2].
D[2]=(x=+1,z=+1)=FDR. F CW: (x=+1,y=-1)->(-1,-1). FDL=(x=-1,y=-1). -Y->-X. FDL on L: L[8]=(y=-1,z=+1)=FDL. D[2]->L[8].
D[2,1,0]->L[8,5,2]. Reversed. Code has L[8,5,2]. ✓ CORRECT.

L right col: L[2]=(y=+1,z=+1)=FUL. F CW: (x=-1,y=+1)->(+1,+1). FUR=(x=+1,y=+1). -X(L sticker): (-1,0) in (x,y): (-1,0)->(0,+1)=+Y=U. FUR on U: U[8]=(x=+1,z=+1)=FUR. L[2]->U[8].
L[8]=(y=-1,z=+1)=FDL. F CW: (x=-1,y=-1)->(-1,+1). FUL=(x=-1,y=+1). -X->+Y=U. FUL on U: U[6]=(x=-1,z=+1)=FUL. L[8]->U[6].
L[8,5,2]->U[6,7,8]. Same! Wait: L[8]->U[6], L[2]->U[8]: reversed? L[8,5,2] means L[8] first, going to U[6,7,8]: L[8]->U[6], L[5]->U[7], L[2]->U[8]. ✓ Code has U[6,7,8]. ✓ CORRECT.

CONCLUSION: Original F cycle is COMPLETELY CORRECT.
"""

print("F cycle is verified correct. The bugs are only in:")
print("- U cycle: B should be [2,1,0] not [0,1,2]")
print("- R cycle: B should be [8,5,2] not [6,3,0]")
print("- L cycle: B should be [6,3,0] not [8,5,2]")
print()
print("Now let me derive B cycle and D cycle:")
print()

# B cycle: B face is at z=-1, viewed from behind.
# B[0]=BUL=(y=+1,x=-1), B[2]=BUR=(y=+1,x=+1), B[6]=BDL=(y=-1,x=-1), B[8]=BDR=(y=-1,x=+1)
# B CW (viewed from behind, in -Z direction, looking +Z):
# Right=+X, up=+Y. CW: +X->-Y, -Y->-X, -X->+Y, +Y->+X.
# (x,y)->(y,-x) for pieces at z=-1.
# But wait: B is at z=-1. "Looking at B from behind" = looking in +Z direction (from -inf z toward cube).
# From -Z looking toward +Z: you're BEHIND the cube. "Forward" = +Z.
# CW when looking +Z: (x,y) CW = (x,y)->(y,-x)?
# Check: +X=(1,0)->(0,-1)=-Y. CW from +Z: +X->-Y->-X->+Y. ✓

# B CW affects z=-1 slice.
# U back row: U[0]=(x=-1,z=-1)=BUL, U[2]=(x=+1,z=-1)=BUR.
# Wait, U[0] is at z=-1 because U[0]=BUL with U[0]=(x=-1,z=-1) (from my analysis where U[0]=back-left since U's back row is adjacent to B).
# U[0]=(x=-1,z=-1,y=+1)=BUL. B CW: (x=-1,y=+1)->(+1,+1). BUR=(x=+1,y=+1,z=-1). +Y direction: (0,1)->(1,0)=+X=R. BUR on R: R[2]=(y=+1,z=-1)=BUR. U[0]->R[2].
# U[2]=(x=+1,z=-1,y=+1)=BUR. B CW: (x=+1,y=+1)->(+1,-1). BDR=(x=+1,y=-1,z=-1). +Y->+X=R. R[8]=(y=-1,z=-1)=BDR. U[2]->R[8].
# U[0,1,2]->R[2,1,8]? U[0]->R[2], U[1]->R[5], U[2]->R[8]. Going R[2,5,8]. Same? No: U[0]->R[2] means idx_U[0]=0 and idx_R[0]=2. U[2]->R[8]: idx_U[2]=2, idx_R[2]=8.
# So U[0,1,2]->R[2,5,8]: U[0]->R[2], U[1]->R[5], U[2]->R[8]. And R receives at [2,5,8] from U [0,1,2].
# With right-shift cycle [U,R,...]: R[idx_R[j]]=U[idx_U[j]]. R[2]=U[0], R[5]=U[1], R[8]=U[2]. idx_R=[2,5,8], idx_U=[0,1,2].

# R right col (z=-1 side): R[2]=(y=+1,z=-1)=BUR, R[5]=(y=0,z=-1), R[8]=(y=-1,z=-1)=BDR.
# R[2] at (x=+1,y=+1,z=-1)=BUR. B CW: (x=+1,y=+1)->(+1,-1). BDR=(x=+1,y=-1). +X(R sticker): (1,0)->(0,-1)=-Y=D. BDR on D: D[2]? Wait with D[0]=FDL=(x=-1,z=+1): D[2]=FDR=(x=+1,z=+1). But BDR=(x=+1,z=-1). What D index is BDR?
# D layout: D[0]=FDL,D[1]=FDM,D[2]=FDR,D[3]=MDL,D[4]=center,D[5]=MDR,D[6]=BDL,D[7]=BDM,D[8]=BDR.
# BDR on D = D[8]=(x=+1,z=-1)? Let me verify: D[8]=bottom-right in D's below view. D below view: right=-X (? or +X?). Let me re-examine.
# D[0]=FDL means front-left. D is viewed from below with front at top of view. Right = -X (since right=-X when looking at D from below with front at top? Or right=+X?).
# Wait: when I said D[0]=FDL, I should verify: D[0]=top-left in below-view. If front at TOP of view and right=-X (looking up, right is -X... no.
# Actually: looking at D from below (looking up, +Y direction). If front is at the BOTTOM of the view (standard), or TOP?
# There's ambiguity here. Let me just use:
# D[0]=FDL means F's bottom-left corner D sticker. D[2]=FDR. D[6]=BDL. D[8]=BDR.
# BDR = D[8]. ✓

# R[2]->D[8]: (x=+1,y=+1) at BUR -> BDR after B CW. +X->-Y=D. D[8]=BDR. ✓
# R[8]=(y=-1,z=-1)=BDR. B CW: (x=+1,y=-1)->(-1,-1). BDL=(x=-1,y=-1,z=-1). +X->-Y=D. D[6]=BDL. R[8]->D[6].
# R[2,5,8]->D[8,5,6]? Wait: R[2]->D[8], R[5]->D[5]?, R[8]->D[6]. D receives at [8,5,6]... D[8,5,6] not sequential!
# R[2,5,8] as source, D receives: D[idx_D[j]]=R[idx_R[j]]. D[8]=R[2], D[5]=R[5], D[6]=R[8].
# idx_D=[8,5,6]. Hmm that's weird: [8,5,6] not a standard reversed column.
# Let me re-examine R[5]->D[?]: R[5]=(y=0,z=-1,x=+1)=BMR. B CW: (x=+1,y=0)->(0,-1). BMD=(x=0,y=-1,z=-1). -Y direction +X->? (0,0) for BM... +X direction: (1,0)->(0,-1)=-Y. BMD on D: D[7]? D[7]=(x=0,z=-1)? Wait with D layout: D[0]=FDL, D[1]=FDM, D[2]=FDR, ..., D[6]=BDL, D[7]=BDM=(x=0,z=-1), D[8]=BDR. So (x=0,z=-1)=D[7]. R[5]->D[7].
# R[2,5,8]->D[8,7,6]! ✓ These are D[8]=BDR, D[7]=BDM, D[6]=BDL = D's back row reversed. idx_D=[8,7,6].

# D back row: D[6]=BDL, D[7]=BDM, D[8]=BDR. After B CW:
# D[8]=(x=+1,z=-1)=BDR. B CW: (x=+1,y=-1)->(-1,-1). BDL=(x=-1,y=-1). -Y->-X=L. BDL on L: L[6]=(y=-1,z=-1)=BDL. D[8]->L[6].
# D[6]=(x=-1,z=-1)=BDL. B CW: (x=-1,y=-1)->(-1,+1). BUL=(x=-1,y=+1). -Y->-X=L. BUL on L: L[0]=(y=+1,z=-1)=BUL. D[6]->L[0].
# D[8,7,6]->L[6,3,0]? D[8]->L[6], D[7]->L[3], D[6]->L[0]. ✓ idx_L=[6,3,0].

# L back col: L[0]=BUL=(y=+1,z=-1), L[3]=BML, L[6]=BDL. After B CW:
# L[0]=(y=+1,z=-1,x=-1)=BUL. B CW: (x=-1,y=+1)->(+1,+1). BUR=(x=+1,y=+1). -X(L sticker): (-1,0)->(0,+1)=+Y=U. BUR on U: U[2]=(x=+1,z=-1)=BUR. L[0]->U[2].
# L[6]=(y=-1,z=-1,x=-1)=BDL. B CW: (x=-1,y=-1)->(-1,+1). BUL=(x=-1,y=+1). -X->+Y=U. U[0]=(x=-1,z=-1)=BUL. L[6]->U[0].
# L[0,3,6]->U[2,3,0]? L[0]->U[2], L[3]->U[1], L[6]->U[0]. idx_U=[2,1,0]! Reversed.
# So idx_L=[0,3,6] and idx_U=[2,1,0]. U[2]=L[0], U[1]=L[3], U[0]=L[6]. ✓

# CORRECT B cycle: [('U',[0,1,2]),('R',[2,5,8]),('D',[8,7,6]),('L',[6,3,0])] with right-shift
# = [U[0,1,2], R[2,5,8], D[8,7,6], L[6,3,0]]
# Right-shift: U gets from L, R gets from U, D gets from R, L gets from D.
# U[idx_U[j]]=L[idx_L[j]]: U[2]=L[0], U[1]=L[3], U[0]=L[6]. idx_U=[2,1,0], idx_L=[0,3,6]. Wait: U[0,1,2] getting from... hmm I need to check.
# Cycle [U(k=0),R(k=1),D(k=2),L(k=3)]:
# U(k=0) gets from L(k=3): U[idx_U[j]]=L[idx_L[j]]. U[2]=L[0]: idx_U[0]=2, idx_L[0]=0. idx_U=[2,1,0], idx_L=[0,3,6]. ✓
# R(k=1) gets from U(k=0): R[idx_R[j]]=U[idx_U[j]]. R[2]=U[2]: R[2]=U[0]? No: U[idx_U[j]] = U at position idx_U[j]. idx_U=[2,1,0]: U[2] is first, U[1] second, U[0] third. But U[0,1,2] are the stickers, and they go to R. U[0]->R[2], U[1]->R[5], U[2]->R[8].
# At k=1 (R), gets from U at k=0. U stored after k=0 ran = U's saved values. R[idx_R[j]]=saved_U[j].
# saved_U uses idx_U=[2,1,0]: saved[0]=U[2], saved[1]=U[1], saved[2]=U[0].
# R[idx_R[0]]=U[2]: idx_R[0]=2. ✓ R[idx_R[2]]=U[0]: idx_R[2]=8. idx_R=[2,5,8]. ✓
# D gets from R: D[idx_D[j]]=R[idx_R[j]]: D[8]=R[2], D[7]=R[5], D[6]=R[8]. idx_D=[8,7,6], idx_R=[2,5,8]. ✓
# L gets from D: L[idx_L[j]]=D[idx_D[j]]: L[0]=D[8], L[3]=D[7], L[6]=D[6]. idx_L=[0,3,6], idx_D=[8,7,6]. ✓

# CORRECT B cycle: [('U',[2,1,0]),('R',[2,5,8]),('D',[8,7,6]),('L',[0,3,6])]
# CODE B cycle:    [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]
# Completely different! Different list order and different indices.

print("CORRECT B cycle: [('U',[2,1,0]),('R',[2,5,8]),('D',[8,7,6]),('L',[0,3,6])]")
print("CODE B cycle:    [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]")
print()

# Now also check D cycle:
# D CW (viewed from below): right=+X? I established D[0]=FDL=(x=-1,z=+1).
# If D is viewed from below with front at TOP: right = ?
# Looking at D from below (+Y up, facing -Y direction... hmm).
# Actually for the D cycle, I can derive it from symmetry with U.
# D CW (viewed from below): F->L->B->R->F (opposite direction from U CW which is F->R->B->L).
# D CW from below:  right = -X when looking at D from below? Or +X?
# Let me just compute directly.
# D is at y=-1. D CW (viewed from below, looking +Y): same as CW when viewing from -Y direction (outside).
# Actually "D CW" = D face rotates CW when viewed from below. Looking from -Y toward +Y.
# From -Y looking +Y: right = ?
# facing = +Y = (0,1,0). Let's say front of cube (+Z) appears "up" in this view (you're under the cube looking up, and the F face is in front of you = above you in the view? Or below?).
# Convention: when looking at D from below, F face is toward viewer's feet (at the bottom of the view), like U from above where F is at the bottom.
# If F is at bottom: "up" = -Z. right = ?
# facing +Y, up = -Z: right = up x forward = (-Z) x (+Y) = (0,0,-1)x(0,1,0) = (0*0-(-1)*1, (-1)*0-0*0, 0*1-0*0) = (1,0,0)=+X.
# So looking at D from below with F at bottom: right = +X, up = -Z.
# D[0] = top-left in view = up-left = (-Z, -X) = (x=-1, z=-1) = BDL? But I said D[0]=FDL!
# CONTRADICTION. Let me figure this out.
# If right=+X and up=-Z: D[0]=top-left=(upper=-Z, left=-X)=(z=-1,x=-1)=BDL=(x=-1,z=-1,y=-1).
# But for the net to work correctly (D adjacent to F), D's front row (z=+1) must be at TOP in the net.
# D is below F in the net. D's top row (row 0, D[0,1,2]) in the net is adjacent to F.
# F-adjacent row = front (z=+1) row.
# If D[0]=BDL=(z=-1), then D[0,1,2] = back row (z=-1) = NOT adjacent to F. Problem!
#
# If instead we use convention that F is at TOP when looking at D from below:
# up = +Z (toward F). right = -X (? let me verify).
# facing +Y, up = +Z: right = up x forward = (+Z) x (+Y) = (0,0,1)x(0,1,0) = (0*0-1*1, 1*0-0*0, 0*1-0*0) = (-1,0,0)=-X.
# So right = -X when up = +Z.
# D[0] = top-left = (+Z, +X) = (z=+1, x=-1) = FDL. ✓ D[0]=FDL as I had!
#
# So: looking at D from below with F at TOP of view: right = -X, up = +Z.
# D CW (CW when viewed from -Y with this orientation):
# CW: right->down->left->up = -X -> -Z -> +X -> +Z.
# (x,z) plane: -X->-Z means (x=-1,z=0) goes to (x=0,z=-1). Transformation: (x,z)->(-z,x)?
# Check: (-1,0)->(-0,-1)=(0,-1)=-Z? Hmm: (-z,x) for (-1,0): new_x=-z=0, new_z=x=-1. (0,-1)=-Z? That's the z-direction, but in (x,z) plane (0,-1) means (x=0,z=-1)=z=-1 direction. Not -Z direction but z negative.
# Actually: +X direction for a piece: +X = (1,0) in (x,z). Under D CW: new_x=-z? Let's check:
# -X->-Z should mean: piece at -X direction goes to -Z. For direction vector: -X=(-1,0) in (x,z): new_x=-z=0, new_z=x=-1. (-Z direction) = (0,-1) in (x,z). ✓ So -X->-Z under D CW.
# +Z->-X should follow: +Z=(0,1): new_x=-1, new_z=0. (-1,0)=-X. ✓ +Z->-X.
# Transformation: (x,z)->(-z,x)? Let me verify with +X=(1,0): new_x=-z=0, new_z=x=1. (0,1)=+Z. But +X should go to +Z? CW: -X->-Z->+X->+Z->-X. From -X->-Z: ✓. From +X->+Z: ✓ new_x=0, new_z=1. ✓
# So D CW: (x,z)->(-z,x). ✓

# F bottom -> D front -> B bottom -> L -> F cycle for D CW:
# F[6,7,8] -> L[6,7,8] (same) - this is already in orig code.
# Let me verify: F[6]=(y=-1,x=-1,z=+1)=FDL. D CW: (x=-1,z=+1)->(-1,-1). BDL=(x=-1,y=-1,z=-1).
# +Z sticker: (0,1) in (x,z): new_x=-z=-1, new_z=x=-1? Wait: (x,z)->(-z,x): (0,1)->(-1,0)=-X=L.
# BDL on L: L[6]=(y=-1,z=-1)=BDL. F[6]->L[6]. ✓
# F[8]=(y=-1,x=+1,z=+1)=FDR. D CW: (x=+1,z=+1)->(-1,+1). FDL? (x=-1... wait: new_x=-z=-1, new_z=x=+1. (x=-1,z=+1)=FDL. +Z->-X=L. FDL on L: L[8]=(y=-1,z=+1)=FDL. F[8]->L[8]. ✓ Same idx!
# F[6,7,8]->L[6,7,8]. Code has this. ✓

# L[6,7,8]->B[?]: L[6]=(y=-1,z=-1,x=-1)=BDL. D CW: (x=-1,z=-1)->(+1,-1). Position (x=-1? No: new_x=-z=+1, new_z=x=-1. (x=+1,y=-1,z=-1)=BDR. -X(L sticker): (-1,0) in (x,z): new_x=-z=0, new_z=x=-1. (0,-1)=-Z=B. BDR on B: B[8]=(y=-1,x=+1)=BDR. L[6]->B[8].
# L[8]=(y=-1,z=+1,x=-1)=FDL. D CW: (x=-1,z=+1)->(-1,-1). BDL=(x=-1,y=-1,z=-1). -X->-Z=B. B[6]=(y=-1,x=-1)=BDL. L[8]->B[6].
# L[6,7,8]->B[8,7,6]. Reversed. Code has B[6,7,8] for D cycle. WRONG!
# Should be B[8,7,6].

# B back row [8,7,6]->R[?]: B[8]=(y=-1,x=+1)=BDR. D CW: (x=+1,z=-1): (new_x=-z=+1, new_z=x=+1). Wait: D CW is (x,z)->(-z,x). For z=-1: (x=+1,z=-1)->(-(-1),+1)=(+1,+1). FDR=(x=+1,y=-1,z=+1)? (x=+1,y=-1,z=+1)=FDR. -Z sticker: (0,-1) in (x,z): (-(-1),0)=(+1,0)=+X=R. FDR on R: R[6]=(y=-1,z=+1)=FDR. B[8]->R[6].
# B[6]=(y=-1,x=-1)=BDL. D CW: (x=-1,z=-1)->(+1,-1). BDR=(x=+1,y=-1,z=-1). Wait: new_x=-z=+1, new_z=x=-1. (x=+1,z=-1)=BDR. -Z sticker: (+1,0)=+X=R. R[8]=(y=-1,z=-1)=BDR. B[6]->R[8].
# B[8,7,6]->R[6,7,8]. idx_B=[8,7,6], idx_R=[6,7,8]. But wait: R[6]=FDR (z=+1) and R[8]=BDR (z=-1). The right col of R in the D slice is R[6,7,8]. ✓ Code has D cycle R[6,7,8]. ✓

# R[6,7,8]->F[?]: R[6]=(y=-1,z=+1)=FDR. D CW: (x=+1,z=+1)->(-1,+1). FDL=(x=-1,y=-1,z=+1). +X->+Z=F. F[6]=(y=-1,x=-1)=FDL. R[6]->F[6].
# R[8]=(y=-1,z=-1)=BDR. (x=+1,z=-1)->(+1,+1). FDR=(x=+1,y=-1,z=+1). +X->+Z=F. F[8]=(y=-1,x=+1)=FDR. R[8]->F[8]. ✓ Same idx.
# R[6,7,8]->F[6,7,8]. ✓ Code has F[6,7,8]. ✓

# CORRECT D cycle: [('F',[6,7,8]),('L',[6,7,8]),('B',[8,7,6]),('R',[6,7,8])]
# CODE D cycle:    [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])]
# Only B is wrong: code [6,7,8], should be [8,7,6].

print("CORRECT D cycle: [('F',[6,7,8]),('L',[6,7,8]),('B',[8,7,6]),('R',[6,7,8])]")
print("Only B indices wrong in D cycle: [8,7,6] not [6,7,8]")
print()

_SOLVED = {'U':'W','D':'Y','F':'G','B':'B','R':'R','L':'O'}

_FIXED3 = {
    'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',[2,1,0]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[8,7,6]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[2,1,0]),('L',[8,5,2])]),
    'B': ('B', [('U',[2,1,0]),('R',[2,5,8]),('D',[8,7,6]),('L',[0,3,6])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[8,5,2]),('D',[2,5,8])]),
    'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',[6,3,0]),('U',[0,3,6])]),
}

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

def find_order(cycles, alg, max_n=100):
    ct = CubeTest(cycles)
    for i in range(1, max_n+1):
        ct.apply(alg)
        if ct.is_solved():
            return i
    return None

print("FIXED3 (all 6 cycles corrected):")
tests = [
    ("R L R' L'", "R L R' L'", 1),
    ("U D U' D'", "U D U' D'", 1),
    ("F B F' B'", "F B F' B'", 1),
    ("R U R' U' x6", "R U R' U'", 6),
    ("T-perm x2", "R U R' U' R' F R2 U' R' U' R U R' F'", 2),
    ("Sune x8", "R U R' U R U2 R'", 8),
    ("F-perm x2", "R' U' F' R U R' U' R' F R2 U' R' U' R U R' U R", 2),
]
for name, alg, exp in tests:
    order = find_order(_FIXED3, alg)
    print(f"  {name}: {order} (exp {exp}) {'OK' if order==exp else 'FAIL'}")

for m in ['U','D','F','B','R','L']:
    ct = CubeTest(_FIXED3)
    for _ in range(4): ct.apply(m)
    print(f"  {m}x4: {'OK' if ct.is_solved() else 'FAIL'}")
    ct2 = CubeTest(_FIXED3)
    ct2.apply(m + " " + m + "'")
    print(f"  {m} {m}': {'OK' if ct2.is_solved() else 'FAIL'}")
