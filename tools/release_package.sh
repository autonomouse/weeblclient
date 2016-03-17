#!/bin/bash
# Should be run from top of source tree with local weeblclient in PYTHONPATH
rm -rf *.egg-info
[[ -n "$(git status --porcelain)" ]] && echo "Repo not clean" && exit 1
distro=${1:-"precise"}
git_version=$(git describe --dirty)
full_version=${git_version}~${distro}-0ubuntu1
echo $full_version
dch -b -D $distro --newversion ${full_version} "PPA build."
debcommit
git clean -xdf
fakeroot debian/rules get-orig-source
debuild -sa -S
rc=$?
# revert the PPA build changelog entry and revision
git reset --hard HEAD
rm -rf *.egg-info
[[ ! $rc ]] && echo "Build failed" && exit 1
echo "Run: dput ppa:oil-ci/integration ../weeblclient_${full_version}_source.changes"
