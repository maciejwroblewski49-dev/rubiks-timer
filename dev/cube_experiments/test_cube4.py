# Let me approach this differently.
# The existing code passes:
# - Each single move followed by its inverse = solved
# - Each move repeated 4 times = solved
# - Opposite face commutators: U D U' D' = solved, R L R' L' = solved, F B F' B' = solved
#
# But FAILS:
# - U F U' F' != solved (commutator of adjacent faces)
# - T-perm twice != solved
# - Sune has order 6 instead of 8
#
# The DISPLAY issue reported is that the scrambled state "doesn't show correctly".
# This could mean: the move simulation is correct but the NET DRAWING is wrong.
# OR the move simulation itself is wrong.
#
# Let me first check if the simulation is actually wrong by verifying against
# a known algorithm with a known visual result.
#
# The simplest test: if I apply R then look at the cube state, are the colors correct?

_MOVE_CYCLES = {
    'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',[0,1,2]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[2,1,0]),('L',[8,5,2])]),
    'B': ('B', [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[6,3,0]),('D',[2,5,8])]),
    'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',[8,5,2]),('U',[0,3,6])]),
}

_SOLVED = {'U':'W','D':'Y','F':'G','B':'B','R':'R','L':'O'}
_STICKER_LABEL = {  # face -> face_letter (first char of color name)
    'U':'W','D':'Y','F':'G','B':'B','R':'R','L':'O'
}

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

    def print_net(self):
        """Print a simple ASCII net showing face colors at each position."""
        def row(face, r):
            return ''.join(self.faces[face][r*3+c][0] for c in range(3))

        # U
        for r in range(3):
            print('   ' + row('U', r))
        # L F R B
        for r in range(3):
            print(row('L', r) + row('F', r) + row('R', r) + row('B', r))
        # D
        for r in range(3):
            print('   ' + row('D', r))

# Apply U move and display
print("=== After U CW ===")
cs = CubeState()
cs.apply("U")
cs.print_net()
print()
print("Expected after U CW:")
print("   WWW          (U rotated, all white)")
print("   WWW")
print("   WWW")
print("BBBGGGRRRBB?   (L gets B's top, F gets L's top, R gets F's top, B gets R's top)")
print("Wait - let me think carefully...")
print()
print("U CW (from above): F top -> R top, R top -> B top, B top -> L top, L top -> F top")
print("Initial: F=G, L=O, R=R, B=B (solved colors)")
print("After: F top = L top = Orange, R top = F top = Green, B top = R top = Red, L top = B top = Blue")
print()

# Apply F move and display
print("=== After F CW ===")
cs2 = CubeState()
cs2.apply("F")
cs2.print_net()
print()
print("Expected after F CW:")
print("F CW (from front): U bottom -> R left, R left -> D top, D top -> L right, L right -> U bottom")
print("Initial: U=W, R=R, D=Y, L=O")
print("After: U bottom = L right = Orange (reversed order), R left = U bottom = White,")
print("       D top = R left = Red (reversed), L right = D top = Yellow (reversed)")

# Apply R move and display
print()
print("=== After R CW ===")
cs3 = CubeState()
cs3.apply("R")
cs3.print_net()
print()
print("Expected after R CW:")
print("R CW (from right): F right -> U right, U right -> B left(reversed), B left(reversed) -> D right, D right -> F right")

# Check if simple known result is correct
# Apply R and see if R face CW, and edge stickers are correct
print()
print("=== Verify R CW stickers ===")
print("R face should be rotated CW:")
print("  R face:", cs3.faces['R'])
print("  Expected CW rotation of [R]*9: still all R but rotated (all same so no visible change)")
print()
print("  F right col (F[2,5,8]):", cs3.faces['F'][2], cs3.faces['F'][5], cs3.faces['F'][8])
print("  Expected: D right col originally = [Y,Y,Y], so F[2,5,8] should be Yellow")
print()
print("  U right col (U[2,5,8]):", cs3.faces['U'][2], cs3.faces['U'][5], cs3.faces['U'][8])
print("  Expected: F right col originally = [G,G,G], so U[2,5,8] should be Green")
print()
print("  B col (B[6,3,0]):", cs3.faces['B'][6], cs3.faces['B'][3], cs3.faces['B'][0])
print("  Expected: U right col originally = [W,W,W], so B[6,3,0] should be White")
print()
print("  D right col (D[2,5,8]):", cs3.faces['D'][2], cs3.faces['D'][5], cs3.faces['D'][8])
print("  Expected: B[6,3,0] originally = [B,B,B] reversed = [B,B,B], so D[2,5,8] should be Blue")
