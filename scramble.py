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

PUZZLES = {"3x3":gen_333,"2x2":gen_222,"4x4":gen_444,"5x5":gen_555,
           "Pyraminx":gen_pyra,"Skewb":gen_skewb,"Megaminx":gen_mega,
           "FTO":gen_fto,"Clock":gen_clock,"3x3 OH":gen_333,"3x3 BLD":gen_333}
