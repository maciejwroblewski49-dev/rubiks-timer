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

# Fix R and U only
cycles_ru = {
    'U': ('U', [('F',[0,1,2]),('R',[2,1,0]),('B',[2,1,0]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[2,1,0]),('L',[8,5,2])]),
    'B': ('B', [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[8,5,2]),('D',[8,5,2])]),
    'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',[8,5,2]),('U',[0,3,6])]),
}
print("R and U corrected:")
print("  Sune:", find_order(cycles_ru, "R U R' U R U2 R'"), "(expected 8)")
print("  R U R' U' x6:", find_order(cycles_ru, "R U R' U'"), "(expected 6)")
ct=CubeTest(cycles_ru); [ct.apply("U") for _ in range(4)]; print("  Ux4:", "OK" if ct.is_solved() else "FAIL")
ct=CubeTest(cycles_ru); [ct.apply("R") for _ in range(4)]; print("  Rx4:", "OK" if ct.is_solved() else "FAIL")
ct=CubeTest(cycles_ru); ct.apply("U U'"); print("  U U':", "OK" if ct.is_solved() else "FAIL")
ct=CubeTest(cycles_ru); ct.apply("R R'"); print("  R R':", "OK" if ct.is_solved() else "FAIL")
print()

# Now with ALL corrected cycles
cycles_all = {
    'U': ('U', [('F',[0,1,2]),('R',[2,1,0]),('B',[2,1,0]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[8,7,6]),('R',[8,7,6])]),
    'F': ('F', [('U',[6,7,8]),('R',[2,5,8]),('D',[8,7,6]),('L',[8,5,2])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[8,5,2]),('D',[8,5,2])]),
    'B': ('B', [('U',[0,1,2]),('R',[2,5,8]),('D',[2,1,0]),('L',[6,3,0])]),
    'L': ('L', [('F',[0,3,6]),('D',[6,3,0]),('B',[6,3,0]),('U',[0,3,6])]),
}
print("ALL corrected:")
print("  Sune:", find_order(cycles_all, "R U R' U R U2 R'"), "(expected 8)")
print("  R U R' U' x6:", find_order(cycles_all, "R U R' U'"), "(expected 6)")
print("  T-perm x2:", find_order(cycles_all, "R U R' U' R' F R2 U' R' U' R U R' F'"), "(expected 2)")
print("  F-perm x2:", find_order(cycles_all, "R' U' F' R U R' U' R' F R2 U' R' U' R U R' U R"), "(expected 2)")
for m in ['U','D','F','B','R','L']:
    ct=CubeTest(cycles_all)
    for _ in range(4): ct.apply(m)
    print(f"  {m}x4:", "OK" if ct.is_solved() else "FAIL")
