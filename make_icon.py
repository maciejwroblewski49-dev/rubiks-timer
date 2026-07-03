"""Generates icon.ico — isometric Rubik's cube on a dark rounded background."""
from PIL import Image, ImageDraw
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")

# colour palette
PALETTE = {
    "Y": (255, 213,   0),   # yellow
    "R": (200,  16,  46),   # red
    "B": (  0,  61, 165),   # blue
    "W": (245, 245, 245),   # white
    "O": (255,  88,   0),   # orange
    "G": (  0, 155,  72),   # green
}

# face patterns  — row 0 = top of face
TOP   = [["Y","Y","Y"],["Y","W","Y"],["Y","Y","Y"]]
RIGHT = [["R","R","R"],["R","R","O"],["R","R","R"]]
LEFT  = [["B","B","B"],["G","B","B"],["B","B","B"]]


def _add(pt, *steps):
    x, y = pt
    for sx, sy, n in steps:
        x += sx * n; y += sy * n
    return (x, y)


def _draw(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d   = ImageDraw.Draw(img)

    # rounded dark background
    r = max(size // 7, 3)
    d.rounded_rectangle([0, 0, size - 1, size - 1],
                        radius=r, fill=(28, 28, 42, 255))

    f   = size * 0.285          # face height in px
    cx  = size / 2.0
    # vertical centre: shift cube up slightly
    ty  = (size - f * 2.0) / 2.0 - size * 0.04

    # ── seven key isometric vertices ──────────────────────────────
    top    = (cx,              ty)
    right  = (cx + f * 0.866,  ty + f * 0.5)
    left_  = (cx - f * 0.866,  ty + f * 0.5)
    center = (cx,              ty + f)
    bottom = (cx,              ty + f * 2.0)

    # grid step vectors (1/3 of each face axis)
    tr = ((right[0]  - top[0])    / 3, (right[1]  - top[1])    / 3)
    tb = ((left_[0]  - top[0])    / 3, (left_[1]  - top[1])    / 3)
    rr = ((right[0]  - center[0]) / 3, (right[1]  - center[1]) / 3)
    ll = ((left_[0]  - center[0]) / 3, (left_[1]  - center[1]) / 3)
    dn = ((bottom[0] - center[0]) / 3, (bottom[1] - center[1]) / 3)

    outline  = (12, 12, 20)
    face_bdr = max(1, size // 96)

    def draw_face(pattern, origin, s1, s2):
        for row in range(3):
            for col in range(3):
                pts = [
                    _add(origin, (s1[0], s1[1], col),     (s2[0], s2[1], row)),
                    _add(origin, (s1[0], s1[1], col + 1), (s2[0], s2[1], row)),
                    _add(origin, (s1[0], s1[1], col + 1), (s2[0], s2[1], row + 1)),
                    _add(origin, (s1[0], s1[1], col),     (s2[0], s2[1], row + 1)),
                ]
                d.polygon(pts, fill=PALETTE[pattern[row][col]])
                d.polygon(pts, outline=outline)

    # draw order: top → left → right (right is "in front" at center edge)
    draw_face(TOP,   top,    tr, tb)
    draw_face(LEFT,  center, ll, dn)
    draw_face(RIGHT, center, rr, dn)

    # thick outer border for each main face
    bw = max(1, size // 60)
    for poly in [
        [top, right, center, left_],
        [center, right, (right[0], right[1] + f), bottom],
        [center, left_, (left_[0], left_[1] + f), bottom],
    ]:
        d.line(poly + [poly[0]], fill=outline, width=bw)

    return img


def main():
    sizes  = [256, 128, 64, 48, 32, 16]
    frames = [_draw(s) for s in sizes]
    frames[0].save(
        OUT, format="ICO",
        append_images=frames[1:],
        sizes=[(s, s) for s in sizes],
    )
    print(f"Created: {OUT}")


if __name__ == "__main__":
    main()
