from ufl import conditional, dot, grad, sqrt


class Domain:
    def __init__(self, omega):
        self.omega = omega

    def phi(self, x):
        tol = 1e-10
        return (1 - tol) * self.omega.phi(x) + tol

    def scaled_normal(self, x):
        return -grad(self.phi(x))

    def surface_delta(self, x):
        return sqrt(dot(self.scaled_normal(x), self.scaled_normal(x)))

    def normal(self, x):
        tol = 1e-10
        sd = conditional(self.surface_delta(x) > tol, self.surface_delta(x), tol)
        return self.scaled_normal(x) / sd  # grad(self.omega(x))

    def bndSDFs(self, SDFname):
        sdf = self.omega.search(SDFname)
        if sdf is None:
            raise ValueError(f"No SDF with name {SDFname}")
        return sdf

    def bndProjSDFs(self, SDFname):
        sdf = self.omega.search(SDFname)
        if sdf is None:
            raise ValueError(f"No SDF with name {SDFname}")
        return self.generate_projSDF(sdf)

    def generate_projSDF(self, sdf):
        w = lambda x: sdf.phi(x) * (1 - sdf.phi(x))
        return lambda x: w(self.omega.boundary_projection(x))
