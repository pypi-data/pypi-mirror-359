from kdcount import sphere
from kdcount import cluster
from kdcount import correlate
import numpy
from numpy.testing import assert_equal, assert_allclose


def test_cluster():
    numpy.random.seed(1234)
    dec = numpy.arcsin(numpy.random.uniform(-1, 1, size=100000)) / numpy.pi * 180
    ra = numpy.random.uniform(0, 2 * numpy.pi, size=100000) / numpy.pi * 180

    # testing bootstrap
    for area, rand, in sphere.bootstrap(4, (ra, dec), 41252.96 / len(dec)):
        pass

    dataset = sphere.points(ra, dec)

    r = cluster.fof(dataset, 0.00001, np=None)

    assert r.N == len(dataset)

    binning = sphere.FastAngularBinning(numpy.linspace(0, 1.0, 10))
    binning1 = sphere.AngularBinning(numpy.linspace(0, 1.0, 10))
    binningR = correlate.RBinning(binning.edges)

    r = correlate.paircount(dataset, dataset, binning=binning)
    r1 = correlate.paircount(dataset, dataset, binning=binning1, compute_mean_coords=True)

    r2 = correlate.paircount(dataset, dataset, binning=binningR)

    # make sure mean_centers compute angular centers
    for i, val in enumerate(r1.mean_centers):
        assert binning.angular_edges[i] < val < binning.angular_edges[i+1]
    assert_equal(r1.sum1, r2.sum1)
    assert_equal(r1.sum1, r.sum1)
    assert_allclose(
    r.sum1,
    numpy.diff(2 * numpy.pi * (1 - numpy.cos(numpy.radians(binning.angular_edges)))) / ( 4 * numpy.pi) * len(ra) ** 2, rtol=10e-2)

def test_field():
    numpy.random.seed(1234)
    dec = numpy.arcsin(numpy.random.uniform(-1, 1, size=100000)) / numpy.pi * 180
    ra = numpy.random.uniform(0, 2 * numpy.pi, size=100000) / numpy.pi * 180

    dataset = sphere.field(ra, dec, value=numpy.ones_like(dec) * 0.5)

    binning = sphere.AngularBinning(numpy.linspace(0, 1.0, 10))
    r = correlate.paircount(dataset, dataset, binning=binning)
    # FIXME: assert on correctness.

def test_bootstrap():
    numpy.random.seed(1234)
    dec = numpy.arcsin(numpy.random.uniform(-1, 1, size=10000)) / numpy.pi * 180
    ra = numpy.random.uniform(0, 2 * numpy.pi, size=10000) / numpy.pi * 180
    dec1 = numpy.arcsin(numpy.random.uniform(-1, 1, size=100)) / numpy.pi * 180
    ra1 = numpy.random.uniform(0, 2 * numpy.pi, size=100) / numpy.pi * 180

    # testing bootstrap with small eff area (high nbar)
    for area, rand, d1, d2 in sphere.bootstrap(16, (ra, dec), 41252.96 / (1000* len(dec)), (ra1, dec1), (ra, dec)):
        pass
