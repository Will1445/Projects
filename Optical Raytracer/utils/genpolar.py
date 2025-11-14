"""Genpolar module

Contains the function for generating a ring of positions

Functions:
rtrings -- generates a list of positions in ring patterns
"""

import numpy as np


def rtrings(rmax, nrings, multi):
    """Generates a set of rings of positions around (0, 0)

    Args:
        rmax (float): maximum radius of the outer ring
        nrings (_type_): number of rings generated
        multi (_type_): determines the density of points in each ring

    Yields:
        tuple(float, float): (x, y) positions of points in the rings
    """
    radii = [float(x) for x in np.linspace(0, rmax, nrings+1)]

    ring = 0
    for radius in radii:
        if radius == 0:
            yield (0.0, 0.0)

        else:
            ring += 1
            n_points = ring * multi
            for i in range(n_points):
                theta = 2*np.pi/n_points * i
                yield (radius*np.cos(theta), radius*np.sin(theta))
