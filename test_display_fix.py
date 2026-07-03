# The issue: B stickers are stored with the WRONG orientation.
# After R CW: B[0,3,6] (left col from behind) gets White, but physically R should put White at B[2,5,8] (right col from behind).
# This is because the R cycle has a bug: uses B[6,3,0] instead of B[8,5,2].
#
# For the DISPLAY to be correct, we need the B face in the net to show:
# - B[2,5,8] (right col from behind) as the LEFT column in the net (adjacent to R)
# This means B must be drawn LEFT-RIGHT MIRRORED.
#
# BUT: if we just mirror B in drawing without fixing the simulation, will the net be correct?
# Let's check: after R CW with the ORIGINAL (buggy) cycles:
# B face: B[0]=W, B[3]=W, B[6]=W (left col = White), rest = Blue.
# Drawing B mirrored (B[2-c] for column c):
# B drawn col 0 = B[2,5,8] = Blue, Blue, Blue (right col from behind)
# B drawn col 2 = B[0,3,6] = White, White, White (left col from behind)
# Net shows: B left (adjacent to R) = Blue, B right = White.
# But physically: B left (adjacent to R) should show White (from U), B right should show Blue.
# WRONG DIRECTION! The mirroring would show Blue adjacent to R, but White should be adjacent to R.
#
# So just mirroring B is NOT the fix.
#
# The real fix must be in the simulation cycles.
#
# Let me try a different approach: what if I DON'T touch B in the R cycle at all?
# And instead, accept that B may be stored in a non-standard way, but find cycles that
# make the VISUAL DISPLAY consistent?
#
# Actually wait - maybe the SIMPLEST fix is:
# The R cycle should use B[2,5,8] instead of B[6,3,0]. Let me check if this alone fixes things.
# With B[2,5,8]: B[2]=W, B[5]=W, B[8]=W after R CW (right col = White).
# Net (no mirror): B[2,5,8]=White on right side = correct for physical net.
#
# But earlier when I tested "Only R corrected" (with B=[8,5,2]), R U R' U' gave None (infinite order).
# That's because changing R's B mapping changes what R' reads back from B, and U also interacts with B.
#
# WAIT: I think I see the issue now. The U cycle uses B[0,1,2] (top row).
# Original U: B[0,1,2] are the BACK ROW of B = adjacent to U.
# After U CW: B[0,1,2] gets R[0,1,2] (R's top row).
# R[0,1,2] = R's top row. With ORIGINAL R layout: R[0]=FUR (z=+1), R[1]=FMR, R[2]=BUR.
# So B[0,1,2] = R's top row = [FUR, top-mid, BUR].
# But physically: after U CW, B's back row (adjacent to U) should get R's RIGHT COLUMN.
# B's back row from behind = B[0,1,2] going from left(BUL) to right(BUR).
# R's right column going top to bottom = R[2,5,8] = BUR,BMR,FDR. After U CW: B's row goes right to left (because R's right stickers arrive at B's right-to-left direction).
#
# With corrected U: B[2,1,0] gets R[2,1,0]. B[2]=BUR=R[2]=BUR's R sticker -> B[2]=R sticker.
# After U CW: R's right column (R[0]=FUR, R[1]=FMR, R[2]=BUR) goes to B.
# U CW moves the y=+1 layer. R[2]=(y=+1,z=-1)=BUR -> after CW in XZ plane: (x=+1,z=-1)->(z=-1,-x=-1)=(-1,-1). Position (x=-1,y=+1,z=-1)=BUL. +X direction (R sticker): (1,0)->(0,-1)... wait U CW is (x,z)->(z,-x): (1,-1)->(-1,-1)=(x=-1,y=+1,z=-1)=BUL. R sticker direction +X: (1,0)->(0,-1)=-Z=B face. BUL on B: B[0]=(y=+1,x=-1)=BUL. R[2]->B[0].
# But with corrected U cycle: B[2] gets R[2]. B[2]=BUR ≠ B[0]=BUL. Wrong!
# The correct result: R[2]->B[0]. So B[0] should get R[2].
# With corrected U [B[2,1,0] paired with R[2,1,0]]: B[2]=R[2]. But should be B[0]=R[2]. Mismatch!
#
# So my "corrected" U cycle is WRONG. The correct mapping should have B[0] getting R[2], not B[2].
# For B[0]=R[2]: cycle has R at some position j where idx_R[j]=2 and idx_B[j]=0.
# With list [F,R,B,L] right-shift: B gets from R at position j: B[idx_B[j]]=R[idx_R[j]].
# B[0]=R[2]: idx_B[0]=0, idx_R[0]=2. idx_R starts with 2. R[0,1,2] maps to B[?,?,?].
# R[0]->B[?]: R[0]=(y=+1,z=+1)=FUR. U CW: (x=+1,z=+1)->(+1,-1)=(new_x=+1,new_z=-1)=BUR. +X->-Z=B. BUR=B[2]. R[0]->B[2]. idx_B[j_for_R[0]]=2. If idx_R=[2,1,0]: position j where idx_R[j]=0 is j=2. B[idx_B[2]]=R[0]. B[2]=R[0]. So R[0]->B[2], R[1]->B[1], R[2]->B[0]. ✓ with idx_B=[0,1,2] and idx_R=[2,1,0].
# My original "corrected" U had idx_R=[2,1,0] and idx_B=[2,1,0]. WRONG for B.
# Correct: idx_R=[2,1,0], idx_B=[0,1,2].
# So the CORRECT U cycle is:
# [('F',[0,1,2]), ('R',[2,1,0]), ('B',[0,1,2]), ('L',[0,1,2])]
# Only R is reversed, B stays [0,1,2]!

# Let me verify L->F and B->L:
# R[2]->B[0] (from above). idx_R=[2,1,0], idx_B=[0,1,2]: B[0]=R[2], B[1]=R[1], B[2]=R[0]. ✓ R[2]->B[0]. ✓
# B[0]->L[?]: B[0]=(y=+1,x=-1,z=-1)=BUL. U CW: (x=-1,z=-1): new_x=z=-1, new_z=-x=+1. FUL=(x=-1,y=+1,z=+1). -Z direction: (0,-1)->(+1,0)? Hmm: (x,z)->direction. -Z direction = (0,-1) in (x,z): new_x=z=-1, new_z=-x=+0=0? (0,-1): new_x=-1, new_z=0. That's (-1,0)=-X=L face. FUL on L: L[2]=(y=+1,z=+1)=FUL. B[0]->L[2].
# B[2]->L[?]: B[2]=(y=+1,x=+1,z=-1)=BUR. (x=+1,z=-1): new_x=-1,new_z=-1. BUL. -Z direction: new_x=-1,new_z=0. -X=L. BUL on L: L[0]=(y=+1,z=-1)=BUL. B[2]->L[0].
# B[0,1,2]->L[2,1,0]. idx_B=[0,1,2] as source, L gets at [2,1,0]: L[2]=B[0], L[1]=B[1], L[0]=B[2]. ✓
# So idx_L=[2,1,0]. But I need to check idx_B and idx_L in context: L[idx_L[j]] = B[idx_B[j]].
# With idx_B=[0,1,2] and cycle has L after B (L[idx_L[j]]=B[idx_B[j]]):
# L[idx_L[0]]=B[0] -> L[?]=B[0]. B[0]->L[2]: idx_L[0]=2. B[1]->L[1]: idx_L[1]=1. B[2]->L[0]: idx_L[2]=0. idx_L=[2,1,0].
#
# L[2,1,0]->F[?]: L[2]=(y=+1,z=+1,x=-1)=FUL. (x=-1,z=+1): new_x=+1, new_z=+1. FUR. -X direction: (-1,0): new_x=z=+1, new_z=-x=+1. (+1,+1)=... wait that's not a unit direction. Actually -X direction = (-1,0) in (x,z). After (x,z)->(z,-x): (-1,0)->(0,+1)=+Z=F. FUR on F: F[2]=(y=+1,x=+1). L[2]->F[2].
# L[0]=(y=+1,z=-1,x=-1)=BUL. (x=-1,z=-1): new_x=-1, new_z=+1. FUL. -X->+Z=F. F[0]=(y=+1,x=-1)=FUL. L[0]->F[0].
# L[2,1,0]->F[2,1,0]. idx_L=[2,1,0] as source, F gets at [2,1,0]?
# F[idx_F[j]] = L[idx_L[j]]: F[idx_F[0]]=L[2]. L[2]->F[2]: idx_F[0]=2. L[1]->F[1]: idx_F[1]=1. L[0]->F[0]: idx_F[2]=0. idx_F=[2,1,0].
# But idx_F should match the original idx_F=[0,1,2]! For F[0,1,2] going to R... hmm.
# Actually there's NO requirement that idx_F=[0,1,2]. The cycle just says which positions are involved.
# But if idx_F=[2,1,0] (cycle says F[2]=from_L, F[1]=from_L, F[0]=from_L):
# Then for the F->R part: R[idx_R[j]] = F[idx_F[j]]. F[2]->R[2], F[1]->R[1], F[0]->R[0] with idx_R=[2,1,0].
# But we need: F[0]->R[2] (F[0]=FUL, after U CW goes to R[2]=BUR on R face? Let me verify:
# F[0]=(y=+1,x=-1,z=+1)=FUL. U CW: (x=-1,z=+1): new_x=+1, new_z=+1. FUR=(x=+1,y=+1,z=+1). +Z direction: (0,+1)->(+1,0)=+X=R. FUR on R: R[0]=(y=+1,z=+1)=FUR. F[0]->R[0]. NOT R[2]!
# I made an error earlier! F[0]=(FUL) -> R[0]=FUR. NOT reversed!
# Let me recheck: FUL=(x=-1,y=+1,z=+1). U CW: (x,z)->(z,-x): (-1,+1)->(+1,+1). (x=+1,y=+1,z=+1)=FUR. FUR on R: R[0]=(y=+1,z=+1)=FUR. F[0]->R[0]. SAME INDEX!
# F[2]=(y=+1,x=+1,z=+1)=FUR. (x=+1,z=+1)->(+1,-1). BUR=(x=+1,y=+1,z=-1). R[2]=(y=+1,z=-1)=BUR. F[2]->R[2]. SAME!
# So F[0]->R[0], F[1]->R[1], F[2]->R[2]. F[0,1,2] -> R[0,1,2]. SAME INDICES. My earlier coordinate analysis was WRONG for F->R!

print("CORRECTED ANALYSIS:")
print("F[0](FUL) after U CW -> FUR = R[0]. F[0]->R[0]. (same index)")
print("F[2](FUR) after U CW -> BUR = R[2]. F[2]->R[2]. (same index)")
print()
print("So the CORRECT U cycle is:")
print("[('F',[0,1,2]), ('R',[0,1,2]), ('B',[0,1,2]), ('L',[2,1,0])]")
print("Only L is reversed!")
print()
print("Wait, let me also verify B[0,1,2]->L[2,1,0]:")
print("B[0]->L[2], B[2]->L[0] (as derived above)")
print("And L->F: L[2]->F[2], L[0]->F[0] (same indices when idx_L=[2,1,0]? NO: idx_L=[2,1,0] means L[2] first.)")
print("With cycle [F,R,B,L] and idx_L=[2,1,0]: F[idx_F[j]]=L[idx_L[j]]: F[idx_F[0]]=L[2].")
print("L[2]->F[2] means idx_F[0]=2, so idx_F=[2,1,0]. But then F[2]->R[2] with idx_R=[2,1,0]")
print("means R[idx_R[0]]=F[idx_F[0]]: R[2]=F[2]. But we need F[2]->R[2] and F[0]->R[0].")
print("With idx_F=[2,1,0] and idx_R=[2,1,0]: R[2]=F[2]. That means F[2]->R[2].")
print("But there's no F[0]->R[0] in this... wait: R[idx_R[j]]=F[idx_F[j]].")
print("j=0: R[2]=F[2]. j=1: R[1]=F[1]. j=2: R[0]=F[0]. F[0]->R[0] ✓, F[2]->R[2] ✓.")
print()
print("So idx_F=[2,1,0] and idx_R=[2,1,0] gives F[2]->R[2], F[1]->R[1], F[0]->R[0]. Correct!")
print()
print("Final check: does idx_L=[2,1,0] and idx_F=[2,1,0] work for L->F?")
print("F[2]=L[2], F[1]=L[1], F[0]=L[0]. L[0]->F[0], L[2]->F[2].")
print("But we need L[2]->F[2] and L[0]->F[0]. Same check: ✓")
print()
print("But wait: for B->L, we derived B[0]->L[2], B[2]->L[0].")
print("B[idx_B[j]] stored at B[0,1,2] (idx_B=[0,1,2] from previous analysis)")
print("L[idx_L[j]]=B[idx_B[j]]: L[2]=B[0], L[1]=B[1], L[0]=B[2]. So B[0]->L[2]. ✓")
print("idx_L=[2,1,0] and idx_B=[0,1,2].")
print()
print("But idx_F=[2,1,0] means F is READ from position [2,1,0] (as source for R)")
print("AND WRITTEN at position [2,1,0] (as destination from L).")
print("With idx_L=[2,1,0]: L[2]=B[0] (position j=0: idx_L[0]=2, idx_B[0]=0)")
print("With idx_F=[2,1,0]: F[2]=L[2] (j=0: idx_F[0]=2, idx_L[0]=2): F[2]=L[2]=B[0]. ✓ (F[2]<-B[0])")
print()
print("So CORRECT U cycle: [('F',[2,1,0]), ('R',[2,1,0]), ('B',[0,1,2]), ('L',[2,1,0])]")
print("OR equivalently with F[0,1,2] as-is: we need to verify R[0,1,2] directly.")

# WAIT: I derived F[0]->R[0] (same), and separately B[0]->L[2] (reversed), L[2]->F[2] (reversed).
# These create a cycle of length: F[0] -> R[0] -> B[0] -> L[2] -> F[2] -> R[2] -> B[2] -> L[0] -> F[0].
# This is NOT a simple single-index cycle! It's two separate orbit paths?
# F[0]->R[0]->B[0]->L[2]->F[2]->R[2]->B[2]->L[0]->F[0]: length 8!
# For U CW to be valid, we should have cycles of length 3 (for edge pieces) or 4 (for corner pieces, since there are 4 corners).
# A U CW move has: 4 corner pieces cycling, 4 edge pieces cycling. That gives two 4-cycles.
# Sticker positions involved: for top row [0,1,2] of each of F,R,B,L:
# Position 0 of each = corner stickers (4 corners of U).
# Position 1 of each = edge stickers (4 edges of U).
# Position 2 of each = other corner stickers.
# Corners cycle: F[0]->R[0]->B[0]->L[0]->F[0] for one set, F[2]->R[2]->B[2]->L[2]->F[2] for another.
# Edges cycle: F[1]->R[1]->B[1]->L[1]->F[1].
#
# So corner sticker cycle 1: F[0]->R[0]->B[0]->L[0]->F[0]. Same indices!
# Corner sticker cycle 2: F[2]->R[2]->B[2]->L[2]->F[2]. Same indices!
# Edge cycle: F[1]->R[1]->B[1]->L[1]->F[1]. Same indices!
# THEREFORE: U cycle should be [F[0,1,2],R[0,1,2],B[0,1,2],L[0,1,2]] with ALL SAME INDICES!
#
# But wait: I computed F[0]->R[0] (same) but B[0]->L[2] (reversed). Let me recheck B->L:
# B[0]=(y=+1,x=-1,z=-1)=BUL. U CW: (x=-1,z=-1): new_x=-1, new_z=+1. FUL=(x=-1,y=+1,z=+1).
# -Z direction: (0,-1) in (x,z) -> (z,-x) = (-1,0)?? Wait: (x,z)->(z,-x): (0,-1)->(-(-1),0)=(+1,0)=+X. That's R face!
# -Z direction = sticker pointing in -Z direction (B face is -Z plane, sticker points outward = in -Z direction).
# After U CW: this direction rotates. -Z direction vector = (x=0,y=0,z=-1). Rotation around Y axis:
# U CW: (x,z)->(z,-x). For direction vector: new_x=z=-1, new_z=-x=0. New direction: (x=-1,y=0,z=0)=-X=L face!
# So B stickers (pointing -Z) become L stickers (pointing -X) after U CW. ✓
#
# B[0]=(y=+1,x=-1,z=-1)=BUL corner. The sticker at BUL pointing -Z.
# After U CW: piece at BUL moves to FUL=(x=-1,y=+1,z=+1). Sticker now points -X (L face).
# FUL on L face: L[2]=(y=+1,z=+1)=FUL. B[0]->L[2]. ✓ (confirmed B[0] goes to L[2], NOT L[0])
#
# But for the 4-cycle: U CW should cycle corners as FUL->FUR->BUR->BUL->FUL.
# At FUL: B sticker is B face sticker (there is no B sticker at FUL, only F, U, L stickers!).
# OH WAIT: BUL corner has B, U, L stickers. FUL corner has F, U, L stickers. These are DIFFERENT corners!
# The U CW cycle moves pieces: FUL->FUR->BUR->BUL->FUL.
# Sticker B[0] is at BUL corner (back-up-left). It moves to FUL corner (after U CW: BUL->FUL? Let me check).
# BUL=(x=-1,y=+1,z=-1). U CW: (x=-1,z=-1)->(z=-1,-x=+1). So new (x=+1,y=+1,z=-1)=BUR? No: new_x=z=-1, new_z=-x=+1. (x=-1... wait: new_x=z_old and new_z=-x_old. x_old=-1,z_old=-1: new_x=-1, new_z=+1. So (x=-1,y=+1,z=+1)=FUL.
# BUL MOVES TO FUL. So U CW moves the BACK corners to FRONT (BUL->FUL,BUR->FUR,FUL->FUR? No wait):
# U CW piece movement (all corners at y=+1):
# FUL=(-1,+1,+1): (x=-1,z=+1)->(+1,+1). FUR=(+1,+1,+1). FUL->FUR.
# FUR=(+1,+1,+1): (x=+1,z=+1)->(+1,-1). BUR=(+1,+1,-1). FUR->BUR.
# BUR=(+1,+1,-1): (x=+1,z=-1)->(-1,-1)... wait new_x=z_old=-1, new_z=-x_old=-1. BDL?? No: (x=-1,y=+1,z=-1)=BUL. BUR->BUL.
# BUL=(-1,+1,-1): (x=-1,z=-1)->(-1,+1). FUL. BUL->FUL.
# So cycle: FUL->FUR->BUR->BUL->FUL. ✓ (CW from above)
#
# B sticker B[0] is at BUL. BUL moves to FUL (as computed). AT FUL, the B-direction sticker becomes L-direction (as computed). FUL has L[2] sticker. B[0]->L[2]. ✓
#
# But for the cycle F[0]->R[0]->B[0]->L[0]->F[0] to be valid, B[0] should go to L[0], not L[2].
# B[0] is at BUL (not FUL or FUR). It goes to L[2] (FUL position, L sticker).
# The CORNER STICKER CYCLE for BUL corner:
# BUL has stickers: B[0]=BUL B-sticker, U[0]=BUL U-sticker, L[0]=BUL L-sticker.
# After U CW: BUL->FUL. At FUL:
# - B[0](B-sticker) at BUL becomes L-sticker at FUL = L[2]. ✓
# - U[0](U-sticker) at BUL remains U-sticker but at FUL = U[6]. U[0]->U[6].
# - L[0](L-sticker) at BUL becomes F-sticker at FUL = F[0]. L[0]->F[0]. ✓ SAME INDEX!
#
# So: L[0]->F[0] (same) but B[0]->L[2] (different). The cycle is NOT consistent with same indices.
# FUL corner cycle (U CW: FUL->FUR): F[0](FUL F-sticker)->R[0](FUR R-sticker), U[6]->U[8], L[2]->F[2].
#
# Cycle for position-0 stickers:
# F[0](FUL F-sticker) -> R[0](FUR R-sticker) after FUL->FUR. ✓ (F[0]->R[0], same index)
# R[0](FUR R-sticker) -> B[?]: FUR->BUR after U CW. R-sticker becomes B-sticker? No: R[0]=FUR's R-sticker.
# FUR moves to BUR. At BUR, R-direction sticker: R direction is +X. After U CW: +X direction: (1,0) in (x,z) -> (0,-1)=-Z=B face. B[2]=(y=+1,x=+1)=BUR. R[0]->B[2]. NOT B[0]!
#
# So the sticker cycle for position 0 is:
# F[0](FUL)->R[0](FUR)->B[2](BUR)->L[0](BUL)->F[0](FUL).
# DIFFERENT indices! F[0]->R[0]->B[2]->L[0]->F[0].
#
# This means the 4-cycle goes F[0]->R[0] (same), R[0]->B[2] (REVERSED TO 2), B[2]->L[0] (but above I said B[0]->L[2]...
# Let me check B[2]->L[?]: B[2]=(y=+1,x=+1,z=-1)=BUR. U CW: (x=+1,z=-1)->(-1,-1). BUL=(x=-1,y=+1,z=-1). -Z direction: (0,-1)->(+1,0)=+X. That would be R, not L!
# Wait: (x,z)->(z,-x): (0,-1): new_x=z=-1, new_z=-x=0. (-1,0)=-X=L. BUL on L: L[0]=(y=+1,z=-1)=BUL. B[2]->L[0]. ✓
#
# So: F[0]->R[0]->B[2]->L[0]->F[0]. These form the cycle for the BUL/FUL/FUR/BUR corner cluster!
# The sticker travels: F[0](at FUL F-sticker) -> R[0](FUR R-sticker) -> B[2](BUR B-sticker) -> L[0](BUL L-sticker) -> F[0].
#
# This is a 4-cycle involving F[0], R[0], B[2], L[0]. NOT all same indices.
# The correct U CW cycle representation:
# At position j=0: involves F[0], R[0], B[2], L[0].
# At position j=1: F[1], R[1], B[1], L[1] (edge, symmetric).
# At position j=2: F[2], R[2], B[0], L[2].
#
# For the algorithm: B[j] = R[idx_R[j]], and B[idx_B[j]] = R[idx_R[j]].
# With idx_R=[0,1,2] and B's index being 2 when j=0: idx_B[0]=2. And idx_B[2]=0.
# idx_B=[2,1,0]. And idx_R=[0,1,2].
# L[idx_L[j]] = B[idx_B[j]]: L[?]=B[2](j=0). B[2]->L[0]: idx_L[0]=0. B[1]->L[1]: idx_L[1]=1. B[0]->L[2]: idx_L[2]=2.
# idx_L=[0,1,2]. Same! And F[idx_F[j]]=L[idx_L[j]]: F[?]=L[0](j=0). L[0]->F[0]: idx_F[0]=0. idx_F=[0,1,2]. Same!
#
# FINAL CORRECT U CYCLE: [('F',[0,1,2]), ('R',[0,1,2]), ('B',[2,1,0]), ('L',[0,1,2])]
# ONLY B IS REVERSED.
#
# Let me verify: with right-shift [F,R,B,L]: R gets from F, B gets from R, L gets from B, F gets from L.
# R[0]=F[0], R[1]=F[1], R[2]=F[2]: F[0]->R[0], F[2]->R[2]. ✓
# B[2]=R[0], B[1]=R[1], B[0]=R[2]: R[0]->B[2], R[2]->B[0]. ✓
# L[0]=B[2], L[1]=B[1], L[2]=B[0]: B[2]->L[0], B[0]->L[2]. ✓
# F[0]=L[0], F[1]=L[1], F[2]=L[2]: L[0]->F[0]. ✓
# PERFECT!

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

# Test with corrected U (B=[2,1,0]) and corrected R (B=[8,5,2], D=[8,5,2])
cycles_test = {
    'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',[2,1,0]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[2,1,0]),('L',[8,5,2])]),
    'B': ('B', [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[8,5,2]),('D',[8,5,2])]),
    'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',[8,5,2]),('U',[0,3,6])]),
}

print("U corrected (B=[2,1,0]) + R corrected:")
print("  Sune:", find_order(cycles_test, "R U R' U R U2 R'"), "(expected 8)")
print("  R U R' U' x6:", find_order(cycles_test, "R U R' U'"), "(expected 6)")
print("  T-perm x2:", find_order(cycles_test, "R U R' U' R' F R2 U' R' U' R U R' F'"), "(expected 2)")
for m in ['U','D','F','B','R','L']:
    ct=CubeTest(cycles_test); [ct.apply(m) for _ in range(4)]
    print(f"  {m}x4:", "OK" if ct.is_solved() else "FAIL")
