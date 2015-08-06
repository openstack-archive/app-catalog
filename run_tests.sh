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
  pushd $root/openstack_catalog/web > /dev/null
  for x in murano_apps heat_templates glance_images; do
    python $root/tools/yaml2json.py < static/$x.yaml > static/$x.json
  done
  ${command_wrapper} python $root/tools/testserver.py runserver $testopts $testargs
  popd > /dev/null
  echo "Server stopped."
}

# Development server
if [ $runserver -eq 1 ]; then
    run_server
    exit $?
fi

