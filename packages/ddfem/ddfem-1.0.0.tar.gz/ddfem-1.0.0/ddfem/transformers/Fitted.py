from functools import reduce

from ufl import Min, conditional, eq, grad

from ..boundary import BndFlux_c, BndFlux_v, BndValue, boundary_validation
from .transformer_base import transformer_base


def Fitted(OriginalModel, domainDescription):
    Model = transformer_base(OriginalModel, domainDescription)

    class Fitted(Model):
        def sigma(t, x, U, DU=None):
            if DU:
                return DU
            return grad(U)

        boundary = Model.BT.physical
        bndSDFs = {k: Model.domain.bndSDFs(k) for k in Model.BT.diffuse.keys()}

        def make_boundary_function(key, mv, bndSDFs=bndSDFs):
            sdf = bndSDFs[key]
            closest_sdf = lambda x: reduce(
                Min,
                ([abs(v(x)) for b, v in bndSDFs.items()]),
            )

            boundary_map = lambda x: conditional(eq(closest_sdf(x), abs(sdf(x))), 1, 0)

            if isinstance(mv, BndFlux_v):
                return BndFlux_v(
                    lambda t, x, u, DU, n: boundary_map(x) * mv(t, x, u, DU, n),
                )

            elif isinstance(mv, BndFlux_c):
                return BndFlux_c(
                    lambda t, x, u, n: boundary_map(x) * mv(t, x, u, n),
                )

        boundary_flux_cs, boundary_flux_vs, boundary_values = boundary_validation(
            Model, override_boundary_dict=Model.BT.diffuse
        )

        def make_boundary_conditional(key, bndSDFs=bndSDFs, tol=0.01):
            sdf = bndSDFs[key]
            return lambda x: abs(sdf(x)) < tol

        for bc_key, bc_value in boundary_values.items():
            boundary[make_boundary_conditional(bc_key)] = bc_value

        for bc_key in boundary_flux_cs.keys() | boundary_flux_vs.keys():
            if bc_key in boundary_flux_cs and bc_key in boundary_flux_vs:
                af = make_boundary_function(bc_key, boundary_flux_cs[bc_key])
                df = make_boundary_function(bc_key, boundary_flux_vs[bc_key])
                boundary[make_boundary_conditional(bc_key)] = [af, df]

            elif bc_key in boundary_flux_cs and bc_key not in boundary_flux_vs:
                af = make_boundary_function(bc_key, boundary_flux_cs[bc_key])
                boundary[make_boundary_conditional(bc_key)] = af

            elif bc_key not in boundary_flux_cs and bc_key in boundary_flux_vs:
                df = make_boundary_function(bc_key, boundary_flux_vs[bc_key])
                boundary[make_boundary_conditional(bc_key)] = df
            else:
                raise ValueError()

    return Fitted
