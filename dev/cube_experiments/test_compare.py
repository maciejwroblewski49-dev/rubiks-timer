"""Compare original vs corrected for various single moves."""
_SOLVED = {'U':'W','D':'Y','F':'G','B':'B','R':'R','L':'O'}

_ORIG = {
    'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',[0,1,2]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[2,1,0]),('L',[8,5,2])]),
    'B': ('B', [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[6,3,0]),('D',[2,5,8])]),
    'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',[8,5,2]),('U',[0,3,6])]),
}

# My corrected cycles - only change the known bugs:
# R: B[8,5,2] and D[8,5,2] instead of B[6,3,0] and D[2,5,8]
# F: D[8,7,6] instead of D[2,1,0]
# U: B[2,1,0] instead of B[0,1,2]
_NEW = {
    'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',[2,1,0]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[8,7,6]),('L',[8,5,2])]),
    'B': ('B', [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[8,5,2]),('D',[8,5,2])]),
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
    def net(self):
        def r(f, row):
            return ''.join(self.faces[f][row*3+c][0] for c in range(3))
        lines = []
        for i in range(3): lines.append("   "+r('U',i))
        for i in range(3): lines.append(r('L',i)+r('F',i)+r('R',i)+r('B',i))
        for i in range(3): lines.append("   "+r('D',i))
        return '\n'.join(lines)

moves = ['U', 'D', 'F', 'R', 'B', 'L']
for m in moves:
    o = CS(_ORIG); o.apply(m)
    n = CS(_NEW); n.apply(m)
    nets_same = o.net() == n.net()
    print(f"=== After {m} CW === (nets same: {nets_same})")
    if not nets_same:
        on = o.net().split('\n')
        nn = n.net().split('\n')
        for i, (ol, nl) in enumerate(zip(on, nn)):
            flag = " <--" if ol != nl else ""
            print(f"  ORIG: {ol}  NEW: {nl}{flag}")
    print()
