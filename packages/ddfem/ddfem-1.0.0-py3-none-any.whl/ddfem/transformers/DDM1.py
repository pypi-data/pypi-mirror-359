from ufl import grad, zero

from .transformer_base import transformer_base


def DDM1(OriginalModel, domainDescription):
    Model = transformer_base(OriginalModel, domainDescription)

    class DDModel(Model):
        def sigma(t, x, U, DU=None):
            if DU:
                return DU
            return grad(U)

        def S_e_source(t, x, U, DU):
            return DDModel.phi(x) * Model.S_e(t, x, U, DDModel.sigma(t, x, U, DU))

        def S_e_convection(t, x, U, DU):
            return DDModel.BT.BndFlux_cExt(t, x, U)

        if hasattr(Model, "S_e") and hasattr(Model, "F_c"):
            print("DDM1: S_e and F_c")

            def S_e(t, x, U, DU):
                return DDModel.S_e_source(t, x, U, DU) + DDModel.S_e_convection(
                    t, x, U, DU
                )

        elif hasattr(Model, "S_e"):
            print("DDM1: S_e")

            def S_e(t, x, U, DU):
                return DDModel.S_e_source(t, x, U, DU)

        elif hasattr(Model, "F_c"):
            print("DDM1: F_c")

            def S_e(t, x, U, DU):
                return DDModel.S_e_convection(t, x, U, DU)

        def S_i_stability(t, x, U, DU):
            return -Model.stabFactor * (
                DDModel.BT.jumpV(t, x, U) * (1 - DDModel.phi(x)) / (DDModel.epsilon**3)
            )

        def S_i_source(t, x, U, DU):
            return DDModel.phi(x) * Model.S_i(t, x, U, DDModel.sigma(t, x, U, DU))

        def S_i_diffusion(t, x, U, DU):
            if DDModel.BT.BndFlux_vExt is not None:
                diffusion = DDModel.BT.BndFlux_vExt(t, x, U, DU)
            else:
                diffusion = zero(U.ufl_shape)
            return diffusion

        if hasattr(Model, "S_i") and hasattr(Model, "F_v"):
            print("DDM1: S_i and F_v")

            def S_i(t, x, U, DU):
                return (
                    DDModel.S_i_stability(t, x, U, DU)
                    + DDModel.S_i_source(t, x, U, DU)
                    + DDModel.S_i_diffusion(t, x, U, DU)
                )

        elif hasattr(Model, "F_v"):
            print("DDM1: F_v")

            def S_i(t, x, U, DU):
                return DDModel.S_i_stability(t, x, U, DU) + DDModel.S_i_diffusion(
                    t, x, U, DU
                )

        elif hasattr(Model, "S_i"):
            print("DDM1: S_i")

            def S_i(t, x, U, DU):
                return DDModel.S_i_stability(t, x, U, DU) + DDModel.S_i_source(
                    t, x, U, DU
                )

        if hasattr(Model, "F_c"):
            print("DDM1: F_c")

            def F_c(t, x, U):
                return DDModel.phi(x) * Model.F_c(t, x, U)

        if hasattr(Model, "F_v"):
            print("DDM1: F_v")

            def F_v(t, x, U, DU):
                return DDModel.phi(x) * Model.F_v(t, x, U, DDModel.sigma(t, x, U, DU))

    return DDModel
