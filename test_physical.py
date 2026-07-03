"""
Test the physical correctness of each cycle empirically.
After each move, verify that:
1. The pieces at the face's interface stickers are correct colors
2. The visual net shows what you'd physically see

Physical conventions:
- White=U, Yellow=D, Green=F, Blue=B, Red=R, Orange=L
- Face indices from 0-8, left-to-right, top-to-bottom when looking at each face from outside.

U face (viewed from above, F side at bottom of view):
  0 1 2   <- back row (adjacent to B)
  3 4 5
  6 7 8   <- front row (adjacent to F)

F face (viewed from front, standard):
  0 1 2   <- top row (adjacent to U bottom)
  3 4 5
  6 7 8   <- bottom row (adjacent to D top)

R face (viewed from right, F side at left):
  0 1 2   <- top row (y=+1)
  3 4 5
  6 7 8   <- bottom row

In the net:
        U(0,1,2 at top = back of U)
L(0..8) F(0..8) R(0..8) B(0..8)
        D(0,1,2 at top = ?)

After F CW: D's front row (adjacent to F) should get R's left column stickers.
Question: is D's front row in the code D[0,1,2] or D[6,7,8]?

Let's figure this out from the F cycle:
F cycle: [U[6,7,8], R[0,3,6], D[2,1,0], L[8,5,2]]
Right-shift: D gets from R. D[2]=R[0], D[1]=R[3], D[0]=R[6].
D[2,1,0] are being set. What is D[2] in 3D?
From my coordinate analysis: D[0]=BDL=(x=-1,z=-1), D[2]=BDR=(x=+1,z=-1).
These are the BACK row of D.
After F CW, D's back row gets R's left column? But F only affects the FRONT slice (z=+1)!
D's front row = D[6,7,8] = FDL,FDM,FDR (z=+1). D's back row = D[0,1,2] (z=-1) should NOT be affected by F CW!

So the original F cycle is WRONG physically: it writes to D[2,1,0] (back row) when it should write to D[6,7,8] (front row).

BUT: this also means my coordinate assignment for D might be wrong!
Let me verify: D[0] should be at what corner?
D face is viewed from below. "Top" in the below view = the row that, when the net is folded, connects to which face?
In the net, D is below F. D's top row (row 0) in the net should connect to F's bottom row.
After folding: D rotates around the horizontal axis between F and D.
D's row 0 (D[0,1,2]) is the top row in the net = the row adjacent to F when folded.
So D[0,1,2] should be ADJACENT TO F = the front row of D in 3D = z=+1 side.
This means D[0]=(x=-1,z=+1)=FDL, D[2]=(x=+1,z=+1)=FDR!

But this contradicts my coordinate analysis. Let me re-derive D face layout.

When looking at D from outside (from below, from -y direction):
The standard WCA convention: when looking at D from below, you typically flip the cube so F side is "up" in your view (or "down"). Let me use a specific convention:

Looking at D from below (-y direction, looking up toward +y), with the cube's FRONT (+z) at the BOTTOM of your view:
- "Up" in your view = -z (back of cube)
- "Right" in your view = +x (same as looking at U from above with same front-orientation)

Wait: if front (+z) is at BOTTOM of your view when looking up at D, that matches how U is viewed from above (front at BOTTOM of view). So D and U have the same "top=back" convention.

D[0] = top-left-in-view = back-left = (x=-1, z=-1) = BDL.
D[6] = bottom-left = front-left = (x=-1, z=+1) = FDL.

BUT: for the net, D is placed BELOW F. D's top edge in the net connects to F's bottom edge.
F's bottom edge = F[6,7,8] = FDL, FDM, FDR (z=+1, y=-1 area).
D's top edge in net = D[0,1,2] row = D[0]=BDL, D[1]=BDM, D[2]=BDR (z=-1 area).

These DON'T match (F's bottom = z=+1, D's top-in-net = z=-1)!

So either:
a) D is stored with a DIFFERENT convention (D[0]=FDL, not BDL), or
b) D is rendered upside-down in the net intentionally

Let me check WHAT MAKES THE VISUAL DISPLAY WORK for the original code.
The original F cycle puts stickers at D[2,1,0] from R[0,3,6].
After F CW: D[0]=R[6], D[1]=R[3], D[2]=R[0]. These show at D's TOP ROW in net = D[0,1,2] = Red.
This means after F CW, D's top row in the net (adjacent to F in the net) shows Red from R's left column.
Physically: after F CW, R's left column stickers ended up... where? They went to D via F cycle.
The VISUAL says D's top = Red, and the top of D is adjacent to F's bottom in the net.
This IS what you'd see on a physical cube: D's stickers adjacent to F changed.

So the ORIGINAL code is correct for F: D[0,1,2] corresponds to D's front row (adjacent to F).
This means D[0] = FDL, not BDL! My coordinate analysis was wrong for D.

Let me reconsider: D is viewed from below. If you hold the cube with front toward you and look UP at D:
- Front of cube (+z) is "up" in your view (toward you as you look up)
- Your right = cube's +x
- D[0] = top-left = front-left = FDL = (x=-1,z=+1,y=-1)
- D[2] = top-right = front-right = FDR = (x=+1,z=+1,y=-1)
- D[6] = bottom-left = back-left = BDL = (x=-1,z=-1,y=-1)
- D[8] = bottom-right = back-right = BDR = (x=+1,z=-1,y=-1)

THIS is the correct D layout! D[0,1,2] = front row, D[6,7,8] = back row.

This means my earlier analysis had D upside-down. With this correction:
- F cycle: D[2,1,0] corresponds to D's front row REVERSED (FDR, FDM, FDL) = correct!
- Original is CORRECT for F cycle's D part.
- My "corrected" F cycle changing D to [8,7,6] is WRONG.
"""

_SOLVED = {'U':'W','D':'Y','F':'G','B':'B','R':'R','L':'O'}
_ORIG = {
    'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',[0,1,2]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[2,1,0]),('L',[8,5,2])]),
    'B': ('B', [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[6,3,0]),('D',[2,5,8])]),
    'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',[8,5,2]),('U',[0,3,6])]),
}

class CS:
    def __init__(self, cycles):
        self.cycles = cycles
        self.faces = {f: [_SOLVED[f]] * 9 for f in 'UDFBRL'}
    def _rcw(self, f):
        c = self.faces[f][:]
        self.faces[f] = [c[6],c[3],c[0], c[7],c[4],c[1], c[8],c[5],c[2]]
    def _cw(self, base):
        if base not in self.cycles: return
        face, cycle = self.cycles[base]
        self._rcw(face)
        n = len(cycle)
        saved = [[self.faces[fn][i] for i in idx] for fn, idx in cycle]
        for k in range(n):
            fn, idx = cycle[k]
            src = saved[(k - 1) % n]
            for j, i in enumerate(idx):
                self.faces[fn][i] = src[j]
    def apply(self, m):
        for tok in m.split():
            if tok.endswith("'"):
                for _ in range(3): self._cw(tok[:-1])
            elif tok.endswith('2'):
                for _ in range(2): self._cw(tok[:-1])
            else:
                self._cw(tok)

# With D[0]=FDL, R[0]=FUR, here are the correct sticker mappings:
# F CW: U bottom -> R left -> D front(rev) -> L right -> U bottom
# U[6,7,8]: U[6]=(x=-1,z=+1)=FUL, U[7]=(x=0,z=+1), U[8]=(x=+1,z=+1)=FUR. Front row. ✓
# R[0,3,6]: R[0]=(y=+1,z=+1)=FUR, R[3]=(y=0,z=+1), R[6]=(y=-1,z=+1)=FDR. Left col (adjacent to F).
#   Wait: R's left column = z=+1 side = R[0,3,6]. ✓ (Adjacent to F since F is z=+1)
# D[2,1,0]: D[0]=(x=-1,z=+1)=FDL, D[1]=(x=0,z=+1), D[2]=(x=+1,z=+1)=FDR. D[2,1,0]=FDR,FDM,FDL reversed. ✓ (Adjacent to F, in reversed order for CW rotation)
# L[8,5,2]: L[2]=(y=+1,z=+1)=FUL, L[5]=(y=0,z=+1), L[8]=(y=-1,z=+1)=FDL. L right col reversed. ✓

# So ORIGINAL F cycle IS CORRECT with D[0]=FDL.
print("ORIGINAL F cycle is physically correct (D[0]=front-left).")
print()

# Now check R cycle:
# R CW: F right -> U right -> B left? -> D right -> F right
# F[2,5,8]: F[2]=(y=+1,x=+1)=FUR, F[5]=(y=0,x=+1), F[8]=(y=-1,x=+1)=FDR. Right col (x=+1 side). ✓
# U[2,5,8]: U[2]=(x=+1,z=-1)=BUR, U[5]=(x=+1,z=0), U[8]=(x=+1,z=+1)=FUR. Right col (x=+1 side). ✓
# B[6,3,0]: B[0]=(y=+1,x=-1)=BUL, B[3]=(y=0,x=-1), B[6]=(y=-1,x=-1)=BDL. LEFT col of B reversed. ✓?
#   Physically: B is adjacent to R at B's x=+1 side (BUR,BMR,BDR) = B[2,5,8]. NOT B[6,3,0]=left col!
#   But wait: with the B face coordinate convention:
#   B is viewed from behind (-z looking toward +z). Right in that view = +x.
#   B[0]=top-left=(y=+1,x=-1)=BUL ✓
#   B[2]=top-right=(y=+1,x=+1)=BUR ✓
#   B[8]=bottom-right=(y=-1,x=+1)=BDR ✓
#   B's x=+1 side = B[2,5,8]. Adjacent to R (x=+1 face). ✓
#   B[6,3,0] = B's x=-1 side = LEFT column of B = adjacent to L face. NOT adjacent to R!
#   So R cycle using B[6,3,0] is WRONG.
print("ORIGINAL R cycle is WRONG: uses B[6,3,0] (adjacent to L) instead of B[2,5,8] (adjacent to R)")
print()

# D[2,5,8]: D[0]=FDL=(x=-1,z=+1), D[2]=FDR=(x=+1,z=+1), D[5]=(x=+1,z=0), D[8]=BDR=(x=+1,z=-1)?
#   Wait with D[0]=FDL=(x=-1,z=+1): D layout:
#   0(FDL) 1(FDM) 2(FDR)
#   3(MDL) 4(center) 5(MDR)
#   6(BDL) 7(BDM) 8(BDR)
#   D's right col = D[2,5,8] = FDR, MDR, BDR = x=+1 column. ✓ Adjacent to R face.
#   R cycle using D[2,5,8] = R's right column (D face). ✓ (x=+1 side of D = adjacent to R)
print("ORIGINAL R cycle D[2,5,8]: D's right col (FDR,MDR,BDR) = adjacent to R face. Correct D part.")
print()

# So R cycle bug: B[6,3,0] should be B[8,5,2] (reversed right col of B = BDR,BMR,BUR).
# Wait: B[2,5,8] = BUR(top-right), BMR(mid-right), BDR(bot-right). Going top-to-bottom from B's perspective.
# After R CW: U[2,5,8] goes to B (reversed). U[2]=BUR should go to B's BUR position.
# But with R CW: the piece at BUR moves to BDR (R CW in the x=+1 slice: +Y->-Z, so BUR y=+1,z=-1 -> y=-1 area... let me just check:
# R CW moves x=+1 slice. BUR=(x=+1,y=+1,z=-1). R CW (y,z)->(z,-y): (y=+1,z=-1)->(-1,-1). (y=-1,z=-1)=BDR. ✓
# U[2]=BUR's U-sticker (+Y). After R CW: +Y direction -> +Y->-Z (R CW: +Y->-Z). At BDR, -Z = B face. B[8]=(y=-1,x=+1)=BDR. U[2]->B[8]. ✓
# U[8]=FUR's U-sticker. FUR=(x=+1,y=+1,z=+1). R CW: (y=+1,z=+1)->(+1,-1)=BUR. +Y->-Z. B[2]=(y=+1,x=+1)=BUR. U[8]->B[2]. ✓
# U[2,5,8]->B[8,5,2]. ✓ CORRECTED R cycle with B[8,5,2] is correct for D convention D[0]=FDL.

print("CORRECTED R cycle: B[8,5,2] (BDR,BMR,BUR reversed) = correct for U->B part of R CW.")
print()

# Now verify D part of R cycle:
# B[8,5,2] (BDR,BMR,BUR) -> D[?]:
# B[8]=BDR=(x=+1,y=-1,z=-1). R CW: (y=-1,z=-1)->(-1,+1). (y=-1,z=+1)=FDR. -Z direction -> +Y? No:
# -Z direction under R CW: (0,-1) in (y,z): (0,-1)->(-(-1),0)=(+1,0)=+Y=U face! But piece is going to FDR...
# Wait: B sticker faces -Z. After R CW: -Z direction: (y-component=0, z-component=-1) -> transformed by (y,z)->(z,-y): (0,-1)->(-(-1),0)=(+1,0)=+Y=U face. But that puts U[something], not D[something]!
# But B[8] piece (at BDR) moves to FDR after R CW. -Z sticker becomes +Y sticker? +Y sticker is on U face.
# FDR has coordinates (x=+1,y=-1,z=+1). But this is below the cube at z=+1... pieces at y=-1 are in the D layer. A sticker at FDR pointing +Y would be on the INSIDE of the cube (between D and F faces). That can't be right.
# Let me recompute: R CW (y,z)->(z,-y). B[8] at (x=+1,y=-1,z=-1)=BDR. After R CW: (y=-1,z=-1)->(z=-1,-y=+1). New position: (x=+1,y=+1,z=-1)=BUR. Not FDR!
# I made an error. Let me redo: (y=-1,z=-1)->(new_y=z=-1, new_z=-y=+1). (y=-1,z=+1)=... wait: new_y=z_old=-1, new_z=-y_old=+1. Position (x=+1,y=-1,z=+1)=FDR. BUT: FDR has y=-1 (it's the BOTTOM right front), which is in the D layer. ✓
# -Z sticker direction: -Z=(0,-1) in (y,z) plane: transformed to (new_y=z=-1, new_z=-y=0)=(-1,0)=-Y=D face. ✓
# D face at FDR = D[2]=(x=+1,z=+1)=FDR. B[8]->D[2]. ✓ (x=+1,z=+1)
# B[2]=BUR=(x=+1,y=+1,z=-1). (y=+1,z=-1)->(z=-1,-y=-1)=(-1,-1). (y=-1,z=-1)=BDR. -Z->(+1,0)=wait: -Z=(0,-1): new_y=-1, new_z=0. (-1,0)=-Y=D. BDR on D: D[8]=(x=+1,z=-1)=BDR. B[2]->D[8]. ✓
# B[8,5,2]->D[2,5,8]. idx_B=[8,5,2] as source, D gets D[idx_D[j]]=B[idx_B[j]]: D[2]=B[8], D[5]=B[5], D[8]=B[2]. idx_D=[2,5,8]. Same as ORIGINAL! Code has D[2,5,8]. ✓
print("ORIGINAL R cycle D[2,5,8] is correct for B->D part with D[0]=FDL convention.")
print()

# Summary: Original R cycle is wrong ONLY in B part: should be B[8,5,2] not B[6,3,0].
# D[2,5,8] is actually correct!

# Let me also verify U cycle with D[0]=FDL:
# U CW: F->R->B->L cycle for top row.
# F[0,1,2]->R[0,1,2]->B[2,1,0]->L[0,1,2] (from my analysis above). Only B is reversed.
# Let me verify R[0]->B[?] with D[0]=FDL:
# R[0]=(y=+1,z=+1)=FUR. U CW: (x=+1,z=+1): new_x=+1, new_z=-1. BUR. +X direction: (1,0)->(0,-1)=-Z=B.
# BUR on B: B[2]=(y=+1,x=+1)=BUR. R[0]->B[2]. ✓ (B gets R[0] at B[2] position)
# B[2]->L[?]: B[2]=BUR. (x=+1,z=-1)->(z=-1,x'=+1? No: (x,z)->(z,-x): (+1,-1)->(-1,-1)=BUL. -Z: (0,-1)->(+1,0)=+X? No: U CW (x,z)->(z,-x): -Z direction (0,-1)->(z=-1,-x=0)=(-1,0)=-X=L. BUL on L: L[0]=(y=+1,z=-1)=BUL. B[2]->L[0]. ✓
# So: R[0]->B[2], B[2]->L[0]. With right-shift: B[idx_B[j]]=R[idx_R[j]], L[idx_L[j]]=B[idx_B[j]].
# idx_R=[0,1,2]: B[idx_B[0]]=R[0]. R[0]->B[2]: idx_B[0]=2. B[idx_B[1]]=R[1]. R[1]->B[1]: idx_B[1]=1. B[idx_B[2]]=R[2]. R[2]->B[0]: idx_B[2]=0. idx_B=[2,1,0]. ✓ CORRECTED U cycle.
print("CORRECTED U cycle: B[2,1,0] is correct. Original B[0,1,2] is wrong.")
print()

# So the ONLY bugs are:
# R cycle: B[6,3,0] -> should be B[8,5,2]
# U cycle: B[0,1,2] -> should be B[2,1,0]
# All other cycles are correct (original F, D, B, L cycles are fine)!

# Let me now test ONLY these two changes:
_FIXED = {
    'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',[2,1,0]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[2,1,0]),('L',[8,5,2])]),
    'B': ('B', [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[8,5,2]),('D',[2,5,8])]),
    'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',[8,5,2]),('U',[0,3,6])]),
}

def find_order(cycles, alg, max_n=100):
    ct = CS(cycles)
    for i in range(1, max_n+1):
        ct.apply(alg)
        if ct.is_solved():
            return i
    return None

print("Testing FIXED cycles (only U.B and R.B changed):")
tests = [
    ("R U R' U' x6", "R U R' U'", 6),
    ("T-perm x2", "R U R' U' R' F R2 U' R' U' R U R' F'", 2),
    ("Sune x8", "R U R' U R U2 R'", 8),
    ("F-perm x2", "R' U' F' R U R' U' R' F R2 U' R' U' R U R' U R", 2),
]
for name, alg, exp in tests:
    order = find_order(_FIXED, alg)
    print(f"  {name}: {order} (exp {exp}) {'OK' if order==exp else 'FAIL'}")

for m in ['U','D','F','B','R','L']:
    ct = CS(_FIXED)
    for _ in range(4): ct.apply(m)
    print(f"  {m}x4: {'OK' if ct.is_solved() else 'FAIL'}")
