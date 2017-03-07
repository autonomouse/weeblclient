#!/bin/bash -e
PROJECTS="weeblclient"

for project in $PROJECTS; do
    echo "Testing $project"
    if echo "$@" | grep -q "lint" ; then
      echo "Running flake8 lint tests..."
      flake8 --exclude ${project}/tests/ ${project} --ignore=F403
      echo "OK"
    fi

    if echo "$@" | grep -q "unit" ; then
      echo "Running unit tests..."
      /usr/bin/nosetests -v --nologcapture --with-coverage ${project}/
    fi
done
