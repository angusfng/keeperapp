#!/usr/bin/env python3
"""Write a QR code as an SVG, with no third-party packages.

Byte mode, error correction level M, versions 1 to 6 (up to 106 bytes).

Usage:
  python3 scripts/make_qr.py "https://apps.apple.com/app/id6793817811" public/assets/qr-app-store.svg
"""

import sys

# (total codewords, ec codewords per block, [data codewords per block...]) for level M
VERSIONS = {
    1: (26, 10, [16]),
    2: (44, 16, [28]),
    3: (70, 26, [44]),
    4: (100, 18, [32, 32]),
    5: (134, 24, [43, 43]),
    6: (172, 16, [27, 27, 27, 27]),
}
ALIGN = {1: [], 2: [6, 18], 3: [6, 22], 4: [6, 26], 5: [6, 30], 6: [6, 34]}

# GF(256) tables
EXP, LOG = [0] * 512, [0] * 256
x = 1
for i in range(255):
    EXP[i] = x
    LOG[x] = i
    x <<= 1
    if x & 0x100:
        x ^= 0x11D
for i in range(255, 512):
    EXP[i] = EXP[i - 255]


def gmul(a, b):
    return 0 if a == 0 or b == 0 else EXP[LOG[a] + LOG[b]]


def rs_ec(data, n):
    gen = [1]
    for i in range(n):
        gen = [a ^ b for a, b in zip(gen + [0], [0] + [gmul(g, EXP[i]) for g in gen])]
    rem = list(data) + [0] * n
    for i in range(len(data)):
        c = rem[i]
        if c:
            for j, g in enumerate(gen):
                rem[i + j] ^= gmul(g, c)
    return rem[len(data):]


def encode(text):
    data = text.encode("utf-8")
    for ver, (total, ecn, blocks) in VERSIONS.items():
        cap = sum(blocks)
        if len(data) + 2 <= cap:
            break
    else:
        sys.exit("text too long")
    bits = "0100" + format(len(data), "08b") + "".join(format(b, "08b") for b in data)
    bits += "0000"[: max(0, cap * 8 - len(bits))]
    bits += "0" * (-len(bits) % 8)
    cw = [int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)]
    pad = [0xEC, 0x11]
    while len(cw) < cap:
        cw.append(pad[(len(cw) - len(bits) // 8) % 2])
    # Split into blocks, add EC, interleave
    dblocks, pos = [], 0
    for n in blocks:
        dblocks.append(cw[pos:pos + n])
        pos += n
    eblocks = [rs_ec(b, ecn) for b in dblocks]
    out = []
    for i in range(max(blocks)):
        out += [b[i] for b in dblocks if i < len(b)]
    for i in range(ecn):
        out += [b[i] for b in eblocks]
    return ver, out


def build(ver, codewords):
    size = 17 + 4 * ver
    m = [[None] * size for _ in range(size)]

    def finder(r, c):
        for dr in range(-1, 8):
            for dc in range(-1, 8):
                rr, cc = r + dr, c + dc
                if 0 <= rr < size and 0 <= cc < size:
                    on = (0 <= dr <= 6 and dc in (0, 6)) or (0 <= dc <= 6 and dr in (0, 6)) or (2 <= dr <= 4 and 2 <= dc <= 4)
                    m[rr][cc] = on

    finder(0, 0)
    finder(0, size - 7)
    finder(size - 7, 0)
    for i in range(8, size - 8):
        m[6][i] = m[i][6] = i % 2 == 0
    for r in ALIGN[ver]:
        for c in ALIGN[ver]:
            if m[r][c] is not None:
                continue
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    m[r + dr][c + dc] = max(abs(dr), abs(dc)) != 1
    m[size - 8][8] = True  # dark module
    reserved = [[v is not None for v in row] for row in m]
    for i in range(9):
        if i < size:
            reserved[8][i] = reserved[i][8] = True
    for i in range(8):
        reserved[8][size - 1 - i] = reserved[size - 1 - i][8] = True

    bits = "".join(format(c, "08b") for c in codewords) + "0" * 7
    idx, up = 0, True
    col = size - 1
    while col > 0:
        if col == 6:
            col -= 1
        rows = range(size - 1, -1, -1) if up else range(size)
        for r in rows:
            for c in (col, col - 1):
                if not reserved[r][c]:
                    m[r][c] = bits[idx] == "1" if idx < len(bits) else False
                    idx += 1
        up = not up
        col -= 2

    masks = [
        lambda r, c: (r + c) % 2 == 0, lambda r, c: r % 2 == 0, lambda r, c: c % 3 == 0,
        lambda r, c: (r + c) % 3 == 0, lambda r, c: (r // 2 + c // 3) % 2 == 0,
        lambda r, c: (r * c) % 2 + (r * c) % 3 == 0, lambda r, c: ((r * c) % 2 + (r * c) % 3) % 2 == 0,
        lambda r, c: ((r + c) % 2 + (r * c) % 3) % 2 == 0,
    ]

    def fmt_bits(mask):
        d = (0b00 << 3) | mask  # level M = 00
        v = d << 10
        for i in range(14, 9, -1):
            if v & (1 << i):
                v ^= 0x537 << (i - 10)
        return ((d << 10) | v) ^ 0x5412

    def apply(mask):
        g = [row[:] for row in m]
        for r in range(size):
            for c in range(size):
                if not reserved[r][c] and masks[mask](r, c):
                    g[r][c] = not g[r][c]
        f = fmt_bits(mask)
        for i in range(15):
            b = (f >> i) & 1 == 1
            # around top-left finder
            if i < 6:
                g[i][8] = b
            elif i < 8:
                g[i + 1][8] = b
            else:
                g[8][14 - i if i > 8 else 7] = b
            # split copy
            if i < 8:
                g[8][size - 1 - i] = b
            else:
                g[size - 15 + i][8] = b
        g[size - 8][8] = True
        return g

    def penalty(g):
        p = 0
        for line in g + [list(col) for col in zip(*g)]:
            run = 1
            for i in range(1, size):
                if line[i] == line[i - 1]:
                    run += 1
                else:
                    if run >= 5:
                        p += run - 2
                    run = 1
            if run >= 5:
                p += run - 2
            s = "".join("1" if v else "0" for v in line)
            p += 40 * (s.count("10111010000") + s.count("00001011101"))
        for r in range(size - 1):
            for c in range(size - 1):
                if g[r][c] == g[r + 1][c] == g[r][c + 1] == g[r + 1][c + 1]:
                    p += 3
        dark = sum(v for row in g for v in row)
        p += abs(dark * 20 // (size * size) - 10) * 10
        return p

    return min((apply(k) for k in range(8)), key=penalty)


def svg(grid, quiet=2):
    size = len(grid)
    n = size + 2 * quiet
    path = "".join(
        f"M{c + quiet} {r + quiet}h1v1h-1z" for r in range(size) for c in range(size) if grid[r][c]
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" shape-rendering="crispEdges">'
        f'<rect width="{n}" height="{n}" fill="#fff"/><path fill="#1C1C1E" d="{path}"/></svg>\n'
    )


if __name__ == "__main__":
    text, out = sys.argv[1], sys.argv[2]
    ver, cw = encode(text)
    open(out, "w").write(svg(build(ver, cw)))
    print(f"wrote {out} (version {ver})")
