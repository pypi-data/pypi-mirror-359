import sys
from distutils.core import setup

if not any(cmd in sys.argv for cmd in ["sdist", "egg_info"]):
    raise Exception(
        """
        Installation terminated!
        This is a stub package intended to mitigate the risks of dependency confusion.
        It reclaims a once-popular package name that the original author has since removed.
        This is package not intended to be installed and highlight problems in your setup.
        
        Read more: https://protsenko.dev/dependency-confusion
        """
    )

setup()
