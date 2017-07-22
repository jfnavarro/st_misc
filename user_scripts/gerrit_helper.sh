# It might be useful to put this content into your ~/.bashrc



function clone {
  # Don't forget to edit the variable gerrit_username below!
  gerrit_username=esjolund
  now=`date +"%A-%H:%M"`
  tmpdir=`mktemp -d /tmp/$1-clone-${now}-XXX`
  chmod 700 $tmpdir
  pushd $tmpdir
  gerrit_URL=ssh://${gerrit_username}@gerrit.spatialtranscriptomics.com:29418/$1
  git clone $gerrit_URL && scp -p -P 29418 ${gerrit_username}@gerrit.spatialtranscriptomics.com:hooks/commit-msg $1/.git/hooks/
  cd $1
  git remote add gerrit $gerrit_URL
  echo run \"popd\" to get back to previous directory
}

alias gpush='git push origin HEAD:refs/for/master'
