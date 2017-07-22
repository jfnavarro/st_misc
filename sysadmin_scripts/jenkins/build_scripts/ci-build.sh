#!/bin/bash

# This shell script is used by jenkins at st-ci-master.spatialtranscriptomics.com
# to build st_client.
#
# See also st_code/jenkins/README.txt

set -e

install_dir=`mktemp -d --tmpdir=/tmp tmp.build.XXXXXXXXXX`

qtdir=/var/lib/jenkins/Qt/5.5/gcc_64
#cmake_path=/var/lib/jenkins/st-deps/cmake-3.3.2-Linux-x86_64/bin/cmake
cmake_install_dir=/var/lib/jenkins/st-deps/cmake-3.0.1-Linux-i386/
cmake_path=$cmake_install_dir/bin/cmake
ctest_path=$cmake_install_dir/bin/ctest

cmake_extra_option="-G Ninja \"-DCMAKE_MODULE_PATH=$qt3d_dir;$qtdir\" -DCMAKE_BUILD_TYPE=$buildtype -DSERVER:STRING=production"
export PATH=/usr/lib/ccache:$PATH

# We just want to run cppcheck once. The combination "clang" and "Release" was chosen so we test the production version.
if [ $compiler = "clang" -a $buildtype = "Release" ]; then
  cppcheck -I $WORKSPACE/src --std=c++11 --enable=all --suppress=missingInclude --suppress=unusedFunction --error-exitcode=2 --template "{file}({line}): {severity} ({id}): {message}" $WORKSPACE/src
fi

case $compiler in
    clang)
  export CC="ccache clang -Qunused-arguments"
  export CXX="ccache clang++ -Qunused-arguments"
        ;;
    gcc)
        ;;
    *)
  echo "Error: unknown compiler: $1"
  exit
esac

build_dir=`mktemp -d --tmpdir=/tmp tmp.build.XXXXXXXXXX`
cd $build_dir
$cmake_path $cmake_extra_option  -DCMAKE_PREFIX_PATH="$qtdir;"  -DCMAKE_INSTALL_PREFIX="$install_dir" "$WORKSPACE"
ninja

# To circumvent: "QXcbConnection: Could not connect to display :0"
# http://unix.stackexchange.com/a/191310/9360
Xvfb :1 &
PID=$!
DISPLAY=:1 $ctest_path -E .\*_gui_.\*
kill $PID

rm -rf "$build_dir"
rm -rf "$install_dir"
