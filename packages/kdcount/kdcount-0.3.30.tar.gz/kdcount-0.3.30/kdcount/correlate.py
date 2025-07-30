"""
Correlation function (pair counting) with KDTree.

Pair counting is the basic algorithm to calculate correlation functions.
Correlation function is a commonly used metric in cosmology to measure
the clustering of matter, or the growth of large scale structure in the universe.

We implement :py:class:`paircount` for pair counting. Since this is a discrete
estimator, the binning is modeled by subclasses of :py:class:`Binning`. For example

- :py:class:`RBinning`
- :py:class:`RmuBinning`
- :py:class:`XYBinning`
- :py:class:`FlatSkyBinning`
- :py:class:`FlatSkyMultipoleBinning`

kdcount takes two types of input data: 'point' and 'field'.

:py:class:`kdcount.models.points` describes data with position and weight. For example, galaxies and
quasars are point data.
point.pos is a row array of the positions of the points; other fields are
used internally.
point.extra is the extra properties that can be used in the Binning. One use
is to exclude the Lyman-alpha pixels and Quasars from the same sightline.

:py:class:`kdcount.models.field` describes a continious field sampled at given positions, each sample
with a weight; a notorious example is the over-flux field in Lyman-alpha forest
it is a proxy of the over-density field sampled along quasar sightlines.

In the Python Interface, to count, one has to define the 'binning' scheme, by
subclassing :py:class:`Binning`. Binning describes a multi-dimension binning
scheme. The dimensions can be derived, for example, the norm of the spatial
separation can be a dimension the same way as the 'x' separation. For example,
see :py:class:`RmuBinning`.


"""
import numpy
import warnings

# local imports
from .models import points, field
from . import utils


def compute_sum_values(i, j, data1, data2):
    """
    Return the sum1_ij and sum2_ij values given
    the input indices and data instances.

    Notes
    -----
    This is called in `Binning.update_sums` to compute
    the `sum1` and `sum2` contributions for indices `(i,j)`

    Parameters
    ----------
    i,j : array_like
        the bin indices for these pairs
    data1, data2 : `points`, `field` instances
        the two `points` or `field` objects

    Returns
    -------
    sum1_ij, sum2_ij : float, array_like (N,...)
        contributions to sum1, sum2 -- either a float or array
        of shape (N, ...) where N is the length of `i`, `j`
    """
    sum1_ij = 1.
    for idx, d in zip([i,j], [data1, data2]):
        if isinstance(d, field): sum1_ij *= d.wvalue[idx]
        elif isinstance(d, points): sum1_ij *= d.weights[idx]
        else:
            raise NotImplementedError("data type not recognized")
    sum2_ij = data1.weights[i] * data2.weights[j]

    return sum1_ij, sum2_ij

class Binning(object):
    """
    Binning of the correlation function. Pairs whose distance is
    within a bin is counted towards the bin.

    Attributes
    ----------
    dims    :  array_like
        internal; descriptors of binning dimensions.
    edges   :  array_like
        edges of bins per dimension


    Class Attributes
    ----------------
    enable_fast_node_count : bool
        if True, use the C implementation of node-node pair counting; this only works for point datasets;
        and does not properly compute the mean coordinates.
        if False, use the Python implementation of point-point pair counting; the supports all features via
        the `digitize` method of the binning object.

    """

    enable_fast_node_count = False # if True, allow using the C implementation of node-node pair counting on point datasets.

    def __init__(self, dims, edges, channels=None):
        """
        Parameters
        ----------
        dims : list
            a list specifying the binning dimension names
        edges : list
            a list giving the bin edges for each dimension
        channels: list, or None
            a list giving the channels to count of per bin; these channels can be, e.g. multipoles.
        """
        if len(dims) != len(edges):
            raise ValueError("size mismatch between number of dimensions and edges supplied")

        self.dims    = dims
        self.Ndim    = len(self.dims)
        self.edges   = edges
        self.channels = channels

        self.centers = []
        for i in range(self.Ndim):
            center = 0.5 * (self.edges[i][1:] + self.edges[i][:-1])
            self.centers.append(center)

        # setup the info we need from the edges
        self._setup()

        if self.Ndim == 1:
            self.edges   = self.edges[0]
            self.centers = self.centers[0]

    def _setup(self):
        """
        Set the binning info we need from the `edges`
        """
        dtype = [('inv', 'f8'), ('min', 'f8'), ('max', 'f8'),('N', 'i4'), ('spacing','object')]
        dtype        = numpy.dtype(dtype)
        self._info   = numpy.empty(self.Ndim, dtype=dtype)
        self.min     = self._info['min']
        self.max     = self._info['max']
        self.N       = self._info['N']
        self.inv     = self._info['inv']
        self.spacing = self._info['spacing']

        for i, dim in enumerate(self.dims):

            self.N[i] = len(self.edges[i])-1
            self.min[i] = self.edges[i][0]
            self.max[i] = self.edges[i][-1]

            # determine the type of spacing
            self.spacing[i] = None
            lin_diff = numpy.diff(self.edges[i])
            with numpy.errstate(divide='ignore', invalid='ignore'):
                log_diff = numpy.diff(numpy.log10(self.edges[i]))
            if numpy.allclose(lin_diff, lin_diff[0]):
                self.spacing[i] = 'linspace'
                self.inv[i] = self.N[i] * 1.0 / (self.max[i] - self.min[i])
            elif numpy.allclose(log_diff, log_diff[0]):
                self.spacing[i] = 'logspace'
                self.inv[i] = self.N[i] * 1.0 / numpy.log10(self.max[i] / self.min[i])

        self.shape = self.N + 2

        # store Rmax
        self.Rmax = self.max[0]


    def linear(self, **paircoords):
        """
        Linearize bin indices.

        This function is called by subclasses. Refer to the source
        code of :py:class:`RBinning` for an example.

        Parameters
        ----------
        args    : list
            a list of bin index, (xi, yi, zi, ..)

        Returns
        -------
        linearlized bin index
        """
        N = len(paircoords[list(paircoords.keys())[0]])
        integer = numpy.empty(N, ('i8', (self.Ndim,))).T

        # do each dimension
        for i, dim in enumerate(self.dims):

            if self.spacing[i] == 'linspace':
                x = paircoords[dim] - self.min[i]
                integer[i] = numpy.ceil(x * self.inv[i])

            elif self.spacing[i] == 'logspace':
                x = paircoords[dim].copy()
                x[x == 0] = self.min[i] * 0.9
                x = numpy.log10(x / self.min[i])
                integer[i] = numpy.ceil(x * self.inv[i])

            elif self.spacing[i] is None:
                edge = self.edges if self.Ndim == 1 else self.edges[i]
                integer[i] = numpy.searchsorted(edge, paircoords[dim], side='left')

        return numpy.ravel_multi_index(integer, self.shape, mode='clip')

    def digitize(self, r, i, j, data1, data2):
        """
        Calculate the bin number of pairs separated by distances r,
        Use :py:meth:`linear` to convert from multi-dimension bin index to
        linear index.

        Parameters
        ----------
        r   : array_like
            separation

        i, j : array_like
            index (i, j) of pairs.

        data1, data2 :
            The position of first point is data1.pos[i], the position of second point is
            data2.pos[j].

        Returns
        -------
        dig : the integer bin number for each pair
        paircoords: the coordinate of pairs, dictionary one array for each dimension, optional
                    if not provided, the bin center is not computed (may raise an error if requested)
        weights : the weighting for each bin on each channel, of shape (nchannel, len(dig)), optional, only
                  used for multi-channel counts.
        """
        raise NotImplementedError()

    def update_sums(self, r, i, j, data1, data2, sum1, sum2, N=None, centers_sum=None):
        """
        The main function that digitizes the pair counts,
        calls bincount for the appropriate `sum1` and `sum2`
        values, and adds them to the input arrays,

        will modify sum1, sum2, N, and centers_sum inplace.

        """
        # the summation values for this (r,i,j)
        sum1_ij, sum2_ij = compute_sum_values(i, j, data1, data2)

        # digitize
        digr = self.digitize(r, i, j, data1, data2)

        if len(digr) == 3 and isinstance(digr[1], dict):
            dig, paircoords, weights = digr
        elif len(digr) == 2 and isinstance(digr[1], dict):
            dig, paircoords = digr
            weights = None
        else:
            dig = digr
            paircoords = None
            weights = None

        # sum 1
        def add_one_channel(sum1c, sum1_ijc):
            if numpy.isscalar(sum1_ijc) or sum1_ijc.ndim == 1:
                sum1c.flat[:] += utils.bincount(dig, sum1_ijc, minlength=sum1c.size)
            else:
                for d in range(sum1c.shape[0]):
                    sum1c[d].flat[:] += utils.bincount(dig, sum1_ijc[...,d], minlength=sum1c[d].size)

        if self.channels:
            if weights is None:
                raise RuntimeError("`digitize` of multi channel paircount did not return a weight array for the channels")

            sum1_ij = weights * sum1_ij
            # sum1_ij[ichannel, dig, dim]
            for ichannel in range(len(self.channels)):
                add_one_channel(sum1[ichannel], sum1_ij[ichannel])
        else:
            # sum1_ij[dig, dim]
            add_one_channel(sum1, sum1_ij)

        # sum 2, if both data are not points
        if not numpy.isscalar(sum2):
            sum2.flat[:] += utils.bincount(dig, sum2_ij, minlength=sum2.size)

        if N is not None:
            if not paircoords:
                raise RuntimeError("Bin center is requested but not returned by digitize")
            # update the mean coords
            self._update_mean_coords(dig, N, centers_sum, **paircoords)

    def sum_shapes(self, data1, data2):
        """
        Return the shapes of the summation arrays,
        given the input data and shape of the bins
        """
        # the linear shape (put extra dimensions first)
        linearshape = [-1] + list(self.shape)

        # determine the full shape
        subshapes = [list(d.subshape) for d in [data1, data2] if isinstance(d, field)]
        subshape = []
        if len(subshapes) == 2:
            assert subshapes[0] == subshapes[1]
            subshape = subshapes[0]
        elif len(subshapes) == 1:
            subshape = subshapes[0]
        fullshape = subshape + list(self.shape)

        # prepend the shape for different channels
        if self.channels:
            fullshape = [len(self.channels)] + fullshape

        return linearshape, fullshape

    def _update_mean_coords(self, dig, N, centers_sum, **paircoords):
        """
        Update the mean coordinate sums
        """
        if N is None or centers_sum is None: return

        N.flat[:] += utils.bincount(dig, 1., minlength=N.size)
        for i, dim in enumerate(self.dims):
            size = centers_sum[i].size
            centers_sum[i].flat[:] += utils.bincount(dig, paircoords[dim], minlength=size)

    def update_mean_coords(self, dig, N, centers_sum, **paircoords):
        warnings.warn("update_mean_coords is deprecated. Return a dictionary of paircoords in digitize function instead.", DeprecationWarning, stacklevel=2)
        self._update_mean_coords(dig, N, centers_sum, **paircoords)

class RmuBinning(Binning):
    """
    Binning in R and mu (angular along line of sight)
    mu = cos(theta), relative to line of sight from a given observer.

    Parameters
    ----------
    rbins : array_like
        the array of R bin edges
    Nmu : int
        number of bins in mu direction.
    observer : array_like (Ndim)
        location of the observer (for line of sight)
    mu_min : float, optional
        the lower edge of the first``mu`` bin; default is ``-1``
    mu_max : float, optional
        the upper edge of the last ``mu`` bin; default is ``1``
    absmu : bool, optional
        if ``mu_min`` > 0, this flag specifies whether to take the
        absolute magnitude of ``mu`` such that pairs with negative ``mu``
        are included
    """
    def __init__(self, rbins, Nmu, observer, mu_min=-1., mu_max=1., absmu=False):

        assert -1.0 <= mu_min <= 1.0, 'mu_min must be >= -1 and <= 1'
        assert -1.0 <= mu_max <= 1.0, 'mu_max must be >= -1 and <= 1'
        assert mu_min < mu_max, 'mu_min must be less than mu_max'

        mubins = numpy.linspace(mu_min, mu_max, Nmu+1)
        Binning.__init__(self, ['r', 'mu'], [rbins, mubins])
        self.observer = numpy.array(observer)
        self.absmu = absmu and mu_min >= 0

    def digitize(self, r, i, j, data1, data2):

        r1 = data1.pos[i]
        r2 = data2.pos[j]
        center = 0.5 * (r1 + r2) - self.observer
        dr = r1 - r2
        dot = numpy.einsum('ij, ij->i', dr, center)
        center = numpy.einsum('ij, ij->i', center, center) ** 0.5

        with numpy.errstate(invalid='ignore'):
            mu = dot / (center * r)
        mu[r == 0] = 10.0
        if self.absmu: mu = numpy.abs(mu)
        dig = self.linear(r=r, mu=mu)

        return dig, dict(r=r, mu=mu)

class XYBinning(Binning):
    """
    Binning along Sky-Line-of-sight directions.

    The bins are be (sky, los)

    Parameters
    ----------
    Rmax     : float
        max radius to go to
    Nbins    : int
        number of bins in each direction.
    observer   : array_like (Ndim)
        location of the observer (for line of sight)

    Notes
    -----
    with numpy imshow , the second axis los, will be vertical
            with imshow( ..T,) the sky will be vertical.
    """

    def __init__(self, Rmax, Nbins, observer):
        self.Rmax = Rmax
        sky_bins = numpy.linspace(0, Rmax, Nbins)
        los_bins = numpy.linspace(-Rmax, Rmax, 2*Nbins)
        Binning.__init__(self, ['sky', 'los'], [sky_bins, los_bins])
        self.observer = observer

    def digitize(self, r, i, j, data1, data2):
        r1 = data1.pos[i]
        r2 = data2.pos[j]
        center = 0.5 * (r1 + r2) - self.observer
        dr = r1 - r2
        dot = numpy.einsum('ij, ij->i', dr, center)
        center2 = numpy.einsum('ij, ij->i', center, center)
        los = dot / center2 ** 0.5
        dr2 = numpy.einsum('ij, ij->i', dr, dr)
        x2 = numpy.abs(dr2 - los ** 2)
        sky = x2 ** 0.5

        dig = self.linear(sky=sky, los=los)

        return dig, dict(sky=sky, los=los)

class RBinning(Binning):
    """
    Binning along radial direction.

    Parameters
    ----------
    rbins : array_like
        the R bin edges
    """
    def __init__(self, rbins):
        Binning.__init__(self, ['r'], [rbins])

    def digitize(self, r, i, j, data1, data2):

        # linear bins
        dig = self.linear(r=r)

        return dig, dict(r=r)

class FastRBinning(RBinning):
    """
    Binning along radial direction, use the fast node count algorithm when possible.

    Parameters
    ----------
    rbins : array_like
        the R bin edges
    """
    enable_fast_node_count = True


class MultipoleBinning(Binning):
    """
    Binning in R and `ell`, the multipole number, in the
    flat sky approximation, such that all pairs have the
    same line-of-sight, which is taken to be the axis specified
    by the `los` parameter (default is the last dimension)

    Parameters
    ----------
    rbins : array_like
        the array of R bin edges
    ells : list of int
        the multipole numbers to compute
    los : int, {0, 1, 2}
        the axis to treat as the line-of-sight

    Notes
    -----
    This can be slow, especially for a large set of `ells`. It is
    likely better to use finely-binned :class:`RmuBinning` and
    simply integrate the results against the appropriate Legendre
    polynomial to compute multipoles
    """
    def __init__(self, rbins, ells):
        from scipy.special import legendre

        Binning.__init__(self, ['r'], [rbins], ells)

        self.ells = numpy.array(ells)
        self.legendre = [legendre(l) for l in self.channels]


    def digitize(self, r, i, j, data1, data2):

        r1 = data1.pos[i]
        r2 = data2.pos[j]
        center = 0.5 * (r1 + r2)
        dr = r1 - r2
        dot = numpy.einsum('ij, ij->i', dr, center)
        center = numpy.einsum('ij, ij->i', center, center) ** 0.5

        with numpy.errstate(invalid='ignore', divide='ignore'):
            mu = dot / (center * r)

        # linear bin index and weights
        dig = self.linear(r=r)
        w = numpy.array([leg(mu) for leg in self.legendre]) # shape should be (N_ell, len(r1))
        w *= (2*self.ells+1)[:,None]

        return dig, dict(r=r), w


class FlatSkyMultipoleBinning(Binning):
    """
    Binning in R and `ell`, the multipole number, in the
    flat sky approximation, such that all pairs have the
    same line-of-sight, which is taken to be the axis specified
    by the `los` parameter (default is the last dimension)


    Parameters
    ----------
    rbins : array_like
        the array of R bin edges
    ells : list of int
        the multipole numbers to compute
    los : int, {0, 1, 2}
        the axis to treat as the line-of-sight
    """
    def __init__(self, rbins, ells, los, **kwargs):
        from scipy.special import legendre

        Binning.__init__(self, ['r'], [rbins], ells)

        self.los = los
        self.ells = numpy.array(ells)
        self.legendre = [legendre(l) for l in self.channels]


    def digitize(self, r, i, j, data1, data2):

        r1 = data1.pos[i]
        r2 = data2.pos[j]

        # parallel separation
        d_par = (r1-r2)[:,self.los]

        # enforce periodic boundary conditions
        if data1.boxsize is not None:
            L = data1.boxsize[self.los]
            d_par[d_par > L*0.5] -= L
            d_par[d_par <= -L*0.5] += L

        # mu
        with numpy.errstate(invalid='ignore'):
            mu = d_par / r

        # linear bin index and weights
        dig = self.linear(r=r)
        w = numpy.array([leg(mu) for leg in self.legendre]) # shape should be (N_ell, len(r1))
        w *= (2*self.ells+1)[:,None]

        return dig, dict(r=r), w

class FlatSkyBinning(Binning):
    """
    Binning in R and mu, in the flat sky approximation, such
    that all pairs have the same line-of-sight, which is
    taken to be the axis specified by the `los` parameter
    (default is the last dimension)


    Parameters
    ----------
    rbins : array_like
        the array of R bin edges
    Nmu : int
        the number of bins in `mu` direction.
    los : int, {0, 1, 2}
        the axis to treat as the line-of-sight
    mu_min : float, optional
        the lower edge of the first``mu`` bin; default is ``-1``
    mu_max : float, optional
        the upper edge of the last ``mu`` bin; default is ``1``
    absmu : bool, optional
        if ``mu_min`` > 0, this flag specifies whether to take the
        absolute magnitude of ``mu`` such that pairs with negative ``mu``
        are included
    """
    def __init__(self, rbins, Nmu, los, mu_min=-1., mu_max=1., absmu=False):

        assert -1.0 <= mu_min <= 1.0, 'mu_min must be >= -1 and <= 1'
        assert -1.0 <= mu_max <= 1.0, 'mu_max must be >= -1 and <= 1'
        assert mu_min < mu_max, 'mu_min must be less than mu_max'

        mubins = numpy.linspace(mu_min, mu_max, Nmu+1)
        Binning.__init__(self, ['r','mu'], [rbins, mubins])
        self.los = los
        self.absmu = absmu and mu_min >= 0.

    def digitize(self, r, i, j, data1, data2):
        r1 = data1.pos[i]
        r2 = data2.pos[j]

        # parallel separation
        d_par = (r1-r2)[:,self.los]

        # enforce periodic boundary conditions
        if data1.boxsize is not None:
            L = data1.boxsize[self.los]
            d_par[d_par > L*0.5] -= L
            d_par[d_par <= -L*0.5] += L

        # mu
        with numpy.errstate(invalid='ignore'):
            mu = d_par / r
        mu[r == 0] = 10.0 # ignore self pairs by setting mu out of bounds
        if self.absmu: mu = numpy.abs(mu)

        # linear bin index
        dig = self.linear(r=r, mu=mu)

        return dig, dict(r=r, mu=mu)

class paircount(object):
    """
    Paircounting via a KD-tree, on two data sets.

    Attributes
    ----------
    sum1 :  array_like
        the numerator in the correlator
    sum2 :  array_like
        the denominator in the correlator
    centers : list
        the centers of the corresponding corr bin, one item per
        binning direction.
    edges :   list
        the edges of the corresponding corr bin, one item per
        binning direction.
    binning : :py:class:`Binning`
        binning object of this paircount
    data1   : :py:class:`dataset`
        input data set1. It can be either
        :py:class:`field` for discrete sampling of a continuous
        field, or :py:class:`kdcount.models.points` for a point set.
    data2   : :py:class:`dataset`
        input data set2, see above.
    np : int
        number of parallel processes. set to 0 to disable parallelism

    Notes
    -----
    The value of sum1 and sum2 depends on the types of input

    For :py:class:`kdcount.models.points` and :py:class:`kdcount.models.points`:
      - sum1 is the per bin sum of products of weights
      - sum2 is always 1.0

    For :py:class:`kdcount.models.field` and :py:class:`kdcount.models.points`:
      - sum1 is the per bin sum of products of weights and the field value
      - sum2 is the per bin sum of products of weights

    For :py:class:`kdcount.models.field` and :py:class:`kdcount.models.field`:
      - sum1 is the per bin sum of products of weights and the field value
        (one value per field)
      - sum2 is the per bin sum of products of weights

    With this convention the usual form of Landy-Salay estimator is (
    for points x points:

        (DD.sum1 -2r DR.sum1 + r2 RR.sum1) / (r2 RR.sum1)

        with r = sum(wD) / sum(wR)

    """
    def __init__(self, data1, data2, binning, compute_mean_coords=False, usefast=None, np=None):
        """
        binning is an instance of Binning, (eg, RBinning, RmuBinning)

        Notes
        -----
        *   if the value has multiple components, return counts with be 'tuple',
            one item for each component
        *   if `compute_mean_coords` is `True`, then `meancenters` will hold
            the mean coordinate value in each bin.
        """
        if usefast is not None:
            warnings.warn("usefast is no longer supported. Declare a binning class is compatible"
                          "to the node counting implementation with `enable_fast_node_count=True` as a class attribute",
                            DeprecationWarning, stacklevel=2)

        pts_only = isinstance(data1, points) and isinstance(data2, points)
        if binning.enable_fast_node_count:
            if not pts_only:
                raise ValueError("fast node based paircount only works with points")
            if compute_mean_coords:
                raise ValueError("fast node based paircount cannot count for mean coordinates of a bin")

        with utils.MapReduce(np=np) as pool:

            size_hint = pool.np * 2

            # run the work, using a context manager
            with paircount_queue(self, binning, [data1, data2],
                size_hint=size_hint,
                compute_mean_coords=compute_mean_coords,
                pts_only=pts_only,
                ) as queue:

                pool.map(queue.work, range(queue.size), reduce=queue.reduce)

        self.weight = data1.norm * data2.norm

class paircount_queue(object):
    """
    A queue of paircount jobs. roughly size_hint jobs are created, and they are
    reduced to the paircount objects when the queue is joined.

    """
    def __init__(self, pc, binning, data, size_hint, compute_mean_coords, pts_only):
        """
        Parameters
        ----------
        pc : `paircount`
            the parent pair count object, which we will attach the final results to
        binning : `Binning`
            the binning instance
        data : tuple
            tuple of the two data trees that we are correlating
        size_hint : int, optional
            the number of jobs to create, as an hint. None or zero to create 1 job.
        compute_mean_coords : bool, optional
            whether to compute the average coordinate value of each pair per bin
        """
        self.pc      = pc
        self.bins    = binning
        self.data    = data
        self.size_hint      = size_hint
        self.compute_mean_coords = compute_mean_coords
        self.pts_only = pts_only

    def work(self, i):
        """
        Internal function that performs the pair-counting
        """
        n1, n2 = self.p[i]

        # initialize the total arrays for this process
        sum1 = numpy.zeros_like(self.sum1g)
        sum2 = 1.
        if not self.pts_only: sum2 = numpy.zeros_like(self.sum2g)

        if self.compute_mean_coords:
            N = numpy.zeros_like(self.N)
            centers_sum = [numpy.zeros_like(c) for c in self.centers]
        else:
            N = None; centers_sum = None

        if self.bins.enable_fast_node_count:
            # field x points is not supported.
            # because it is more likely need to deal
            # with broadcasting
            sum1attrs = [ d.attr for d in self.data ]

            counts, sum1c = n1.count(n2, self.bins.edges,
                                attrs=sum1attrs)
            sum1[..., :-1] = sum1c.T
            sum1[..., -1] = 0
        else:

            def callback(r, i, j):
                # just call the binning function, passing the
                # sum arrays to fill in
                self.bins.update_sums(r, i, j, self.data[0], self.data[1], sum1, sum2, N=N, centers_sum=centers_sum)

            n1.enum(n2, self.bins.Rmax, process=callback)

        if not self.compute_mean_coords:
            return sum1, sum2
        else:
            return sum1, sum2, N, centers_sum

    def reduce(self, sum1, sum2, *args):
        """
        The internal reduce function that sums the results from various
        processors
        """
        self.sum1g[...] += sum1
        if not self.pts_only: self.sum2g[...] += sum2

        if self.compute_mean_coords:
            N, centers_sum = args
            self.N[...] += N
            for i in range(self.bins.Ndim):
                self.centers[i][...] += centers_sum[i]

    def _partition(self, tree1, tree2, size_hint=128):
        if size_hint is None or size_hint == 0: # serial mode
            return [(tree1, tree2)]

        import heapq
        def makeitem(n1, n2):
            if n1.size > n2.size:
                return (-n1.size, 0, (n1, n2))
            else:
                return (-n2.size, 1, (n1, n2))
        heap = []
        heapq.heappush(heap, makeitem(tree1, tree2))
        while len(heap) < size_hint:
            junk, split, n = heapq.heappop(heap)
            if n[split].less is None:
                # put it back!
                heapq.heappush(heap, makeitem(*n))
                break
            item = list(n)
            item[split] = n[split].less
            heapq.heappush(heap, makeitem(*item))
            item[split] = n[split].greater
            heapq.heappush(heap, makeitem(*item))
        p = []
        while heap:
            junk, split, n = heapq.heappop(heap)
            p.append(n)
        return p

    def __enter__(self):
        """
        Initialize and setup the various arrays needed to do the work
        """
        tree1 = self.data[0].tree.root
        tree2 = self.data[1].tree.root

        self.p = self._partition(tree1, tree2, self.size_hint)
        self.size = len(self.p)

        # initialize arrays to hold total sum1 and sum2
        # grabbing the desired shapes from the binning instance
        linearshape, self.fullshape = self.bins.sum_shapes(*self.data)
        self.sum1g = numpy.zeros(self.fullshape, dtype='f8').reshape(linearshape)
        if not self.pts_only:
            self.sum2g = numpy.zeros(self.bins.shape, dtype='f8').reshape(linearshape)

        # initialize arrays for computing mean coords
        # for storing the mean values in each bin
        # computed when pair counting
        self.N = None; self.centers = None
        if self.compute_mean_coords:
            self.N = numpy.zeros(self.bins.shape)
            self.centers = [numpy.zeros(self.bins.shape) for i in range(self.bins.Ndim)]

        return self

    def __exit__(self, type, value, traceback):
        """
        Finalize the work, attaching the results of the work to the parent
        `paircount` instance

        The following attributes are attached:

        `fullsum1`, `sum1`, `fullsum2`, `sum2`, `binning`, `edges`, `centers`,
        `pair_counts`, `mean_centers_sum`, `mean_centers`
        """
        self.pc.fullsum1 = self.sum1g.reshape(self.fullshape).copy()
        self.pc.sum1 = self.pc.fullsum1[tuple([Ellipsis] + [slice(1, -1)] * self.bins.Ndim)]

        self.pc.fullsum2 = None; self.pc.sum2 = None
        if not self.pts_only:
            self.pc.fullsum2 = self.sum2g.reshape(self.bins.shape).copy()
            self.pc.sum2 = self.pc.fullsum2[tuple([slice(1, -1)] * self.bins.Ndim)]

        self.pc.binning = self.bins
        self.pc.edges = self.bins.edges
        self.pc.centers = self.bins.centers

        # add the mean centers info
        if self.compute_mean_coords:

            # store the full sum too
            sl = tuple([slice(1, -1)] * self.bins.Ndim)
            self.pc.pair_counts = self.N[sl]
            self.pc.mean_centers_sum = []

            # do the division too
            self.pc.mean_centers = []
            with numpy.errstate(invalid='ignore'):
                for i in range(self.bins.Ndim):
                    self.pc.mean_centers_sum.append(self.centers[i][sl])
                    y = self.pc.mean_centers_sum[-1] / self.pc.pair_counts
                    self.pc.mean_centers.append(y)

            if self.bins.Ndim == 1:
                self.pc.mean_centers = self.pc.mean_centers[0]


#------------------------------------------------------------------------------
# main functions for testing
#------------------------------------------------------------------------------
def _main():
    pm = numpy.fromfile('A00_hodfit.raw').reshape(-1, 8)[::1, :3]
    wm = numpy.ones(len(pm))
    martin = points(pm, wm)
    pr = numpy.random.uniform(size=(1000000, 3))
    wr = numpy.ones(len(pr))
    random = points(pr, wr)
    binning = RBinning(numpy.linspace(0, 0.1, 40))
    DR = paircount(martin, random, binning)
    DD = paircount(martin, martin, binning)
    RR = paircount(random, random, binning)
    r = martin.norm / random.norm
    return binning.centers, (DD.sum1 -
            2 * r * DR.sum1 + r ** 2 * RR.sum1) / (r ** 2 * RR.sum1)

def _main2():
    sim = numpy.fromfile('grid-128.raw', dtype='f4')
    pos = numpy.array(numpy.unravel_index(numpy.arange(sim.size),
        (128, 128, 128))).T / 128.0
    numpy.random.seed(1000)
    sample = numpy.random.uniform(size=len(pos)) < 0.1
    value = numpy.tile(sim[sample], (2, 1)).T
#    value = sim[sample]
    data = field(pos[sample], value=value)
    print('data ready')
    binning = RBinning(numpy.linspace(0, 0.1, 40))
    DD = paircount(data, data, binning)

    return DD.centers, DD.sum1 / DD.sum2

def _main3():
    sim = numpy.fromfile('grid-128.raw', dtype='f4')
    pos = numpy.array(numpy.unravel_index(numpy.arange(sim.size),
        (128, 128, 128))).T / 128.0
    numpy.random.seed(1000)
    sample = numpy.random.uniform(size=len(pos)) < 0.2
    value = numpy.tile(sim[sample], (2, 1)).T
    data = field(pos[sample], value=value)
    print('data ready')
    rbins = numpy.linspace(0, 0.10, 8)
    Nmu = 20
    DD = paircount(data, data, RmuBinning(rbins, Nmu, 0.5))
    return DD
