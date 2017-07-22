#!/bin/sh

# This shell script is used by jenkins at st-ci-master.spatialtranscriptomics.com
# to build st_pipeline
#
# See also st_code/jenkins/README.txt

set -e

# Create some temp folders
installdir=`mktemp -d --tmpdir=/tmp star.installdir.XXXXXXXXXX`
pipeline_sourcecopy_dir=`mktemp -d --tmpdir=/tmp pipeline.sourcecopy.XXXXXXXXXX`

# Ensure the PYENV environment
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# Copy pipeline source to temp folder
cp -r $WORKSPACE $pipeline_sourcecopy_dir

# Install STAR and make it accesible
cd $pipeline_sourcecopy_dir/workspace/pipeline/dependencies
unzip STAR-STAR_2.4.0j.zip
cd STAR-STAR_2.4.0j/bin/Linux_x86_64
mkdir $installdir/bin
cp STAR $installdir/bin/

# Export STAR install folder paths 
export PATH=$PATH:$installdir/bin

# Install pipeline
# it would be cleaner to install the pipeline in a tmp folder
# but there seems to be problems with taggd when doing that
# so we install the pipeline in the default pyenv folder
# jenkins builds for the pipeline are unique anyways
cd $pipeline_sourcecopy_dir/workspace/pipeline
pip install numpy
pip install invoke
invoke clean
python setup.py clean
python setup.py build
python setup.py install 
pyenv rehash
# Check for unit-tests to pass
python setup.py test
# Check that the binary can be executed
tmpfile=`mktemp`
# As we have previously run "set -e", the script would end after this line if we would not append " || /bin/true"
st_pipeline_run.py 2> $tmpfile || /bin/true
cd /tmp
rm -rf "$installdir"
rm -rf "$pipeline_sourcecopy_dir"
if grep -q "st_pipeline_run.py: error: too few arguments" $tmpfile; then exit 0 ; else exit 1; fi
