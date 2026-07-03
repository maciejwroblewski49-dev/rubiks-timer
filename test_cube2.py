_MOVE_CYCLES = {
    'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',[0,1,2]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[2,1,0]),('L',[8,5,2])]),
    'B': ('B', [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[6,3,0]),('D',[2,5,8])]),
    'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',[8,5,2]),('U',[0,3,6])]),
}

_SOLVED = {'U':'W','D':'Y','F':'G','B':'B','R':'R','L':'O'}

class CubeState:
    def __init__(self):
        self.faces = {f: [_SOLVED[f]] * 9 for f in 'UDFBRL'}

    def _rotate_cw(self, f):
        c = self.faces[f][:]
        self.faces[f] = [c[6],c[3],c[0], c[7],c[4],c[1], c[8],c[5],c[2]]

    def _apply_cw(self, base):
        if base not in _MOVE_CYCLES: return
        face, cycle = _MOVE_CYCLES[base]
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

# Test each move pair (m then m') = solved
print("=== Move self-inverse tests ===")
moves_to_test = ['U', 'D', 'F', 'B', 'R', 'L']
for m in moves_to_test:
    cs = CubeState()
    cs.apply(m + " " + m + "'")
    print(f"  {m} {m}': {'OK' if cs.is_solved() else 'FAIL'}")

# Test each move x4 = solved
print("\n=== Move x4 tests ===")
for m in moves_to_test:
    cs = CubeState()
    for _ in range(4): cs.apply(m)
    print(f"  {m}x4: {'OK' if cs.is_solved() else 'FAIL'}")

# Test U D U' D' = solved (U and D commute)
print("\n=== Commutator tests ===")
commutators = [
    "U D U' D'",
    "R L R' L'",
    "F B F' B'",
    "U F U' F'",
    "R F R' F'",
]
for seq in commutators:
    cs = CubeState()
    cs.apply(seq)
    print(f"  {seq}: {'solved' if cs.is_solved() else 'NOT SOLVED'}")

# Check T-perm order
print("\n=== T-perm order ===")
tperm = "R U R' U' R' F R2 U' R' U' R U R' F'"
cs = CubeState()
for i in range(1, 20):
    cs.apply(tperm)
    if cs.is_solved():
        print(f"  T-perm order: {i}")
        break
else:
    print("  T-perm order > 19 or bug!")

# Check which moves are wrong by testing simple formulas
# U' D F' B R' L (each pair of opposite moves combined) has order...
print("\n=== Specific tests ===")
# Sune has order 8
sune = "R U R' U R U2 R'"
cs2 = CubeState()
for i in range(1, 20):
    cs2.apply(sune)
    if cs2.is_solved():
        print(f"  Sune order: {i} (expected 8)")
        break
else:
    print("  Sune order > 19")

# Niklas
niklas = "R U' L' U R' U' L"
cs3 = CubeState()
for i in range(1, 20):
    cs3.apply(niklas)
    if cs3.is_solved():
        print(f"  Niklas order: {i} (expected 8 or similar)")
        break

# Test F specifically
print("\n=== F move test ===")
cs4 = CubeState()
cs4.apply("F")
print("After F:")
print("  U bottom (U[6,7,8]) should be Orange(L right col):", cs4.faces['U'][6:9])
print("  R left (R[0,3,6]) should be White(U bottom):", [cs4.faces['R'][0], cs4.faces['R'][3], cs4.faces['R'][6]])
print("  D top (D[0,1,2] reversed) should be Red(R left col):", cs4.faces['D'][0:3])
print("  L right (L[2,5,8]) should be Yellow(D top):", [cs4.faces['L'][2], cs4.faces['L'][5], cs4.faces['L'][8]])

# For F CW (viewed from front):
# U's bottom row -> R's left column (going down)
# R's left column -> D's top row (reversed: R goes down, D goes right)
# D's top row (reversed) -> L's right column (going up)
# L's right column -> U's bottom row (reversed)
# F cycle: [U[6,7,8], R[0,3,6], D[2,1,0], L[8,5,2]]
# With right-shift: each face gets from previous in list
# U gets from L (last), R gets from U, D gets from R, L gets from D
# U[6,7,8] = L[8,5,2] (reversed L right col)
# R[0,3,6] = U[6,7,8] (U bottom row)
# D[2,1,0] = R[0,3,6] (R left col) -> so D[2]=R[0], D[1]=R[3], D[0]=R[6]
# L[8,5,2] = D[2,1,0] -> L[8]=D[2], L[5]=D[1], L[2]=D[0]
#
# On solved cube: L[8,5,2]=Orange, U[6,7,8]=White, R[0,3,6]=Red, D[2,1,0]=Yellow
# After F CW:
# U[6,7,8] = L[8,5,2] = [O,O,O] -- U bottom gets Orange from L right col reversed
# R[0,3,6] = U[6,7,8] = [W,W,W] -- R left gets White from U bottom
# D[2,1,0] = R[0,3,6] = [R,R,R] -> D[2]=R, D[1]=R, D[0]=R -- D top (reversed) gets Red
# L[8,5,2] = D[2,1,0] = [Y,Y,Y] -- L right gets Yellow from D top reversed

print("\nExpected after F:")
print("  U[6,7,8] = [O,O,O] (Orange from L right col)")
print("  R[0,3,6] = [W,W,W] (White from U bottom)")
print("  D[0,1,2] = [R,R,R] (Red from R left col, reversed stored as D[2,1,0])")
print("  L[2,5,8] = [Y,Y,Y] (Yellow from D top, stored reversed as L[8,5,2])")
