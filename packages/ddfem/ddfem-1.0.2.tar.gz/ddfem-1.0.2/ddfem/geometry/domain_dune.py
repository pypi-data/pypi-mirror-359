import time

import dune.fem
import dune.grid

from .domain import Domain


class DomainDune(Domain):
    def __init__(self, omega, x, gridView):
        super().__init__(omega)
        self.x = x
        self.gridView = gridView

        self._phi = None
        self._bndProj = None
        self._extProj = None
        self._bndProjSDFs = {}

        self.fullSDF = self.gridFunction(self.omega(self.x), name="full-sdf")

    def gridFunction(self, expr, name):
        start_ = time.time()
        gf = dune.fem.function.gridFunction(expr, name=name, gridView=self.gridView)
        print(f"{name} setup: {time.time() - start_}")
        return gf

    def phi(self, x):
        if self._phi is None:
            p = super().phi(self.x)
            self._phi = self.gridFunction(p, "phidomain")

        return self._phi

    def boundary_projection(self, x):
        if self._bndProj is None:
            p = super().boundary_projection(self.x)
            self._bndProj = self.gridFunction(p, "bndproj")

        return self._bndProj

    def external_projection(self, x):
        if self._extProj is None:
            p = super().external_projection(self.x)
            self._extProj = self.gridFunction(p, "extproj")

        return self._extProj

    def generate_projSDF(self, sdf):
        projSDF = self._bndProjSDFs.get(sdf.name)
        if projSDF is None:
            projSDF = super().generate_projSDF(sdf)
            gf = self.gridFunction(projSDF(self.x), f"sdfproj{sdf.name}")
            self._bndProjSDFs[sdf.name] = lambda x: gf
            projSDF = self._bndProjSDFs[sdf.name]
        return projSDF

    def adapt(self, level, lowerTol=-0.1, upperTol=0.1):
        for _ in range(level):

            def mark(e):
                v = self.fullSDF(e, self.gridView.dimension * [1.0 / 3.0])
                return (
                    dune.grid.Marker.refine
                    if v > lowerTol and v < upperTol
                    else dune.grid.Marker.keep
                )

            self.gridView.hierarchicalGrid.adapt(mark)
            print(self.gridView.size(0))
            lowerTol /= 2
            upperTol /= 2

    def _filter(self, tolerance=1):
        sd = self.fullSDF
        tol = tolerance  # * self.epsilon.value: issue here with epsilon being a UFL expression due to CSG approach
        phiFilter = (
            lambda e: sd(e, self.gridView.dimension * [1.0 / 3.0]) < tol
        )  # bary needs fixing for squares
        return dune.fem.view.filteredGridView(
            self.gridView, phiFilter, domainId=1, useFilteredIndexSet=True
        )
