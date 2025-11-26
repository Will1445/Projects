import sys
from PyQt5.QtOpenGL import QGLWidget, QGLFormat
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QDockWidget, QLabel, QHBoxLayout, QSlider, QScrollArea, QGroupBox
from PyQt5.QtCore import Qt, QPoint
from OpenGL.GL import *
from OpenGL.GLU import *
from utils.elements import *
from utils.genpolar import *
from utils.lenses import *
from utils.physics import *
from utils.rays import *


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
        
        # Coordinate axes
        self.draw_axes()
        
        # Optical elements
        self.draw_elements()
        
        # Rays
        glColor3f(1.0, 0.0, 0.0)
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

    # Zooming function
    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120.0
        zoom_factor = 1.0 + delta * self.zoom_sensitivity
        
        new_scale = self.scale * zoom_factor
        self.scale = max(self.min_scale, min(new_scale, self.max_scale))
        self.update()
    
    

    def draw_axes(self):
        glBegin(GL_LINES)
        
        # X axis
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(-100, 0, 0)
        glVertex3f(100, 0, 0)
        
        # Y axis
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0, -100, 0)
        glVertex3f(0, 100, 0)
        
        # Z axis
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0, 0, -100)
        glVertex3f(0, 0, 100)
        
        glEnd()

    def draw_elements(self):
        for elem in self.elements:
            if isinstance(elem, Lens):
                self.draw_lens(elem)
            elif isinstance(elem, OutputPlane):
                self.draw_output_plane(elem)

    def draw_lens(self, lens):
        try:
            z_center = lens.z_0()
            thickness = lens.thickness()
            aperture = lens.aperture()
            
            glColor3f(0.0, 0.5, 1.0) 
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            
            # Draw cylindrical body
            glPushMatrix()
            glTranslatef(0, 0, z_center)
            gluCylinder(gluNewQuadric(), aperture, aperture, thickness, 32, 1)
            glPopMatrix()
            
            # Front face
            glPushMatrix()
            glTranslatef(0, 0, z_center)
            gluDisk(gluNewQuadric(), 0, aperture, 32, 1)
            glPopMatrix()
            
            # Back face
            glPushMatrix()
            glTranslatef(0, 0, z_center + thickness)
            gluDisk(gluNewQuadric(), 0, aperture, 32, 1)
            glPopMatrix()
            
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            
        except Exception as e:
            print(f"Error drawing lens: {e}")

    def draw_output_plane(self, plane):
        glColor3f(0.0, 1.0, 0.0)
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
        
        # Set initial positions
        self.initial_lens_z = 100.
        self.initial_plane_z = 250.
        


        self.glWidget = GLWidget()
        self.setCentralWidget(self.glWidget)
        
        # Setup ray bundle and optical elements
        self.bundle = RayBundle(rmax=5, nrings=3, multi=6)
        self.glWidget.elements = [
            BiConvex(z_0=self.initial_lens_z, curvature1=0.02, curvature2=-0.02, 
                    n_inside=1.5168, n_outside=1., thickness=5., aperture=50.),
            OutputPlane(z_0=self.initial_plane_z)
        ]
        self.glWidget.rays = self.bundle.get_rays()
        self.bundle.propagate_bundle(self.glWidget.elements)
        
        # Setup lens controls
        self.lens_controls = []
        self.lens_count = 1
        
        self.setup_ui()
    
    def setup_ui(self):
        dock = QDockWidget("Controls", self)
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Lens controls
        lens_header = QLabel("<b>Lens Controls</b>")
        layout.addWidget(lens_header)
        
        # Section for lens position controls
        self.lens_scroll = QScrollArea()
        self.lens_scroll.setWidgetResizable(True)
        self.lens_container = QWidget()
        self.lens_layout = QVBoxLayout(self.lens_container)
        self.lens_layout.setContentsMargins(5, 5, 5, 5)
        self.lens_scroll.setWidget(self.lens_container)
        layout.addWidget(self.lens_scroll)
        self.add_lens_controls(0, self.initial_lens_z)
        
        # Add lens button
        add_lens_btn = QPushButton("Add Biconvex Lens")
        add_lens_btn.clicked.connect(self.add_lens)
        layout.addWidget(add_lens_btn)
        
        # Section for output plane controls 
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
        
        # Basic system controls
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
        
        # Key 
        key = QLabel("Mouse Controls:\n"
                     "- Left drag: Rotate\n"
                     "- Right drag: Pan\n"
                     "- Wheel: Zoom")
        layout.addWidget(key)
        
        widget.setLayout(layout)
        dock.setWidget(widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def refresh(self):
        # Create ray bundle on refresh 
        self.bundle = RayBundle(rmax=5, nrings=3, multi=6)
        
        # Set optical elements order
        sorted_elements = sorted(
            self.glWidget.elements,
            key=lambda elem: elem.z_0() if hasattr(elem, 'z_0') else float('inf')
        )
        
        # Propagate ray bundle
        self.bundle.propagate_bundle(sorted_elements)
        self.glWidget.rays = self.bundle.get_rays()
        self.glWidget.update()

    # Add lens controls
    def add_lens_controls(self, index, initial_z):

        group = QGroupBox(f"Lens {index+1}")
        group_layout = QVBoxLayout()
        
        pos_layout = QHBoxLayout()
        pos_label = QLabel("Position:")
        slider = QSlider(Qt.Horizontal)
        slider.setRange(50, 300)
        slider.setValue(int(initial_z))
        slider.valueChanged.connect(lambda value, i=index: self.update_lens_position(i, value))
        
        pos_layout.addWidget(pos_label)
        pos_layout.addWidget(slider)
        group_layout.addLayout(pos_layout)
        
        # Remove lens button
        remove_btn = QPushButton("Remove Lens")
        remove_btn.clicked.connect(lambda _, i=index: self.remove_lens(i))
        group_layout.addWidget(remove_btn)
        
        group.setLayout(group_layout)
        self.lens_layout.addWidget(group)
        
        self.lens_controls.append((slider, initial_z))

    # Update lens position on refresh
    def update_lens_position(self, index, value):
        lenses = [elem for elem in self.glWidget.elements if isinstance(elem, Lens)]
        if index < len(lenses):
            lenses[index].set_z0(float(value))
            self.refresh()

    # Update plane position on refresh
    def update_plane_position(self, value):
        for elem in self.glWidget.elements:
            if isinstance(elem, OutputPlane):
                elem.set_z0(float(value))
                self.refresh()
    
    # Reset positions on reset
    def reset_positions(self):
        for i, (slider, initial_z) in enumerate(self.lens_controls):
            slider.setValue(int(initial_z))
            self.update_lens_position(i, initial_z)
        
        self.plane_z_slider.setValue(int(self.initial_plane_z))
        self.update_plane_position(self.initial_plane_z)
        
    # Remove a lens
    def remove_lens(self, index):
        lenses = [elem for elem in self.glWidget.elements if isinstance(elem, Lens)]
        
        if index < len(lenses):
            self.glWidget.elements.remove(lenses[index])
            
            control_group = self.lens_layout.itemAt(index).widget()
            control_group.deleteLater()
            self.lens_controls.pop(index)
            
            for i in range(index, self.lens_layout.count()):
                widget = self.lens_layout.itemAt(i).widget()
                if widget: 
                    widget.setTitle(f"Lens {i+1}") 
            
            # Updated lens count   
            self.lens_count -= 1
            self.refresh()
        
    def add_lens(self):
        # add a new lens 
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
        
        # add to element list and controls 
        self.glWidget.elements.append(new_lens)
        self.add_lens_controls(self.lens_count, new_z)
        self.lens_count += 1
        
        self.refresh()
        
     
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RayTracer3DGUI()
    window.show()
    sys.exit(app.exec_())