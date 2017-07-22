Firstly these dependencies are needed absolutely all the time

    pip install numpy
    pip install matplotlib
    pip install python-cjson

Then one need to install some things with e.g. homebrew.

    brew install swig
    brew install pyqt
    cp -r /usr/local/lib/python2.7/site-packages/PyQt4 ~/.virtualenvs/spatial/lib/python2.7/site-packages/
    cp /usr/local/lib/python2.7/site-packages/sip* ~/.virtualenvs/spatial/lib/python2.7/site-packages/

The rest can be installed with `pip`

    pip install cython

However, `chaco` needs the development version of `enable` when running on Lion or Mountain Lion:

    pip install -e git+https://github.com/enthought/enable.git@fd2e69f24dbe07eedfc8f8fbde240c15ae495677#egg=enable-dev

Now it should be fine to install `chaco`

    pip install chaco

Then install the scripts and modules for the packages. Your life will be easier if you install it in `develop` mode.

    cd st_code/st_toolbox
    python setup.py develop
