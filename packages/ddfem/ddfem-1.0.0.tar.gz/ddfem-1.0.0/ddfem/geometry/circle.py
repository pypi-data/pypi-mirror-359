from ufl import as_vector

from .helpers import ufl_length
from .primitive_base import ORIGIN, SDF


class Circle(SDF):
    def __init__(self, radius, center=ORIGIN, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.radius = radius

        assert len(center) == 2
        if isinstance(center, (list, tuple)):
            center = as_vector(center)
        self.center = center

    def __repr__(self):
        return f"Circle({self.radius}, {self.center})"

    def sdf(self, x):
        center_x = x - self.center
        return ufl_length(center_x) - self.radius

class Sphere(SDF):
    def __init__(self, radius, center=ORIGIN, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.radius = radius

        if isinstance(center, (list, tuple)):
            center = as_vector(center)
        self.center = center

    def __repr__(self):
        return f"Circle({self.radius}, {self.center})"

    def sdf(self, x):
        center_x = x - self.center
        return ufl_length(center_x) - self.radius

