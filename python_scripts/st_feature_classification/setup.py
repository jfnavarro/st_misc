from setuptools import setup, find_packages
from glob import glob

setup(name="st_feature_classification",
      scripts=glob("scripts/*.py"),
      packages=find_packages()
    )
