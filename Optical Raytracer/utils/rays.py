"""Ray initialisation module

Classes:
Ray -- initialises a single optical ray with position and direction
RayBundle -- initialises a group (bundle) of optical rays
"""

import numpy as np
import matplotlib.pyplot as plt
from utils.genpolar import rtrings


class Ray:
    """Defines an optical ray.

    Methods:
    pos -- returns the ray's position
    direc -- returns the ray's direction
    append -- sets a new ray position and direction
    vertices -- returns the ray's stored positions

    Attributes:
    pos (list) -- the position of the ray (default [0, 0, 0])
    direc (list) -- the direction of propagation of the ray (default [0, 0, 1])
    """
    def __init__(self, pos=[0, 0, 0], direc=[0, 0, 1]):
        if not isinstance(pos, (list, tuple, np.ndarray)):
            raise TypeError("pos must be a list, tuple, or numpy array")
        if len(pos) != 3:
            raise ValueError("pos must be of length 3 (x, y, z)")

        if not isinstance(direc, (list, tuple, np.ndarray)):
            raise TypeError("direc must be a list, tuple, or numpy array")
        if len(direc) != 3:
            raise ValueError("direc must be of length 3 (x, y, z)")

        direc = np.array(direc, dtype=float)
        self.__pos = np.array(pos, dtype=float)
        self.__direc = direc/np.linalg.norm(direc)
        self.__pos_list = [self.__pos]

    def pos(self):
        """Gets ray position.

        Returns:
            np.array[float, float, float]: x,y,z position of ray
        """
        return self.__pos

    def direc(self):
        """Gets ray direction.

        Returns:
            np.array[float, float, float]: x,y,z direction of ray
        """
        return self.__direc

    def append(self, pos=[0, 0, 0], direc=[0, 0, 1]):
        """Sets new ray position and direction, stores updated position.

        Keyword arguments:
        pos -- new ray position (default [0, 0, 0])
        direc -- new ray direction (default [0, 0, 1])
        """
        if not isinstance(pos, (list, tuple, np.ndarray)):
            raise TypeError("pos must be a list, tuple, or numpy array")
        if len(pos) != 3:
            raise ValueError("pos must be of length 3 (x, y, z)")

        if not isinstance(direc, (list, tuple, np.ndarray)):
            raise TypeError("direc must be a list, tuple, or numpy array")
        if len(direc) != 3:
            raise ValueError("direc must be of length 3 (x, y, z)")

        direc = np.array(direc, dtype=float)
        self.__pos = np.array(pos, dtype=float)
        self.__direc = direc/np.linalg.norm(direc)
        self.__pos_list.append(self.__pos)

    def vertices(self):
        """Return the stored ray positions.

        Returns:
            list[np.array[float, float, float]]: x,y,z position list of ray
        """
        return self.__pos_list


class RayBundle:
    """Defines a group (bundle) of rays.

    Methods:
    get_rays -- returns the list of ray objects in the bundle
    propagate_bundle -- passes the ray bundle through a list of elements
    track_plot -- returns a plot of the path of each ray
    rms -- returns the rms size of the bundle
    spot_plot -- returns a plot of the rays at the output plane
    spot_plot_coords -- returns the (x,y) coordinates of each ray

    Attributes:
    rmax (float) -- maximum radius of the bundle (default 5.0)
    nrings (int) -- number of rings in the bundle (default 5)
    multi (int) -- number of rays per ring (default 6)
    """
    def __init__(self, rmax=5., nrings=5, multi=6):
        self.__rays = []

        for x, y in rtrings(rmax=rmax, nrings=nrings, multi=multi):
            self.__rays.append(Ray(pos=[x, y, 0]))

    def get_rays(self):
        """Returns the list of rays

        Returns:
            list[object]: list of the ray objects in the bundle
        """
        return self.__rays

    def propagate_bundle(self, elements):
        """Propagates the bundle through a list of elements.

        Args:
        elements -- a list of optical elements
        """
        for elem in elements:
            for ray in self.get_rays():
                elem.propagate_ray(ray)

    def track_plot(self):
        """Produces a plot of the path of each ray.

        Returns:
            matplotlib.figure: figure of path of each ray
        """
        pointsz = []
        pointsy = []
        fig, ax = plt.subplots()
        for ray in self.get_rays():
            pointsy = [point[1] for point in ray.vertices()]
            pointsz = [point[2] for point in ray.vertices()]

            ax.plot(pointsz, pointsy, color='blue')
            ax.set_xlabel("z position (mm)")
            ax.set_ylabel("y position (mm)")

        return fig

    def rms(self):
        """Returns the root mean square (rms) size of the bundle.

        Returns:
            float: rms size of bundle
        """
        rms = 0
        rays = self.get_rays()
        for ray in rays:
            rms += ray.vertices()[-1][0]**2 + ray.vertices()[-1][1]**2
        rms = np.sqrt(rms/len(rays))

        return rms

    def spot_plot(self):
        """Produces a plot of the final position of each ray.

        Returns:
            matplotlib.figure: figure of (x,y positions)
        """
        pointsx = []
        pointsy = []
        fig, ax = plt.subplots()
        for ray in self.get_rays():
            pointsx.append(ray.vertices()[-1][0])
            pointsy.append(ray.vertices()[-1][1])

        ax.plot(pointsx, pointsy, 'x', color='blue')
        ax.set_xlabel("x position (mm)")
        ax.set_ylabel("y position (mm)")


        return fig

    def spot_plot_coords(self):
        """Returns the (x,y) coordinates of the final position of each ray.

        Returns:
            list[list[float], list[float]]: (x,y) coordinates of final position of each ray
        """
        pointsx = []
        pointsy = []
        for ray in self.get_rays():
            pointsx.append(ray.vertices()[-1][0])
            pointsy.append(ray.vertices()[-1][1])

        return [pointsx, pointsy]
