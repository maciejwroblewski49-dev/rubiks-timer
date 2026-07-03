_SOLVED = {'U':'W','D':'Y','F':'G','B':'B','R':'R','L':'O'}
_MOVE_CYCLES = {
    'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',[0,1,2]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[2,1,0]),('L',[8,5,2])]),
    'B': ('B', [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[6,3,0]),('D',[2,5,8])]),
    'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',[8,5,2]),('U',[0,3,6])]),
}

class CubeState:
    _SOLVED = {'U':'W','D':'Y','F':'G','B':'B','R':'R','L':'O'}
    def __init__(self):
        self.faces = {f: [self._SOLVED[f]] * 9 for f in 'UDFBRL'}
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
        return all(self.faces[f] == [self._SOLVED[f]]*9 for f in 'UDFBRL')
    def net_with_fix(self):
        lines = []
        for r in range(3):
            lines.append('   '+''.join(self.faces['U'][r*3+c][0] for c in range(3)))
        for r in range(3):
            row = ''
            for face in ['L','F','R','B']:
                for c in range(3):
                    dc = (2-c) if face == 'B' else c
                    row += self.faces[face][r*3+dc][0]
            lines.append(row)
        for r in range(3):
            lines.append('   '+''.join(self.faces['D'][r*3+c][0] for c in range(3)))
        return '\n'.join(lines)

# Solved state
print("Solved cube (B should show as solid Blue):")
cs = CubeState()
print(cs.net_with_fix())
print()

# After sexy move x6 = solved
cs2 = CubeState()
for _ in range(6): cs2.apply("R U R' U'")
print("After sexy move x6 (should be solved = all solid):")
print(cs2.net_with_fix())
print("Is solved:", cs2.is_solved())
print()

# After R CW
cs3 = CubeState()
cs3.apply("R")
print("After R CW:")
print(cs3.net_with_fix())
print("B should show: [B,B,W] per row (Blue at left adj to R, White at right from U)")
print()

# After U CW
cs4 = CubeState()
cs4.apply("U")
print("After U CW:")
print(cs4.net_with_fix())
print("B top row should be Red (from R), rest Blue")
print()

# After B CW
cs5 = CubeState()
cs5.apply("B")
print("After B CW:")
print(cs5.net_with_fix())
print("B face rotated. U back=Red(from R), R right col=Yellow(from D), etc.")
