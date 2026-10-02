"""Scramble generators for every supported puzzle type."""
import random

_OPP = {"U":"D","D":"U","R":"L","L":"R","F":"B","B":"F"}

def _gen(faces, mods, n):
    moves, last, prev = [], None, None
    while len(moves) < n:
        f = random.choice(faces)
        if f == last: continue
        if prev and f == prev and _OPP.get(f,"?") == last: continue
        moves.append(f + random.choice(mods)); prev, last = last, f
    return "  ".join(moves)

def gen_333():  return _gen(["U","D","R","L","F","B"], ["","'","2"], 20)
def gen_222():  return _gen(["U","R","F"], ["","'","2"], 9)
def gen_444():  return _gen(["U","D","R","L","F","B","Uw","Dw","Rw","Lw","Fw","Bw"], ["","'","2"], 40)
def gen_555():  return _gen(["U","D","R","L","F","B","Uw","Dw","Rw","Lw","Fw","Bw",
                              "3Uw","3Dw","3Rw","3Lw","3Fw","3Bw"], ["","'","2"], 60)
_BIG = ["U","D","R","L","F","B","Uw","Dw","Rw","Lw","Fw","Bw"]
def gen_666():  return _gen(_BIG + ["3Uw","3Dw","3Rw","3Lw","3Fw","3Bw"], ["","'","2"], 80)
def gen_777():  return _gen(_BIG + ["3Uw","3Dw","3Rw","3Lw","3Fw","3Bw"], ["","'","2"], 100)
def gen_fmc():
    # WCA FMC scrambles start and end with R' U' F
    return "R'  U'  F  " + gen_333() + "  R'  U'  F"

def gen_sq1(twists=12):
    """Square-1, random-move: (top,bottom) turns separated by slices "/".

    Each layer is 12 slots of 30 degrees; a corner fills 2 slots, an edge 1.
    A slice is only legal when no piece straddles the cut on either layer,
    i.e. there is a piece boundary at slot 0 and slot 6.
    """
    top = ["e0","c0","c0","e1","c1","c1","e2","c2","c2","e3","c3","c3"]
    bot = ["c4","c4","e4","c5","c5","e5","c6","c6","e6","c7","c7","e7"]
    rot = lambda layer, k: layer[-k % 12:] + layer[:-k % 12]
    ok = lambda l: l[11] != l[0] and l[5] != l[6]
    out = []
    for _ in range(twists):
        while True:
            x, y = random.randint(-5, 6), random.randint(-5, 6)
            if (x, y) == (0, 0) and out:
                continue
            t, b = rot(top, x), rot(bot, y)
            if ok(t) and ok(b):
                break
        out.append(f"({x},{y})")
        top, bot = b[:6] + t[6:], t[:6] + b[6:]           # the slice swaps the halves
    return " / ".join(out) + " /"

def gen_pyra():
    body = _gen(["U","L","R","B"], ["","'"], 9).split("  ")
    tips = [t+random.choice(["","'"]) for t in random.sample(["u","l","r","b"], random.randint(2,4))]
    return "  ".join(body + tips)
def gen_skewb(): return _gen(["U","R","L","B"], ["","'"], 9)
def gen_fto():
    # Face-Turning Octahedron — Gottlieb notation (U L R F B D BL BR).
    faces = ["U","L","R","F","B","D","BL","BR"]
    moves, last = [], None
    while len(moves) < 30:
        f = random.choice(faces)
        if f == last:
            continue
        moves.append(f + random.choice(["", "'"])); last = f
    return "  ".join(moves)
def gen_clock():
    # Rubik's Clock — WCA notation: 9 front + 5 back dial turns, then pins.
    def amt():
        a = random.randint(0, 11)
        if a == 0: return "0+"
        return f"{a}+" if a <= 6 else f"{12-a}-"
    front = ["UR","DR","DL","UL","U","R","D","L","ALL"]
    back  = ["U","R","D","L","ALL"]
    parts = [n+amt() for n in front] + ["y2"] + [n+amt() for n in back]
    pins  = [p for p in ("UR","DR","DL","UL") if random.random() < 0.5]
    return "  ".join(parts + pins)
def gen_mega():
    rows = []
    for _ in range(7):
        row = []
        for _ in range(5):
            row.append("R"+random.choice(["++","--"]))
            row.append("D"+random.choice(["+","-"]))
        rows.append("  ".join(row))
    rows.append("U"+random.choice(["","'"]))
    return "\n".join(rows)

# same order as the WCA event list in csTimer
PUZZLES = {"3x3":gen_333, "2x2":gen_222, "4x4":gen_444, "5x5":gen_555,
           "6x6":gen_666, "7x7":gen_777, "3x3 BLD":gen_333, "3x3 FMC":gen_fmc,
           "3x3 OH":gen_333, "Clock":gen_clock, "Megaminx":gen_mega,
           "Pyraminx":gen_pyra, "Skewb":gen_skewb, "Square-1":gen_sq1,
           "4x4 BLD":gen_444, "5x5 BLD":gen_555, "FTO":gen_fto}
