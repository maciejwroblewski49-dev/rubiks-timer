"""
Derive correct L cycle B indices.

L CW (viewed from left, looking in +X direction):
F left col -> D left col -> B left col -> U left col

B's left col (x=-1 side, adjacent to L face):
B[0]=(y=+1,x=-1)=BUL, B[3]=(y=0,x=-1)=BML, B[6]=(y=-1,x=-1)=BDL

L CW rotation around -X axis (from left, looking +X):
Physical direction: from left looking +X, CW means front face stickers go DOWN.
+Z->-Y->-Z->+Y (CW around -X... actually CW when looking in +X direction means):
Looking in +X: CW: up->right->down->left. Up=+Y, right=-Z (wait: if front is to your left when looking at L from outside).

Actually: looking at L from outside (-X direction, you look toward +X):
- When you look in +X, the cube's front (+Z) is to your RIGHT.
- CW rotation: right->down->left->up = +Z->-Y->-Z->+Y.
Wait: CW when you face +X with right=+Z (as I calculated before using forward x up method):
Looking in +X direction with right=+Z (toward cube's front), CW = right->down->left->up:
+Z -> -Y -> -Z -> +Y -> +Z.

For direction transformations under L CW (looking in +X, CW as described):
+Z->-Y means a +Z direction sticker becomes -Y.
+Y->+Z.
-Z->+Y.
-Y->-Z.

L CW for pieces at x=-1:
F left col = F[0,3,6] at (x=-1, z=+1) with sticker facing +Z.
After L CW: +Z->-Y. The piece moves (in x=-1 slice): (y,z) rotation CW when looking +X.
CW around +X: (y,z)->? Looking in +X direction, right=+Z, up=+Y. CW: +Y->-Z, so new_y=-z, new_z=y?
Check: +Y=(1,0) in (y,z) -> (new_y=-z=0, new_z=y=1)=(0,1)=+Z. Hmm: +Y goes to +Z? That means CW from +X: +Y->+Z->-Y->-Z->+Y.
Actually let me use the fact that CW from +X side (standard physics convention):
thumb in +X direction, curl = CW. For y-z plane: (y,z) CW when viewed from +X is (y,z)->(z,-y).
Check: +Y=(1,0)->(0,-1)=-Z. +Z=(0,1)->(1,0)=+Y. So: +Y->-Z, +Z->+Y. This is the standard CW rotation of y-z plane when viewed from +X.

So L CW: (y,z)->(z,-y).

F[0]=(y=+1,z=+1,x=-1). L CW: (y=+1,z=+1)->(+1,-1). Position (x=-1,y=+1,z=-1)=BUL. +Z direction (F sticker): (0,1)->new_y=1, new_z=0. = +Y=U face. BUL on U: U[0]=(x=-1,z=-1)=BUL. F[0]->U[0]? Wait let me check:
(0,1) in (y,z): new_y=z=1, new_z=-y=0. (1,0)=+Y=U. BUL on U: U[0]=(x=-1,z=-1)=BUL. ✓
F[6]=(y=-1,z=+1,x=-1). (y=-1,z=+1)->(+1,+1). (x=-1,y=+1,z=+1)=FUL. +Z->+Y. U[6]=(x=-1,z=+1)=FUL. F[6]->U[6].
F[0,3,6]->U[0,3,6]. Same indices. ✓ (matches original L cycle U[0,3,6])

U left col: U[0]=(x=-1,z=-1)=BUL, U[3]=(x=-1,z=0), U[6]=(x=-1,z=+1)=FUL. After L CW:
U[0] at (y=+1,z=-1): (+Y sticker). (y=+1,z=-1)->(-1,-1). (-1,... wait: (z,-y)=(-1,-1). (y=-1,z=-1)=BDL? Position (x=-1,y=-1,z=-1)=BDL. +Y direction: (1,0)->(0,-1)=-Z=B. BDL on B: B[6]=(y=-1,x=-1)=BDL. U[0]->B[6].
U[6] at (y=+1,z=+1): (y=+1,z=+1)->(+1,-1). (y=+1,z=-1)=BUL? No: (new_y=z=+1, new_z=-y=-1). (y=+1,z=-1)=BUL. Wait position: (x=-1,y=+1,z=-1)=BUL. B[0]=(y=+1,x=-1)=BUL. +Y->(0,-1)=-Z=B. B[0]. U[6]->B[0].
U[0,3,6]->B[6,3,0]. ✓ Reversed B indices.

B left col (x=-1): B[0]=(y=+1,x=-1)=BUL, B[3]=(y=0,x=-1), B[6]=(y=-1,x=-1)=BDL. After L CW:
B[0] at (y=+1,z=-1): (y=+1,z=-1)->(-1,-1). (y=-1,z=-1)=BDL. -Z direction (B sticker): (0,-1)->new_y=-1,new_z=0. (-1,0)=-Y=D. BDL on D: D[6]=(x=-1,z=-1)? Wait: with D[0]=FDL=(x=-1,z=+1), D[6]=BDL=(x=-1,z=-1). Wait I need to recheck D layout.
D[0]=FDL: so D[0]=(x=-1,z=+1,y=-1). D[6]=? Row 2, col 0: D[6]=(x=-1,z=-1,y=-1)=BDL.
B[0]->D[?]: position is BDL=(x=-1,y=-1,z=-1). On D face: D[6]=(x=-1,z=-1)=BDL. -Z sticker (B) at BUL -> BDL position. -Z direction: (0,-1) in (y,z): (new_y=z=-1, new_z=-y=-1). Wait: -Z direction has y-component=0, z-component=-1. (y,z)->(z,-y): (-1,-1) in (y,z)... but direction vector is (0,-1). (y=0,z=-1) under (z,-y): (new_y=z=-1, new_z=-y=0)=(-1,0)=-Y=D. BDL on D: D[6]=(x=-1,z=-1,y=-1). D face at BDL=D[6]. B[0]->D[6].
B[6]=(y=-1,z=-1,x=-1)=BDL. (y=-1,z=-1)->(-1,+1). (y=-1,z=+1)=FDL. Position (x=-1,y=-1,z=+1)=FDL. -Z->-Y=D. FDL on D: D[0]=(x=-1,z=+1)=FDL. B[6]->D[0].
B[0,3,6]->D[6,3,0]. Reversed indices.

D left col: D[0]=(x=-1,z=+1)=FDL, D[3]=(x=-1,z=0), D[6]=(x=-1,z=-1)=BDL. After L CW:
D[0] at (y=-1,z=+1): (-Y sticker). (y=-1,z=+1)->(+1,+1). Position (x=-1,y=+1,z=+1)=FUL. -Y direction: (-1,0) in (y,z): (-1,0)->(0,+1)=+Z=F. FUL on F: F[0]=(y=+1,x=-1)=FUL. D[0]->F[0].
D[6] at (y=-1,z=-1): (y=-1,z=-1)->(-1,+1). (y=-1,z=+1)=FDL? No: (new_y=z=-1, new_z=-y=+1). (y=-1,z=+1)=FDL. F[6]=(y=-1,x=-1)=FDL. D[6]->F[6]. ✓
D[0,3,6]->F[0,3,6]. Same. ✓

Summary of L CW sticker movements:
F[0,3,6] -> U[0,3,6] (same)
U[0,3,6] -> B[6,3,0] (reversed!)
B[6,3,0] -> D[0,3,6] (different order but going in cycle: B[0]->D[6], B[6]->D[0])
Actually: B[0,3,6]->D[6,3,0] (reversed)
D[0,3,6] -> F[0,3,6] (same)

With right-shift on cycle [F,D,B,U]:
- F gets from U: F[idx_F]=U[idx_U]: F[0]=U[0]. idx_F=idx_U=[0,3,6]. ✓
- D gets from F: D[idx_D]=F[idx_F]: D[?]=F[0]. F[0]->D[0]: idx_D[0]=0. D[0,3,6]. ✓
- B gets from D: B[idx_B]=D[idx_D]: D[0,3,6] flows. B[?]=D[0]=FDL-sticker.
  B[0,3,6]->D[6,3,0] (B gives to D). With reverse: D[6]=B[0], D[3]=B[3], D[0]=B[6].
  So D gets from B: idx_B (source): B's stickers. B[idx_B[j]] flows to D[idx_D[j]].
  D[idx_D[0]]=B[idx_B[0]]: D[0]=B[?]. B[6]->D[0]: idx_B[0]=6. D[3]=B[3]: idx_B[1]=3. D[6]=B[0]: idx_B[2]=0. idx_B=[6,3,0].
- U gets from B: U[idx_U]=B[idx_B]: U[0]=B[6], U[3]=B[3], U[6]=B[0]. ✓ But from our derivation: U[0,3,6]->B[6,3,0]. So B[6]->U[0], B[3]->U[3], B[0]->U[6]. That means U[0]=B[6], U[6]=B[0]. ✓

CORRECT L cycle: [('F',[0,3,6]),('D',[0,3,6]),('B',[6,3,0]),('U',[0,3,6])]
Note: B[6,3,0] NOT B[8,5,2]!
CODE has: [('F',[0,3,6]),('D',[0,3,6]),('B',[8,5,2]),('U',[0,3,6])]
B[8,5,2] = B's right col reversed. WRONG. Should be B[6,3,0] = B's left col reversed.
"""

_SOLVED = {'U':'W','D':'Y','F':'G','B':'B','R':'R','L':'O'}

# Now test with correct R.B=[8,5,2] and correct L.B=[6,3,0]:
_FIXED2 = {
    'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',[2,1,0]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[2,1,0]),('L',[8,5,2])]),
    'B': ('B', [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]),
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

print("FIXED2 (U.B=2,1,0 + R.B=8,5,2 + L.B=6,3,0):")
tests = [
    ("R L R' L'", "R L R' L'", 1),
    ("F B F' B'", "F B F' B'", 1),
    ("U D U' D'", "U D U' D'", 1),
    ("R U R' U' x6", "R U R' U'", 6),
    ("T-perm x2", "R U R' U' R' F R2 U' R' U' R U R' F'", 2),
    ("Sune x8", "R U R' U R U2 R'", 8),
]
for name, alg, exp in tests:
    order = find_order(_FIXED2, alg)
    print(f"  {name}: {order} (exp {exp}) {'OK' if order==exp else 'FAIL'}")

for m in ['U','D','F','B','R','L']:
    ct = CubeTest(_FIXED2)
    for _ in range(4): ct.apply(m)
    print(f"  {m}x4: {'OK' if ct.is_solved() else 'FAIL'}")
