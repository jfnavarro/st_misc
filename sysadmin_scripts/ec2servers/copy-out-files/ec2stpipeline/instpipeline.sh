#!/bin/bash
set -e

st_pipeline_dir="$1"

print_usage_and_exit() {
  echo Usage: $0 stpipeline_dir >&2
  exit 1
}

if [ $# -ne 1 ]; then
    print_usage_and_exit
fi

if [ ! -d "$st_pipeline_dir" ]; then
  echo Wrong command line parameters >&2
  print_usage_and_exit
fi

if [ \( ! -d "$st_pipeline_dir/pairReadsHadoop" \) -o \( ! -d "$st_pipeline_dir/pipeline" \) ]; then
  echo The directory  "$st_pipeline_dir" does not seem to be a git clone of the st_pipeline  >&2
  print_usage_and_exit
fi
   
git clone git://github.com/yyuu/pyenv.git ~/.pyenv
git -C ~/.pyenv checkout cb65df8becb4ddf99acf711ecad399f4e55182c7
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.profile
echo 'export PATH="$PYENV_ROOT/bin:$HOME/bin:$PATH"' >> ~/.profile
echo 'eval "$(pyenv init -)"' >> ~/.profile
. ~/.profile
pyenv install 2.7.6
pyenv rehash
pyenv global 2.7.6
mkdir -p ~/bin
unzip -p "$st_pipeline_dir/pipeline/dependencies/STAR-STAR_2.4.0j.zip" STAR-STAR_2.4.0j/bin/Linux_x86_64/STAR > ~/bin/STAR
chmod 755 ~/bin/STAR
pip install numpy==1.10.1
cd "$st_pipeline_dir/pipeline"
python setup.py build
python setup.py install
pyenv rehash
python setup.py test
