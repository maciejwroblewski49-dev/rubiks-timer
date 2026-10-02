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

def test_all(cycles, label=""):
    tests = [
        ("R U R' U' x6", "R U R' U'", 6),
        ("T-perm x2", "R U R' U' R' F R2 U' R' U' R U R' F'", 2),
        ("Sune x8", "R U R' U R U2 R'", 8),
        ("F-perm x2", "R' U' F' R U R' U' R' F R2 U' R' U' R U R' U R", 2),
    ]
    ok_count = 0
    for name, alg, exp in tests:
        order = find_order(cycles, alg)
        ok = order == exp
        if ok: ok_count += 1
        print(f"  {name}: {order} (exp {exp}) {'OK' if ok else 'FAIL'}")
    for m in ['U','D','F','B','R','L']:
        ct=CubeTest(cycles); [ct.apply(m) for _ in range(4)]
        ok = ct.is_solved()
        if ok: ok_count += 1
        print(f"  {m}x4: {'OK' if ok else 'FAIL'}")
    print(f"{label}: {ok_count}/10")
    return ok_count == 10

# Derived: CORRECT U cycle = [F[0,1,2], R[0,1,2], B[2,1,0], L[0,1,2]]
# Because: F[0]->R[0](same), R[0]->B[2](B reversed), B[2]->L[0](same), L[0]->F[0](same)
# For CORRECT R cycle: sticker cycle at right col:
# F[2,5,8](right col)->U[2,5,8](right col): R[0]=FUR. F[2]->U[2]: same. OK
# U[2,5,8]->B[8,5,2](reversed right col): U[2]->B[8]: reversed.
# B[8,5,2]->D[8,5,2](same): B[8]->D[8]: same.
# D[8,5,2]->F[2,5,8]: D[8]->F[2]: reversed? Let me verify:
# D[8]=(x=+1,z=+1,y=-1)=FDR. R CW: (y=-1,z=+1)->(+1,+1). FUR. -Y dir -> +Z=F. F[2]=(y=+1,x=+1)=FUR.
# Wait: D[8] is at (y=-1,z=+1)=FDR. After R CW: (y=-1,z=+1): new_y=z=+1, new_z=-y=+1. (y=+1,z=+1)=FUR. -Y direction: (-1,0) in (y,z) -> (z,-y)=(+1,+1)? That's not a unit vector. -Y=(0,-1) in (y,z): new_y=z, new_z=-y. For direction (-1,0) being -Y in y-coord: use vector (0,-1) for -Y direction in (y,z): new_y=-1, new_z=0. (-1,0)=-Y? No, (-1,0) is -Y itself. Hmm.
# Actually: -Y direction sticker (D face is -Y plane, sticker points -Y outward). Direction vector = (0,-1,0). In (y,z) plane: (y-component=-1, z-component=0) = (-1,0). After R CW (y,z)->(z,-y): (-1,0)->(0,+1)=+Z=F. D[8]->F[2]? D[8] is at (x=+1,y=-1,z=+1)=FDR. After moving to FUR=(x=+1,y=+1,z=+1). F face sticker at FUR = F[2]=(y=+1,x=+1). D[8]->F[2].
# And D[2]=(x=+1,z=-1,y=-1)=BDR. (y=-1,z=-1): new_y=-1, new_z=+1. FDR=(y=-1,z=+1). +Z=F. F[8]=(y=-1,x=+1). D[2]->F[8].
# D[8,5,2]->F[2,5,8]: reversed (D[8]->F[2], D[2]->F[8]). But idx_D=[8,5,2] and idx_F=[2,5,8]:
# F[idx_F[j]] = D[idx_D[j]]: F[2]=D[8], F[5]=D[5], F[8]=D[2]. F[2]=D[8] means D[8]->F[2]. Correct!
# So correct R: [F[2,5,8], U[2,5,8], B[8,5,2], D[8,5,2]]
# This is the same as my earlier derivation. But we showed it breaks things when combined with the existing F cycle.
# The issue might be in the F cycle. Let me re-derive F:
# F CW: F[0,1,2,3,4,5,6,7,8] rotates. Affecting edges:
# U bottom row -> R left col -> D top row -> L right col
# Let me re-derive with corrected coordinate mapping:
# U[6,7,8] = bottom row of U. U[6]=(x=-1,z=+1,y=+1)=FUL. F CW: (x,y) at z=+1.
# (x,y)->(y,-x) for F CW (as I derived): FUL=(x=-1,y=+1): new_x=y=+1, new_y=-x=+1. FUR=(x=+1,y=+1). +Y direction (U sticker): (0,1) in (x,y): new_x=y=1, new_y=-x=0. (+1,0)=+X=R. FUR on R: R[0]=(y=+1,z=+1)=FUR. U[6]->R[0].
# U[8]=(x=+1,z=+1,y=+1)=FUR. (x=+1,y=+1): new_x=+1, new_y=-1. FDR=(x=+1,y=-1,z=+1). +Y: same. R[6]=(y=-1,z=+1)=FDR. U[8]->R[6].
# U[6,7,8]->R[0,3,6]: reversed order? U[6]->R[0], U[7]->R[3], U[8]->R[6]. Same column same direction (all going top-to-bottom). idx_U=[6,7,8] and idx_R=[0,3,6]. With right-shift on [U,R,D,L]: R[idx_R[j]]=U[idx_U[j]]. R[0]=U[6], R[3]=U[7], R[6]=U[8]. ✓ This is what CODE has!
# So F cycle's U->R is CORRECT in the original code.
# Now R->D: R[0]=(y=+1,z=+1,x=+1)=FUR. F CW: (x=+1,y=+1): new_x=+1, new_y=-1. FDR=(x=+1,y=-1,z=+1). +X direction: (1,0) in (x,y): new_x=y=+1, new_y=-x=-1. (new_x=0+1... wait: direction +X=(1,0). F CW: (x,y)->(y,-x): (1,0)->(0,-1)=-Y=D. FDR on D: D[8]=(x=+1,z=+1)=FDR. R[0]->D[8].
# R[6]=(y=-1,z=+1,x=+1)=FDR. F CW: (x=+1,y=-1): new_x=-1, new_y=-1. FDL? No: (x,y)->(y,-x): (1,-1)->(-1,-1). (x=-1,y=-1,z=+1)=FDL. +X direction ->(0,-1)? (1,0): new_x=y=-1, new_y=-x=-1? Wait: direction (1,0) in (x,y): (x,y)->(y,-x): (1,0)->(0,-1)=-Y. Position goes to FDL. -Y=D. FDL on D: D[6]=(x=-1,z=+1)=FDL. R[6]->D[6].
# R[0,3,6]->D[8,5,6]? Wait: R[0]->D[8], R[3]->D[5]? R[3]=(y=0,z=+1)=FMR. (x=+1,y=0): new_x=0, new_y=-1. FMD=(x=0,y=-1,z=+1)? D[7]=(x=0,z=+1)=FMD. R[3]->D[7]. So R[0,3,6]->D[8,7,6]? Wait that's reversed. Hmm. R[0]->D[8], R[3]->D[7], R[6]->D[6]. That goes D[8] then D[7] then D[6] = right-to-left in D's front row.
# idx_R=[0,3,6] and idx_D=[8,7,6]? No wait: we need D[idx_D[j]]=R[idx_R[j]]. D[?]=R[0]: R[0]->D[8]: idx_D[0]=8. D[?]=R[3]: R[3]->D[7]: idx_D[1]=7. R[6]->D[6]: idx_D[2]=6. idx_D=[8,7,6].
# BUT CODE HAS idx_D=[2,1,0]. Code: D[2]=R[0], D[1]=R[3], D[0]=R[6]. WRONG.
# Correct: idx_D=[8,7,6]. Code has [2,1,0]. These are DIFFERENT POSITIONS (front vs back row of D).
# So the F cycle's R->D part is wrong. The code puts stickers at D[2,1,0] (back row) when they should go to D[8,7,6] (front row, reversed).
# This confirms F cycle has a bug in D indices.
# D[8,7,6]->L[?]: D[8]=(x=+1,z=+1,y=-1)=FDR. F CW: (x=+1,y=-1): new_x=-1, new_y=-1. FDL=(x=-1,y=-1). -Y direction: (0,-1): new_x=-1, new_y=0. (-1,0)=-X=L. FDL on L: L[8]=(y=-1,z=+1)=FDL. D[8]->L[8].
# D[6]=(x=-1,z=+1,y=-1)=FDL. (x=-1,y=-1): new_x=-1, new_y=+1. FUL=(x=-1,y=+1). -Y->-X=L. FUL on L: L[2]=(y=+1,z=+1)=FUL. D[6]->L[2].
# D[8,7,6]->L[8,5,2]: D[8]->L[8], D[7]->L[5], D[6]->L[2]. idx_D=[8,7,6], idx_L=[8,5,2]. ✓ Same!
# L[8,5,2]->U[?]: L[8]=(y=-1,z=+1,x=-1)=FDL. F CW: (x=-1,y=-1): new_x=-1, new_y=+1. FUL. -X direction: (-1,0): new_x=0, new_y=+1=+Y=U. FUL on U: U[6]=(x=-1,z=+1)=FUL. L[8]->U[6]. ✓
# L[2]=(y=+1,z=+1,x=-1)=FUL. F CW: (x=-1,y=+1): new_x=+1, new_y=+1. FUR. -X->+Y=U. U[8]=(x=+1,z=+1)=FUR. L[2]->U[8]. ✓
# L[8,5,2]->U[6,7,8]. Matches code's idx_L=[8,5,2] and idx_U=[6,7,8]. ✓ CORRECT in code!
#
# CORRECT F cycle: [('U',[6,7,8]), ('R',[0,3,6]), ('D',[8,7,6]), ('L',[8,5,2])]
# CODE F cycle:    [('U',[6,7,8]), ('R',[0,3,6]), ('D',[2,1,0]), ('L',[8,5,2])]
# ONLY D IS WRONG: [8,7,6] vs [2,1,0].

cycles_test2 = {
    'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',[2,1,0]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[8,7,6]),('L',[8,5,2])]),
    'B': ('B', [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[8,5,2]),('D',[8,5,2])]),
    'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',[8,5,2]),('U',[0,3,6])]),
}

print("U(B=2,1,0) + F(D=8,7,6) + R(B=8,5,2,D=8,5,2):")
test_all(cycles_test2)
