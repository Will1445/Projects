"""Lens module

A collection of classes to define different optical lenses

Classes:
Lens -- default lens class from which other lenses inherit from
PlanoConvex -- constructs a plano-convex lens
ConvexPlano -- constructs a convex-plano lens
Biconvex -- contructs a bi-convex lens
"""

from utils.elements import SphericalRefraction
from utils.elements import OpticalElement


class Lens(OpticalElement):
    """ Defines a default optical lens.

    Methods:
    curvature1 -- returns the curvature of the left face
    curvature2 -- returns the curvature of the right face
    z_0 -- returns the z-axis intercept of the lens
    ninside -- returns the refractive index inside the lens
    noutside -- returns the refractive index outside the lens
    thickness -- returns the thickness of the lens
    aperture -- returns the aperture of the lens
    propagate_ray -- propagates a ray through the two surfaces of the lens
    focal_point -- returns the focal point of the lens

    Attributes:
    z_0 (float) -- point on z-axis the lens intercepts (default 50.0)
    curvature1 (float) -- curvature of the left face of the lens (default 0.0)
    curvature2 (float) -- curvature of the right face of the lens (default 0.0)
    n_inside (float) -- refractive index within the lens (default 1.0)
    n_outside (float) -- refractive index outside the lens (default 1.0)
    thickness (float) -- thickness of the lens (default 1.0)
    aperture (float) -- maximum extent of the lens from the z-axis (default 1.0)
    """

    def __init__(self, z_0=50., curvature1=0., curvature2=0., n_inside=1., n_outside=1., thickness=1., aperture=1.):
        self.__surface1 = SphericalRefraction(z_0=z_0, curvature=curvature1, n_1=n_outside,
                                              n_2=n_inside, aperture=aperture)
        self.__surface2 = SphericalRefraction(z_0=z_0 + thickness, curvature=curvature2,
                                              n_1=n_inside, n_2=n_outside, aperture=aperture)
        self.__curvature1 = curvature1
        self.__curvature2 = curvature2
        self.__z0 = z_0
        self.__ninside = n_inside
        self.__noutside = n_outside
        self.__thickness = thickness
        self.__aperture = aperture

    def curvature1(self):
        """Returns the curvature of the left face.

        Returns:
            float: the curvature of the left face
        """
        return self.__curvature1

    def curvature2(self):
        """Returns the curvature of the right face.

        Returns:
            float: the curvature of the right face
        """
        return self.__curvature2

    def z_0(self):
        """Returns the z-axis intercept.

        Returns:
            float: the z coordinate the lens intercepts
        """
        return self.__z0

    def ninside(self):
        """Returns ninside for the lens

        Returns:
            float: the refractive index within the lens
        """
        return self.__ninside

    def noutside(self):
        """Returns noutside for the lens

        Returns:
            float: the refractive index outside the lens
        """
        return self.__noutside

    def thickness(self):
        """Returns the thickness of the lens

        Returns:
            float: the thickness of the lens
        """
        return self.__thickness

    def aperture(self):
        """Returns the aperture of the lens

        Returns:
            float: the extent of the lens from the z-axis
        """
        return self.__aperture

    def propagate_ray(self, ray):
        """Propagates a ray through the two surfaces of the lens.

        Args:
            ray (object): ray object defined by the Ray class
        """
        self.__surface1.propagate_ray(ray)
        self.__surface2.propagate_ray(ray)

    def focal_point(self):
        """Returns the focal point of the lens.

        Returns:
            float: z coordinate intercept
        """
        if self.__curvature1 == 0:
            focal_point = self.__z0 + (1/abs(self.__curvature2))/(
                self.__ninside/self.__noutside - 1) + self.__thickness
            return focal_point
        elif self.__curvature2 == 0:
            focal_point = self.__z0 + (1/self.__curvature1)/(self.__ninside/self.__noutside - 1)
            focal_point = focal_point * (
                1 + (self.__ninside-1)*self.__thickness/(self.__ninside*(1/self.__curvature1))) - self.__thickness
            return focal_point
        else:
            focal_point = (self.__ninside/self.__noutside - 1)*(self.__curvature1 - self.__curvature2)
            return 1/focal_point + self.__z0 + self.__thickness


class PlanoConvex(Lens):
    """Defines a plano-convex lens.

    Inherits from the Lens class to form a plano-convex lens

    Attributes:
    z_0 (float) -- point on z-axis the lens intercepts (default 50.0)
    curvature (float) -- curvature of the convex face of the lens (default 0.0)
    n_inside (float) -- refractive index within the lens (default 1.0)
    n_outside (float) -- refractive index outside the lens (default 1.0)
    thickness (float) -- thickness of the lens (default 1.0)
    aperture (float) -- maximum extent of the lens from the z-axis (default 1.0)
    """
    def __init__(self, z_0=50., curvature=0., n_inside=1., n_outside=1., thickness=1., aperture=1.):
        Lens.__init__(self, z_0=z_0, curvature1=0., curvature2=curvature,
                      n_inside=n_inside, n_outside=n_outside, thickness=thickness, aperture=aperture)


class ConvexPlano(Lens):
    """Defines a convex-plano lens.

    Inherits from the Lens class to form a convex-plano lens

    Attributes:
    z_0 (float) -- point on z-axis the lens intercepts (default 50.0)
    curvature (float) -- curvature of the convex face of the lens (default 0.0)
    n_inside (float) -- refractive index within the lens (default 1.0)
    n_outside (float) -- refractive index outside the lens (default 1.0)
    thickness (float) -- thickness of the lens (default 1.0)
    aperture (float) -- maximum extent of the lens from the z-axis (default 1.0)
    """
    def __init__(self, z_0=50., curvature=0., n_inside=1., n_outside=1., thickness=1., aperture=1.):
        Lens.__init__(self, z_0=z_0, curvature1=curvature, curvature2=0.,
                      n_inside=n_inside, n_outside=n_outside, thickness=thickness, aperture=aperture)


class BiConvex(Lens):
    """Defines a bi-convex lens.

    Inherits from the Lens class to form a bi-convex lens

    Attributes:
    z_0 (float) -- point on z-axis the lens intercepts (default 50.0)
    curvature1 (float) -- curvature of the left face of the lens (default 0.0)
    curvature2 (float) -- curvature of the right face of the lens (default 0.0)
    n_inside (float) -- refractive index within the lens (default 1.0)
    n_outside (float) -- refractive index outside the lens (default 1.0)
    thickness (float) -- thickness of the lens (default 1.0)
    aperture (float) -- maximum extent of the lens from the z-axis (default 1.0)
    """

    def __init__(self, z_0=50., curvature1=0., curvature2=0., n_inside=1., n_outside=1., thickness=1., aperture=1.):
        Lens.__init__(self, z_0=z_0, curvature1=curvature1, curvature2=curvature2,
                      n_inside=n_inside, n_outside=n_outside, thickness=thickness, aperture=aperture)
