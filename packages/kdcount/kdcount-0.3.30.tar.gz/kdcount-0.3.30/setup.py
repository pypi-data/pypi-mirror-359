from distutils.core import setup
from Cython.Build import cythonize
from distutils.extension import Extension
import numpy

extensions = [
        Extension("kdcount.pykdcount",
            sources = ["kdcount/pykdcount.pyx",
            'kdcount/kdtree.c',
            'kdcount/kd_fof.c',
            'kdcount/kd_fof_linkedlist.c',
            'kdcount/kd_enum.c',
            'kdcount/kd_force.c',
            'kdcount/kd_count.c', 'kdcount/kd_integrate.c'],
            include_dirs=["kdcount/", numpy.get_include()],
            extra_compile_args=['-O3', '-g'],
            extra_link_args=['-O3', '-g'],
            libraries = ['m']
            )
        ]

def find_version(path):
    import re
    # path shall be a plain ascii text file.
    s = open(path, 'rt').read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              s, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Version not found")

setup(name="kdcount", version=find_version("kdcount/version.py"),
      author="Yu Feng",
      author_email="rainwoodman@gmail.com",
      description="A slower KDTree cross correlator",
      url="http://github.com/rainwoodman/kdcount",
      zip_safe=False,
      package_dir = {'kdcount': 'kdcount'},
      packages = [
        'kdcount', 'kdcount.tests'
      ],
      license='GPL3',
      requires=['numpy', 'cython'],
      ext_modules = cythonize(extensions),
      )

