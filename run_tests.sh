#!/bin/bash

set -o errexit

function usage {
  echo "Usage: $0 [OPTION]..."
  echo "Run App Catalog's test suite(s)"
  echo ""
  echo "  --runserver              Run the development server for"
  echo "                           openstack_catalog in the virtual"
  echo "                           environment."
  echo "  -h, --help               Print this usage message"
  echo ""
  exit
}

# DEFAULTS FOR RUN_TESTS.SH
#
root=`pushd $(dirname $0) > /dev/null; pwd; popd > /dev/null`
venv=$root/.venv

runserver=0
testopts=""
testargs=""

# Jenkins sets a "JOB_NAME" variable, if it's not set, we'll make it "default"
[ "$JOB_NAME" ] || JOB_NAME="default"

function process_option {
  case "$1" in
    -h|--help) usage;;
    --runserver) runserver=1;;
    -*) testopts="$testopts $1";;
    *) testargs="$testargs $1"
  esac
}

# PROCESS ARGUMENTS, OVERRIDE DEFAULTS
for arg in "$@"; do
    process_option $arg
done

function run_server {
  echo "Starting development server..."
  $root/tools/update_assets.sh
  if [ ! -d $venv ]; then
    virtualenv $venv
    . $venv/bin/activate
  fi
  . $venv/bin/activate
  pip install -r $root/requirements.txt
#FIXME make venv cleaner.

# FIXME remove when CORS works
#  pushd $root/openstack_catalog/web > /dev/null
#  ${command_wrapper} python $root/tools/testserver.py runserver $testopts $testargs
  ${command_wrapper} python manage.py runserver $testopts $testargs
#  popd > /dev/null
  echo "Server stopped."
}

# Development server
if [ $runserver -eq 1 ]; then
    if [ "x$testargs" = "x" -o "$testargs x" = " x" ]; then
      testargs="127.0.0.1:18001"
    fi
    run_server
    exit $?
fi

