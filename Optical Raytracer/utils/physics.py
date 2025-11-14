"""Physics module

Contains the necessary functions for related processes in ray propagation.

Functions:
refract -- refracts a ray through a surface
reflect -- reflects a ray off a surface
"""

import numpy as np


def refract(direc, normal, n_1, n_2):
    """Determines the refracted vector direction using Snell's Law

    Args:
    direc (list[float, float, float]) -- input ray direction
    normal (list[float, float, float]) -- refractive surface normal
    n_1 (float) -- refractive index outside the surface
    n_2 (float) -- refractive index inside the surface

    Returns:
        np.array[float, float, float]: normalised refracted direction
    """

    direc_norm = direc/np.linalg.norm(direc)
    normal_norm = normal/np.linalg.norm(normal)

    if np.dot(direc_norm, normal_norm) > 0:
        normal_norm = -normal_norm

    theta1 = np.arccos(-np.dot(direc_norm, normal_norm))

    if n_2 <= n_1:
        if theta1 > np.arcsin(n_2/n_1):
            return None

    theta2 = np.arcsin(n_1*np.sin(theta1)/n_2)

    refracted_direc = (n_1/n_2) * direc_norm + ((n_1/n_2) * np.cos(theta1)
                                                - np.cos(theta2)) * normal_norm

    return refracted_direc/np.linalg.norm(refracted_direc)


def reflect(direc, normal):
    """Determines the reflected vector direction using Snell's Law

    Args:
    direc (list[float, float, float]) -- input ray direction
    normal (list[float, float, float]) -- refractive surface normal

    Returns:
        np.array[float, float, float]: normalised reflected direction
    """

    direc_norm = direc/np.linalg.norm(direc)
    normal_norm = normal/np.linalg.norm(normal)

    if np.dot(direc_norm, normal_norm) > 0:
        normal_norm = -normal_norm

    reflected_direc = direc_norm - 2 * np.dot(direc_norm, normal_norm) * normal_norm

    return reflected_direc/np.linalg.norm(reflected_direc)
