"""
Verify that mirroring B in draw_net fixes the display for common moves.
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

def print_net_mirrored_b(cs, label=""):
    if label: print(f"  {label}:")
    def r(face, row):
        return ''.join(cs.faces[face][row*3+c][0] for c in range(3))
    def rb(row):  # B face mirrored
        return ''.join(cs.faces['B'][row*3+(2-c)][0] for c in range(3))
    for i in range(3): print("     "+r('U',i))
    for i in range(3): print("  "+r('L',i)+r('F',i)+r('R',i)+rb(i))
    for i in range(3): print("     "+r('D',i))

# Test all 6 single moves and verify the net makes physical sense
moves_and_expectations = [
    ("U", {
        'F_top': 'O', 'R_top': 'G', 'B_top_in_net': 'R',  # B's top row: net left=? right=?
        # After U CW: F gets L(O), R gets F(G), B gets R(R), L gets B(B)
        # B[0,1,2] = [R,R,R] with orig code. Mirrored: net shows [R,R,R] = same (symmetric)
        'desc': "F top=Orange, R top=Green, B top=Red, L top=Blue"
    }),
    ("R", {
        'desc': "U right=Green, F right=Yellow, B adj R=Blue, D right=Blue"
        # After R CW: F right->U right(Green), D right->F right(Yellow), B adj R->D right(Blue), U right->B(White becomes White on B)
        # Net B left (adj R): should be Blue (unchanged on original B adj side)
        # Original: B[0,3,6]=White (WRONG without mirror), Mirrored: B[0,3,6] shown as B[2,5,8]=Blue (CORRECT)
    }),
    ("F", {
        'desc': "U bottom=Orange(from L right), R left=White(from U bottom), D top=Red(from R left reversed), L right=Yellow(from D top)"
        # F doesn't affect B directly
    }),
    ("B", {
        'desc': "U back row changes, R right col changes, D back row changes, L left col changes"
        # B CW: check if B stickers are displayed correctly after rotation
    }),
    ("L", {
        'desc': "F left->D left, D left->B left(net right), B left(net right)->U left, U left->F left"
        # L CW: affects B's left col (B[0,3,6]) physically = B's LEFT from behind = B's RIGHT in mirrored net
    }),
    ("D", {
        'desc': "F bottom->L bottom, L bottom->B bottom(mirrored), B bottom->R bottom, R bottom->F bottom"
    }),
]

print("Testing with B mirrored in display:")
print()
for move, info in moves_and_expectations:
    cs = CS(_ORIG)
    cs.apply(move)
    print(f"After {move}: {info['desc']}")
    print_net_mirrored_b(cs)
    print()

# Now test a specific scramble and verify visually
print("=== Test scramble: R U R' U' ===")
cs = CS(_ORIG)
cs.apply("R U R' U'")
print("Net with B mirrored:")
print_net_mirrored_b(cs)
print()
print("This is the sexy move. After 6 repetitions the cube should be solved.")
print("Let's check visually that after 1 application it looks plausible.")
