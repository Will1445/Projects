import sys
import numpy as np
from PyQt5.QtOpenGL import QGLWidget, QGLFormat
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QDockWidget, QLabel, QHBoxLayout, 
                             QSlider, QScrollArea, QGroupBox)
from PyQt5.QtCore import Qt, QPoint
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLU import gluDisk


def rtrings(rmax, nrings, multi):
    radius = [float(x) for x in np.linspace(0, rmax, nrings+1)]
    
    ring = 0
    for radius in radius:
        if radius == 0:
            yield (0.0,0.0)
            
        else:
            ring += 1
            N_points = ring * multi
            for i in range(N_points):
                theta = 2*np.pi/N_points * i
                yield (radius*np.cos(theta), radius*np.sin(theta))


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
    propagate_bundle -- passes the ray bundle through a list of elements
    track_plot -- returns a plot of the path of each ray
    rms -- returns the rms size of the bundle
    spot_plot -- returns a plot of the rays at the output plane
    spot_plot_coords -- returns the (x,y) coordinates of each ray
    get_rays -- returns the list of ray objects in the bundle

    Attributes:
    rmax (float) -- maximum radius of the bundle (default 5.0)
    nrings (int) -- number of rings in the bundle (default 5)
    multi (int) -- number of rays per ring (default 6)
    """
    def __init__(self, rmax=5., nrings=5, multi=6):
        self.__rmax = rmax
        self.__nrings = nrings
        self.__multi = multi
        self.__rays = []

        for x, y in rtrings(rmax=rmax, nrings=nrings, multi=multi):
            self.__rays.append(Ray(pos=[x, y, 0]))

    def propagate_bundle(self, elements):
        """Propagates the bundle through a list of elements.

        Args:
        elements -- a list of optical elements
        """
        for elem in elements:
            for ray in self.__rays:
                elem.propagate_ray(ray)

    def track_plot(self):
        """Produces a plot of the path of each ray.

        Returns:
            matplotlib.figure: figure of path of each ray
        """
        pointsz = []
        pointsy = []
        fig, ax = plt.subplots()
        for ray in self.__rays:
            pointsy = [point[1] for point in ray.vertices()]
            pointsz = [point[2] for point in ray.vertices()]

            ax.plot(pointsz, pointsy)

        return fig

    def rms(self):
        """Returns the root mean square (rms) size of the bundle.

        Returns:
            float: rms size of bundle
        """
        rms = 0
        for ray in self.__rays:
            rms += ray.vertices()[-1][0]**2 + ray.vertices()[-1][1]**2
        rms = np.sqrt(rms/len(self.__rays))

        return rms

    def spot_plot(self):
        """Produces a plot of the final position of each ray.

        Returns:
            matplotlib.figure: figure of (x,y positions)
        """
        pointsx = []
        pointsy = []
        fig, ax = plt.subplots()
        for ray in self.__rays:
            pointsx.append(ray.vertices()[-1][0])
            pointsy.append(ray.vertices()[-1][1])

        ax.plot(pointsx, pointsy, 'x')

        return fig

    def spot_plot_coords(self):
        """Returns the (x,y) coordinates of the final position of each ray.

        Returns:
            list[list[float], list[float]]: (x,y) coordinates of final position of each ray
        """
        pointsx = []
        pointsy = []
        for ray in self.__rays:
            pointsx.append(ray.vertices()[-1][0])
            pointsy.append(ray.vertices()[-1][1])

        return [pointsx, pointsy]
    
    def get_rays(self):
        """Returns the list of rays

        Returns:
            list[object]: list of the ray objects in the bundle
        """
        return self.__rays


class OpticalElement:
    def intercept(self, ray):
        raise NotImplementedError('intercept() needs to be implemented in derived classes')

    def propagate_ray(self, ray):
        raise NotImplementedError('propagate_ray() needs to be implemented in derived classes')


class InterceptElement(OpticalElement):
    """Constructs a spherical optical surface centred on the z-axis.

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
    
    def set_z0(self, value):
        self.__z0 = value


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
            self.__R = abs(1/self.curvature())
            self.__k = ray_direc / np.linalg.norm(ray_direc)
            self.__r = ray_pos - np.array([0, 0, self.z_0() + 1/self.curvature()])

            self.__l1 = (
                -np.dot(self.__r, self.__k)
                + np.sqrt(
                    np.dot(self.__r, self.__k) ** 2
                    - (np.linalg.norm(self.__r) ** 2 - self.__R ** 2))
                )

            self.__l2 = (
                -np.dot(self.__r, self.__k)
                - np.sqrt(
                    np.dot(self.__r, self.__k) ** 2
                    - (np.linalg.norm(self.__r) ** 2 - self.__R ** 2))
                )

            if np.isnan(self.__l1):
                return None
            else:
                pos_roots = [root for root in [self.__l1, self.__l2] if root > 0]

                if not pos_roots:
                    return None
                else:
                    if self.curvature() > 0:
                        self.__l = min(pos_roots)
                    else:
                        self.__l = max(pos_roots)

                    intercept = ray_pos + self.__k * self.__l
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

        self.__intercept = self.intercept(ray)

        if self.__intercept is not None:
            if self.curvature() == 0:
                refract_direc = refract(ray.direc(), np.array([0, 0, 1]), self.n_1(), self.n_2())

            else:
                refract_direc = refract(ray.direc(), self.__intercept - 
                                        np.array([0, 0, self.z_0() + 1/self.curvature()]), self.n_1(), self.n_2())

            if refract_direc is not None:
                ray.append(self.__intercept, refract_direc)

    def focal_point(self):
        """Returns the focal point of the surface

        Returns:
            float: z position of the focal point
        """
        self.__focal = (self.n_2()/self.curvature())/(self.n_2()-self.n_1()) + self.z_0()
        return self.__focal


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


class Lens(OpticalElement):
    """ Defines a default optical lens.

    Methods:
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

    def z_0(self):
        return self.__z0
    
    def set_z0(self, value):
        self.__z0 = value
        # Update both surfaces of the lens
        self.__surface1.set_z0(value)
        self.__surface2.set_z0(value + self.__thickness)

    def curvature1(self):
        return self.__curvature1

    def curvature2(self):
        return self.__curvature2

    def thickness(self):
        return self.__thickness

    def aperture(self):
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
    



class GLWidget(QGLWidget):
    def __init__(self, parent=None):
        fmt = QGLFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QGLFormat.CompatibilityProfile)
        super().__init__(fmt, parent)
        
        self.lastPos = QPoint()
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        self.scale = 0.5
        self.min_scale = 0.01
        self.max_scale = 50.0
        self.zoom_sensitivity = 0.04
        self.translation = [0, 0, -50]
        self.rays = []
        self.elements = []

    def initializeGL(self):
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Camera setup
        glTranslatef(*self.translation)
        glRotatef(self.xRot / 16.0, 1.0, 0.0, 0.0)
        glRotatef(self.yRot / 16.0, 0.0, 1.0, 0.0)
        glRotatef(self.zRot / 16.0, 0.0, 0.0, 1.0)
        glScalef(self.scale, self.scale, self.scale)
        
        # Draw coordinate axes
        self.draw_axes()
        
        # Draw optical elements
        self.draw_elements()
        
        # Draw rays
        glColor3f(1.0, 0.0, 0.0)  # Red
        for ray in self.rays:
            verts = ray.vertices()
            if len(verts) > 1:
                glBegin(GL_LINE_STRIP)
                for v in verts:
                    glVertex3f(v[0], v[1], v[2])
                glEnd()

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = width / float(height)
        gluPerspective(45.0, aspect, 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.xRot += dy
            self.yRot += dx
        elif event.buttons() & Qt.RightButton:
            self.translation[0] += dx * 0.1
            self.translation[1] -= dy * 0.1

        self.lastPos = event.pos()
        self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120.0
        # Exponential zoom for better control at both ends
        zoom_factor = 1.0 + delta * self.zoom_sensitivity
        
        # Apply zoom with limits
        new_scale = self.scale * zoom_factor
        self.scale = max(self.min_scale, min(new_scale, self.max_scale))
        self.update()
    
    

    def draw_axes(self):
        glBegin(GL_LINES)
        # X axis (Red)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(-100, 0, 0)
        glVertex3f(100, 0, 0)
        # Y axis (Green)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0, -100, 0)
        glVertex3f(0, 100, 0)
        # Z axis (Blue)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0, 0, -100)
        glVertex3f(0, 0, 100)
        glEnd()

    def draw_elements(self):
        for elem in self.elements:
            if isinstance(elem, Lens):  # Check for base Lens class
                self.draw_lens(elem)
            elif isinstance(elem, OutputPlane):
                self.draw_output_plane(elem)

    def draw_lens(self, lens):
        try:
            # Extract parameters
            z_center = lens.z_0()
            thickness = lens.thickness()
            aperture = lens.aperture()
            
            glColor3f(0.0, 0.5, 1.0)  # Blue
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            
            # Draw cylindrical body
            glPushMatrix()
            glTranslatef(0, 0, z_center)
            gluCylinder(gluNewQuadric(), aperture, aperture, thickness, 32, 1)
            glPopMatrix()
            
            # Draw front face
            glPushMatrix()
            glTranslatef(0, 0, z_center)
            gluDisk(gluNewQuadric(), 0, aperture, 32, 1)
            glPopMatrix()
            
            # Draw back face
            glPushMatrix()
            glTranslatef(0, 0, z_center + thickness)
            gluDisk(gluNewQuadric(), 0, aperture, 32, 1)
            glPopMatrix()
            
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            
        except Exception as e:
            print(f"Error drawing lens: {e}")

    def draw_output_plane(self, plane):
        glColor3f(0.0, 1.0, 0.0)  # Green
        size = 50
        glBegin(GL_LINE_LOOP)
        glVertex3f(-size, -size, plane.z_0())
        glVertex3f(size, -size, plane.z_0())
        glVertex3f(size, size, plane.z_0())
        glVertex3f(-size, size, plane.z_0())
        glEnd()

class RayTracer3DGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Ray Tracer")
        self.setGeometry(100, 100, 800, 600)
        
        # Define initial positions
        self.initial_lens_z = 100.
        self.initial_plane_z = 250.
        
        # Create OpenGL widget
        self.glWidget = GLWidget()
        self.setCentralWidget(self.glWidget)
        
        # Initialize ray bundle and elements
        self.bundle = RayBundle(rmax=5, nrings=3, multi=6)
        self.glWidget.elements = [
            BiConvex(z_0=self.initial_lens_z, curvature1=0.02, curvature2=-0.02, 
                    n_inside=1.5168, n_outside=1., thickness=5., aperture=50.),
            OutputPlane(z_0=self.initial_plane_z)
        ]
        self.glWidget.rays = self.bundle.get_rays()
        self.bundle.propagate_bundle(self.glWidget.elements)
        
        # Track lenses and their controls
        self.lens_controls = []  # Stores (slider, initial_z) for each lens
        self.lens_count = 1
        
        self.setup_ui()
    
    def setup_ui(self):
        dock = QDockWidget("Controls", self)
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Lens controls header
        lens_header = QLabel("<b>Lens Controls</b>")
        layout.addWidget(lens_header)
        
        # Container for lens sliders
        self.lens_scroll = QScrollArea()
        self.lens_scroll.setWidgetResizable(True)
        self.lens_container = QWidget()
        self.lens_layout = QVBoxLayout(self.lens_container)
        self.lens_layout.setContentsMargins(5, 5, 5, 5)
        self.lens_scroll.setWidget(self.lens_container)
        layout.addWidget(self.lens_scroll)
        
        # Create controls for initial lens
        self.add_lens_controls(0, self.initial_lens_z)
        
        # Add lens button
        add_lens_btn = QPushButton("Add Biconvex Lens")
        add_lens_btn.clicked.connect(self.add_lens)
        layout.addWidget(add_lens_btn)
        
        # Output plane controls
        plane_header = QLabel("<b>Output Plane Controls</b>")
        layout.addWidget(plane_header)
        
        # Output plane position controls
        plane_z_layout = QHBoxLayout()
        plane_z_label = QLabel("Position:")
        self.plane_z_slider = QSlider(Qt.Horizontal)
        self.plane_z_slider.setRange(200, 300)
        self.plane_z_slider.setValue(int(self.initial_plane_z))
        self.plane_z_slider.valueChanged.connect(self.update_plane_position)
        
        plane_z_layout.addWidget(plane_z_label)
        plane_z_layout.addWidget(self.plane_z_slider)
        layout.addLayout(plane_z_layout)
        
        # System controls
        system_header = QLabel("<b>System Controls</b>")
        layout.addWidget(system_header)
        
        # Reset button
        reset_btn = QPushButton("Reset All Positions")
        reset_btn.clicked.connect(self.reset_positions)
        layout.addWidget(reset_btn)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Rays")
        refresh_btn.clicked.connect(self.refresh)
        layout.addWidget(refresh_btn)
        
        # Info label
        info = QLabel("Mouse Controls:\n"
                     "- Left drag: Rotate\n"
                     "- Right drag: Pan\n"
                     "- Wheel: Zoom")
        layout.addWidget(info)
        
        widget.setLayout(layout)
        dock.setWidget(widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def refresh(self):
        # Create new bundle and propagate through ALL elements in proper order
        self.bundle = RayBundle(rmax=5, nrings=3, multi=6)
        
        # Sort elements by z-position to ensure proper propagation order
        sorted_elements = sorted(
            self.glWidget.elements,
            key=lambda elem: elem.z_0() if hasattr(elem, 'z_0') else float('inf')
        )
        
        self.bundle.propagate_bundle(sorted_elements)
        self.glWidget.rays = self.bundle.get_rays()
        self.glWidget.update()

    # Create controls for a lens
    def add_lens_controls(self, index, initial_z):
        # Create lens control group
        group = QGroupBox(f"Lens {index+1}")
        group_layout = QVBoxLayout()
        
        # Position slider
        pos_layout = QHBoxLayout()
        pos_label = QLabel("Position:")
        slider = QSlider(Qt.Horizontal)
        slider.setRange(50, 300)
        slider.setValue(int(initial_z))
        slider.valueChanged.connect(lambda value, i=index: self.update_lens_position(i, value))
        
        pos_layout.addWidget(pos_label)
        pos_layout.addWidget(slider)
        group_layout.addLayout(pos_layout)
        
        # Remove button
        remove_btn = QPushButton("Remove Lens")
        remove_btn.clicked.connect(lambda _, i=index: self.remove_lens(i))
        group_layout.addWidget(remove_btn)
        
        group.setLayout(group_layout)
        self.lens_layout.addWidget(group)
        
        # Store control reference
        self.lens_controls.append((slider, initial_z))

    # Update specific lens position
    def update_lens_position(self, index, value):
        # Find lens in elements list
        lenses = [elem for elem in self.glWidget.elements if isinstance(elem, Lens)]
        if index < len(lenses):
            lenses[index].set_z0(float(value))
            self.refresh()

    def update_plane_position(self, value):
        for elem in self.glWidget.elements:
            if isinstance(elem, OutputPlane):
                elem.set_z0(float(value))
                self.refresh()
        
    def reset_positions(self):
        # Reset all lenses to their initial positions
        for i, (slider, initial_z) in enumerate(self.lens_controls):
            slider.setValue(int(initial_z))
            self.update_lens_position(i, initial_z)
        
        # Reset output plane
        self.plane_z_slider.setValue(int(self.initial_plane_z))
        self.update_plane_position(self.initial_plane_z)
        
    # Remove a lens
    def remove_lens(self, index):
        # Find all lenses in elements list
        lenses = [elem for elem in self.glWidget.elements if isinstance(elem, Lens)]
        if index < len(lenses):
            # Remove from elements list
            self.glWidget.elements.remove(lenses[index])
            
            # Remove controls
            control_group = self.lens_layout.itemAt(index).widget()
            control_group.deleteLater()
            self.lens_controls.pop(index)
            
            # Update labels for remaining lenses
            for i in range(index, self.lens_layout.count()):
                widget = self.lens_layout.itemAt(i).widget()
                if widget:  # Check if widget exists
                    widget.setTitle(f"Lens {i+1}")
            
            self.lens_count -= 1
            self.refresh()
        
    def add_lens(self):
        # Create a new lens with same parameters
        new_z = self.initial_lens_z + self.lens_count * 50
        new_lens = BiConvex(
            z_0=new_z,
            curvature1=0.02,
            curvature2=-0.02,
            n_inside=1.5168,
            n_outside=1.0,
            thickness=5.0,
            aperture=50.0
        )
        
        # Add to elements list
        self.glWidget.elements.append(new_lens)
        
        # Add controls for new lens
        self.add_lens_controls(self.lens_count, new_z)
        
        # Update lens count
        self.lens_count += 1
        
        # Refresh to show new lens
        self.refresh()
        
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RayTracer3DGUI()
    window.show()
    sys.exit(app.exec_())