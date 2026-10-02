"""
Test whether the ORIGINAL code cycles (unchanged) produce visually correct output.
Strategy: apply a simple known scramble and compare the visual net against what a
physical cube would look like.

Test case: apply only U (clockwise).
Expected visual net:
     [U]
  W W W
  W W W
  W W W
[L][F][R][B]
  B O G R   <- top rows (B got top from before=Blue, F got Orange from L, R got Green from F, B got Red from R)
  O G R B   <- but wait: B[0,1,2] = Red, but in net B is drawn with B[0] at top-left
  O G R B   <- and B's top row should show 'R' (Red) BUT:
     [D]           after U CW, B top row in NET represents the stickers adjacent to U's back row
  Y Y Y
  Y Y Y
  Y Y Y

With ORIGINAL code (B cycle in U = B[0,1,2]): B[0,1,2] = R(Red) after U CW.
The net draws B[0]=R at top-left of B area.
But for a correct physical net: B is unfolded to the right of R.
When folding B back, B's LEFT column in net becomes B's adjacent-to-R edge.
B's adjacent-to-R edge = B's right column from behind (B[2,5,8]).
The code puts R(Red) at B[0,1,2] (top row), which in the NET shows as the TOP of B.
B's top in the net connects to U's back row when folded.
After U CW: B's top row = Red. U's back row = White (unchanged). Correct for adjacent edge display.

With CORRECTED code (B cycle in U = B[2,1,0]): B[2,1,0] = R(Red) after U CW.
B[2]=R, B[1]=R, B[0]=R. In the net, B's top row = B[0,1,2] = R,R,R. Same visual output!
Wait, both give B's top row = Red? Let me check...

For ORIGINAL code U cycle [F[0,1,2], R[0,1,2], B[0,1,2], L[0,1,2]]:
Right-shift: B gets from R[0,1,2] = F's original top row = Green.
Wait no: after U CW, B[0,1,2] gets R[0,1,2] (R's top row before move).
On solved cube: R[0,1,2] = [R,R,R] (Red). B[0,1,2] = [R,R,R]. B's top row = Red. ✓

For CORRECTED code U cycle [F[0,1,2], R[0,1,2], B[2,1,0], L[0,1,2]]:
B[2,1,0] gets R[0,1,2]. B[2]=R[0]=R, B[1]=R[1]=R, B[0]=R[2]=R. B[0,1,2] = [R,R,R]. Same!

For both U cycles: after U CW, B[0,1,2] = [R,R,R] on a solved cube.
For a solved cube with all same colors, the visual output is IDENTICAL.
The difference only shows when stickers are DIFFERENT colors within a row.

Let me test with R move:
ORIGINAL R cycle: B[6,3,0] = U[2,5,8] = [W,W,W].
B[0]=W, B[3]=W, B[6]=W. B's left column = White. In net: B shows White on left side.

CORRECTED R cycle: B[8,5,2] = U[2,5,8] = [W,W,W].
B[2]=W, B[5]=W, B[8]=W. B's right column = White. In net: B shows White on right side.

Physically: after R CW, White (from U) should appear on which side of B in the net?
B is to the right of R. R's right edge is adjacent to B in the net.
After R CW: the stickers on R's right column should be at B's adjacent edge.
But what ACTUAL stickers are at B's edge adjacent to R?
After R CW: the pieces at the R-B interface (x=+1, z=-1) are: they come from U (R CW: U->B).
U's stickers at x=+1 (right column): U[2,5,8] = White (on solved cube). These go to B.
These stickers end up at B's x=+1 side (BUR, BMR, BDR) = B[2,5,8] (right column from behind).
In the NET: B is drawn with B[0] at top-left, B[2] at top-right.
B[2,5,8] (right column) = White. Shown on RIGHT side of B area in net.
In the net, B's RIGHT side is adjacent to ... nothing (it's the far right of the net, no face there).
B's LEFT side in net is adjacent to R's right side.
So: in the net, the edge between R and B shows: R's right stickers on the R side, and B's left stickers on the B side.
These should be from the SAME physical pieces (both at the R-B interface).
After R CW: R's right column (R[2,5,8]) has Yellow (from D). B's side adjacent to R = B[2,5,8] or B[0,3,6]?
B[2,5,8] = right column of B from behind = x=+1 side. The R-B interface is at x=+1,z=-1.
On B face: x=+1 side = B[2,5,8]. These are adjacent to R in 3D.
In the net: B's left column (B[0,3,6]) is adjacent to R's right column (R[2,5,8]) as displayed.
After R CW: R[2,5,8] = Yellow (correct). B[0,3,6] in the net (with CORRECTED cycle) = unchanged = Blue.
But physically: B[2,5,8] = White (what R put there). B[2] is at the TOP RIGHT of B in net.
The net shows B's LEFT column as Blue, B's RIGHT column as White.
Physically adjacent edge: R[2,5,8]=Yellow adjacent to B[2,5,8]=White = THESE ARE SAME PIECES, different faces.
This is correct: Yellow from D is on R face, White from U is on B face of the same piece.

With ORIGINAL R cycle: B[0,3,6] = White. In net: B's LEFT column = White.
And R[2,5,8] = Yellow (adjacency: R's right edge is Yellow).
Left edge of B in net shows White. But physically the pieces at R-B interface should show Blue on B (since R CW moved U's White pieces to B's right col, not left col).
So ORIGINAL shows B's left = White (WRONG), CORRECTED shows B's right = White (CORRECT display).
"""

_SOLVED = {'U':'W','D':'Y','F':'G','B':'B','R':'R','L':'O'}
_MOVE_CYCLES_ORIG = {
    'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',[0,1,2]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[2,1,0]),('L',[8,5,2])]),
    'B': ('B', [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[6,3,0]),('D',[2,5,8])]),
    'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',[8,5,2]),('U',[0,3,6])]),
}
_MOVE_CYCLES_NEW = {
    'U': ('U', [('F',[0,1,2]),('R',[0,1,2]),('B',[2,1,0]),('L',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('L',[6,7,8]),('B',[6,7,8]),('R',[6,7,8])]),
    'F': ('F', [('U',[6,7,8]),('R',[0,3,6]),('D',[8,7,6]),('L',[8,5,2])]),
    'B': ('B', [('D',[6,7,8]),('R',[8,5,2]),('U',[2,1,0]),('L',[0,3,6])]),
    'R': ('R', [('F',[2,5,8]),('U',[2,5,8]),('B',[8,5,2]),('D',[8,5,2])]),
    'L': ('L', [('F',[0,3,6]),('D',[0,3,6]),('B',[8,5,2]),('U',[0,3,6])]),
}

class CubeState:
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
    def print_net(self, label=""):
        def r(face, row):
            return ''.join(self.faces[face][row*3+c][0] for c in range(3))
        if label:
            print(f"=== {label} ===")
        print("     U     ")
        for i in range(3): print("  ", r('U',i))
        print("  L  F  R  B")
        for i in range(3):
            print(r('L',i)+r('F',i)+r('R',i)+r('B',i))
        print("     D     ")
        for i in range(3): print("  ", r('D',i))

cs1 = CubeState(_MOVE_CYCLES_ORIG)
cs1.apply("R")
cs1.print_net("ORIGINAL cycles, after R CW")

print()
cs2 = CubeState(_MOVE_CYCLES_NEW)
cs2.apply("R")
cs2.print_net("CORRECTED cycles, after R CW")

print()
print("Physical expectation after R CW:")
print("U right column (U[2,5,8]) should have Green (from F right col)")
print("B's x=+1 side (right col from behind = B[2,5,8]) should have White (from U)")
print("D right col should have Blue (from B)")
print("F right col should have Yellow (from D)")
print()
print("In the net display (B drawn left-to-right as stored):")
print("ORIGINAL: B left column (B[0,3,6]) = White. WRONG (should be B right col = White)")
print("CORRECTED: B right column (B[2,5,8]) = White. CORRECT")
print()
print("B face - ORIGINAL:", cs1.faces['B'])
print("B face - CORRECTED:", cs2.faces['B'])
