#!/bin/bash
# Should be run from top of source tree with local weeblclient in PYTHONPATH
rm -rf *.egg-info
[[ -n "$(git status --porcelain)" ]] && echo "Repo not clean" && exit 1
distro=${1:-"precise"}
version="$(python -c 'from weeblclient import weebl_python2; print(weebl_python2.__version__)')"
echo $version
git_commit=$(git log -1 --date=short --format="%h")
dch -b -D $distro \
  --newversion ${version}~git${git_commit}~${distro}-0ubuntu1 \
  "PPA build."
debcommit
git clean -xdf
fakeroot debian/rules get-orig-source
debuild -sa -S
rc=$?
# revert the PPA build changelog entry and revision
git reset --hard HEAD
rm -rf *.egg-info
[[ ! $rc ]] && echo "Build failed" && exit 1
echo "Run: dput ppa:canonical-ci/oil-ci ../weeblclient*git${git_commit}*.changes"
