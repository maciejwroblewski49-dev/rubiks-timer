"""
Create a reference Rubik's cube implementation using a different representation
and compare it against our simulation.

I'll represent the cube as 6 faces x 9 stickers, using a 2D array indexed as:
face[0..5][0..8] where faces are: 0=U, 1=D, 2=F, 3=B, 4=R, 5=L

Using the kociemba/standard representation for moves.
"""
# Standard 3x3 cube moves - well-known correct implementation
# Uses faces: U=0 D=1 F=2 B=3 R=4 L=5
# Stickers: 0-8 left-to-right, top-to-bottom when looking at the face from outside
#
# U face from above:
# 0 1 2
# 3 4 5
# 6 7 8
# where row 0 is adjacent to B, row 2 is adjacent to F.
#
# Standard MOVES (well-tested cycles from cubing community):
# U CW: U face rotates CW. Stickers: F[0,1,2]->R[0,1,2]->B[0,1,2]->L[0,1,2]->F[0,1,2]
# BUT: the direction depends on the convention.

# Let me use a different approach: build a cube from scratch using direct physical simulation.
# The cube state is 54 stickers. I'll number them:
# U face: 0-8, D face: 9-17, F face: 18-26, B face: 27-35, R face: 36-44, L face: 45-53

# Actually, let me find a simple Python Rubik's cube implementation online pattern.
# Most correct implementations I know use this pattern for U:
# U CW: cycle 4 groups of 3 stickers:
#   F[0,1,2] -> R[0,1,2] -> B[0,1,2] -> L[0,1,2]  (simple same-index cycle)
# This is the most common representation and IS correct.
# If that's true, then the ORIGINAL code's U cycle [F[0,1,2],R[0,1,2],B[0,1,2],L[0,1,2]] is CORRECT.

# So why does T-perm give wrong order? Let me check with a completely fresh implementation
# using the standard cycles that are known to be correct from the internet.

# Known correct cycles (from https://github.com/adrianmanrique/rubiks-cube-solver/blob/master/cube.py
# and similar references):

FACES = {'U':0, 'D':1, 'F':2, 'B':3, 'R':4, 'L':5}
SOLVED_COLORS = ['W']*9 + ['Y']*9 + ['G']*9 + ['B']*9 + ['R']*9 + ['O']*9

# Standard adjacent face cycles (these are well-established):
# U CW: F->R->B->L for indices 0,1,2 (top row of each)
# D CW: F->L->B->R for indices 6,7,8 (bottom row of each)
# F CW: U->R->D->L for specific indices
# B CW: U->L->D->R for specific indices
# R CW: F->U->B->D for specific indices
# L CW: F->D->B->U for specific indices

# Let me use a completely verified implementation:
# Face sticker numbering:
#   U face: U0 U1 U2 / U3 U4 U5 / U6 U7 U8
#   (viewed from outside - U from above with F at bottom: U6 adjacent to F)

class RefCube:
    """Reference implementation using permutation arrays."""

    # Standard cycles for each CW move
    # Each move is a list of 4-cycles (groups of 4 sticker positions that rotate)
    # Format: [[a,b,c,d], ...] means a->b->c->d->a (sticker at a goes to b, etc.)

    FACE_ROTATIONS = {
        'U': [0,1,2,5,8,7,6,3],   # face stickers in CW order
        'D': [9,10,11,14,17,16,15,12],
        'F': [18,19,20,23,26,25,24,21],
        'B': [27,28,29,32,35,34,33,30],
        'R': [36,37,38,41,44,43,42,39],
        'L': [45,46,47,50,53,52,51,48],
    }

    # Edge cycles: [from_pos, to_pos, from_pos2, to_pos2, ...]
    # Using the standard representation where each sticker has a global index 0-53
    # U=0-8, D=9-17, F=18-26, B=27-35, R=36-44, L=45-53
    # Within each face, sticker i is at row i//3, col i%3 when viewed from outside
    # U face (from above, F at bottom):
    #   0  1  2   <- back (adjacent to B)
    #   3  4  5
    #   6  7  8   <- front (adjacent to F)
    # F face (from front):
    #   18 19 20  <- top (adjacent to U bottom)
    #   21 22 23
    #   24 25 26  <- bottom (adjacent to D)
    # R face (from right, F at left):
    #   36 37 38  <- top (adjacent to U right)
    #   39 40 41
    #   42 43 44  <- bottom
    # B face (from behind, opposite convention):
    #   27 28 29  <- top (adjacent to U back)
    #   30 31 32
    #   33 34 35  <- bottom
    # D face (from below, F at top):
    #   9  10 11  <- front (adjacent to F bottom)
    #   12 13 14
    #   15 16 17  <- back (adjacent to B bottom)
    # L face (from left, F at right):
    #   45 46 47  <- top
    #   48 49 50
    #   51 52 53  <- bottom

    # Edge cycles for each move (4-cycle notation: [a,b,c,d] means sticker at a->b, b->c, c->d, d->a)
    # U CW: top rows of F,R,B,L cycle
    EDGE_CYCLES = {
        'U': [[18,36,27,45], [19,37,28,46], [20,38,29,47]],  # F[0,1,2]->R[0,1,2]->B[0,1,2]->L[0,1,2]
        'D': [[24,51,33,42], [25,52,34,43], [26,53,35,44]],  # F bottom -> L bottom -> B bottom -> R bottom
        'F': [[6,36,11,53], [7,39,10,50], [8,42,9,47]],     # U bottom -> R left -> D top -> L right
        'B': [[0,48,17,41], [1,51,16,38], [2,54-9,15,35]],  # hmm need to think
        'R': [[2,27+2,17-2,20+2], ...],  # getting complicated
    }

# Actually let me just hard-code known-correct move tables.
# Reference: https://medium.com/@benjamin.botto/implementing-an-optimal-rubiks-cube-solver-using-korf-s-algorithm-bf750b332cf9
# The standard face sticker indices (0-53):
# 0-8: U face  9-17: D face  18-26: F face  27-35: B face  36-44: R face  45-53: L face

# U CW: F[0..2] -> R[0..2] -> B[0..2] -> L[0..2]  (same indices within face)
# D CW: F[6..8] -> L[6..8] -> B[6..8] -> R[6..8]  (same indices)
# But for B: B[0..2] after U CW should come from R[0..2].
# Hmm but B is viewed from BEHIND. B[0] is B's top-LEFT when viewed from behind.
# After U CW: R's top row goes to B's top row.
# R[0,1,2] (top row of R) -> B[0,1,2] (top row of B from behind) ? OR B[2,1,0] (reversed)?
# This depends on which direction "left" and "right" are oriented relative to each other.
# R's top row: R[0]=top-left of R (as seen from right), R[2]=top-right of R.
# B's top row: B[0]=top-left of B (as seen from behind), B[2]=top-right.
# After U CW: R's top-right (R[2]) goes to B's top-left (B[0]) because:
# - R[2]=BUR corner (back-top-right of cube)
# - After U CW, BUR piece goes to BUL position
# - At BUL, the old R-face sticker becomes B-face sticker
# So R[2]->B[0] (reversed). Thus B[2,1,0] gets R[0,1,2]. This matches MY derivation.
#
# But many online cube implementations use B[0,1,2] gets R[0,1,2] (same indices).
# This means they define B face differently: B[0] = top-RIGHT from behind = BUR.
#
# The question is: is B face stored as left=LEFT or left=RIGHT when looking from behind?
# In many simulators: B face is stored as if you're looking at it from INSIDE the cube (from front face looking through). In that view: what's physically left is still left.
# This gives B[0]=top-LEFT from the CUBE'S perspective (physically left = -X). = top-LEFT from behind. ✓
#
# OR: B face is stored as if it were "reflected" - B[0]=top-left would be top-right from the standard view.
#
# Let me try with the ORIGINAL U cycle (B[0,1,2] same as others) and see if T-perm is order 2:

_SOLVED = {'U':'W','D':'Y','F':'G','B':'B','R':'R','L':'O'}

# Try: Original U cycle (all [0,1,2]) with corrected R.B=[8,5,2] and L.B=[6,3,0] and correct B and D:
_TRY1 = {
    'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',[0,1,2]),('L',[0,1,2])]),  # ORIGINAL U
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[8,7,6]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[2,1,0]),('L',[8,5,2])]),
    'B': ('B', [('U',[0,1,2]),('R',[2,5,8]),('D',[8,7,6]),('L',[0,3,6])]),
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

tests = [
    ("R L R' L'", "R L R' L'", 1),
    ("U D U' D'", "U D U' D'", 1),
    ("F B F' B'", "F B F' B'", 1),
    ("R U R' U' x6", "R U R' U'", 6),
    ("T-perm x2", "R U R' U' R' F R2 U' R' U' R U R' F'", 2),
    ("Sune x8", "R U R' U R U2 R'", 8),
]

for label, cycles in [("Original U + fixed others", _TRY1)]:
    print(f"{label}:")
    for name, alg, exp in tests:
        order = find_order(cycles, alg)
        print(f"  {name}: {order} (exp {exp}) {'OK' if order==exp else 'FAIL'}")
    print()
