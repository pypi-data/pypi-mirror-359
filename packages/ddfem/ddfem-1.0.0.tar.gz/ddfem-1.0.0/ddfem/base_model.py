import inspect

import ufl
from ufl import as_matrix, as_vector, diff, dot, inner, outer, variable, zero
from ufl.algorithms.ad import expand_derivatives
from ufl.algorithms.apply_derivatives import apply_derivatives


class BaseModel:
    boundary = {}

    @staticmethod
    def function(self, *args, **kwargs):
        uh = self._function(*args, **kwargs)
        uh.boundary = self.boundary
        return uh

    # U_t + div[F_c(x,t,U) - F_v(x,t,U,grad[U]) ] = S(x,t,U, grad[U]).

    @classmethod
    def F_c_lin(cls, t, x, U):
        U = variable(U)
        d = diff(cls.F_c(t, x, U), U)
        d = apply_derivatives(expand_derivatives(d))
        return d

    # U.ufl_shape == (1,)
    # F_c(U).ufl_shape == (1, 2,)
    # diff(F_c(U), U).ufl_shape == (1, 2, 1)
    # n.ufl_shape == (2,)
    #
    # s, t = F_c(U).ufl_shape
    # f_c = as_matrix([[dot(d[i, j, :], U) for j in range(t)] for i in range(s)])
    #
    # w, = U.ufl_shape
    # convec = as_vector([dot([f_c[w, :], n) for i in range(w)]) # f_c * n
    #
    # switch order

    @classmethod
    def F_c_lin_mult(cls, t, x, U, n):
        G = cls.F_c_lin(t, x, U)
        # try:
        #     d = dot(G, n)
        #     print("F_c dot")
        #     return d
        # except:
        m, d, m_ = G.ufl_shape
        return as_matrix([[dot(G[i, :, k], n) for k in range(m_)] for i in range(m)])

    @classmethod
    def F_v_lin(cls, t, x, U, DU):
        DU = variable(DU)
        d = diff(cls.F_v(t, x, U, DU), DU)
        d = apply_derivatives(expand_derivatives(d))
        return d

    @classmethod
    def F_v_lin_mult(cls, t, x, U, DU, v):
        G = cls.F_v_lin(t, x, U, DU)
        # try:
        #     d = dot(G, v)
        #     print("F_v dot")
        #     return d
        # except:
        m, d = v.ufl_shape
        return as_matrix(
            [[inner(G[i, k, :, :], v) for k in range(d)] for i in range(m)]
        )

    # avoid issue with variable capturing in lambdas in the for loop below
    # https://www.geeksforgeeks.org/why-do-python-lambda-defined-in-a-loop-with-different-values-all-return-the-same-result/
    def _createV(v, U=None):
        if U is None:
            return lambda t, x, u: v  # classify
        return lambda t, x: v(t, x, U)  # jumpV

    def _createF(v, U=None, DU=None, N=None):
        if U is None and DU is None and N is None:
            return lambda t, x, u, _, n: v(t, x, u, n)  # classify
        elif U and N and DU is None:
            return lambda t, x: v(t, x, U, N)  # jumpAF
        elif U and N and DU:
            return lambda t, x: v(t, x, U, DU, N)  # jumpDF

    @staticmethod
    def classify_boundary(Model):
        boundaryDict = getattr(Model, "boundary_d", {})

        boundaryAFlux = {}  # Fluxes for the advection term
        boundaryDFlux = {}  # Fluxes for the diffusion term
        boundaryValue = {}  # Boundary values for Dirichlet

        hasAdvFlux = hasattr(Model, "F_c")
        hasDiffFlux = hasattr(Model, "F_v")

        for k, f in boundaryDict.items():
            if isinstance(f, (tuple, list)):
                assert (
                    hasAdvFlux and hasDiffFlux
                ), "two boundary fluxes provided but only one bulk flux given"
                boundaryAFlux[k], boundaryDFlux[k] = f
                # (f[0](t, x, u, n), f[1](t, x, u, grad(u), n))

            elif isinstance(f, ufl.core.expr.Expr):
                boundaryValue[k] = BaseModel._createV(f)

            else:
                num_args = len(inspect.signature(f).parameters)

                if num_args == 3:
                    boundaryValue[k] = f  # f(t, x, u)

                elif num_args == 4:
                    if hasAdvFlux and not hasDiffFlux:
                        boundaryAFlux[k] = f  # f(t, x, u, n)
                    elif not hasAdvFlux and hasDiffFlux:
                        boundaryDFlux[k] = BaseModel._createF(f)
                    else:
                        assert not (
                            hasAdvFlux and hasDiffFlux
                        ), "one boundary fluxes provided but two bulk fluxes given"

                else:
                    raise NotImplementedError(f"boundary function {num_args} arguments")

        return boundaryAFlux, boundaryDFlux, boundaryValue

    @staticmethod
    def boundaryTerms(Model, domain):
        boundaryAFlux, boundaryDFlux, boundaryValue = BaseModel.classify_boundary(Model)
        bd_weight = []
        bN_weight = []

        for model_key in boundaryValue.keys():
            phi_i_proj = domain.bndProjSDFs(model_key)
            bd_weight.append(phi_i_proj)

        for model_key in {*boundaryAFlux.keys(), *boundaryDFlux.keys()}:
            phi_i_proj = domain.bndProjSDFs(model_key)
            bN_weight.append(phi_i_proj)

        def total_weight(t, x):
            weight = 1e-10  # tol
            for w in bd_weight + bN_weight:
                weight += w(t, x)
            return weight

        # perhaps switch methods around so that gExt is setup and then
        # jumpD does sum(w)*U - gExt. But then the exception needs to be caught...
        def jumpV(t, x, U, U1=None):
            jdv = zero(U.ufl_shape)

            if U1 is None:
                U1 = U

            for g, w in zip(boundaryValue.values(), bd_weight):
                g_tmp = BaseModel._createV(v=g, U=U)
                g_ext = domain.omega.boundary_extend(g_tmp)

                jdv += w(t, x) * (U1 - g_ext(t, x))

            return jdv / total_weight(t, x)

        if len(boundaryValue) == 0:
            gExt = None
        else:

            def gExt(t, x, U):
                z = zero(U.ufl_shape)
                return -jumpV(t, x, U, z)

        # the models expect to be provided with a unit normal in the boundary fluxes
        def jumpDF(t, x, U, DU, Fv):
            # (sigma.n-gN)*ds(N) = - wN ( sigma.Dphi + gN|Dphi| )
            #   = wN ( (-sigma.Dphi) - gN(t,x,-Dphi/|Dphi|)|Dphi| )
            #   = wN ( sigma.sn - gN(t,x,sn) ) with sn = -Dphi
            jdf = zero(U.ufl_shape)

            fv_scaled = Fv * domain.scaledNormal(x)
            for g, w in zip(boundaryDFlux.values(), bN_weight):
                g_tmp = BaseModel._createF(v=g, U=U, DU=DU, N=domain.scaledNormal(x))
                g_ext = domain.omega.boundary_extend(g_tmp)

                jdf += w(t, x) * (fv_scaled - g_ext(t, x))

            return jdf / total_weight(t, x)

        def jumpAF(t, x, U):
            jda = zero(U.ufl_shape)

            for g, w in zip(boundaryAFlux.values(), bN_weight):
                g_tmp = BaseModel._createF(v=g, U=U, N=domain.scaledNormal(x))
                g_ext = domain.omega.boundary_extend(g_tmp)

                jda += -w(t, x) * g_ext(t, x)

            return jda / total_weight(t, x)

        return jumpV, gExt, jumpDF, jumpAF
