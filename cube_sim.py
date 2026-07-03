"""All puzzle-state simulators (3x3, 2x2, 4x4, Skewb, FTO, Clock) and the 2D net drawing for each, plus the dispatch used by the timer's scramble-preview UI."""
import math

_WCA_HEX = {
    'W': '#FFFFFF', 'Y': '#FFD500', 'G': '#009B48',
    'B': '#0046AD', 'R': '#B71234', 'O': '#FF5800',
}

# Edge cycles for each CW move.
# Algorithm: right-shift — face[k] gets stickers from face[k-1].
# Meaning stickers "travel" in list order: [0]→[1]→[2]→[3]→[0].
_MOVE_CYCLES = {
    'U': ('U', [('F',[0,1,2]),('L',[0,1,2]),('B',[0,1,2]),('R',[0,1,2])]),
    'D': ('D', [('F',[6,7,8]),('R',[6,7,8]),('B',[6,7,8]),('L',[6,7,8])]),
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
        if base not in _MOVE_CYCLES:
            return
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
            if not tok:
                continue
            if tok.endswith("'"):
                for _ in range(3): self._apply_cw(tok[:-1])
            elif tok.endswith('2'):
                for _ in range(2): self._apply_cw(tok[:-1])
            else:
                self._apply_cw(tok)

    def draw_net(self, canvas, x0, y0, cell):
        # Layout:   [U]
        #       [L][F][R][B]
        #           [D]
        origins = {
            'U': (x0 + 3*cell, y0),
            'L': (x0,           y0 + 3*cell),
            'F': (x0 + 3*cell,  y0 + 3*cell),
            'R': (x0 + 6*cell,  y0 + 3*cell),
            'B': (x0 + 9*cell,  y0 + 3*cell),
            'D': (x0 + 3*cell,  y0 + 6*cell),
        }
        bw = max(1, cell // 10)
        for face, (fx, fy) in origins.items():
            for i, col in enumerate(self.faces[face]):
                r, c = divmod(i, 3)
                x1 = fx + c * cell
                y1 = fy + r * cell
                canvas.create_rectangle(
                    x1, y1, x1 + cell - 1, y1 + cell - 1,
                    fill=_WCA_HEX[col], outline='#111111', width=bw,
                )


_MOVE_CYCLES_2 = {
    'U': ('U', [('F',[0,1]),('L',[0,1]),('B',[0,1]),('R',[0,1])]),
    'D': ('D', [('F',[2,3]),('R',[2,3]),('B',[2,3]),('L',[2,3])]),
    'F': ('F', [('U',[2,3]),('R',[0,2]),('D',[1,0]),('L',[3,1])]),
    'B': ('B', [('D',[2,3]),('R',[3,1]),('U',[1,0]),('L',[0,2])]),
    'R': ('R', [('F',[1,3]),('U',[1,3]),('B',[2,0]),('D',[1,3])]),
    'L': ('L', [('F',[0,2]),('D',[0,2]),('B',[3,1]),('U',[0,2])]),
}

class Cube2State:
    _SOLVED = {'U':'W','D':'Y','F':'G','B':'B','R':'R','L':'O'}

    def __init__(self):
        self.faces = {f: [self._SOLVED[f]] * 4 for f in 'UDFBRL'}

    def _rotate_cw(self, f):
        c = self.faces[f][:]
        self.faces[f] = [c[2],c[0],c[3],c[1]]

    def _apply_cw(self, base):
        if base not in _MOVE_CYCLES_2: return
        face, cycle = _MOVE_CYCLES_2[base]
        self._rotate_cw(face)
        n = len(cycle)
        saved = [[self.faces[fn][i] for i in idx] for fn, idx in cycle]
        for k in range(n):
            fn, idx = cycle[k]
            src = saved[(k-1) % n]
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

    def draw_net(self, canvas, x0, y0, cell):
        origins = {
            'U': (x0+2*cell, y0),
            'L': (x0,         y0+2*cell),
            'F': (x0+2*cell,  y0+2*cell),
            'R': (x0+4*cell,  y0+2*cell),
            'B': (x0+6*cell,  y0+2*cell),
            'D': (x0+2*cell,  y0+4*cell),
        }
        bw = max(1, cell//8)
        for face, (fx, fy) in origins.items():
            for i, col in enumerate(self.faces[face]):
                r, c = divmod(i, 2)
                canvas.create_rectangle(
                    fx+c*cell, fy+r*cell,
                    fx+c*cell+cell-1, fy+r*cell+cell-1,
                    fill=_WCA_HEX[col], outline='#111111', width=bw)


# ── 4x4x4 (Rubik's Revenge) — 3D-coordinate model, same technique as Skewb
# below: each sticker is a point (x,y,z) with an outward normal, and a move
# rotates every sticker whose axis coordinate falls in the turning layer(s)
# by the matching 90°/180° rotation matrix. This avoids hand-authoring
# face-cycle tables (error-prone to get right by hand — the classic mirror/
# wrong-direction bug). Verified against Herbert Kociemba's two-phase-solver
# corner-permutation tables (cpU/cpR/cpF/cpD in
# https://github.com/hkociemba/RubiksCube-TwophaseSolver/blob/master/cubie.py):
# a single U/D/R/F move here produces exactly the same corner cycle as that
# reference implementation.

_C4_FACE_NORMALS = {
    'U': (0, 1, 0), 'D': (0, -1, 0), 'F': (0, 0, 1),
    'B': (0, 0, -1), 'L': (-1, 0, 0), 'R': (1, 0, 0),
}
_C4_SOLVED = {'U': 'W', 'D': 'Y', 'F': 'G', 'B': 'B', 'L': 'O', 'R': 'R'}

# Per-face (row, col) convention chosen to already match the flat-net drawing
# orientation (U top, L-F-R-B row, D bottom) — see draw_net below.
def _c4_forward(face, row, col):
    if face == 'U': return (2*col-3, 3, 2*row-3)
    if face == 'D': return (2*col-3, -3, 3-2*row)
    if face == 'F': return (2*col-3, 3-2*row, 3)
    if face == 'B': return (3-2*col, 3-2*row, -3)
    if face == 'L': return (-3, 3-2*row, 2*col-3)
    if face == 'R': return (3, 3-2*row, 3-2*col)

def _c4_inverse(face, x, y, z):
    if face == 'U': return (z+3)//2, (x+3)//2
    if face == 'D': return (3-z)//2, (x+3)//2
    if face == 'F': return (3-y)//2, (x+3)//2
    if face == 'B': return (3-y)//2, (3-x)//2
    if face == 'L': return (3-y)//2, (z+3)//2
    if face == 'R': return (3-y)//2, (3-z)//2

def _c4_rx(y, z, a):
    if a == 90:  return -z, y
    if a == -90: return z, -y
    return -y, -z          # 180

def _c4_ry(x, z, a):
    if a == 90:  return z, -x
    if a == -90: return -z, x
    return -x, -z

def _c4_rz(x, y, a):
    if a == 90:  return -y, x
    if a == -90: return y, -x
    return -x, -y

# letter -> (axis, base_angle for one CW turn, outer-layer coord, wide-layer coords)
_C4_BASE = {
    'U': ('y', -90, frozenset({3}),  frozenset({3, 1})),
    'D': ('y',  90, frozenset({-3}), frozenset({-3, -1})),
    'R': ('x', -90, frozenset({3}),  frozenset({3, 1})),
    'L': ('x',  90, frozenset({-3}), frozenset({-3, -1})),
    'F': ('z', -90, frozenset({3}),  frozenset({3, 1})),
    'B': ('z',  90, frozenset({-3}), frozenset({-3, -1})),
}
_C4_AXIS_IDX = {'x': 0, 'y': 1, 'z': 2}


class Cube4State:
    def __init__(self):
        self.stickers = []   # list of [x,y,z, nx,ny,nz, color]
        for face, normal in _C4_FACE_NORMALS.items():
            color = _C4_SOLVED[face]
            for row in range(4):
                for col in range(4):
                    x, y, z = _c4_forward(face, row, col)
                    self.stickers.append([x, y, z, *normal, color])

    def _turn(self, axis, layers, angle):
        ai = _C4_AXIS_IDX[axis]
        for s in self.stickers:
            if s[ai] not in layers:
                continue
            if axis == 'x':
                s[1], s[2] = _c4_rx(s[1], s[2], angle)
                s[4], s[5] = _c4_rx(s[4], s[5], angle)
            elif axis == 'y':
                s[0], s[2] = _c4_ry(s[0], s[2], angle)
                s[3], s[5] = _c4_ry(s[3], s[5], angle)
            else:
                s[0], s[1] = _c4_rz(s[0], s[1], angle)
                s[3], s[4] = _c4_rz(s[3], s[4], angle)

    def apply(self, move_str):
        for tok in move_str.split():
            if not tok:
                continue
            base_info = _C4_BASE.get(tok[0])
            if base_info is None:
                continue
            axis, base_angle, outer, wide = base_info
            rest = tok[1:]
            is_wide = rest.startswith('w')
            if is_wide:
                rest = rest[1:]
            layers = wide if is_wide else outer
            if rest == '':
                angle = base_angle
            elif rest == "'":
                angle = -base_angle
            elif rest == '2':
                angle = 180
            else:
                continue
            self._turn(axis, layers, angle)

    def draw_net(self, canvas, x0, y0, cell):
        grids = {}
        for face, normal in _C4_FACE_NORMALS.items():
            grid = [[None] * 4 for _ in range(4)]
            for s in self.stickers:
                if (s[3], s[4], s[5]) != normal:
                    continue
                r, c = _c4_inverse(face, s[0], s[1], s[2])
                grid[r][c] = s[6]
            grids[face] = grid
        origins = {
            'U': (x0 + 4*cell,  y0),
            'L': (x0,           y0 + 4*cell),
            'F': (x0 + 4*cell,  y0 + 4*cell),
            'R': (x0 + 8*cell,  y0 + 4*cell),
            'B': (x0 + 12*cell, y0 + 4*cell),
            'D': (x0 + 4*cell,  y0 + 8*cell),
        }
        bw = max(1, cell // 10)
        for face, (fx, fy) in origins.items():
            grid = grids[face]
            for r in range(4):
                for c in range(4):
                    x1 = fx + c*cell
                    y1 = fy + r*cell
                    canvas.create_rectangle(
                        x1, y1, x1 + cell - 1, y1 + cell - 1,
                        fill=_WCA_HEX[grid[r][c]], outline='#111111', width=bw)


# ── Skewb — geometric model (user grip) + isometric 2D net ───────
# A 3-D Skewb: each sticker carries an outward normal + a location (a cube
# corner ±1, or the face centre).  A move rotates the half of the puzzle on
# the move-corner's side of the cut plane by 120° about the cube diagonal.
# Move axes are set to the COMMON SOLVER GRIP — white on top, green front-
# left, red front-right (held corner-forward).  In that grip U/R/L/B turn the
# corners UBL/DBR/DFL/DBL; this is the official WCA move set rotated 90° about
# U (e.g. this R == the official scrambler's B).  Verified: a single R puts
# one green sticker on the white top, matching the physical cube.

_SKB_NORM2FACE = {(0,1,0):'U',(0,-1,0):'D',(0,0,1):'F',
                  (0,0,-1):'B',(1,0,0):'R',(-1,0,0):'L'}
_SKB_FACE2NORM = {v:k for k,v in _SKB_NORM2FACE.items()}
_SKB_FACE2COL  = {'U':'W','D':'Y','F':'G','B':'B','R':'R','L':'O'}

# corner location -> net slot (TL/TR/BR/BL) within each face
_SKB_SLOT = {
    'U': {(-1,1,-1):'TL',(1,1,-1):'TR',(1,1,1):'BR',(-1,1,1):'BL'},
    'D': {(-1,-1,1):'TL',(1,-1,1):'TR',(1,-1,-1):'BR',(-1,-1,-1):'BL'},
    'F': {(-1,1,1):'TL',(1,1,1):'TR',(1,-1,1):'BR',(-1,-1,1):'BL'},
    'B': {(1,1,-1):'TL',(-1,1,-1):'TR',(-1,-1,-1):'BR',(1,-1,-1):'BL'},
    'R': {(1,1,1):'TL',(1,1,-1):'TR',(1,-1,-1):'BR',(1,-1,1):'BL'},
    'L': {(-1,1,-1):'TL',(-1,1,1):'TR',(-1,-1,1):'BR',(-1,-1,-1):'BL'},
}

# move letter -> cube diagonal it turns, in the solver grip (see note above)
_SKB_AXES = {'U':(-1,1,-1), 'R':(1,-1,-1), 'L':(-1,-1,1), 'B':(-1,-1,-1)}

def _skb_rot120(axis):
    """Integer 3×3 matrix: a turn = -120° (clockwise) about a cube diagonal."""
    n = math.sqrt(3.0)
    x, y, z = axis[0]/n, axis[1]/n, axis[2]/n
    c = math.cos(-2*math.pi/3); s = math.sin(-2*math.pi/3); t = 1 - c
    M = [
        [t*x*x + c,     t*x*y - s*z, t*x*z + s*y],
        [t*x*y + s*z,   t*y*y + c,   t*y*z - s*x],
        [t*x*z - s*y,   t*y*z + s*x, t*z*z + c],
    ]
    return [[int(round(v)) for v in row] for row in M]

_SKB_MATS = {b: _skb_rot120(a) for b, a in _SKB_AXES.items()}

# (face, slot) -> (isometric transform slot, sticker path).  Lays the net out
# white-top / green-front-left / red-front-right, matching the solver grip.
_SKB_DRAW = {
    'U': {'C':(0,0),'TL':(0,2),'TR':(0,4),'BR':(0,3),'BL':(0,1)},
    'D': {'C':(3,0),'TL':(3,3),'TR':(3,1),'BR':(3,2),'BL':(3,4)},
    'F': {'C':(4,0),'TL':(4,1),'TR':(4,2),'BR':(4,4),'BL':(4,3)},
    'B': {'C':(1,0),'TL':(1,1),'TR':(1,2),'BR':(1,4),'BL':(1,3)},
    'R': {'C':(2,0),'TL':(2,1),'TR':(2,2),'BR':(2,4),'BL':(2,3)},
    'L': {'C':(5,0),'TL':(5,1),'TR':(5,2),'BR':(5,4),'BL':(5,3)},
}

# sticker outline in a face's local [-1,1] frame: 0=centre diamond, 1..4 corners
_SKB_PATHS = [
    [(-1,0),(0,1),(1,0),(0,-1)],
    [(-1,0),(-1,-1),(0,-1)],
    [(0,-1),(1,-1),(1,0)],
    [(-1,0),(-1,1),(0,1)],
    [(0,1),(1,1),(1,0)],
]

def _skb_transforms():
    """Six isometric face placements.  Per face the affine is
    screenX = m00*x + m01*y + m02 ; screenY = m10*x + m11*y + m12."""
    k = math.sqrt(3) / 2; P = 1.0; g = 0.12
    return [
        (P*k, -P/2, P*k,  P/2, (4*P+1.5*g)*k, P),            # 0 top
        (P*k, -P/2, 0,    P,   (7*P+3*g)*k,   1.5*P),        # 1 upper-right flap
        (P*k, -P/2, 0,    P,   (5*P+2*g)*k,   2.5*P+0.5*g),  # 2 front-right
        (0,    P,  -P*k, -P/2, (3*P+g)*k,     4.5*P+1.5*g),  # 3 bottom flap
        (P*k,  P/2, 0,    P,   (3*P+g)*k,     2.5*P+0.5*g),  # 4 front-left
        (P*k,  P/2, 0,    P,   P*k,           1.5*P),        # 5 upper-left flap
    ]

_SKB_TRANS = _skb_transforms()


class SkewbState:
    def __init__(self):
        self.st = []   # list of [nx,ny,nz, px,py,pz, face]
        for face, slots in _SKB_SLOT.items():
            nx, ny, nz = _SKB_FACE2NORM[face]
            self.st.append([nx, ny, nz, nx, ny, nz, face])      # centre sticker
            for (px, py, pz) in slots:
                self.st.append([nx, ny, nz, px, py, pz, face])  # corner sticker

    def _turn(self, ax, M):
        for s in self.st:
            if ax[0]*s[3] + ax[1]*s[4] + ax[2]*s[5] > 0:        # piece on cap side
                nx = M[0][0]*s[0] + M[0][1]*s[1] + M[0][2]*s[2]
                ny = M[1][0]*s[0] + M[1][1]*s[1] + M[1][2]*s[2]
                nz = M[2][0]*s[0] + M[2][1]*s[1] + M[2][2]*s[2]
                px = M[0][0]*s[3] + M[0][1]*s[4] + M[0][2]*s[5]
                py = M[1][0]*s[3] + M[1][1]*s[4] + M[1][2]*s[5]
                pz = M[2][0]*s[3] + M[2][1]*s[4] + M[2][2]*s[5]
                s[0],s[1],s[2],s[3],s[4],s[5] = nx,ny,nz,px,py,pz

    def apply(self, move_str):
        for tok in move_str.split():
            if not tok:
                continue
            prime = tok.endswith("'"); two = tok.endswith('2')
            base = tok[:-1] if (prime or two) else tok
            if base not in _SKB_AXES:
                continue
            n = 2 if (prime or two) else 1   # 120° CCW == two CW turns (order 3)
            ax, M = _SKB_AXES[base], _SKB_MATS[base]
            for _ in range(n):
                self._turn(ax, M)

    def _facecolors(self):
        out = {f: {} for f in 'UDFBRL'}
        for s in self.st:
            face = _SKB_NORM2FACE[(s[0], s[1], s[2])]
            if (s[3], s[4], s[5]) == (s[0], s[1], s[2]):
                out[face]['C'] = s[6]
            else:
                out[face][_SKB_SLOT[face][(s[3], s[4], s[5])]] = s[6]
        return out

    def draw_net(self, canvas, x0, y0, cell):
        nc, nr = 8, 7
        W, H = nc * cell, nr * cell
        cols = self._facecolors()
        polys = []; xs = []; ys = []
        for face in 'UDFBRL':
            for slot in ('C', 'TL', 'TR', 'BR', 'BL'):
                tf, ts = _SKB_DRAW[face][slot]
                m00, m10, m01, m11, m02, m12 = _SKB_TRANS[tf]
                pts = [(m00*x + m01*y + m02, m10*x + m11*y + m12)
                       for (x, y) in _SKB_PATHS[ts]]
                polys.append((pts, _WCA_HEX[_SKB_FACE2COL[cols[face][slot]]]))
                xs += [p[0] for p in pts]; ys += [p[1] for p in pts]
        bx0, by0, bx1, by1 = min(xs), min(ys), max(xs), max(ys)
        bw, bh = (bx1 - bx0) or 1, (by1 - by0) or 1
        sc = min(W / bw, H / bh) * 0.96
        ox = x0 + (W - bw*sc) / 2 - bx0*sc
        oy = y0 + (H - bh*sc) / 2 - by0*sc
        lw = max(1, cell // 12)
        for pts, col in polys:
            flat = []
            for (px, py) in pts:
                flat += [ox + px*sc, oy + py*sc]
            canvas.create_polygon(*flat, fill=col, outline='#111111', width=lw)


# ── Pyraminx — faithful TNoodle port + 2D net ─────────────────────
# State = TNoodle's PyraminxPuzzle.PyraminxState: image[4][9], face order
# F,D,L,R matching the WCA default color scheme (green/yellow/red/blue).
# Moves are TNoodle's exact 3-cycles: a face move (U/L/R/B) is a 3-cycle
# of 3 layer stickers plus the tip 3-cycle together; a tip move (u/l/r/b)
# is the tip 3-cycle alone. Net unfolding and the 9-triangle-per-face
# subdivision are ported from TNoodle's drawMinx/drawTriangle geometry.
# Cross-checked: the "L" tip's 3 stickers (F idx6, L idx2's own idx6, D
# idx0) land at the same shared tetrahedron vertex both in the swap table
# and in the net's pixel geometry.
# Source: https://github.com/thewca/tnoodle-lib/blob/master/scrambles/src/main/java/org/worldcubeassociation/tnoodle/puzzle/PyraminxPuzzle.java

_PYR_HEX = ['#00A651', '#FFD500', '#ED1C24', '#0051BA']   # F, D, L, R

_PYR_TURN_SWAPS = {
    0: [(0,8,3,8,2,2), (0,1,3,1,2,4), (0,2,3,2,2,5)],   # U
    1: [(2,8,1,2,0,8), (2,7,1,1,0,7), (2,5,1,8,0,5)],   # L
    2: [(3,8,0,5,1,5), (3,7,0,4,1,4), (3,5,0,2,1,2)],   # R
    3: [(1,8,2,2,3,5), (1,7,2,1,3,4), (1,5,2,8,3,2)],   # B
}
_PYR_TIP_SWAP = {
    0: (0,0,3,0,2,3),
    1: (0,6,2,6,1,0),
    2: (0,3,1,3,3,6),
    3: (1,6,2,0,3,3),
}
_PYR_AXIS = {'U': 0, 'L': 1, 'R': 2, 'B': 3}


class PyraminxState:
    def __init__(self):
        self.image = [[f] * 9 for f in range(4)]

    def _swap3(self, f1, s1, f2, s2, f3, s3):
        img = self.image
        tmp = img[f1][s1]
        img[f1][s1] = img[f2][s2]
        img[f2][s2] = img[f3][s3]
        img[f3][s3] = tmp

    def _turn_tip(self, axis):
        self._swap3(*_PYR_TIP_SWAP[axis])

    def _turn(self, axis):
        for cyc in _PYR_TURN_SWAPS[axis]:
            self._swap3(*cyc)
        self._turn_tip(axis)

    def apply(self, move_str):
        for tok in move_str.split():
            if not tok:
                continue
            letter = tok[0]
            is_tip = letter.islower()
            axis = _PYR_AXIS.get(letter.upper())
            if axis is None:
                continue
            reps = 2 if tok.endswith("'") else 1   # 120° CCW == two CW turns (order 3)
            for _ in range(reps):
                if is_tip:
                    self._turn_tip(axis)
                else:
                    self._turn(axis)

    @staticmethod
    def _tri_cells(p0, p1, p2):
        """Split triangle p0,p1,p2 into 9 small triangles. Index layout
        matches TNoodle's drawTriangle: 0/3/6 are the corner (tip)
        triangles at p0/p1/p2, the rest fill the middle."""
        pts = [p0, p1, p2]
        xs = [None] * 6
        for i in range(3):
            a, b = pts[i], pts[(i + 1) % 3]
            xs[i]     = (a[0] + (b[0]-a[0])/3.0, a[1] + (b[1]-a[1])/3.0)       # near a
            xs[i + 3] = (a[0] + 2*(b[0]-a[0])/3.0, a[1] + 2*(b[1]-a[1])/3.0)   # near b
        center = (sum(p[0] for p in pts) / 3.0, sum(p[1] for p in pts) / 3.0)
        cells = [None] * 9
        for i in range(3):
            cells[3*i]     = [pts[i], xs[i], xs[3 + (2 + i) % 3]]
            cells[3*i + 1] = [xs[i], xs[3 + (i + 2) % 3], center]
            cells[3*i + 2] = [xs[i], xs[i + 3], center]
        return cells

    def _face_triangles(self):
        """Returns {face: (p0, p1, p2)} matching TNoodle's drawMinx layout:
        F points up in the middle, D points down below it, L/R flank above."""
        ps, gap = 1.0, 0.15
        rad = 3 ** 0.5 * ps
        def verts(cx, cy, point_up):
            base = [7/6, 11/6, 1/2]
            if point_up:
                base = [a + 1/3 for a in base]
            return [(cx + rad * math.cos(a * math.pi), cy + rad * math.sin(a * math.pi)) for a in base]
        f_c = (2*gap + 3*ps, gap + 3**0.5*ps)
        d_c = (2*gap + 3*ps, 2*gap + 2*3**0.5*ps)
        l_c = (gap + 1.5*ps, gap + 3**0.5/2*ps)
        r_c = (3*gap + 4.5*ps, gap + 3**0.5/2*ps)
        return {
            0: verts(*f_c, True),
            1: verts(*d_c, False),
            2: verts(*l_c, False),
            3: verts(*r_c, False),
        }

    def draw_net(self, canvas, x0, y0, cell):
        nc, nr = 8, 7
        W, H = nc * cell, nr * cell
        faces = self._face_triangles()
        polys = []; xs = []; ys = []
        for face, (p0, p1, p2) in faces.items():
            for i, tri in enumerate(self._tri_cells(p0, p1, p2)):
                color = _PYR_HEX[self.image[face][i]]
                polys.append((tri, color))
                xs += [p[0] for p in tri]; ys += [p[1] for p in tri]
        bx0, bx1 = min(xs), max(xs); by0, by1 = min(ys), max(ys)
        bw, bh = (bx1 - bx0) or 1, (by1 - by0) or 1
        sc = min(W / bw, H / bh) * 0.94
        ox = x0 + (W - bw*sc) / 2 - bx0*sc
        oy = y0 + (H - bh*sc) / 2 - by0*sc
        lw = max(1, cell // 16)
        for tri, color in polys:
            flat = []
            for (px, py) in tri:
                flat += [ox + px*sc, oy + py*sc]
            canvas.create_polygon(*flat, fill=color, outline='#111111', width=lw)


# ── FTO (Face-Turning Octahedron) — faithful csTimer port + 2D net ─
# State = csTimer's FtoCubie (cp,co,ep,uf,rl); moves are csTimer's exact
# piece permutations.  Display notation U L R F B D BL BR maps to csTimer's
# internal U L R F B D l r (BL->l, BR->r).  Net layout taken from csTimer's
# toString(): two diamonds, each four triangular faces of 9 facelets.
# Verified vs the port: 8 moves order-3, X X' solved, colours conserved,
# scramble+inverse solves (500 random scrambles).

_FTO_HEX = ['#FFFFFF','#009B48','#8E44AD','#FF69B4',
            '#FFD500','#0046AD','#B71234','#FF5800']   # U F r l D B R L

_FU,_FF,_Fr,_Fl,_FD,_FB,_FR,_FL = 0,9,18,27,36,45,54,63

_FTO_CORN = [
    [_FU+0,_FR+0,_FF+0,_FL+0],[_FU+4,_FB+8,_Fr+4,_FR+8],[_FU+8,_FL+4,_Fl+8,_FB+4],
    [_Fl+0,_FD+0,_Fr+0,_FB+0],[_FF+4,_FD+8,_Fl+4,_FL+8],[_Fr+8,_FD+4,_FF+8,_FR+4],
]
_FTO_EDGE = [
    [_FU+1,_FR+3],[_FU+3,_FL+1],[_FU+6,_FB+6],[_Fl+1,_FD+3],[_Fr+3,_FD+1],[_FF+6,_FD+6],
    [_FF+3,_FR+1],[_FF+1,_FL+3],[_Fl+6,_FL+6],[_Fl+3,_FB+1],[_Fr+1,_FB+3],[_Fr+6,_FR+6],
]
_FTO_CTUF = [_FU+2,_FU+5,_FU+7,_FF+2,_FF+5,_FF+7,_Fr+2,_Fr+5,_Fr+7,_Fl+2,_Fl+5,_Fl+7]
_FTO_CTRL = [_FD+2,_FD+5,_FD+7,_FB+2,_FB+5,_FB+7,_FL+2,_FL+5,_FL+7,_FR+2,_FR+5,_FR+7]

# base move cubies (cp, co, ep, uf, rl) — csTimer internal names
_FTO_MOVES = {
 'U':([1,2,0,3,4,5],[0,0,0,0,0,0],[2,0,1,3,4,5,6,7,8,9,10,11],[1,2,0,3,4,5,6,7,8,9,10,11],[0,1,2,3,6,7,11,9,8,5,10,4]),
 'F':([4,1,2,3,5,0],[1,0,0,0,1,0],[0,1,2,3,4,6,7,5,8,9,10,11],[0,1,2,4,5,3,6,7,8,9,10,11],[0,9,10,3,4,5,2,7,1,8,6,11]),
 'r':([0,5,2,1,4,3],[0,1,0,0,0,1],[0,1,2,3,10,5,6,7,8,9,11,4],[0,1,2,3,4,5,7,8,6,9,10,11],[5,3,2,11,4,10,6,7,8,9,0,1]),
 'l':([0,1,3,4,2,5],[0,0,1,1,0,0],[0,1,2,8,4,5,6,7,9,3,10,11],[0,1,2,3,4,5,6,7,8,10,11,9],[8,1,7,2,0,5,6,3,4,9,10,11]),
 'D':([0,1,2,5,3,4],[0,0,0,0,0,0],[0,1,2,4,5,3,6,7,8,9,10,11],[0,1,2,3,9,10,5,7,4,8,6,11],[1,2,0,3,4,5,6,7,8,9,10,11]),
 'B':([0,3,1,2,4,5],[0,1,1,0,0,0],[0,1,10,3,4,5,6,7,8,2,9,11],[0,6,7,3,4,5,11,9,8,2,10,1],[0,1,2,4,5,3,6,7,8,9,10,11]),
 'R':([5,0,2,3,4,1],[1,1,0,0,0,0],[6,1,2,3,4,5,11,7,8,9,10,0],[5,3,2,8,4,7,6,0,1,9,10,11],[0,1,2,3,4,5,6,7,8,10,11,9]),
 'L':([2,1,4,3,0,5],[1,0,1,0,0,0],[0,8,2,3,4,5,6,1,7,9,10,11],[11,1,10,2,0,5,6,7,8,9,3,4],[0,1,2,3,4,5,7,8,6,9,10,11]),
}
_FTO_DISP2INT = {'U':'U','F':'F','BR':'r','BL':'l','D':'D','B':'B','R':'R','L':'L'}

def _fto_mult(a, b):
    acp,aco,aep,auf,arl = a; bcp,bco,bep,buf,brl = b
    return ([acp[bcp[i]] for i in range(6)],
            [aco[bcp[i]] ^ bco[i] for i in range(6)],
            [aep[bep[i]] for i in range(12)],
            [auf[buf[i]] for i in range(12)],
            [arl[brl[i]] for i in range(12)])

# 2D net: face name -> (facelet base, apex, vertex@facelet8, vertex@facelet4)
_FTO_O = 3.0
_FTO_FACES = {
    'U':(_FU, (0,0),       (-1,1),(1,1)),       'R':(_FR, (0,0),       (1,1),(1,-1)),
    'F':(_FF, (0,0),       (1,-1),(-1,-1)),      'L':(_FL, (0,0),       (-1,-1),(-1,1)),
    'B':(_FB, (_FTO_O,0),  (_FTO_O-1,1),(_FTO_O+1,1)),
    'l':(_Fl, (_FTO_O,0),  (_FTO_O+1,1),(_FTO_O+1,-1)),
    'D':(_FD, (_FTO_O,0),  (_FTO_O+1,-1),(_FTO_O-1,-1)),
    'r':(_Fr, (_FTO_O,0),  (_FTO_O-1,-1),(_FTO_O-1,1)),
}

def _fto_cells(A, V8, V4):
    ux,uy = (V8[0]-A[0])/3.0, (V8[1]-A[1])/3.0
    vx,vy = (V4[0]-A[0])/3.0, (V4[1]-A[1])/3.0
    def P(i,j): return (A[0]+i*ux+j*vx, A[1]+i*uy+j*vy)
    up   = lambda i,j: [P(i,j),P(i+1,j),P(i,j+1)]
    dn   = lambda i,j: [P(i+1,j),P(i,j+1),P(i+1,j+1)]
    return [up(0,0),up(0,1),dn(0,0),up(1,0),up(0,2),dn(0,1),up(1,1),dn(1,0),up(2,0)]


class FTOState:
    def __init__(self):
        self.state = ([0,1,2,3,4,5],[0,0,0,0,0,0],list(range(12)),
                      list(range(12)),list(range(12)))

    def apply(self, move_str):
        for tok in move_str.split():
            if not tok:
                continue
            prime = tok.endswith("'"); base = tok[:-1] if prime else tok
            if base not in _FTO_DISP2INT:
                continue
            m = _FTO_MOVES[_FTO_DISP2INT[base]]
            self.state = _fto_mult(self.state, m)
            if prime:
                self.state = _fto_mult(self.state, m)   # prime = base² (order 3)

    def _facecube(self):
        cp,co,ep,uf,rl = self.state
        f = [0]*72
        for i in range(6):
            for j in range(4):
                f[_FTO_CORN[i][(j + co[i]*2) % 4]] = _FTO_CORN[cp[i]][j] // 9
        for i in range(12):
            for j in range(2):
                f[_FTO_EDGE[i][j]] = _FTO_EDGE[ep[i]][j] // 9
        for i in range(12):
            f[_FTO_CTUF[i]] = _FTO_CTUF[uf[i]] // 9
        for i in range(12):
            f[_FTO_CTRL[i]] = _FTO_CTRL[rl[i]] // 9
        return f

    def draw_net(self, canvas, x0, y0, cell):
        nc, nr = 10, 4
        W, H = nc * cell, nr * cell
        f = self._facecube()
        polys = []; xs = []; ys = []
        for name, (base, A, V8, V4) in _FTO_FACES.items():
            cells = _fto_cells(A, V8, V4)
            for k in range(9):
                polys.append((cells[k], _FTO_HEX[f[base + k]]))
                for px, py in cells[k]:
                    xs.append(px); ys.append(py)
        bx0, by0, bx1, by1 = min(xs), min(ys), max(xs), max(ys)
        bw, bh = (bx1 - bx0) or 1, (by1 - by0) or 1
        sc = min(W / bw, H / bh) * 0.96
        ox = x0 + (W - bw*sc) / 2 - bx0*sc
        oy = y0 + (H - bh*sc) / 2
        lw = max(1, cell // 16)
        for pts, col in polys:
            flat = []
            for (px, py) in pts:
                flat += [ox + px*sc, oy + (by1 - py)*sc]   # flip y for canvas
            canvas.create_polygon(*flat, fill=col, outline='#111111', width=lw)


# ── Rubik's Clock — csTimer move model + 2D dials net ────────────
# State = 14 components (csTimer clock.js moveArr): comp[0..8] = front clocks
# (UL,U,UR,L,C,R,DL,D,DR), comp[9..13] = back U,L,C,R,D.  The 4 back corners
# share an axle with the front corners and mirror them (back = -front).  Each
# scramble move adds moveArr[move]*amount (mod 12).  Verified vs csTimer data.

_CLK_MOVEARR = [
    [0,1,1,0,1,1,0,0,0,0,0,0,0,0],[0,0,0,0,1,1,0,1,1,0,0,0,0,0],
    [0,0,0,1,1,0,1,1,0,0,0,0,0,0],[1,1,0,1,1,0,0,0,0,0,0,0,0,0],
    [1,1,1,1,1,1,0,0,0,0,0,0,0,0],[0,1,1,0,1,1,0,1,1,0,0,0,0,0],
    [0,0,0,1,1,1,1,1,1,0,0,0,0,0],[1,1,0,1,1,0,1,1,0,0,0,0,0,0],
    [1,1,1,1,1,1,1,1,1,0,0,0,0,0],
    [11,0,0,0,0,0,0,0,0,1,0,1,1,0],[0,0,0,0,0,0,11,0,0,0,0,1,1,1],
    [0,0,0,0,0,0,0,0,11,0,1,1,0,1],[0,0,11,0,0,0,0,0,0,1,1,1,0,0],
    [11,0,11,0,0,0,0,0,0,1,1,1,1,0],[11,0,0,0,0,0,11,0,0,1,0,1,1,1],
    [0,0,0,0,0,0,11,0,11,0,1,1,1,1],[0,0,11,0,0,0,0,0,11,1,1,1,0,1],
    [11,0,11,0,0,0,11,0,11,1,1,1,1,1],
]
_CLK_FRONT = {"UR":0,"DR":1,"DL":2,"UL":3,"U":4,"R":5,"D":6,"L":7,"ALL":8}


class ClockState:
    def __init__(self):
        self.comp = [0]*14
        self.pins = set()

    def apply(self, scramble):
        back = False
        for tok in (scramble or "").split():
            if tok == "y2":
                back = True; continue
            if tok in ("UR","DR","DL","UL"):
                self.pins.add(tok); continue            # trailing pin token
            if not tok or tok[-1] not in "+-":
                continue
            body, sign = tok[:-1], tok[-1]
            i = 0
            while i < len(body) and not body[i].isdigit():
                i += 1
            name, num = body[:i], body[i:]
            if name not in _CLK_FRONT or not num.isdigit():
                continue
            n = int(num); amt = n if sign == "+" else (12 - n) % 12
            row = _CLK_MOVEARR[_CLK_FRONT[name] + (9 if back else 0)]
            for k in range(14):
                self.comp[k] = (self.comp[k] + row[k]*amt) % 12

    def _dials(self):
        c = self.comp; m = lambda v: (12 - v) % 12
        front = c[0:9]
        back = [m(c[2]), c[9], m(c[0]), c[10], c[11], c[12], m(c[8]), c[13], m(c[6])]
        return front, back

    def draw_net(self, canvas, x0, y0, cell):
        nc, nr = 12, 5
        W, H = nc * cell, nr * cell
        front, back = self._dials()
        step, R, gap = 2.3, 1.0, 1.4
        clocks = []
        for i, v in enumerate(front):
            clocks.append(((i % 3)*step, (i // 3)*step, v))
        boff = 3*step + gap
        for i, v in enumerate(back):
            clocks.append((boff + (i % 3)*step, (i // 3)*step, v))
        pin_pos = {"UL":(0,0),"UR":(1,0),"DL":(0,1),"DR":(1,1)}
        pins = [((pc+0.5)*step, (pr+0.5)*step, name in self.pins)
                for name,(pc,pr) in pin_pos.items()]
        xs = [c[0] for c in clocks]; ys = [c[1] for c in clocks]
        bx0, bx1 = min(xs)-R, max(xs)+R; by0, by1 = min(ys)-R, max(ys)+R
        bw, bh = bx1-bx0, by1-by0
        s = min(W/bw, H/bh) * 0.96
        ox = x0 + (W - bw*s)/2 - bx0*s
        oy = y0 + (H - bh*s)/2 - by0*s
        rr = R*s
        for cx0, cy0, hour in clocks:
            cx, cy = ox+cx0*s, oy+cy0*s
            canvas.create_oval(cx-rr, cy-rr, cx+rr, cy+rr,
                               fill='#e8e8e0', outline='#222222', width=max(1, int(rr*0.06)))
            for h in range(12):
                a = h*math.pi/6
                canvas.create_line(cx+(rr-rr*0.13)*math.sin(a), cy-(rr-rr*0.13)*math.cos(a),
                                   cx+rr*math.sin(a), cy-rr*math.cos(a), fill='#777777', width=1)
            canvas.create_oval(cx-rr*0.09, cy-rr+rr*0.05, cx+rr*0.09, cy-rr+rr*0.23,
                               fill='#cc0000', outline='')
            a = hour*math.pi/6
            hx, hy = cx+rr*0.74*math.sin(a), cy-rr*0.74*math.cos(a)
            canvas.create_line(cx, cy, hx, hy, fill='#111111', width=max(2, int(rr*0.13)))
            canvas.create_oval(hx-rr*0.14, hy-rr*0.14, hx+rr*0.14, hy+rr*0.14,
                               fill='#cc0000', outline='#660000')
            canvas.create_oval(cx-rr*0.1, cy-rr*0.1, cx+rr*0.1, cy+rr*0.1, fill='#111111', outline='')
        for px0, py0, up in pins:
            px, py = ox+px0*s, oy+py0*s; pr = rr*0.24
            canvas.create_oval(px-pr, py-pr, px+pr, py+pr,
                               fill=('#33dd55' if up else '#444444'),
                               outline='#000000', width=max(1, int(rr*0.05)))


def _is_333_scramble(scramble):
    """True when every move token is a standard 3×3 face move."""
    if not scramble or scramble.startswith("("):
        return False
    valid = {'U', 'D', 'R', 'L', 'F', 'B'}
    tokens = scramble.split()
    if not tokens:
        return False
    for tok in tokens:
        base = tok[:-1] if tok.endswith("'") or tok.endswith("2") else tok
        if base not in valid:
            return False
    return True


def _make_viz_state(puzzle, scramble):
    """Return a solved cube state with scramble applied, or None if no viz."""
    try:
        if puzzle in ("3x3", "3x3 OH", "3x3 BLD"):
            if not _is_333_scramble(scramble): return None
            cs = CubeState(); cs.apply(scramble); return cs
        if puzzle == "2x2":
            valid = {'U','D','R','L','F','B'}
            for tok in (scramble or "").split():
                base = tok[:-1] if tok.endswith("'") or tok.endswith("2") else tok
                if base not in valid: return None
            cs = Cube2State(); cs.apply(scramble); return cs
        if puzzle == "Skewb":
            valid = {'U','R','L','B'}
            for tok in (scramble or "").split():
                base = tok[:-1] if tok.endswith("'") or tok.endswith("2") else tok
                if base not in valid: return None
            cs = SkewbState(); cs.apply(scramble); return cs
        if puzzle == "4x4":
            valid = {'U','D','R','L','F','B'}
            for tok in (scramble or "").split():
                base = tok[:-1] if tok.endswith("'") or tok.endswith("2") else tok
                if base.endswith('w'): base = base[:-1]
                if base not in valid: return None
            cs = Cube4State(); cs.apply(scramble); return cs
        if puzzle == "FTO":
            valid = {'U','L','R','F','B','D','BL','BR'}
            for tok in (scramble or "").split():
                base = tok[:-1] if tok.endswith("'") else tok
                if base not in valid: return None
            cs = FTOState(); cs.apply(scramble); return cs
        if puzzle == "Clock":
            if "y2" not in (scramble or "").split(): return None
            cs = ClockState(); cs.apply(scramble); return cs
        if puzzle == "Pyraminx":
            valid = {'U','L','R','B'}
            for tok in (scramble or "").split():
                base = tok[:-1] if tok.endswith("'") else tok
                if base.upper() not in valid: return None
            cs = PyraminxState(); cs.apply(scramble); return cs
    except Exception:
        pass
    return None


def _viz_net_dims(state):
    """Returns (cols, rows) cell count of the net for this state type."""
    if isinstance(state, SkewbState): return 8, 7
    if isinstance(state, Cube2State): return 8, 6
    if isinstance(state, Cube4State): return 16, 12
    if isinstance(state, PyraminxState): return 8, 7
    if isinstance(state, FTOState): return 10, 4
    if isinstance(state, ClockState): return 12, 5
    return 12, 9
