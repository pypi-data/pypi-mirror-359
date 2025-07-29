"""
Extensions of pyplot functionality. Main differences / modifications are

* :func:`kwplot.mpl_core.figure` can be called with a specific figure number, plot number, and other attributes like if it needs to be cleared or not.

* :func:`kwplot.mpl_core.imshow` uses simpler defaults for showing image data. Extra normalization is only added if requested.

* :func:`kwplot.mpl_core.close_figures` This function closes all open figures, which can be helpful in interactive sessions.


"""
import numpy as np
import ubelt as ub
import matplotlib as mpl
import matplotlib.figure  # NOQA


try:
    from typing import NamedTuple

    class FigureAxes(NamedTuple):
        """
        Backwards compatible helper for functions that returned a tuple of a
        figure and axes. This lets new code avoid magic numbers when accessing
        one or the other.
        """
        fig : mpl.figure.Figure
        ax : mpl.axes.Axes

except ImportError:
    # Is this needed in 3.8?
    from collections import namedtuple
    FigureAxes = namedtuple('FigureAxes', ['fig', 'ax'])

_BASE_FNUM = 9001


def next_fnum(new_base=None):
    global _BASE_FNUM
    if new_base is not None:
        _BASE_FNUM = new_base
    _BASE_FNUM += 1
    return _BASE_FNUM


def ensure_fnum(fnum):
    if fnum is None:
        return next_fnum()
    return fnum


# import xdev  # NOQA
# @xdev.profile  # NOQA
def figure(fnum=None, pnum=(1, 1, 1), title=None, figtitle=None, doclf=False,
           docla=False, projection=None, **kwargs):
    """
    Creates or activates a matplotlib figure and subplot.

    This function wraps around matplotlib's figure and subplot logic to
    streamline subplot creation using a tuple-based or integer-based `pnum`
    specification.  It supports clearing figures (`doclf`) or clearing specific
    axes (`docla`), and can assign titles to either the current subplot or the
    entire figure.

    Args:
        fnum (int | None): Figure number to create or activate. If None, uses the current figure.

        pnum (int | str | tuple): Subplot specifier, interpreted as (nRows, nCols, index),
            e.g., (2, 2, 1) or 221. Can also be a string like '221'.
            Supports advanced formats like slices or lists for multi-cell spanning.

        title (str | None): Title for the active subplot axis. Defaults to None.

        figtitle (str | None): Title for the entire figure (`suptitle`). Defaults to None.

        doclf (bool): If True, clears the figure contents using `fig.clf()`. Defaults to False.

        docla (bool): If True, clears the subplot axis using `ax.cla()` before plotting. Defaults to False.

        projection (str or None): Optional matplotlib projection (e.g., '3d'). Defaults to None.

        **kwargs: Currently unused, reserved for future extension.

    Returns:
        mpl.figure.Figure: fig

    References:
        http://matplotlib.org/users/gridspec.html

    Example:
        >>> import kwplot
        >>> kwplot.autompl()
        >>> import matplotlib.pyplot as plt
        >>> fnum = 1
        >>> fig = figure(fnum, (2, 2, 1))
        >>> fig.gca().text(0.5, 0.5, "ax1", va="center", ha="center")
        >>> fig = figure(fnum, (2, 2, 2))
        >>> fig.gca().text(0.5, 0.5, "ax2", va="center", ha="center")
        >>> show_if_requested()

    Example:
        >>> import kwplot
        >>> kwplot.autompl()
        >>> import matplotlib.pyplot as plt
        >>> fnum = 1
        >>> fig = figure(fnum, (2, 2, 1))
        >>> fig.gca().text(0.5, 0.5, "ax1", va="center", ha="center")
        >>> fig = figure(fnum, (2, 2, 2))
        >>> fig.gca().text(0.5, 0.5, "ax2", va="center", ha="center")
        >>> fig = figure(fnum, (2, 4, (1, slice(1, None))))
        >>> fig.gca().text(0.5, 0.5, "ax3", va="center", ha="center")
        >>> show_if_requested()
    """
    fig = _ensure_fig(fnum)
    if doclf:
        fig.clf()
    if pnum is not None:
        _setup_subfigure(fig, pnum, docla, projection)
    # Set the title / figtitle
    if title is not None:
        ax = fig.gca()
        ax.set_title(title)
    if figtitle is not None:
        fig.suptitle(figtitle)
    return fig


def _ensure_fig(fnum):
    import matplotlib.pyplot as plt
    if fnum is None:
        try:
            fig = plt.gcf()
        except Exception:
            fig = plt.figure()
    else:
        try:
            fig = plt.figure(fnum)
        except Exception:
            fig = plt.gcf()
    return fig


def _convert_pnum_int_to_tup(int_pnum):
    # Convert pnum to tuple format if in integer format
    nr = int_pnum // 100
    nc = int_pnum // 10 - (nr * 10)
    px = int_pnum - (nr * 100) - (nc * 10)
    pnum = (nr, nc, px)
    return pnum


def _pnum_to_subspec(pnum):
    import matplotlib.gridspec as gridspec
    if isinstance(pnum, str):
        pnum = list(pnum)
    nrow, ncols, plotnum = pnum
    # if kwargs.get('use_gridspec', True):
    # Convert old pnums to gridspec
    gs = gridspec.GridSpec(nrow, ncols)
    if isinstance(plotnum, (tuple, slice, list)):
        subspec = gs[plotnum]
    else:
        subspec = gs[plotnum - 1]
    return (subspec,)


def _setup_subfigure(fig, pnum, docla, projection):
    import matplotlib.pyplot as plt
    if isinstance(pnum, int):
        pnum = _convert_pnum_int_to_tup(pnum)
    axes_list = fig.get_axes()
    if docla or len(axes_list) == 0:
        if pnum is not None:
            assert pnum[0] > 0, 'nRows must be > 0: pnum=%r' % (pnum,)
            assert pnum[1] > 0, 'nCols must be > 0: pnum=%r' % (pnum,)
            subspec = _pnum_to_subspec(pnum)
            ax = fig.add_subplot(*subspec, projection=projection)
            if len(axes_list) > 0:
                ax.cla()
        else:
            ax = fig.gca()
    else:
        if pnum is not None:
            subspec = _pnum_to_subspec(pnum)
            ax = plt.subplot(*subspec)
        else:
            ax = fig.gca()


_LEGEND_LOCATION = {
    'upper right':  1,
    'upper left':   2,
    'lower left':   3,
    'lower right':  4,
    'right':        5,
    'center left':  6,
    'center right': 7,
    'lower center': 8,
    'upper center': 9,
    'center':      10,
}


def legend(loc='best', fontproperties=None, size=None, fc='w', alpha=1,
           ax=None, handles=None):
    r"""
    Args:
        loc (str): (default = 'best') one of 'best',
            'upper right', 'upper left', 'lower left', 'lower right',
            'right', 'center left', 'center right', 'lower center', or
            'upper center'.

        fontproperties (None): (default = None)

        size (None): (default = None)

    Ignore:
        >>> # xdoctest: +SKIP
        >>> import kwplot
        >>> kwplot.autompl()
        >>> loc = 'best'
        >>> xdata = np.linspace(-6, 6)
        >>> ydata = np.sin(xdata)
        >>> plt.plot(xdata, ydata, label='sin')
        >>> fontproperties = None
        >>> size = None
        >>> result = legend(loc, fontproperties, size)
        >>> print(result)
        >>> show_if_requested()
    """
    from matplotlib import pyplot as plt
    assert loc in _LEGEND_LOCATION or loc == 'best', (
        'invalid loc. try one of %r' % (_LEGEND_LOCATION,))
    if ax is None:
        ax = plt.gca()
    if fontproperties is None:
        prop = {}
        if size is not None:
            prop['size'] = size
        # prop['weight'] = 'normal'
        # prop['family'] = 'sans-serif'
    else:
        prop = fontproperties
    legendkw = dict(loc=loc)
    if prop:
        legendkw['prop'] = prop
    if handles is not None:
        legendkw['handles'] = handles
    legend = ax.legend(**legendkw)
    if legend:
        legend.get_frame().set_fc(fc)
        legend.get_frame().set_alpha(alpha)


def show_if_requested(N=1):
    """
    Used at the end of tests. Handles command line arguments for saving figures

    Referencse:
        http://stackoverflow.com/questions/4325733/save-a-subplot-in-matplotlib

    """
    import matplotlib.pyplot as plt
    # Process figures adjustments from command line before a show or a save

    # save_parts = ub.argflag('--saveparts')
    # fpath_ = ub.argval('--save', default=None)
    # if fpath_ is None:
    #     fpath_ = ub.argval('--saveparts', default=None)
    #     if fpath_ is not None:
    #         save_parts = True

    # if save_parts:
    #     raise NotImplementedError
    # if fpath_ is not None:
    #     raise NotImplementedError

    if ub.argflag('--nointeract'):
        return

    if ub.argflag('--show'):
        plt.show()


def imshow(img,
           fnum=None, pnum=None,
           xlabel=None, title=None, figtitle=None, ax=None,
           norm=None, cmap=None, data_colorbar=False,
           colorspace='rgb',
           interpolation='nearest', alpha=None,
           origin_convention="center",
           show_ticks=False, **kwargs):
    r"""
    A wrapper around pyplot.imshow with extra options and slightly modified
    defaults.

    Args:
        img (ndarray): image data. Height, Width, and Channel dimensions
            can either be in standard (H, W, C) format or in (C, H, W) format.
            If C in [3, 4], we assume data is in the rgb / rgba colorspace by
            default.

        colorspace (str): if the data is 3-4 channels, this indicates the
            colorspace 1 channel data is assumed grayscale. 4 channels assumes
            alpha.

        interpolation (str): either nearest (default), bicubic, bilinear

        norm (bool): if True, normalizes the image intensities to fit in a
            colormap.

        cmap (mpl.colors.Colormap | None):
            color map used if data is not starndard image data

        data_colorbar (bool): if True, displays a color scale indicating how
            colors map to image intensities.

        fnum (int | None): figure number

        pnum (tuple | None): plot number

        xlabel (str | None): sets the label for the x axis

        title (str | None): set axes title (if ax is not given)

        figtitle (str | None): set figure title (if ax is not given)

        show_ticks (bool):
            if False, then remove axis coordinate ticks

        origin_convention (str): either "areas" or "points".
            Areas means the center of the top left pixel will be 0.5, 0.5, and
            the corner of that pixel will be at 0, 0.
            Points means that the center of the top left pixel will be 0,0 and
            the corner of that pixel will be at -0.5, -0.5.
            Defaults to "areas".

            TODO: the areas and points names are confusing, can we do better?
            Can we give a good intuition?

        ax (mpl.axes.Axes | None):
            axes to draw on (alternative to fnum and pnum)

        **kwargs: docla, doclf, projection, and other arguments passed to
            :func:`figure`.

    Returns:
        FigureAxes: a tuple containing the figure and axes that was plotted to.

    Note:
        Calling this function will import pyplot if you have not done so
        already. Be sure to setup the backend correctly (e.g. with
        ``kwplot.autompl()``) before calling this function.

    Example:
        >>> # Simple case of showing an image
        >>> import kwplot
        >>> import kwimage
        >>> kwplot.autompl()
        >>> img = kwimage.grab_test_image('carl')
        >>> fig_ax = kwplot.imshow(img)
        >>> print(f'fig_ax={fig_ax}')
        >>> kwplot.show_if_requested()

    Example:
        >>> # High level control over axes coordinates
        >>> import kwplot
        >>> import kwimage
        >>> kwplot.autompl()
        >>> # The origin_convention argument gives control of the coordinates
        >>> # assigned to pixel centers / corners.
        >>> img = kwimage.checkerboard(dsize=(4, 4), num_squares=4)
        >>> img[-1, :] = 0.5  # mark the bottom of the image
        >>> ax1 = kwplot.imshow(img, show_ticks=True,
        >>>                     title='origin_convention="center" (default).\nTL pixel center is 0.0, 0.0',
        >>>                     fnum=1, pnum=(1, 2, 1), origin_convention='center').ax
        >>> ax2 = kwplot.imshow(img, show_ticks=True,
        >>>                     title='origin_convention="corner" (customized).\nTL pixel center is 0.5, 0.5',
        >>>                     fnum=1, pnum=(1, 2, 2), origin_convention='corner').ax
        >>> # Future vectors respect this coordinate system
        >>> ax1.plot([0, 1], [0, 1], '-o')
        >>> ax2.plot([0, 1], [0, 1], '-o')
        >>> # xdoctest: +REQUIRES(--show)
        >>> kwplot.show_if_requested()
    """
    #import matplotlib as mpl
    import matplotlib.pyplot as plt

    if ax is not None:
        fig = ax.figure
        nospecial = True
    else:
        fig = figure(fnum=fnum, pnum=pnum, title=title, figtitle=figtitle, **kwargs)
        ax = fig.gca()
        nospecial = False

    if isinstance(img, str):
        # Allow for path to image to be specified
        img_fpath = img
        import kwimage
        img = kwimage.imread(img_fpath)

    valid_interpolation_choices = ['nearest', 'bicubic', 'bilinear']

    if interpolation not in valid_interpolation_choices:
        raise KeyError(
            'Invalid interpolation choice {}. Can be {}'.format(
                interpolation, valid_interpolation_choices))

    plt_imshow_kwargs = {
        'interpolation': interpolation,
    }
    if alpha is not None:
        plt_imshow_kwargs['alpha'] = alpha

    if norm is not None:
        if norm is True:
            norm = 'linear'
        if isinstance(norm, str):
            norm_choices = {
                'linear': mpl.colors.Normalize,
                'log': mpl.colors.LogNorm,
            }
            try:
                norm = norm_choices[norm]()
            except KeyError:
                raise KeyError('norm={} not in valid choices: {}'.format(
                    norm, list(norm_choices)
                ))
        if not isinstance(norm, mpl.colors.Normalize):
            raise TypeError('norm={} must be an instance of {} or in {}'.format(
                norm, mpl.colors.Normalize, list(norm_choices)))

        plt_imshow_kwargs['norm'] = norm
    else:
        if cmap is None and not nospecial:
            plt_imshow_kwargs['vmin'] = 0
            if img.dtype.kind == 'u':
                plt_imshow_kwargs['vmax'] = 255
            else:
                plt_imshow_kwargs['vmax'] = 1.0

    # Handle tensor chw format in most cases
    try:
        if 'torch' in img.__module__:
            img = img.cpu().data.numpy()
    except Exception:
        pass

    if img.ndim == 3:
        if img.shape[0] == 3 or img.shape[0] == 1:
            if img.shape[2] > 4:
                # probably in chw format
                img = img.transpose(1, 2, 0)

    if origin_convention == 'corner':
        # References:
        # https://stackoverflow.com/questions/49714222/can-matplotlib-imshow-coordinates-start-at-0-instead-of-0-5
        numrows, numcols = img.shape[0:2]
        plt_imshow_kwargs['extent'] = (0, numcols, numrows, 0)
    elif origin_convention == 'center':
        ...  # default case
    else:
        raise KeyError(f'origin_convention={origin_convention}')

    try:
        if len(img.shape) == 3 and (img.shape[2] == 3 or img.shape[2] == 4):
            # img is in a color format
            dst_space = 'rgb'
            import kwimage
            imgRGB = kwimage.convert_colorspace(img, src_space=colorspace,
                                                dst_space=dst_space,
                                                implicit=True)
            if not norm:
                if  imgRGB.dtype.kind == 'f':
                    maxval = imgRGB.max()
                    if maxval > 1.01 and maxval < 256:
                        imgRGB = np.array(imgRGB, dtype=np.uint8)
            cs = ax.imshow(imgRGB, **plt_imshow_kwargs)

        elif len(img.shape) == 2 or (len(img.shape) == 3 and img.shape[2] == 1):
            # img is in grayscale
            if len(img.shape) == 3:
                imgGRAY = img.reshape(img.shape[0:2])
            else:
                imgGRAY = img
            if cmap is None:
                cmap = plt.get_cmap('gray')
            if isinstance(cmap, str):
                cmap = plt.get_cmap(cmap)
            # for some reason gray floats aren't working right
            # if not norm:
            #     if imgGRAY.max() <= 1.01 and imgGRAY.min() >= -1E-9:
            #         imgGRAY = (imgGRAY * 255).astype(np.uint8)
            cs = ax.imshow(imgGRAY, cmap=cmap, **plt_imshow_kwargs)
        else:
            raise AssertionError(
                'Unknown image format. '
                'img.dtype={!r}, img.shape={!r}'.format(
                    img.dtype, img.shape)
            )
    except TypeError as te:
        print('[imshow] imshow ERROR %r' % (te,))
        raise
    except Exception as ex:
        print('!!! WARNING !!!')
        print('[imshow] type(img) = %r' % type(img))
        if not isinstance(img, np.ndarray):
            print('!!! ERRROR !!!')
            pass
        print('[imshow] img.dtype = %r' % (img.dtype,))
        print('[imshow] type(img) = %r' % (type(img),))
        print('[imshow] img.shape = %r' % (img.shape,))
        print('[imshow] imshow ERROR %r' % ex)
        raise

    if not show_ticks:
        ax.set_xticks([])
        ax.set_yticks([])

    if data_colorbar:
        # Use the axes to supply the colorbar info
        # Does this mean we can depricate `colorbar`?
        cbar = fig.colorbar(cs)

        if isinstance(norm, mpl.colors.LogNorm):
            # References:
            #    https://github.com/matplotlib/matplotlib/issues/8307
            cbar.ax.yaxis.set_major_locator(mpl.ticker.LogLocator())  # <- Why? See refs
            cbar.set_ticks(cbar.ax.yaxis.get_major_locator().tick_values(
                img.min(), img.max()))

        # scores = np.unique(img.flatten())
        # if cmap is None:
        #     cmap = 'hot'
        # colors = scores_to_color(scores, cmap)
        # colorbar(scores, colors)

    if xlabel is not None:
        ax.set_xlabel(xlabel)

    if figtitle is not None:
        set_figtitle(figtitle)
    return FigureAxes(fig, ax)


def set_figtitle(figtitle, subtitle='', forcefignum=True, incanvas=True,
                 size=None, fontfamily=None, fontweight=None,
                 fig=None):
    r"""
    A wrapper around subtitle that also sets the canvas window title if using a
    Qt backend.

    Args:
        figtitle (str):
        subtitle (str):
        forcefignum (bool): (default = True)
        incanvas (bool): (default = True)
        fontfamily (None): (default = None)
        fontweight (None): (default = None)
        size (None): (default = None)
        fig (None): (default = None)

    CommandLine:
        python -m kwplot.mpl_core set_figtitle --show

    Example:
        >>> # xdoctest: +SKIP
        >>> import kwplot
        >>> kwplot.autompl()
        >>> fig = figure(fnum=1, doclf=True)
        >>> result = set_figtitle(figtitle='figtitle', fig=fig)
        >>> # xdoctest: +REQUIRES(--show)
        >>> show_if_requested()
    """
    from matplotlib import pyplot as plt
    if figtitle is None:
        figtitle = ''
    if fig is None:
        fig = plt.gcf()
    figtitle = ub.ensure_unicode(figtitle)
    subtitle = ub.ensure_unicode(subtitle)
    if incanvas:
        if subtitle != '':
            subtitle = '\n' + subtitle
        prop = {
            'family': fontfamily,
            'weight': fontweight,
            'size': size,
        }
        prop = {k: v for k, v in prop.items() if v is not None}
        sup = fig.suptitle(figtitle + subtitle)

        if prop:
            fontproperties = sup.get_fontproperties().copy()
            for key, val in prop.items():
                getattr(fontproperties, 'set_' + key)(val)
            sup.set_fontproperties(fontproperties)
            # fontproperties = mpl.font_manager.FontProperties(**prop)
    else:
        fig.suptitle('')
    # Set title in the window
    window_figtitle = ('fig(%d) ' % fig.number) + figtitle
    window_figtitle = window_figtitle.replace('\n', ' ')
    if fig.canvas.manager is not None:
        fig.canvas.manager.set_window_title(window_figtitle)


def distinct_markers(num, style='astrisk', total=None, offset=0):
    """
    Creates distinct marker codes (as best as possible)

    Args:
        num (int): number of markers to make
        style (str): mplt style code
        total (int): alternative to num
        offset (float): angle offset

    Returns:
        List[Tuple]: marker codes

    Example:
        >>> import kwplot
        >>> plt = kwplot.autoplt()
        >>> style = 'astrisk'
        >>> marker_list = kwplot.distinct_markers(10, style)
        >>> print('marker_list = {}'.format(ub.repr2(marker_list, nl=1)))
        >>> x_data = np.arange(0, 3)
        >>> for count, (marker) in enumerate(marker_list):
        >>>     plt.plot(x_data, [count] * len(x_data), marker=marker, markersize=10, linestyle='', label=str(marker))
        >>> plt.legend()
        >>> kwplot.show_if_requested()
    """
    num_sides = 3
    style_num = {
        'astrisk': 2,
        'star': 1,
        'polygon': 0,
        'circle': 3
    }[style]
    if total is None:
        total = num
    total_degrees = 360.0 / num_sides
    angles = [total_degrees * (count + offset) / total for count in range(num)]
    marker_list = [(num_sides, style_num,  angle) for angle in angles]
    return marker_list


def distinct_colors(N, brightness=.878, randomize=True, hue_range=(0.0, 1.0), cmap_seed=None):
    r"""
    DEPRECATED in favor of :func:`kwimage.Color.distinct`

    Args:
        N (int):
        brightness (float):

    Returns:
        list: RGB_tuples

    TODO:
        - [ ] This is VERY old code that needs massive cleanup.
        - [ ] Favor :func:`kwimage.Color.distinct` instead.

    CommandLine:
        python -m color_funcs --test-distinct_colors --N 2 --show --hue-range=0.05,.95
        python -m color_funcs --test-distinct_colors --N 3 --show --hue-range=0.05,.95
        python -m color_funcs --test-distinct_colors --N 4 --show --hue-range=0.05,.95
        python -m .color_funcs --test-distinct_colors --N 3 --show --no-randomize
        python -m .color_funcs --test-distinct_colors --N 4 --show --no-randomize
        python -m .color_funcs --test-distinct_colors --N 6 --show --no-randomize
        python -m .color_funcs --test-distinct_colors --N 20 --show

    References:
        http://blog.jianhuashao.com/2011/09/generate-n-distinct-colors.html

    CommandLine:
        python -m .color_funcs --exec-distinct_colors --show
        python -m .color_funcs --exec-distinct_colors --show --no-randomize --N 50
        python -m .color_funcs --exec-distinct_colors --show --cmap_seed=foobar

    Ignore:
        >>> # xdoctest: +SKIP
        >>> import kwplot
        >>> kwplot.autompl()
        >>> N = ub.smartcast(ub.get_argval('--N', default=2), int)  # FIXME
        >>> randomize = not ub.argflag('--no-randomize')
        >>> brightness = 0.878
        >>> # execute function
        >>> cmap_seed = ub.get_argval('--cmap_seed', default=None)
        >>> hue_range = ub.smartcast(ub.get_argval('--hue-range', default=(0.00, 1.0)), list)  #FIXME
        >>> RGB_tuples = distinct_colors(N, brightness, randomize, hue_range, cmap_seed=cmap_seed)
        >>> # verify results
        >>> assert len(RGB_tuples) == N
        >>> result = str(RGB_tuples)
        >>> print(result)
        >>> # xdoctest: +REQUIRES(--show)
        >>> color_list = RGB_tuples
        >>> testshow_colors(color_list)
        >>> show_if_requested()
    """
    # TODO: Add sin wave modulation to the sat and value
    # HACK for white figures
    from matplotlib import pyplot as plt
    import colorsys
    remove_yellow = True

    use_jet = False
    if use_jet:
        cmap = plt.cm.jet
        RGB_tuples = list(map(tuple, cmap(np.linspace(0, 1, N))))
    elif cmap_seed is not None:
        # Randomized map based on a seed
        #cmap_ = 'Set1'
        #cmap_ = 'Dark2'
        choices = [
            #'Set1', 'Dark2',
            'jet',
            #'gist_rainbow',
            #'rainbow',
            #'gnuplot',
            #'Accent'
        ]
        cmap_hack = ub.argval('--cmap-hack', default=None)
        ncolor_hack = ub.argval('--ncolor-hack', default=None)
        if cmap_hack is not None:
            choices = [cmap_hack]
        if ncolor_hack is not None:
            N = int(ncolor_hack)
            N_ = N
        seed = sum(list(map(ord, ub.hash_data(cmap_seed))))
        rng = np.random.RandomState(seed + 48930)
        cmap_str = rng.choice(choices, 1)[0]
        #print('cmap_str = %r' % (cmap_str,))
        cmap = plt.cm.get_cmap(cmap_str)
        #.hashstr27(cmap_seed)
        #cmap_seed = 0
        #pass
        jitter = (rng.randn(N) / (rng.randn(100).max() / 2)).clip(-1, 1) * ((1 / (N ** 2)))
        range_ = np.linspace(0, 1, N, endpoint=False)
        #print('range_ = %r' % (range_,))
        range_ = range_ + jitter
        #print('range_ = %r' % (range_,))
        while not (np.all(range_ >= 0) and np.all(range_ <= 1)):
            range_[range_ < 0] = np.abs(range_[range_ < 0] )
            range_[range_ > 1] = 2 - range_[range_ > 1]
        #print('range_ = %r' % (range_,))
        shift = rng.rand()
        range_ = (range_ + shift) % 1
        #print('jitter = %r' % (jitter,))
        #print('shift = %r' % (shift,))
        #print('range_ = %r' % (range_,))
        if ncolor_hack is not None:
            range_ = range_[0:N_]
        RGB_tuples = list(map(tuple, cmap(range_)))
    else:
        sat = brightness
        val = brightness
        hmin, hmax = hue_range
        if remove_yellow:
            hue_skips = [(.13, .24)]
        else:
            hue_skips = []
        hue_skip_ranges = [_[1] - _[0] for _ in hue_skips]
        total_skip = sum(hue_skip_ranges)
        hmax_ = hmax - total_skip
        hue_list = np.linspace(hmin, hmax_, N, endpoint=False, dtype=float)
        # Remove colors (like hard to see yellows) in specified ranges
        for skip, range_ in zip(hue_skips, hue_skip_ranges):
            hue_list = [hue if hue <= skip[0] else hue + range_ for hue in hue_list]
        HSV_tuples = [(hue, sat, val) for hue in hue_list]
        RGB_tuples = [colorsys.hsv_to_rgb(*x) for x in HSV_tuples]
    if randomize:
        import kwarray
        rng = kwarray.ensure_rng(rng=0)
        rng.shuffle(RGB_tuples)
    return RGB_tuples


def phantom_legend(label_to_color=None, label_to_attrs=None, mode='line', ax=None, legend_id=None, loc=0):
    """
    Creates a legend on an axis based on a label-to-color map.

    Args:
        label_to_color (Dict[str, kwimage.Color]):
            mapping from string label to the color.

        label_to_attrs (Dict[str, Dict[str, Any]]):
            mapping from a string label to attributes corresponding to
            plt.Line2D or plt.Circle

            NEW: Prefer this.

    TODO:
        - [ ] More docs and ensure this exists in the right place
    """
    import kwplot
    import kwimage
    import ubelt as ub
    plt = kwplot.autoplt()

    if ax is None:
        ax = plt.gca()

    _phantom_legends = getattr(ax, '_phantom_legends', None)
    if _phantom_legends is None:
        _phantom_legends = ax._phantom_legends = ub.ddict(dict)

    phantom = _phantom_legends[legend_id]
    handles = phantom['handles'] = []
    handles.clear()

    alpha = 1.0
    legend_rows = []
    if isinstance(label_to_color, dict):
        legend_rows = [
            {'label': k, 'color': c, 'type': mode, 'alpha': alpha}
            for k, c in label_to_color.items()]
    else:
        legend_rows = label_to_color

    if label_to_attrs is not None:
        legend_rows = []
        for label, attrs in label_to_attrs.items():
            legend_rows.append(ub.udict({
                'label': label, 'type': mode, 'alpha': alpha,
            }) | attrs)

    for row in legend_rows:
        row_type = row.pop('type')
        color = row['color']
        color = kwimage.Color(color).as01()
        row['color'] = color
        if row_type == 'line':
            phantom_actor = plt.Line2D((0, 0), (1, 1), **row)
        elif row_type == 'circle':
            row['fc'] = row.pop('color')
            phantom_actor = plt.Circle((0, 0), 1, **row)
        elif row_type == 'star':
            row['mfc'] = row.pop('color')
            row['mec'] = row['mfc']
            # https://stackoverflow.com/questions/68120813/how-to-have-a-poligon-in-the-legend
            phantom_actor = plt.Line2D([0], [0], linestyle='none', marker='*', **row)
            # label='blue square'),
            # # not sure why this isn't working
            # star_xy = np.array([[-3.63271264e-01, -1.18033989e-01],
            #                     [-9.51056516e-01,  3.09016994e-01],
            #                     [-2.24513988e-01,  3.09016994e-01],
            #                     [ 6.12323400e-17,  1.00000000e+00],
            #                     [ 2.24513988e-01,  3.09016994e-01],
            #                     [ 9.51056516e-01,  3.09016994e-01],
            #                     [ 3.63271264e-01, -1.18033989e-01],
            #                     [ 5.87785252e-01, -8.09016994e-01],
            #                     [-3.03598782e-17, -3.81966011e-01],
            #                     [-5.87785252e-01, -8.09016994e-01],
            #                     [-3.63271264e-01, -1.18033989e-01]])
            # phantom_actor = plt.Polygon(xy=star_xy, **row)
        else:
            raise KeyError
        handles.append(phantom_actor)

    legend_artist = ax.legend(handles=handles, loc=loc)
    phantom['artist'] = legend_artist

    # Re-add other legends
    for _phantom in _phantom_legends.values():
        artist = _phantom['artist']
        if artist is not legend_artist:
            ax.add_artist(artist)


def close_figures(figures=None):
    """
    Close specified figures. If no figures are specified, close all figure.

    Args:
        figures (List[mpl.figure.Figure]): list of figures to close
    """
    if figures is None:
        figures = all_figures()
    for fig in figures:
        # TODO: make work for more than QT
        if hasattr(fig.canvas.manager, 'window'):
            try:
                qwin = fig.canvas.manager.window
            except AttributeError:
                qwin = fig.canvas.window()
            qwin.close()
        elif hasattr(fig.canvas, 'window'):
            qwin = fig.canvas.window()
            qwin.close()
        else:
            from matplotlib import pyplot as plt
            plt.close(fig)


def all_figures():
    """
    Return a list of all open figures

    Returns:
        List[mpl.figure.Figure]: list of all figures
    """
    #import matplotlib as mpl
    manager_list = mpl._pylab_helpers.Gcf.get_all_fig_managers()
    all_figures = []
    # Make sure you dont show figures that this module closed
    for manager in manager_list:
        try:
            fig = manager.canvas.figure
        except AttributeError:
            continue
        all_figures.append(fig)
    # Return all the figures sorted by their number
    all_figures = sorted(all_figures, key=lambda fig: fig.number)
    return all_figures
