_SOLVED = {'U':'W','D':'Y','F':'G','B':'B','R':'R','L':'O'}

cycles_test2 = {
    'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',[2,1,0]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[8,7,6]),('L',[8,5,2])]),
    'B': ('B', [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[8,5,2]),('D',[8,5,2])]),
    'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',[8,5,2]),('U',[0,3,6])]),
}

class CubeTest:
    def __init__(self, cycles):
        self.cycles = cycles
        self.faces = {f: [f+str(i) for i in range(9)] for f in 'UDFBRL'}
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
        return all(self.faces[f] == [f+str(i) for i in range(9)] for f in 'UDFBRL')

# Trace U CW step
print("=== After U CW ===")
ct = CubeTest(cycles_test2)
ct.apply("U")
print("F top row F[0,1,2]:", ct.faces['F'][0], ct.faces['F'][1], ct.faces['F'][2])
print("R top row R[0,1,2]:", ct.faces['R'][0], ct.faces['R'][1], ct.faces['R'][2])
print("B top row B[0,1,2]:", ct.faces['B'][0], ct.faces['B'][1], ct.faces['B'][2])
print("L top row L[0,1,2]:", ct.faces['L'][0], ct.faces['L'][1], ct.faces['L'][2])
print()
print("Expected after U CW (F->R->B->L cycle):")
print("  F top gets L top: F[0]=L0, F[1]=L1, F[2]=L2")
print("  R top gets F top: R[0]=F0, R[1]=F1, R[2]=F2")
print("  B[2,1,0] gets R top: B[2]=R0, B[1]=R1, B[0]=R2")
print("  L top gets B[2,1,0] = [B2,B1,B0]: L[0]=B2, L[1]=B1, L[2]=B0")
print()

# Physical check:
# After U CW: F's top row should get L's top row (L->F).
# F[0](FUL) should get L[2](FUL L-sticker) -> F gets L's FUL sticker. L[2]=FUL. F[0]=L[2]. ✓?
# Wait: L[2]=(y=+1,z=+1)=FUL. This is at FUL corner. For U CW, FUL piece goes to FUR.
# The L[2] sticker is at FUL corner pointing -X. After U CW: BUL piece goes to FUL (BUL->FUL).
# At FUL after U CW: what was at BUL is now here. L[0]=(y=+1,z=-1)=BUL was at BUL.
# L[0] is BUL corner's L-sticker (-X facing). After U CW: BUL->FUL. At FUL, -X direction... still -X=L.
# So at FUL, the new L sticker is the old BUL L-sticker = L[0]. F[0] gets... F[0] is the F-sticker at FUL.
# F[0]=(y=+1,x=-1,z=+1)=FUL F-sticker. After U CW: FUL->FUR. At FUR, F-direction becomes...
# +Z direction (F) transforms under U CW: (x,z)->(z,-x): +Z=(0,1): new_x=z=1, new_z=-x=0. (+1,0)=+X=R.
# So F[0] becomes R-sticker at FUR. R[0]=(y=+1,z=+1)=FUR. F[0]->R[0]. ✓
#
# But which sticker ends up at F[0] after U CW? The piece that ARRIVES at FUL is from BUL.
# At BUL, the F-direction sticker: there is no F sticker at BUL (BUL is at z=-1, F face is at z=+1).
# Actually: F[0] is the sticker on the F face at the FUL corner position. After U CW, what goes to FUL is the BUL piece.
# The BUL piece has stickers: L[0](L-sticker), U[0](U-sticker), B[0](B-sticker). No F sticker.
# For F[0] to get a value after U CW, F[0] receives the sticker that was at BUL with... wait.
# The F face is at z=+1. F[0] is the sticker at FUL corner on the F face. After U CW:
# The piece that arrives at FUL is from BUL. But BUL's stickers are L,U,B - no F sticker!
# This means F[0] doesn't directly receive from any of those. But in U CW, does FUL piece LEAVE or ARRIVE at FUL?
# U CW: FUL->FUR. FUL piece LEAVES. The piece ARRIVING at FUL is BUL piece.
# After U CW, F face at FUL position = what the BUL piece looks like on the F face.
# But BUL piece is at (x=-1,y=+1,z=-1). After U CW, BUL piece moves to FUL=(x=-1,y=+1,z=+1).
# At FUL, the -Z direction is now +Z? No: the PIECE ORIENTATION changes.
# The sticker that was pointing -Z (B face) now points... under U CW: -Z direction = (0,-1) in (x,z).
# (x,z)->(z,-x): (0,-1)->(-(-1),0)=(+1,0)=+X=R. So B[0]'s direction becomes +X=R, NOT +Z=F.
# The F face needs a sticker pointing +Z. After U CW, which old sticker now points +Z?
# L[0]'s direction was -X = (-1,0) in (x,z). After CW: (-1,0)->(0,-(-1))=(0,+1)=+Z=F. YES!
# So L[0] becomes F[0]. F[0] = L[0].
#
# BUT our cycle says F[0] gets from L[0]: F[0] = L[0]. WITH idx_F=[0,1,2] and idx_L=[0,1,2]:
# F[idx_F[j]] = L[idx_L[j]]: F[0]=L[0]. ✓ F[0]=L[0] (original L[0]=L0 label).
# Expected: F[0] = L0 (the original L[0] value). ✓
#
# So U CW: F[0] = L[0]. The code's U cycle with idx_L=[0,1,2] gives F[0]=L[0]. ✓
# Now what about L[0] after U CW?
# L[0] was at BUL. After U CW, BUL moves to FUL. L[0]'s direction was -X.
# After CW: -X=(-1,0): new_x=0, new_z=+1=+Z=F. But F sticker is ALREADY computed.
# L face sticker: L[0] becomes... L face is at x=-1. After U CW, at FUL (x=-1), which sticker points -X?
# FUL corner: which piece is there after U CW? BUL moved to FUL.
# At FUL, the sticker pointing -X: the BUL piece's B sticker was -Z, L sticker was -X, U sticker was +Y.
# After U CW: -X direction -> (0,+1)? No: (x,z)->(z,-x): -X direction = (-1,0): new_x=z=0, new_z=-x=+1. (0,+1)=+Z=F. So BUL's L sticker(-X) now faces F direction. Not L.
# The sticker now at FUL pointing -X: FUL piece originally was at FUL (piece from BUL arrived at FUL, but the FUL piece moved to FUR). So at FUL, the piece is the OLD BUL piece.
# BUL piece stickers: U[0](-Y?? No, U is +Y), B[0](-Z), L[0](-X). After U CW: these directions become: -X->+Z(F), -Z->+X(R), +Y stays +Y. So none of them point -X anymore. L face at FUL = nothing from BUL piece!
# This means the sticker at L face FUL position (L[2]) should now come from the piece that arrived at FUL pointing -X.
# But BUL piece at FUL doesn't have a -X direction sticker. So what gives L[2]?
# WAIT: U CW doesn't affect the FUL position's L sticker for the L face?
# Actually: U CW moves ALL pieces in the y=+1 layer. FUL piece goes to FUR. BUL piece goes to FUL. FUR->BUR. BUR->BUL.
# At FUL after U CW: BUL piece. BUL piece's L sticker (L[0]) now faces +Z (F direction). So L[2] (FUL's L-face position) is... what piece is now at FUL pointing -X? NONE from U CW directly - the sticker at that position on L face would be FUL corner's L sticker, which just moved. But L[2] is determined by the L face of whatever piece is at FUL.
# The piece at FUL after U CW is the old BUL piece. The L face sticker of FUL (L[2]) is whatever was the -X-facing sticker of the BUL piece. That was L[0]! But it now faces +Z (F), not -X (L). Contradiction.
# I think I'm confusing "sticker position" with "sticker direction". Let me be more careful.
# After U CW, for the L face: L[2] is the position at FUL. The sticker displayed there is determined by which ORIGINAL sticker is now at FUL pointing -X.
# Pieces in the top layer: F(z=+1)+U(y=+1) side had FUL piece, which moved to FUR. So at FUL, the piece is BUL.
# BUL piece originally had: L[0] sticker facing -X, B[0] facing -Z, U[0] facing +Y.
# After U CW (CW rotation around +Y): the PIECE is now at FUL, but its orientation has CHANGED.
# The piece rotated with the layer. Its stickers now face:
# Original -X -> new direction: (-1,0) in (x,z) -> (z,-x) = (0,+1)=+Z. -X became +Z.
# Original -Z -> (0,-1) -> (-(-1),0)=(+1,0)=+X. -Z became +X.
# Original +Y -> +Y (rotation is around Y, so +Y stays +Y).
# So at FUL, the BUL piece's stickers face: +Z (L[0] sticker, was -X), +X (B[0] sticker, was -Z), +Y (U[0] sticker).
# For L face (at x=-1), we need the sticker pointing -X. But none of BUL's stickers point -X at FUL.
# For L[2] (at FUL), the sticker is whatever piece is at FUL pointing -X... which is the FUL corner piece pointing -X.
# But FUL piece MOVED TO FUR. So the sticker at L[2] after U CW is... from FUL's piece at FUR position pointing -X?
# NO: FUL piece moved to FUR. At FUR, L face position is L[0] (wait, FUR is (x=+1,y=+1,z=+1). L face is at x=-1. FUR corner has NO L face sticker!
# AH HA! I see the issue now. U CW moves pieces in the TOP LAYER. The TOP LAYER on the L face is L[0,1,2] (top row of L face). These stickers STAY on the L face (since L face doesn't rotate during U CW - U face rotates, not L). But the PIECES change!
# After U CW: the piece at BUL(=L[0] position) moved to FUL(=L[2] position). So L[2] now has the BUL piece's L-sticker = L[0]. And L[0] now has the piece from BDR... no: FUR->BUR->BUL: BUL's piece comes from FUR (since FUL->FUR->BUR->BUL).
# L[0]=BUL: receives piece from FUR (since FUR->BUR would be counterintuitive). Let me trace: U CW cycle: FUL->FUR, FUR->BUR, BUR->BUL, BUL->FUL. So:
# FUL moves to FUR. FUR moves to BUR. BUR moves to BUL. BUL moves to FUL.
# L[0]=BUL position: FUR piece arrives at BUL. FUR piece has R[0] sticker (+X facing). After rotation: +X -> -Z. So the sticker at BUL pointing -X... FUR piece at BUL has stickers facing: +X->-Z (R[0]), +Z->+X (F[0]? No FUR has F and R and U stickers), +Y->+Y (U[8]).
# At BUL, the -X direction: FUR piece doesn't have a sticker pointing -X. B[0] position sticker (B face at BUL) would be from the BUR piece that moved to BUL.
# Wait: BUR moves to BUL. BUR piece has: R[2]=BUR R-sticker (+X facing), B[2]=BUR B-sticker (-Z facing), U[2]=BUR U-sticker (+Y facing). After U CW: +X->-Z, -Z->+X(??)... no wait: U CW rotation:
# Under U CW (rotation of y=+1 layer around +Y): (x,z)->(z,-x).
# +X direction: (1,0)->(0,-1)=-Z. +X -> -Z.
# -Z direction: (0,-1)->(-(-1),0)=(+1,0)=+X. -Z -> +X.
# +Y stays +Y.
# BUR piece moves to BUL. BUR piece's stickers at BUL:
# R[2](was +X, now -Z=B face sticker): at BUL(-Z, -X), pointing -Z = B face. B[0]=BUL B-position.
# B[2](was -Z, now +X=R face sticker): at BUL, pointing +X = R face. But BUL is at x=-1, not x=+1! So this sticker points toward R face but is at x=-1...
# WAIT: After the piece moves from BUR to BUL, the piece is now AT THE BUL CORNER. At BUL corner, the faces meeting are: B face (-Z), L face (-X), and U face (+Y). So the sticker pointing +X at BUL corner is... NOT adjacent to any face (it would be interior to the cube!). The piece's sticker directions changed as the layer rotated.
# The key insight: when BUR piece moves to BUL, its sticker that was pointing +X is now pointing -Z (and vice versa). Let me redo:
# BUR piece at BUR: stickers face +X (R face), -Z (B face), +Y (U face).
# After U CW rotation, this piece moves to BUL. The piece rotates by 90 degrees CW (around +Y).
# The piece's sticker directions rotate too: (x,z) directions rotate by the same transformation.
# Original +X direction (R sticker): (1,0) in (x,z) -> (0,-1)=-Z. At BUL, -Z = B face. So R[2] becomes B[0].
# Original -Z direction (B sticker): (0,-1) -> (1,0)=+X. At BUL, +X is... the interior? At BUL (x=-1,y=+1,z=-1), the sticker pointing +X is the R sticker of BUL. But BUL is at x=-1, and +X points toward L[0] position on L face? No: at the corner (x=-1,y=+1,z=-1), the sticker pointing +X would be... the BUL corner doesn't have an R sticker (R face is at x=+1).
# But wait: the piece MOVED. The piece that was at BUR is now AT BUL. The piece's sticker that was facing -Z is now facing +X. But the piece is at BUL where x=-1. How can a sticker face +X at x=-1? It can: it faces toward the interior of the cube, in the +X direction, but it's still on the OUTSIDE SURFACE at the BUL corner's... wait, this doesn't make sense for a sticker.
#
# OH I SEE: The piece has stickers on THREE faces. When BUR piece is at BUL, its THREE stickers face:
# old +X -> new -Z. The sticker that faces -Z is on the B face.
# old -Z -> new +X. The sticker faces +X. But at BUL corner, +X direction faces INWARD (toward the cube's right side), meaning this is NOT a visible surface!
# This is physically impossible: a corner piece CANNOT have a sticker pointing inward.
# I must be confusing myself. Let me think again.
#
# At BUL corner: the three faces are L(-X), B(-Z), U(+Y). The piece at BUL should have stickers facing -X, -Z, +Y.
# After U CW: BUR moves to BUL. BUR piece had stickers facing +X(R), -Z(B), +Y(U).
# Rotated directions: +X->-Z, -Z->+X, +Y->+Y.
# At BUL: piece has stickers facing: -Z(old +X), +X(old -Z), +Y(old +Y).
# The three faces at BUL are -X, -Z, +Y. The piece has stickers facing -Z, +X, +Y.
# The sticker facing -Z: at BUL facing -Z = B face sticker. ✓
# The sticker facing +Y: at BUL facing +Y = U face sticker. ✓
# The sticker facing +X: at BUL facing +X = R face??? That's WRONG! BUL is at x=-1, not x=+1. R face is at x=+1.
# THE PIECE ORIENTATION IS WRONG because U CW should ONLY rotate pieces that are in the top SLICE, and the rotation should maintain that each corner occupies a valid corner position.
#
# The issue: BUR piece when placed at BUL should have its faces matching BUL's three faces (-X,-Z,+Y), not (-Z,+X,+Y).
# The transformation (x,z)->(z,-x) doesn't preserve the face assignment for the BUR->BUL movement.
#
# Let me reconsider: U CW moves BUR to BUL. BUR is at (x=+1,y=+1,z=-1). BUL is at (x=-1,y=+1,z=-1).
# After transformation (x,z)->(z,-x): (+1,-1)->(-1,-1). New position (x=-1,y=+1,z=-1). ✓ Goes to BUL.
# The rotation of the piece itself (not just its position): the piece at BUR is an actual cube corner.
# When you rotate the U layer CW, the BUR corner piece goes to BUL. During this rotation:
# The piece physically rotates 90 degrees. Its stickers change which face they're on.
# BUR piece: R sticker (at +X face), B sticker (at -Z face), U sticker (at +Y face).
# After rotation to BUL:
# R sticker (pointing +X at BUR): as the piece rotates, what direction does this sticker face at BUL?
# The PIECE rotates CW around Y axis. The +X face of the piece becomes the -Z face.
# So at BUL: old R sticker (was +X) is now the B sticker (facing -Z). B face at BUL = B[0]. ✓
# Old B sticker (was -Z) is now the L sticker (facing +X after rotation? No: -Z face becomes +X?
# Let's use the rotation: CW around Y: +X->-Z->-X->+Z->+X. So +X->-Z means the +X face becomes the -Z face after CW. And -Z->-X: the -Z face becomes the -X face.
# -Z face -> -X face: so BUR's B sticker (facing -Z) at BUL now faces -X = L face. L[0]=BUL. ✓
# +Y stays +Y: U sticker stays at U face. U[0]=BUL. ✓
#
# So BUR piece at BUL: R sticker -> B[0], B sticker -> L[0], U sticker -> U[0].
# R[2](BUR R-sticker) -> B[0]. R[2]->B[0].
# B[2](BUR B-sticker) -> L[0]. B[2]->L[0].
# U[2](BUR U-sticker) -> U[0]. U[2]->U[0].
#
# That's completely different from what I computed before! I was using the WRONG rotation for the piece direction.
# The piece rotation under U CW: +X->-Z, -Z->-X, -X->+Z, +Z->+X.
# (This is the standard rotation: CW from +Y: right-hand rule or just: +X goes to -Z NOT +Z)
# +X -> -Z -> -X -> +Z -> +X. ✓
#
# So CORRECT U CW sticker movement:
# R[2](BUR R-sticker, facing +X) -> B[0] (BUL B-sticker, facing -Z): because piece moved from BUR to BUL, and +X direction rotated to -Z.
# What does F[0]->R[0] mean? Let me re-derive F[0](FUL F-sticker, facing +Z):
# +Z direction under U CW rotation: +Z -> +X. (From the CW rotation table: +Z->+X.)
# FUL piece moves to FUR. At FUR, the sticker that was facing +Z now faces +X = R face. R[0]=(y=+1,z=+1)=FUR. F[0]->R[0]. ✓ (same index)
#
# And L[0](BUL L-sticker, facing -X):
# -X direction under U CW: -X -> +Z. BUL moves to FUL. At FUL, -X becomes +Z = F face. F[0]=(y=+1,x=-1)=FUL. L[0]->F[0]. ✓ (same index)
#
# So the STICKER MOVEMENTS for U CW, top row:
# F[0](FUL, +Z) -> R[0](FUR, +X): +Z->+X ✓
# R[0](FUR, +X) -> B[2](BUR, -Z): +X->-Z ✓ (R[0] at FUR, piece goes to BUR, +X->-Z, B face at BUR = B[2])
# B[2](BUR, -Z) -> L[0](BUL, -X): -Z->-X ✓ (B[2] at BUR, piece goes to BUL, -Z->-X, L face at BUL = L[0])
# L[0](BUL, -X) -> F[0](FUL, +Z): -X->+Z ✓
#
# CORRECT STICKER CYCLE for position 0: F[0]->R[0]->B[2]->L[0]->F[0]
# For position 2 (symmetric): F[2]->R[2]->B[0]->L[2]->F[2]
# For position 1 (edge): F[1]->R[1]->B[1]->L[1]->F[1]
#
# With right-shift on [F,R,B,L]: R gets from F (same idx), B gets from R (B[2]=R[0]), L gets from B (L[0]=B[2]), F gets from L (same idx).
# idx_F=[0,1,2], idx_R=[0,1,2], idx_B=[2,1,0], idx_L=[0,1,2].
# This is: [('F',[0,1,2]),('R',[0,1,2]),('B',[2,1,0]),('L',[0,1,2])]. ✓ Same as what I had!
#
# So our U cycle IS correct. Let me now check R cycle with correct rotation:
# R[0](FUR, +X) under R CW: R CW goes +Y->-Z->-Y->+Z->+Y for the x=+1 slice.
# F[2](FUR, +Z) -> U[2]: +Z direction at FUR, piece moves to BUR, +Z->+Y (R CW: +Z->+Y), U face at BUR = U[2]. ✓
# U[2](BUR, +Y) -> B[8]: +Y->-Z (R CW: +Y->-Z), piece BUR->BDR, -Z face at BDR = B[8]. ✓
# B[8](BDR, -Z) -> D[8]: -Z->-Y (R CW: -Z->-Y), piece BDR->FDR, -Y face at FDR = D[8]. ✓
# D[8](FDR, -Y) -> F[2]: -Y->+Z (R CW: -Y->+Z), piece FDR->FUR, +Z face at FUR = F[2]. ✓
# Sticker cycle: F[2]->U[2]->B[8]->D[8]->F[2] (for right column, position 2)
# F[8]->U[8]->B[2]->D[2]->F[8] (for right column position 8)
# F[5]->U[5]->B[5]->D[5]->F[5] (middle, same idx)
#
# For right-shift [F,U,B,D]: U gets from F (same idx), B gets from U (B[8]=U[2], reversed), D gets from B (D[8]=B[8], same), F gets from D (same idx for reversed).
# Wait: D gets from B. B[idx_B[j]] sources. idx_B=[8,5,2]. B[8] flows, B[5] flows, B[2] flows. D[idx_D[j]]=B[idx_B[j]]. D[8]=B[8], D[5]=B[5], D[2]=B[2]. idx_D=[8,5,2]. Same as B. ✓
# F[idx_F[j]]=D[idx_D[j]]. F[2]=D[8], F[5]=D[5], F[8]=D[2]. idx_F=[2,5,8], idx_D=[8,5,2]. REVERSED!
# Hmm: idx_F=[2,5,8] and idx_D=[8,5,2]. D[8]->F[2], D[5]->F[5], D[2]->F[8]. D[8,5,2]->F[2,5,8]. ✓
# And U gets from F: U[idx_U[j]]=F[idx_F[j]]. U[2]=F[2], U[5]=F[5], U[8]=F[8]. idx_U=[2,5,8], idx_F=[2,5,8]. Same. ✓
# B gets from U: B[idx_B[j]]=U[idx_U[j]]. B[8]=U[2], B[5]=U[5], B[2]=U[8]. idx_B=[8,5,2], idx_U=[2,5,8]. Reversed. ✓
#
# CONFIRMED: R cycle = [('F',[2,5,8]),('U',[2,5,8]),('B',[8,5,2]),('D',[8,5,2])]. ✓
# And U cycle = [('F',[0,1,2]),('R',[0,1,2]),('B',[2,1,0]),('L',[0,1,2])]. ✓
# These are what cycles_test2 has. But Sune still gives order 6!
#
# Let me trace Sune manually by computing R first, then U, then R', then U, then R, then U2, then R':

def apply_step(faces, cycles, move):
    c = cycles[move] if not move.endswith("'") and not move.endswith("2") else cycles[move[:-1]]
    face_name, cycle = c
    c_copy = {f: faces[f][:] for f in 'UDFBRL'}
    # rotate CW
    cf = c_copy[face_name]
    faces[face_name] = [cf[6],cf[3],cf[0], cf[7],cf[4],cf[1], cf[8],cf[5],cf[2]]
    # apply edge cycle
    n = len(cycle)
    saved = [[c_copy[fn][i] for i in idx] for fn, idx in cycle]
    for k in range(n):
        fn, idx = cycle[k]
        src = saved[(k - 1) % n]
        for j, i in enumerate(idx):
            faces[fn][i] = src[j]

faces = {f: [f+str(i) for i in range(9)] for f in 'UDFBRL'}
cycles = cycles_test2

# R:
for _ in range(1): apply_step(faces, cycles, 'R')
print("After R:")
print("  B:", faces['B'])

# U:
apply_step(faces, cycles, 'U')
print("After R U:")
print("  B:", faces['B'])

# Verify: after R U, what is B?
# R puts values at B[8,5,2]. U moves B[2,1,0] (which includes B[2]).
# After R: B[8]=U2_orig, B[5]=U5_orig, B[2]=U8_orig.
# After U: B[2,1,0] shifts to L. L[0]=B[2]=U8_orig.
# So U takes B[2] (which R just set to U8_orig) and moves it to L[0]. The R' will expect B[2] to still be U8_orig.
# But B[2] is now something from R (from L actually: B[idx_B[j]] = R[idx_R[j]]... no: with U right-shift [F,R,B,L]: B gets from R).
# After U: B[2] gets from R[2]. And B[0] gets from R[0]. What was at R before U?
# After R: R top row R[0,1,2] = unchanged (R cycle doesn't affect R's top row... well R is rotated CW).
# Actually R cycle rotates the R face CW, so R[0,1,2,3,4,5,6,7,8] rotates.
print()
print("After R U, R face:", faces['R'])
print("After R U, B face:", faces['B'])
print("After R U, L face:", faces['L'])
