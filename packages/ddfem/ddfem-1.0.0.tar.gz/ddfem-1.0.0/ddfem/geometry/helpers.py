from ufl import conditional, dot, sqrt
from ufl import max_value as Max
from ufl import min_value as Min


def ufl_length(p):
    # return sqrt(dot(p, p))
    # return ufl_max(sqrt(dot(p, p) + 1e-10), 1e-10)
    return sqrt(dot(p, p))


def ufl_sign(p):
    if isinstance(p, (float, int)):
        return 1 if p > 0 else -1

    return conditional(p > 0, 1, -1)


def ufl_clamp(p, minimum, maximum):
    if isinstance(p, (float, int)):
        return min(max(p, minimum), maximum)

    def ufl_max(p1, p2):
        return conditional(p2 < p1, p1, p2)

    def ufl_min(p1, p2):
        return conditional(p1 < p2, p1, p2)

    return ufl_min(ufl_max(p, minimum), maximum)
    # using Min/Max, seems to break shape Pie?
    return Min(Max(p, minimum), maximum)


def ufl_cross(p1, p2):
    return p1[0] * p2[1] - p1[1] * p2[0]
