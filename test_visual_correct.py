"""
Test whether the ORIGINAL code produces correct VISUAL output for simple scrambles.
The visual test: apply a known scramble and check if specific corner/edge stickers
appear at the correct positions in the net.

Test 1: Apply R CW.
Expected:
- U right col = Green (from F right col)
- F right col = Yellow (from D right col)
- D right col = Blue (from B col adjacent to R)
- B col adjacent to R = White (from U right col)

The B face: which stickers are adjacent to R?
Physically: B face at z=-1, adjacent to R face (x=+1) at B's x=+1 side.
B[2]=BUR=(y=+1,x=+1), B[5]=BMR, B[8]=BDR=(y=-1,x=+1). This is B's RIGHT column from behind.
After R CW: these should be White (from U's right col U[2,5,8]).

With ORIGINAL cycles: B[6,3,0] = U[2,5,8] = White.
B[6]=BDL, B[0]=BUL (LEFT column). NOT B[2,5,8].
So original code puts White at B's LEFT column in the net.
But physically White should be at B's RIGHT column.

In the net display, B is drawn left-to-right as B[0,1,2,...].
B's left in net = B[0] = BUL. B's right in net = B[2] = BUR.
After R CW with original code: B[0,3,6]=White. B's left side in net shows White.
But physically: B[2,5,8]=White should show on B's right side in net.

The net shows B's left side adjacent to R's right side.
After R CW: R's right edge shows Yellow (from D). B's adjacent edge should show White (from U).
Original code: B's adjacent edge in net = B[0,3,6] = White. ✓ (Visually matches!)
Corrected code: B's adjacent edge in net = B[0,3,6] = Blue (unchanged). B[2,5,8]=White (far side). ✗

WAIT. This is the opposite of what I said before!

Let me re-examine: B is to the RIGHT of R in the net. B's LEFT edge in net is adjacent to R's RIGHT edge.
After R CW: the pieces at the R-B interface...

In 3D: R face (x=+1) is adjacent to B face (z=-1) along the x=+1, z=-1 edge.
This edge on R = R's left edge (z=-1 side of R) = R[0,3,6] if R[0]=BUR=(y=+1,z=-1). But wait: I established R[0]=FUR=(y=+1,z=+1). Hmm.

Let me re-examine R face layout with R[0]=FUR:
R[0]=FUR=(y=+1,z=+1), R[2]=BUR=(y=+1,z=-1), R[6]=FDR=(y=-1,z=+1), R[8]=BDR=(y=-1,z=-1).
R's LEFT edge in net = R[0,3,6] = (FUR,FMR,FDR) = z=+1 side = adjacent to F face (NOT adjacent to B!).
R's RIGHT edge in net = R[2,5,8] = (BUR,BMR,BDR) = z=-1 side = adjacent to B face.

After R CW: R's RIGHT edge (R[2,5,8]) should come from... D's right col?
R CW cycle: F[2,5,8]->U[2,5,8]->B[?]->D[?]->F[2,5,8]. R face rotates.
After R CW: R[2,5,8] (the edge adjacent to B in net) = R face CW rotation. From solved: R[2]=R, R[5]=R, R[8]=R. After CW rotation of R face: R[2] gets old R[8] value (from CW rotation formula). All Red, so still Red.

So in the net after R CW:
- R's right edge (adjacent to B) = Red (unchanged, just rotated)
- B's left edge (adjacent to R in net) = ?

With original code: B[0,3,6]=White. In net, B[0,3,6] is the LEFT column of B area (adjacent to R).
Physical: after R CW, the pieces at the R-B interface (x=+1, z=-1):
R face stickers at this interface: R[2,5,8]. After CW rotation of R: R[2]=old R[8]? Wait no:
The R face rotation puts old R[8] (BDR) at new R[0] (FUR position in net). The rotation:
CW: new[0]=old[6], new[1]=old[3], new[2]=old[0], etc.
new R[2] = old R[0] = old FUR = Red (solved).
new R[5] = old R[3] = Red.
new R[8] = old R[6] = Red.
So R[2,5,8] stays Red after R rotation (all same color).

B face stickers at R-B interface: B[2,5,8] = B's right column = BUR,BMR,BDR.
After R CW: U[2,5,8] -> B[?]. Original: B[6,3,0]=White. B[0]=BUL (LEFT), B[2]=BUR (RIGHT).
The physical R-B interface is at B[2,5,8] (B's right col). Original code puts White at B[0,3,6] (left col).
So physically, the R-B interface on B face shows Blue (unchanged) with original code. But it should show White.

In the NET: B's left col (B[0,3,6]) is adjacent to R's right col. Original shows White there.
But PHYSICALLY, the pieces at the R-B interface have R=Red and B=Blue (unchanged) OR after R CW, the pieces MOVED.

After R CW: the pieces at R-B interface MOVED. The OLD R-B interface pieces (at x=+1,z=-1) moved:
- BUR piece (was at R-B-U corner): moved to FUR position (R CW: BUR->FUR).
  At FUR: R sticker = R[0]=Red, F sticker = F[2]=?, U sticker = U[8]=?
- The pieces now AT the R-B interface came from F-R interface (after R CW: F->U->B->D).

After R CW: B gets U's right col values. Specifically:
U[2]=BUR sticker (the sticker at the top of U's right column). This went to B.
Where in B? The U sticker at BUR: after R CW, the BUR piece moved to BDR.
At BDR: U sticker (+Y) -> after R CW: +Y -> -Z = B face. BDR on B = B[8].
So U[2] went to B[8]. With original code: B[0]=U[8], B[6]=U[2]. Wrong positions!

Physical interface check:
After R CW: the NEW pieces at R-B interface (x=+1, z=-1):
- These came from U-R interface (U right col -> B via R CW).
- U[2](BUR) -> B[8](BDR). ✓ This IS at the R-B interface (BDR is at x=+1,z=-1).
- U[5](UMR) -> B[5](BMR). ✓
- U[8](FUR) -> B[2](BUR). ✓ This is at B[2] = B's right column top = BUR, at R-B-U interface.

Physical interface stickers after R CW: B[2,5,8]=White. B[2,5,8] is B's right col.
In the net: B's LEFT col (B[0,3,6]) is shown adjacent to R. B's RIGHT col (B[2,5,8]) is the FAR SIDE.

So the physically correct display should show:
- B's left side (net-adjacent-to-R) = Blue (the old non-moved pieces)
- B's right side (net-far-side) = White (the new pieces from R CW)

ORIGINAL code puts White at B[0,3,6] (net-left = adjacent to R). WRONG display.
CORRECTED code (B[8,5,2] in R cycle) puts White at B[2,5,8] (net-right). CORRECT display.

So my earlier conclusion was right: the CORRECTED R cycle gives correct visual display.
"""

print("Summary of visual analysis:")
print()
print("For R CW:")
print("- ORIGINAL: White appears at B's LEFT column in net (adjacent to R). VISUALLY WRONG.")
print("  (Physically, B's left col is NOT adjacent to R face in 3D)")
print("- CORRECTED (B[8,5,2]): White appears at B's RIGHT column. Still WRONG?")
print("  (In the net, B right col is NOT adjacent to R)")
print()
print("Actually: in the net, B's LEFT column IS adjacent to R's RIGHT column.")
print("After R CW, the R-B interface pieces have their B-face stickers at B[2,5,8].")
print("B[2,5,8] is B's RIGHT column in the net. NOT adjacent to R in the net.")
print()
print("Wait - which B column is at the R-B interface, considering physical vs net orientation?")
print()
print("Physical: R-B interface = x=+1 edge of B face = B's x=+1 side.")
print("B[2,5,8] = B's x=+1 side (BUR,BMR,BDR) = RIGHT column from behind = RIGHT in net.")
print()
print("In the net: B is to the right of R. B's LEFT edge in net is adjacent to R's RIGHT edge.")
print("B's left edge in net = B's leftmost column = B[0,3,6].")
print("B[0,3,6] = B's x=-1 side (BUL,BML,BDL) = LEFT column from behind.")
print()
print("So in the NET: B's LEFT col (B[0,3,6]) is adjacent to R, but physically B's RIGHT col (B[2,5,8]) is adjacent to R.")
print()
print("This is the fundamental geometric inconsistency: the net unfolding flips B's left-right.")
print()
print("For the NET to be visually correct, B must be MIRRORED (drawn right-to-left).")
print("OR: the simulation must store B stickers in the 'mirrored' convention (B[0]=BUR, B[2]=BUL).")
print()
print("CONCLUSION:")
print("The display bug can be fixed in ONE of two ways:")
print("1. Fix draw_net to mirror B when drawing it (draw B[2,1,0] at positions 0,1,2 etc.)")
print("2. Fix the simulation to store B stickers in mirrored convention, which means:")
print("   - B[0]=BUR, B[2]=BUL, B[6]=BDR, B[8]=BDL (mirrored left-right)")
print("   - This changes ALL B interactions but makes net display correct without draw fix")
print()
print("Option 1 is the MINIMAL fix: just change draw_net's B rendering.")
print("The simulation logic stays the same (internally consistent), just the display is fixed.")

# Test: apply R CW with ORIGINAL code, then show what net looks like
# and compare with what would be physically correct.

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

def print_net(cs, b_mirrored=False):
    def r(face, row, mirror=False):
        if mirror:
            return ''.join(cs.faces[face][row*3+(2-c)][0] for c in range(3))
        return ''.join(cs.faces[face][row*3+c][0] for c in range(3))
    for i in range(3): print("   "+r('U',i))
    for i in range(3):
        b_r = r('B',i,b_mirrored)
        print(r('L',i)+r('F',i)+r('R',i)+b_r)
    for i in range(3): print("   "+r('D',i))

cs = CS(_ORIG)
cs.apply("R")
print()
print("After R CW - net (original, B not mirrored):")
print_net(cs, False)
print()
print("After R CW - net (B mirrored in display):")
print_net(cs, True)
print()
print("Physical expectation:")
print("B's edge adjacent to R should show Blue (unchanged), B's far edge shows White (from U)")
print("Net: B[0,3,6] is left (adjacent to R), B[2,5,8] is right")
print("Correct display: B left (adj R) = Blue, B right = White")
print("Original (no mirror): B[0,1,2] = W B B -> left=White WRONG")
print("B mirrored: B[2,1,0] = B B W -> left=Blue CORRECT")
