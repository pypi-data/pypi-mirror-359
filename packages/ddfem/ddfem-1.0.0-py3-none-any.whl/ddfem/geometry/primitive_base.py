from ufl import (
    as_matrix,
    as_vector,
    conditional,
    cos,
    grad,
    pi,
    replace,
    sin,
    tanh,
)
from ufl import max_value as Max
from ufl import min_value as Min

from ufl.algorithms import expand_indices
from ufl.algorithms.apply_algebra_lowering import apply_algebra_lowering
from ufl.algorithms.apply_derivatives import apply_derivatives

ORIGIN = as_vector([0, 0])


class SDF:
    def __init__(self, epsilon=None, name=None, children=None):
        self.name = name
        self.epsilon = epsilon
        self.child_sdf = children if children else []

    def sdf(self, x):
        raise NotImplementedError

    def __call__(self, x):
        return self.sdf(x)

    def search(self, child_name):
        if self.name == child_name:
            return self

        queue = self.child_sdf.copy()

        while queue:
            current_child = queue.pop(0)

            if current_child.name == child_name:
                return current_child

            for child in current_child.child_sdf:
                queue.append(child)

        return None

    def propgate_epsilon(self, epsilon):
        self.epsilon = epsilon
        for child in self.child_sdf:
            child.propgate_epsilon(epsilon)

    def phi(self, x, epsilon=None):
        if not epsilon:
            epsilon = self.epsilon
            assert self.epsilon, "Must define epsilon"
        return 0.5 * (1 - tanh((3 * self.sdf(x) / epsilon)))

    def chi(self, x):
        return conditional(self.sdf(x) <= 0, 1, 0)

    def projection(self, x):
        return -grad(self.sdf(x)) * self.sdf(x)

    def boundary_projection(self, x):
        return x + self.projection(x)

    def external_projection(self, x):
        # return self.chi(x) * x + self.boundary_projection(x) * (1 - self.chi(x))
        return x + self.projection(x) * (1 - self.chi(x))

    def union(self, other):
        return Union(self, other)

    def subtraction(self, other):
        return Subtraction(self, other)

    def intersection(self, other):
        return Intersection(self, other)

    def xor(self, other):
        return Xor(self, other)

    def scale(self, sc):
        return Scale(self, sc)

    def invert(self):
        return Invert(self)

    def rotate(self, angle, radians=True):
        return Rotate(self, angle, radians)

    def translate(self, vector):
        return Translate(self, vector)

    def round(self, sc):
        return Round(self, sc)

    def __or__(self, other):
        return self.union(other)

    def __and__(self, other):
        return self.intersection(other)

    def __sub__(self, other):
        return self.subtraction(other)

    def __xor__(self, other):
        return self.xor(other)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return self.scale(other)
        raise TypeError(f"Cannot multiply a SDF with {type(other)}")

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return self.scale(other)
        raise TypeError(f"Cannot multiply a SDF with {type(other)}")

class BaseOperator(SDF):
    def __init__(self, epsilon, children, *args, **kwargs):

        if not epsilon and all(child.epsilon for child in children):
            if len(children) == 1:
                epsilon = children[0].epsilon
            else:
                epsilon = Min(*[child.epsilon for child in children])

        super().__init__(children=children, epsilon=epsilon, *args, **kwargs)

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(map(repr, self.child_sdf))})"

    def __getitem__(self, key):
        return self.child_sdf[key]


class Union(BaseOperator):
    """Union of two SDFs (OR) - not perfect(negative)"""

    def __init__(self, sdf1, sdf2, epsilon=None, name=None, *args, **kwargs):
        super().__init__(epsilon=epsilon, children=[sdf1, sdf2], *args, **kwargs)
        if self.name is None:
            self.name = f"({sdf1.name}|{sdf2.name})"

    def sdf(self, x):
        return Min(self.child_sdf[0].sdf(x), self.child_sdf[1].sdf(x))


class Subtraction(BaseOperator):
    """Subtraction of two SDFs (difference) - not perfect"""

    def __init__(self, sdf1, sdf2, epsilon=None, name=None, *args, **kwargs):
        super().__init__(epsilon=epsilon, children=[sdf1, sdf2], *args, **kwargs)
        if self.name is None:
            self.name = f"({sdf1.name}-{sdf2.name})"

    def sdf(self, x):
        return Max(self.child_sdf[0].sdf(x), -self.child_sdf[1].sdf(x))


class Intersection(BaseOperator):
    """Intersection of two SDFs (AND) - not perfect"""

    def __init__(self, sdf1, sdf2, epsilon=None, name=None, *args, **kwargs):
        super().__init__(epsilon=epsilon, children=[sdf1, sdf2], *args, **kwargs)
        if self.name is None:
            self.name = f"({sdf1.name}&{sdf2.name})"

    def sdf(self, x):
        return Max(self.child_sdf[0].sdf(x), self.child_sdf[1].sdf(x))


class Xor(BaseOperator):
    """Xor of two SDFs (AND) - perfect"""

    def __init__(self, sdf1, sdf2, epsilon=None, name=None, *args, **kwargs):
        super().__init__(epsilon=epsilon, children=[sdf1, sdf2], *args, **kwargs)
        if self.name is None:
            self.name = f"({sdf1.name}^{sdf2.name})"

    def sdf(self, x):
        a_x = self.child_sdf[0].sdf(x)
        b_x = self.child_sdf[1].sdf(x)
        return Max(Min(a_x, b_x), -Max(a_x, b_x))


class Invert(BaseOperator):
    """Inverts SDF"""

    def __init__(self, sdf1, epsilon=None, name=None, *args, **kwargs):
        super().__init__(epsilon=epsilon, children=[sdf1], *args, **kwargs)
        if self.name is None:
            self.name = f"(-{sdf1.name})"

    def sdf(self, x):
        return -self.child_sdf[0].sdf(x)


class Scale(BaseOperator):
    """Scales SDF"""

    def __init__(self, sdf1, scale, epsilon=None, name=None, *args, **kwargs):
        super().__init__(epsilon=epsilon, children=[sdf1], *args, **kwargs)
        self.scale = scale
        if self.name is None:
            self.name = f"({scale}*{sdf1.name})"

    def sdf(self, x):
        return self.child_sdf[0].sdf(x / self.scale) * self.scale

    def __repr__(self):
        return f"Scale({repr(self.child_sdf[0])}, {self.scale})"


class Rotate(BaseOperator):
    """Rotates SDF, counterclockwise of orgin"""

    def __init__(
        self, sdf1, angle, radians=True, epsilon=None, name=None, *args, **kwargs
    ):
        super().__init__(epsilon=epsilon, children=[sdf1], *args, **kwargs)
        if self.name is None:
            self.name = f"({angle}@{sdf1.name})"

        if not radians:
            angle *= pi / 180
        self.angle = angle

    def sdf(self, x):
        c = cos(self.angle)
        s = sin(self.angle)

        r = as_matrix(((c, -s), (s, c)))
        return self.child_sdf[0].sdf(r.T * x)

    def __repr__(self):
        return f"Rotate({repr(self.child_sdf[0])}, {self.angle})"


class Translate(BaseOperator):
    """Translates SDF"""

    def __init__(self, sdf1, vec, epsilon=None, name=None, *args, **kwargs):
        super().__init__(epsilon=epsilon, children=[sdf1], *args, **kwargs)
        if self.name is None:
            self.name = f"({vec}+{sdf1.name})"

        if isinstance(vec, (list, tuple)):
            vec = as_vector(vec)
        self.vec = vec

    def sdf(self, x):
        return self.child_sdf[0].sdf(x - self.vec)

    def __repr__(self):
        return f"Translate({repr(self.child_sdf[0])}, {self.vec})"


class Round(BaseOperator):
    """Rounds SDF"""

    def __init__(self, sdf1, scale, epsilon=None, name=None, *args, **kwargs):
        super().__init__(epsilon=epsilon, children=[sdf1], *args, **kwargs)
        if self.name is None:
            self.name = f"({scale}~{sdf1.name})"

        assert scale > 0
        self._scale = scale  # careful not to overwrite SDF.scale here

    def sdf(self, x):
        return self.child_sdf[0].sdf(x) - self._scale

    def __repr__(self):
        return f"Round({repr(self.child_sdf[0])}, {self.scale})"
