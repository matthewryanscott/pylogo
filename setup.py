from distutils.core import setup
import warnings
warnings.filterwarnings("ignore", "Unknown distribution option")

__version__ = '0.2'

import sys
# patch distutils if it can't cope with the "classifiers" keyword
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

setup(name="PyLogo",
      version=__version__,
      description="Logo interpreter",
      long_description="""\
An interpreter for the Logo educational programming language.
""",
      classifiers=["Development Status :: 3 - Alpha",
                   "Intended Audience :: Education",
                   "License :: OSI Approved :: Python Software Foundation License",
                   "Programming Language :: Logo",
                   "Programming Language :: Python",
                   "Topic :: Education",
                   "Topic :: Software Development :: Interpreters",
                   ],
      author="Ian Bicking",
      author_email="ianb@colorstudy.com",
      url="http://pylogo.sf.net",
      license="PSF",
      packages=["pylogo"],
      scripts=['scripts/pylogo'],
      download_url="http://prdownloads.sourceforge.net/pylogo/PyLogo-%s.tar.gz?download" % __version__,
      )

# Send announce to:
#   python-announce@python.org
#   python-list@python.org
#   edu-sig@python.org
#   LogoForum@yahoogroups.com
#   Freshmeat
#   PyPI
