from setuptools import setup, find_packages
from glob import glob

setup(name="st_toolbox",
      scripts=glob("scripts/*.py"),
      packages=find_packages()
    )
