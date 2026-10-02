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

def test_cycles(cycles, label=""):
    tests = [
        ("R U R' U' x6", "R U R' U'", 6),
        ("T-perm x2", "R U R' U' R' F R2 U' R' U' R U R' F'", 2),
        ("Sune x8", "R U R' U R U2 R'", 8),
        ("F-perm x2", "R' U' F' R U R' U' R' F R2 U' R' U' R U R' U R", 2),
    ]
    results = []
    all_ok = True
    for name, alg, expected_order in tests:
        order = find_order(cycles, alg)
        ok = order == expected_order
        if not ok: all_ok = False
        results.append(f"  {name}: {order} (exp {expected_order}) {'OK' if ok else 'FAIL'}")
    print(f"{label}: {'ALL OK' if all_ok else 'FAIL'}")
    for r in results: print(r)
    return all_ok

# Let me try a COMPLETELY DIFFERENT approach: use face-index representation where each face
# has stickers laid out consistently from a single fixed viewpoint.
# Convention: face indices from 0-8, row-major, left-to-right, top-to-bottom, viewed from outside.
# The key: the face orientation when looking at each face from outside the cube.
#
# From my correct coordinate analysis:
# U face: viewed from above. Top = -Z (back), right = +X.
# U[0]=(-X,-Z), U[2]=(+X,-Z), U[6]=(-X,+Z), U[8]=(+X,+Z)
# F face: viewed from front. Top = +Y, right = +X.
# F[0]=(-X,+Y), F[2]=(+X,+Y), F[6]=(-X,-Y), F[8]=(+X,-Y)
# R face: viewed from right (looking -X), left=+Z(front), right=-Z(back). Top=+Y.
# R[0]=(+Z,+Y), R[2]=(-Z,+Y), R[6]=(+Z,-Y), R[8]=(-Z,-Y)
# Wait I established R[0]=FUR=(+Z,+Y)=(z=+1,y=+1) and right=-Z. So R[0]=top-LEFT means (+Y,+Z)=(y=+1,z=+1)=FUR.
# Hmm let me re-examine. "Top-left" when looking -X with left=+Z: R[0]=(+Y,+Z)=(y=+1,z=+1)=FUR.
# D face: viewed from below. "top" = +Z (front), right = -X (i.e., looking +Y from below, right=-X).
# Actually I established D[0]=(x=-1,z=-1) with viewing from below with front at bottom.
# Actually: D[0]=(x=-1,z=-1)=BDL meaning the back-left of D face as viewed from below.
#
# Let me just use the coordinate results I computed:
# R[0]=FUR=(y=+1,z=+1), R[2]=BUR=(y=+1,z=-1), R[6]=FDR=(y=-1,z=+1), R[8]=BDR=(y=-1,z=-1).
# L[0]=BUL=(y=+1,z=-1), L[2]=FUL=(y=+1,z=+1), L[6]=BDL=(y=-1,z=-1), L[8]=FDL=(y=-1,z=+1).
# B[0]=BUL=(y=+1,x=-1), B[2]=BUR=(y=+1,x=+1), B[6]=BDL=(y=-1,x=-1), B[8]=BDR=(y=-1,x=+1).
# U[0]=BUL=(x=-1,z=-1), U[2]=BUR=(x=+1,z=-1), U[6]=FUL=(x=-1,z=+1), U[8]=FUR=(x=+1,z=+1).
# D[0]=BDL=(x=-1,z=-1), D[2]=BDR=(x=+1,z=-1), D[6]=FDL=(x=-1,z=+1), D[8]=FDR=(x=+1,z=+1).
# F[0]=FUL=(y=+1,x=-1), F[2]=FUR=(y=+1,x=+1), F[6]=FDL=(y=-1,x=-1), F[8]=FDR=(y=-1,x=+1).
#
# Now Sune = R U R' U R U2 R'. Let me trace the first step R:
# R CW moves x=+1 layer. (y,z)->(z,-y) for pieces at x=+1.
# F right col (x=+1 face stickers): F[2]=(y=+1,z=+1)=FUR, F[5]=(y=0,z=+1)=FMR, F[8]=(y=-1,z=+1)=FDR.
# After R CW: F[2] at (y=+1,z=+1): new_y=z=+1, new_z=-y=-1. Position (y=+1,z=-1)=BUR. +Z-facing sticker -> +Y facing = U face. BUR on U: U[2]=(x=+1,z=-1)=BUR. F[2]->U[2]. ✓
# U right col (x=+1 face stickers): U[2]=(x=+1,z=-1,y=+1)=BUR, U[5]=(x=+1,z=0,y=+1)=MUR, U[8]=(x=+1,z=+1,y=+1)=FUR.
# After R CW: U[2] at (y=+1,z=-1): new_y=-1, new_z=-1. Position BDR=(y=-1,z=-1,x=+1). +Y-facing->-Z facing=B face. BDR on B: B[8]=(y=-1,x=+1)=BDR. U[2]->B[8]. ✓ Wait, in R correct cycle I derived U[2]->B[8].
# Hmm but with correct R cycle [F[2,5,8], U[2,5,8], B[8,5,2], D[8,5,2]]:
# Right-shift: F gets from D (k=0, prev=D=k=3), U gets from F (k=1), B gets from U (k=2), D gets from B (k=3).
# Wait: cycle is [F,U,B,D]. F gets from D (k=0, prev=3), U gets from F (k=1), B gets from U (k=2), D gets from B (k=3).
# Sticker flow: D->F->U->B->D.
# D[8] at position j=0: D[8,5,2] gets from B[8,5,2]: B[8]=D[8], etc.
# B[8,5,2] gets from U[2,5,8]: U[2,5,8] flows to B[8,5,2]. U[2]->B[8], U[8]->B[2]. ✓
# Hmm but U[2]->B[8] means U's BUR sticker goes to B's BDR? Let me verify:
# U[2]=BUR=(x=+1,y=+1,z=-1). R CW: (y=+1,z=-1): new_y=z=-1, new_z=-y=-1. Position: (y=-1,z=-1)=(x=+1,y=-1,z=-1)=BDR. +Y dir -> -Z = B face. B[8]=(y=-1,x=+1)=BDR. U[2]->B[8]. ✓
# And code's R cycle has B[6,3,0]: code gives U[2]->B[6]. B[6]=(y=-1,x=-1)=BDL. COMPLETELY wrong (BUL vs BDL).
# So my correction R[B]=[8,5,2] is right. But Sune still gives 6 with my corrected cycles?
# Oh wait: Sune uses R and U. If R is correct but U is still wrong, it would fail.
# Let me check what Sune order would be if ONLY R is corrected:
# Already tested: "Only R corrected" gives R U R' U' = None. So R corrected alone breaks R U R' U' x6.
# This means R and U corrections are not independent - they're coupled!
# When I change R's B or D indices, it affects the R move behavior. But R U R' U' uses only F, U faces.
# R CW affects F, U, B, D faces. Changing R's B index only affects the B face stickers.
# R U R' U' should still work if B doesn't get involved... but it does indirectly.
# Wait: R U R' U' uses F, U, D, R, and also B (R move affects B face).
# If B indices are wrong in R cycle, then after R, B face has wrong stickers, and then those get used in R' which reads them back. If R and R' are defined consistently (R' = 3x R CW), then R U R' U' should still be identity even if R's B mapping is wrong, as long as U doesn't touch B either... but U does NOT touch B in the corrected U cycle? Let me check.
# Corrected U cycle: [F[0,1,2], R[2,1,0], B[2,1,0], L[0,1,2]]. Yes, U touches B!
# So if R messes up B, and then U tries to read B, and then R' expects to undo the B change...
# The invariant "R U R' U' = identity" requires all moves to be internally consistent.
# Since single moves are identity when repeated 4 times, and R followed by R' is identity,
# R U R' U' should still work if R is well-defined (which it is since Rx4=OK, RR'=OK).
# The "Only R corrected" giving None for R U R' U' means the corrected R is WRONG.
# My coordinate analysis must have an error for R.
#
# Let me go back to fundamentals. The original R cycle works for:
# Rx4=OK, RR'=OK, R U R' U' x6=OK, Sune=6 (wrong: should be 8).
# Sune is R U R' U R U2 R'. The only difference from R U R' U' is the extra R and U2 at end.
# So the Sune bug comes from the sequence R U R' U' being CORRECT in terms of piece cycles but WRONG in terms of orientation. If R U R' U' gives the right pieces back but twisted, then Sune would fail.
# This suggests the bug is in the ROTATION of face stickers, not in the POSITION mapping.
# Let me check: what does R U R' give on a solved cube?

_MOVE_CYCLES_ORIG = {
    'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',[0,1,2]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[2,1,0]),('L',[8,5,2])]),
    'B': ('B', [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[6,3,0]),('D',[2,5,8])]),
    'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',[8,5,2]),('U',[0,3,6])]),
}

ct = CubeTest(_MOVE_CYCLES_ORIG)
ct.apply("R U R'")
print("After R U R':")
for f in 'UDFBRL':
    print(f"  {f}: {ct.faces[f]}")
print()

# Expected: R U R' should move 3 corners on the top layer.
# Specifically: FUR corner's stickers should go to specific positions.
# The FUR corner before move: F[2]=G(Green), R[0]=R(Red), U[8]=W(White).
# After R: FUR piece moves to BUR, so:
# F[2]->U[2] (FUR F-sticker -> U's BUR position).
# Wait: R CW moves F[2] to U[2] (F-sticker at FUR becomes U-sticker at BUR). After U CW: U[2]=(BUR position) moves to R[0](BUR becomes... U[2] at BUR after U CW goes to...).
# This is getting complex. Let me just check what the code gives vs what's expected.

# Actually let me check if the ROTATION function is wrong:
ct2 = CubeTest(_MOVE_CYCLES_ORIG)
ct2.faces = {f: [f+str(i) for i in range(9)] for f in 'UDFBRL'}
ct2.apply("R")
print("After R (labeled):")
for f in 'UDFBRL':
    print(f"  {f}: {ct2.faces[f]}")
print()
print("F right col F[2,5,8] should be at U[2,5,8] after R CW:")
print(f"  U[2]={ct2.faces['U'][2]}, U[5]={ct2.faces['U'][5]}, U[8]={ct2.faces['U'][8]}")
print(f"  Expected: F2, F5, F8")
print()
print("Code has U[2,5,8] gets from F[2,5,8]:")
print("But physically U[2,5,8] should receive from F's right column which is F[2,5,8] ✓")
print("So U[2]=F2, U[5]=F5, U[8]=F8. ✓ confirmed")
print()
print("B face after R:")
print(f"  B: {ct2.faces['B']}")
print("B[6,3,0] should have U[2,5,8] values (U right col):")
print(f"  B[6]={ct2.faces['B'][6]}, B[3]={ct2.faces['B'][3]}, B[0]={ct2.faces['B'][0]}")
print(f"  Expected: B[6]=U2, B[3]=U5, B[0]=U8")
print()
print("But PHYSICALLY: after R CW, U[2](BUR)-> B[8](BDR): U[2] should go to B[8], not B[0]!")
print("Code has B[6]=U2. B[6]=(y=-1,x=-1)=BDL. U[2]=BUR.")
print("BUR sticker should go to BDR=B[8], but code puts it at BDL=B[6]. COMPLETELY WRONG!")

# So the R cycle is definitely wrong for the B face stickers.
# But then how does R U R' U' x6 = identity?
# Because R and R' use the SAME wrong mapping: B[6,3,0] for both CW and CCW.
# R CW: B[6,3,0] = U[2,5,8] (wrong assignment but consistent).
# R CCW (=3x CW): each R CW moves B[6,3,0] <- U[2,5,8]. Three applications:
# After R': B[6,3,0] has D[2,5,8] (the original U values come from D via the cycle going backwards).
# The key: in R U R' U', the R' undoes exactly what R did INCLUDING the wrong B assignments.
# The U move doesn't touch B (in original: it does! U[0,1,2]->L->... wait, original U touches B[0,1,2]).
# U CW moves B[0,1,2]. So after R (which sets B[6,3,0] wrong) and U (which moves B[0,1,2]),
# then R' reads back B[6,3,0] which wasn't changed by U. And U' reads back B[0,1,2] which was correctly moved.
# So R U R' U' x6 = identity is maintained DESPITE wrong B mapping in R, because U touches different B stickers (B[0,1,2]) than R does (B[6,3,0]).
# So B[6,3,0] is used by R but B[0,1,2] is used by U. They don't interfere. That's why R U R' U' x6 works.
# But Sune includes R U R' U R U2 R'. The final R' tries to undo R's wrong B[6,3,0] assignment,
# but the B stickers at [6,3,0] have been moved by some other moves that DO touch those positions.
# What moves touch B[6,3,0]? In Sune (only R and U moves): U moves B[0,1,2] (top row). R moves B[6,3,0].
# These don't overlap, so even in Sune, R and R' should cancel. But Sune gives order 6, not 8!
#
# Wait: Sune is (R U R' U') x? No, Sune = R U R' U R U2 R'. Let me count the R moves:
# R, R', R, (U2 = UU), R'. That's R applied, R' (undoes), R applied, R' at end.
# The U U2 U are the U moves. None of these touch B[6,3,0].
# So why does Sune give order 6 instead of 8?!
# Let me check by actually tracing Sune on the corner pieces...

print()
print("=== TRACING SUNE ===")
ct3 = CubeTest(_MOVE_CYCLES_ORIG)
ct3.faces = {f: [f+str(i) for i in range(9)] for f in 'UDFBRL'}
ct3.apply("R U R' U R U2 R'")
print("After Sune:")
for f in 'UDFBRL':
    print(f"  {f}: {ct3.faces[f]}")
# Check which stickers are not at their original position
wrong = []
for f in 'UDFBRL':
    for i in range(9):
        if ct3.faces[f][i] != f+str(i):
            wrong.append((f, i, ct3.faces[f][i]))
print(f"\n{len(wrong)} stickers in wrong position:")
for f, i, val in wrong:
    print(f"  {f}[{i}] = {val} (expected {f+str(i)})")
