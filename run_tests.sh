#!/bin/bash -e
PROJECT=weebl
APPS=(oilserver)

if echo "$@" | grep -q "lint" ; then
  echo "Running flake8 lint tests..."
  flake8 --exclude ${PROJECT}/tests/ ${PROJECT} --ignore=F403
  echo "OK"
fi

if echo "$@" | grep -q "unit" ; then
  echo "Running unit tests..."
  for APP in $APPS
    do 
      ${PROJECT}/manage.py test $APP
    done
fi

if echo "$@" | grep -q "func" ; then
  echo "Running functional tests..."
  python3 ${PROJECT}/functional_tests.py
fi
