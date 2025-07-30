from matplotlib import pyplot as plt
from dune.fem.function import gridFunction
from ufl import SpatialCoordinate, triangle

def plotSolution(domain,uh,figsize, **kwargs):
    x = SpatialCoordinate(triangle)
    fig, axs = plt.subplots(1,2, figsize=[2*figsize[0],figsize[1]])
    uh.plot(figure=(fig,axs[0]),**kwargs)
    gridFunction(uh*domain.chi(x)).plot(figure=(fig,axs[1]),**kwargs)
    for a in axs:
        gridFunction(domain.phi(x), gridView=uh.space.gridView).plot(
             onlyContours=True,contours=[0.5],gridLines=None,
             contourWidth=2, contourColor="black", figure=(fig,a))
