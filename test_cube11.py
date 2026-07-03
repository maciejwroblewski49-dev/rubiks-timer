_SOLVED = {'U':'W','D':'Y','F':'G','B':'B','R':'R','L':'O'}

# Let me try a completely different approach: use a LEFT-shift instead of right-shift
# Left-shift: face[k] gets from face[k+1 mod n], meaning sticker flows backward in list.

class CubeTest:
    def __init__(self, cycles, direction='right'):
        self.cycles = cycles
        self.direction = direction  # 'right' or 'left'
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
            if self.direction == 'right':
                src = saved[(k - 1) % n]
            else:  # left-shift
                src = saved[(k + 1) % n]
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

def find_order(cycles, alg, max_n=50, direction='right'):
    ct = CubeTest(cycles, direction)
    for i in range(1, max_n+1):
        ct.apply(alg)
        if ct.is_solved():
            return i
    return None

def test_cycles(cycles, label="", direction='right'):
    tests = [
        ("R U R' U' x6", "R U R' U'", 6),
        ("T-perm x2", "R U R' U' R' F R2 U' R' U' R U R' F'", 2),
        ("Sune x8", "R U R' U R U2 R'", 8),
        ("F-perm x2", "R' U' F' R U R' U' R' F R2 U' R' U' R U R' U R", 2),
    ]
    results = []
    for name, alg, expected_order in tests:
        order = find_order(cycles, alg, 50, direction)
        ok = "OK" if order == expected_order else f"WRONG (got {order}, expected {expected_order})"
        results.append(f"  {name}: order={order} {ok}")
    all_ok = all("WRONG" not in r for r in results)
    print(f"{label}: {'ALL OK' if all_ok else 'SOME FAILURES'}")
    if not all_ok:
        for r in results:
            print(r)
    return all_ok

# Original cycles
_MOVE_CYCLES_ORIG = {
    'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',[0,1,2]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[2,1,0]),('L',[8,5,2])]),
    'B': ('B', [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[6,3,0]),('D',[2,5,8])]),
    'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',[8,5,2]),('U',[0,3,6])]),
}

print("=== Testing with ORIGINAL cycles, left-shift ===")
test_cycles(_MOVE_CYCLES_ORIG, "Original Left-shift", 'left')
print()

# My derived cycles
new_cycles = {
    'U': ('U', [('F',[0,1,2]),('R',[2,1,0]),('B',[2,1,0]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[8,7,6]),('R',[8,7,6])]),
    'F': ('F', [('U',[6,7,8]),('R',[2,5,8]),('D',[8,7,6]),('L',[8,5,2])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[8,5,2]),('D',[8,5,2])]),
    'B': ('B', [('U',[0,1,2]),('R',[2,5,8]),('D',[2,1,0]),('L',[6,3,0])]),
    'L': ('L', [('F',[0,3,6]),('D',[6,3,0]),('B',[6,3,0]),('U',[0,3,6])]),
}

print("=== Testing with NEW cycles, right-shift ===")
test_cycles(new_cycles, "New Right-shift", 'right')
print()

print("=== Testing with NEW cycles, left-shift ===")
test_cycles(new_cycles, "New Left-shift", 'left')
print()

# Maybe the issue is just that I have the cycle list ORDER wrong for some moves.
# Let me try reversing the cycle list for specific moves.
# The derived B cycle sticker flow is U->R->D->L->U with right-shift on [U,R,D,L].
# What if I use [L,D,R,U] (reversed)?

print("=== Trying reversed B cycle order ===")
new_cycles_2 = dict(new_cycles)
new_cycles_2['B'] = ('B', [('L',[6,3,0]),('D',[2,1,0]),('R',[2,5,8]),('U',[0,1,2])])
test_cycles(new_cycles_2, "Reversed B", 'right')

# Maybe wrong B index analysis. Let me try the original code's B cycle order but with corrected indices:
new_cycles_3 = dict(new_cycles)
new_cycles_3['B'] = ('B', [('D',[2,1,0]),('R',[2,5,8]),('U',[0,1,2]),('L',[6,3,0])])
test_cycles(new_cycles_3, "B with code order", 'right')

# And try original U/D/R cycles with just F corrected:
mix1 = {
    'U': _MOVE_CYCLES_ORIG['U'],
    'D': _MOVE_CYCLES_ORIG['D'],
    'F': ('F', [('U',[6,7,8]),('R',[2,5,8]),('D',[8,7,6]),('L',[8,5,2])]),
    'R': _MOVE_CYCLES_ORIG['R'],
    'B': _MOVE_CYCLES_ORIG['B'],
    'L': _MOVE_CYCLES_ORIG['L'],
}
print("=== Only F corrected ===")
test_cycles(mix1, "Only F fixed", 'right')

# Only R corrected
mix2 = {
    'U': _MOVE_CYCLES_ORIG['U'],
    'D': _MOVE_CYCLES_ORIG['D'],
    'F': _MOVE_CYCLES_ORIG['F'],
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[8,5,2]),('D',[8,5,2])]),
    'B': _MOVE_CYCLES_ORIG['B'],
    'L': _MOVE_CYCLES_ORIG['L'],
}
print("=== Only R corrected ===")
test_cycles(mix2, "Only R fixed", 'right')

# F and R corrected
mix3 = {
    'U': _MOVE_CYCLES_ORIG['U'],
    'D': _MOVE_CYCLES_ORIG['D'],
    'F': ('F', [('U',[6,7,8]),('R',[2,5,8]),('D',[8,7,6]),('L',[8,5,2])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[8,5,2]),('D',[8,5,2])]),
    'B': _MOVE_CYCLES_ORIG['B'],
    'L': _MOVE_CYCLES_ORIG['L'],
}
print("=== F and R corrected ===")
test_cycles(mix3, "F and R fixed", 'right')
