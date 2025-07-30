from setuptools import setup
from pyappcreator import VERSION

DIST_NAME = "pyappcreator"
__author__ = "baozilaji"
__author_email__ = "baozilaji@gmail.com"

setup(
    name=DIST_NAME,
    version=VERSION,
    description="Python Application Creator",
    packages=[DIST_NAME],
    author=__author__,
    author_email=__author_email__,
    url="https://cnb.cool/baozilaji/pyappcreator",
    python_requires='>=3.9',
    install_requires=open("requirements.txt").read().splitlines(),
)
