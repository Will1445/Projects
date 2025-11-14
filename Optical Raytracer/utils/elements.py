"""Optical element module

A collection of classes for creating optical elements.

Classes:
OpticalElement -- default class for optical elements
InterceptElement -- base class storing methods for calculating ray intercepts
SphericalRefraction -- optical surface for ray refraction
SphericalReflection -- optical surface for ray reflection
OutputPlane -- surface for output (endpoint) of rays
"""

import numpy as np
from utils.physics import refract
from utils.physics import reflect


class OpticalElement:
    """Base class for all optical elements.
    
    Methods:
    intercept -- default method for ray intercept
    propagate_ray -- default method for ray propagation
    """
    def intercept(self, ray):
        """Default intercept method.

        Args:
            ray (object): ray object defined by the Ray class

        Raises:
            NotImplementedError: error if intercept() is not yet implemented
        """
        raise NotImplementedError('intercept() needs to be implemented in derived classes')

    def propagate_ray(self, ray):
        """Default propagate method.

        Args:
            ray (object): ray object defined by the Ray class

        Raises:
            NotImplementedError: error if propagate_ray() is not yet implemented
        """
        raise NotImplementedError('propagate_ray() needs to be implemented in derived classes')


class InterceptElement(OpticalElement):
    """Constructs an optical surface centred on the z-axis.

    Methods:
    z_0 -- retuns the z intercept of the surface
    aperture -- returns the aperture
    curvature -- returns the curvature
    n_1 -- returns n_1
    n_2 -- returns n_2
    intercept -- returns the intercept of a ray and the surface

    Attributes:
    z_0 (float) -- point on z-axis the surface intercepts (default 0.0)
    aperture (float) -- the maximum extent of the surface from the z-axis (default 1.0)
    curvature (float) -- curvature of the surface (default (1.0))
    n_1 (float) -- refractive index outside the surface (default 1.0)
    n_2 (float) -- refractive index within the surface (default 1.0)
    """
    def __init__(self, z_0=0., aperture=1., curvature=1., n_1=1., n_2=1.):
        self.__z0 = z_0
        self.__aperture = aperture
        self.__curvature = curvature
        self.__n1 = n_1
        self.__n2 = n_2

    def z_0(self):
        """Returns the z-axis intercept.

        Returns:
            float: the z coordinate the surface intercepts
        """
        return self.__z0

    def aperture(self):
        """Returns the aperture of the surface.

        Returns:
            float: the maximum extent of the surface from the z-axis
        """
        return self.__aperture

    def curvature(self):
        """Returns the curvature of the surface

        Returns:
            float: the curvature of the surface
        """
        return self.__curvature

    def n_1(self):
        """Returns n_1 for the surface

        Returns:
            float: the refractive index within the surface
        """
        return self.__n1

    def n_2(self):
        """Returns n_2 for the surface

        Returns:
            float: the refractive index outside the surface
        """
        return self.__n2

    def intercept(self, ray):
        """Returns the point of intercept of a ray with the surface.

        Args:
        ray (object): ray object defined by the Ray class

        Returns:
            np.array[float, float, float]: the x,y,z coordinate intercept
        """

        ray_pos = ray.pos()
        ray_direc = ray.direc()

        if self.curvature() == 0:
            intercept = ((self.z_0()-ray_pos[2])/ray_direc[2])*ray_direc + ray_pos

            if abs(intercept[0]) > self.aperture() or abs(intercept[1]) > self.aperture():
                return None

            else:
                return intercept

        else:
            radius = abs(1/self.curvature())
            k_vector = ray_direc / np.linalg.norm(ray_direc)
            r_vector = ray_pos - np.array([0, 0, self.z_0() + 1/self.curvature()])

            root1 = (
                -np.dot(r_vector, k_vector)
                + np.sqrt(
                    np.dot(r_vector, k_vector) ** 2
                    - (np.linalg.norm(r_vector) ** 2 - radius ** 2))
                )

            root2 = (
                -np.dot(r_vector, k_vector)
                - np.sqrt(
                    np.dot(r_vector, k_vector) ** 2
                    - (np.linalg.norm(r_vector) ** 2 - radius ** 2))
                )

            if np.isnan(root1):
                return None
            else:
                pos_roots = [root for root in [root1, root2] if root > 0]

                if not pos_roots:
                    return None
                else:
                    if self.curvature() > 0:
                        root = min(pos_roots)
                    else:
                        root = max(pos_roots)

                    intercept = ray_pos + k_vector * root
                    if abs(intercept[0]) > self.aperture() or abs(intercept[1]) > self.aperture():
                        return None
                    else:
                        return intercept


class SphericalRefraction(InterceptElement):
    """Constructs a spherical surface for refraction.

    Inherits from InterceptElement

    Methods:
    propagate_ray -- refracts the ray off the surface
    focal_point -- returns the focal point of the surface

    Attributes:
    z_0 (float) -- point on z-axis the surface intercepts (default 0.0)
    aperture (float) -- the maximum extent of the surface from the z-axis (default 1.0)
    curvature (float) -- curvature of the surface (default (1.0))
    n_1 (float) -- refractive index outside the surface (default 1.0)
    n_2 (float) -- refractive index within the surface (default 1.0)
    """
    def __init__(self, z_0=0., aperture=1., curvature=1., n_1=1., n_2=1.):
        super().__init__(z_0=z_0, aperture=aperture, curvature=curvature, n_1=n_1, n_2=n_2)

    def propagate_ray(self, ray):
        """Appends the ray's position and direction caused by an intercept.

        Args:
        ray (object): ray object defined by the Ray class
        """

        intercept = self.intercept(ray)

        if intercept is not None:
            if self.curvature() == 0:
                refract_direc = refract(ray.direc(), np.array([0, 0, 1]), self.n_1(), self.n_2())

            else:
                refract_direc = refract(ray.direc(), intercept -
                                        np.array([0, 0, self.z_0() + 1/self.curvature()]), self.n_1(), self.n_2())

            if refract_direc is not None:
                ray.append(intercept, refract_direc)

    def focal_point(self):
        """Returns the focal point of the surface

        Returns:
            float: z position of the focal point
        """
        focal = (self.n_2()/self.curvature())/(self.n_2()-self.n_1()) + self.z_0()
        return focal


class SphericalReflection(InterceptElement):
    """Constructs a spherical surface for reflection.

    Inherits from InterceptElement

    Methods:
    propagate_ray -- refracts the ray off the surface
    focal_point -- returns the focal point of the surface

    Attributes:
    z_0 (float) -- point on z-axis the surface intercepts (default 100.0)
    aperture (float) -- the maximum extent of the surface from the z-axis (default 6.0)
    curvature (float) -- curvature of the surface (default (-0.02))
    """
    def __init__(self, z_0=100., aperture=6., curvature=-0.02):
        super().__init__(z_0=z_0, aperture=aperture, curvature=curvature, n_1=1.0, n_2=1.0)

    def propagate_ray(self, ray):
        """Appends the ray's position and direction caused by an intercept.

        Args:
            ray (object): ray object defined by the Ray class
        """
        intercept = self.intercept(ray)

        if intercept is not None:
            if self.curvature() == 0:
                reflect_direc = reflect(ray.direc(), np.array([0,0,1]))

            else:
                reflect_direc = reflect(ray.direc(), intercept - np.array([0, 0, self.z_0() + 1/self.curvature()]))

            if reflect_direc is not None:
                ray.append(intercept, reflect_direc)

    def focal_point(self):
        """Returns the focal point of the surface.

        Returns:
            float: z position of the focal point
        """
        focal_point = (1/self.curvature())/2 + self.z_0()
        return focal_point


class OutputPlane(InterceptElement):
    """Defines an output plane.

    Inherits from InterceptElement

    Methods:
    propagate_ray -- appends the intercept of a ray to its position

    Attributes:
    z_0 (float) -- the z coordinate of the plane (default 0.0)
    """

    def __init__(self, z_0=0.):
        super().__init__(z_0=z_0, aperture=float("inf"), curvature=0, n_1=1.0, n_2=1.0)

    def propagate_ray(self, ray):
        """Appends the ray-plane intercept to the ray's position

        Args:
            ray (object): ray object defined by the Ray class
        """
        ray.append(self.intercept(ray), ray.direc())
