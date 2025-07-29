"""
Helper for making 3D plots
"""


def plot_surface3d(xgrid, ygrid, zdata, xlabel=None, ylabel=None, zlabel=None,
                   wire=False, mode=None, contour=False, rstride=1, cstride=1,
                   pnum=None, labelkw=None, xlabelkw=None, ylabelkw=None,
                   zlabelkw=None, titlekw=None, *args, **kwargs):
    r"""
    References:
        https://matplotlib.org/2.0.2/mpl_toolkits/mplot3d/tutorial.html

    Example:
        >>> # xdoctest: +SKIP
        >>> import kwplot
        >>> import matplotlib as mpl
        >>> import kwimage
        >>> shape=(19, 19)
        >>> sigma1, sigma2 = 2.0, 1.0
        >>> ybasis = np.arange(shape[0])
        >>> xbasis = np.arange(shape[1])
        >>> xgrid, ygrid = np.meshgrid(xbasis, ybasis)
        >>> sigma = [sigma1, sigma2]
        >>> gausspatch = kwimage.gaussian_patch(shape, sigma=sigma)
        >>> title = 'ksize={!r}, sigma={!r}'.format(shape, (sigma1, sigma2))
        >>> kwplot.plot_surface3d(xgrid, ygrid, gausspatch, rstride=1, cstride=1,
        >>>                   cmap=mpl.cm.coolwarm, title=title)
        >>> kwplot.show_if_requested()
    """
    if titlekw is None:
        titlekw = {}
    if labelkw is None:
        labelkw = {}
    if xlabelkw is None:
        xlabelkw = labelkw.copy()
    if ylabelkw is None:
        ylabelkw = labelkw.copy()
    if zlabelkw is None:
        zlabelkw = labelkw.copy()
    from mpl_toolkits.mplot3d import Axes3D  # NOQA
    import matplotlib.pyplot as plt
    import matplotlib as mpl

    cmap = kwargs.get('cmap', 'magma')  # cm.coolwarm)
    if isinstance(cmap, str):
        if cmap == 'magma':
            kwargs['cmap'] = cmap = mpl.cm.magma
    if pnum is None:
        try:
            ax = plt.gca(projection='3d')
        except Exception:
            fig = plt.gcf()
            ax = fig.add_subplot(projection='3d')
            # ax = Axes3D(fig)
    else:
        fig = plt.gcf()
        #print('pnum = %r' % (pnum,))
        ax = fig.add_subplot(*pnum, projection='3d')
    title = kwargs.pop('title', None)
    if mode is None:
        mode = 'wire' if wire else 'surface'

    if len(xgrid.shape) == 1:
        # TODO: if we are given long-form data points can we quickly check and
        # reshape to the necessary grid
        pass
        # maybe use ax.scatter3D

    if mode == 'wire':
        ax.plot_wireframe(xgrid, ygrid, zdata, rstride=rstride,
                          cstride=cstride, *args, **kwargs)
        #ax.contour(xgrid, ygrid, zdata, rstride=rstride, cstride=cstride,
        #extend3d=True, *args, **kwargs)
    elif mode == 'surface' :
        ax.plot_surface(xgrid, ygrid, zdata, rstride=rstride, cstride=cstride,
                        linewidth=.1, *args, **kwargs)
    else:
        raise NotImplementedError('mode=%r' % (mode,))
    if contour:
        import matplotlib.cm as cm
        xoffset = xgrid.min() - ((xgrid.max() - xgrid.min()) * .1)
        yoffset = ygrid.max() + ((ygrid.max() - ygrid.min()) * .1)
        zoffset = zdata.min() - ((zdata.max() - zdata.min()) * .1)
        cmap = kwargs.get('cmap', cm.coolwarm)
        ax.contour(xgrid, ygrid, zdata, zdir='x', offset=xoffset, cmap=cmap)
        ax.contour(xgrid, ygrid, zdata, zdir='y', offset=yoffset, cmap=cmap)
        ax.contour(xgrid, ygrid, zdata, zdir='z', offset=zoffset, cmap=cmap)
        #ax.plot_trisurf(xgrid.flatten(), ygrid.flatten(), zdata.flatten(), *args, **kwargs)
    if title is not None:
        ax.set_title(title, **titlekw)
    if xlabel is not None:
        ax.set_xlabel(xlabel, **xlabelkw)
    if ylabel is not None:
        ax.set_ylabel(ylabel, **ylabelkw)
    if zlabel is not None:
        ax.set_zlabel(zlabel, **zlabelkw)
    return ax


def plot_points3d(xgrid, ygrid, zdata, xlabel=None, ylabel=None, zlabel=None,
                  mode=None, pnum=None, labelkw=None, xlabelkw=None,
                  ylabelkw=None, zlabelkw=None, titlekw=None, *args, **kwargs):
    r"""
    References:
        http://matplotlib.org/mpl_toolkits/mplot3d/tutorial.html

    Example:
        >>> # DISABLE_DOCTEST
        >>> import kwplot
        >>> import matplotlib as mpl
        >>> import kwimage
        >>> shape=(19, 19)
        >>> sigma1, sigma2 = 2.0, 1.0
        >>> ybasis = np.arange(shape[0])
        >>> xbasis = np.arange(shape[1])
        >>> xgrid, ygrid = np.meshgrid(xbasis, ybasis)
        >>> sigma = [sigma1, sigma2]
        >>> gausspatch = kwimage.gaussian_patch(shape, sigma=sigma)
        >>> title = 'ksize={!r}, sigma={!r}'.format(shape, (sigma1, sigma2))
        >>> plot_points3d(xgrid.ravel(), ygrid.ravel(), gausspatch.ravel(),
        >>>                      cmap=mpl.cm.coolwarm, title=title)
        >>> kwplot.show_if_requested()
    """
    if titlekw is None:
        titlekw = {}
    if labelkw is None:
        labelkw = {}
    if xlabelkw is None:
        xlabelkw = labelkw.copy()
    if ylabelkw is None:
        ylabelkw = labelkw.copy()
    if zlabelkw is None:
        zlabelkw = labelkw.copy()
    from mpl_toolkits.mplot3d import Axes3D  # NOQA
    import matplotlib.pyplot as plt
    import matplotlib as mpl

    cmap = kwargs.get('cmap', 'magma')  # cm.coolwarm)
    if isinstance(cmap, str):
        if cmap == 'magma':
            kwargs['cmap'] = cmap = mpl.cm.magma
    if pnum is None:
        try:
            ax = plt.gca(projection='3d')
        except Exception:
            fig = plt.gcf()
            ax = fig.add_subplot(projection='3d')
            # ax = Axes3D(fig)
    else:
        fig = plt.gcf()
        #print('pnum = %r' % (pnum,))
        ax = fig.add_subplot(*pnum, projection='3d')
    title = kwargs.pop('title', None)
    if mode is None:
        mode = 'points'

    if len(xgrid.shape) == 1:
        # TODO: if we are given long-form data points can we quickly check and
        # reshape to the necessary grid
        pass
        # maybe use ax.scatter3D

    if mode == 'line':
        ax.plot(xgrid, ygrid, zdata, *args, **kwargs)
        #ax.contour(xgrid, ygrid, zdata, rstride=rstride, cstride=cstride,
        #extend3d=True, *args, **kwargs)
    elif mode == 'points':
        ax.scatter(xgrid, ygrid, zdata, linewidth=.1, *args, **kwargs)
    else:
        raise NotImplementedError('mode=%r' % (mode,))
    if title is not None:
        ax.set_title(title, **titlekw)
    if xlabel is not None:
        ax.set_xlabel(xlabel, **xlabelkw)
    if ylabel is not None:
        ax.set_ylabel(ylabel, **ylabelkw)
    if zlabel is not None:
        ax.set_zlabel(zlabel, **zlabelkw)
    return ax
