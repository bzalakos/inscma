"""Extract the vertex declaration here, it's kind of in the way. Edit that first array."""

room = [[6, 2, 2, 3],   # x +->
        [4, 4, 5, 1],   # z
        [4, 4, 20, 5],   # +
        [12, 8, 8, 9]]  # v

# Ignore the invalid variable naming. pylint: disable-msg=C0103
# Y is indeed the up/down axis. x y z r g b u v
l = 0.5   # To ease the sizing, use this constant.
vers = [[[-l, -l, -l], [+l, -l, -l], [+l, -l, +l], [-l, -l, +l],   # sol, v plafond
         [-l, +l, -l], [+l, +l, -l], [+l, +l, +l], [-l, +l, +l]]] + \
       [[[+l, +l, -l], [+l, +l, +l], [+l, -l, +l], [+l, -l, -l]],  # +x
        [[-l, +l, -l], [+l, +l, -l], [+l, -l, -l], [-l, -l, -l]],  # -z
        [[-l, +l, -l], [-l, +l, +l], [-l, -l, +l], [-l, -l, -l]],  # -x
        [[-l, +l, +l], [+l, +l, +l], [+l, -l, +l], [-l, -l, +l]],  # +z
       ] * 2

# Not so bad when there's a bunch of repetition
uval = [[[0.7500, 0.000], [0.8750, 0.000], [0.8750, 0.250], [0.750, 0.250],
         [0.8750, 0.000], [0.9375, 0.000], [0.9375, 0.125], [0.875, 0.125]]] \
     + [[[0.5000, 0.000], [0.7500, 0.000], [0.7500, 0.500], [0.500, 0.500]]] * 4 \
     + [[[0.0000, 0.000], [0.5000, 0.000], [0.5000, 1.000], [0.000, 1.000]]] * 4

# Sure is easy when they're all ones.
blankol = [[[1] * 3] * 8] + [[[1] * 3] * 4] * 8

walls = [[sum(x, []) for x in zip(vers[y], blankol[y], uval[y])] for y in range(len(vers))]

def tadd(*args):
    """Element-wise addition of iterables."""
    return [sum(x) for x in zip(*args)]

def ttim(scal, ite):
    """Scalar multiplication of iterables."""
    return [x * scal for x in ite]

def wall(x, y, side):
    """Returns a list of lists of floats that forms a space."""
    res = [w for w in walls[0]]
    # Skip zero here, just did it.
    res += [w for i in range(8) for w in walls[i+1] if side & 2**i]
    # tile coordinates offset, tile size multiplier
    return [tadd([x, 0, y], r[:3]) + r[3:] for r in res]

vs = [t for y, i in enumerate(room) for x, w in enumerate(i) for t in wall(x, y, w)]
