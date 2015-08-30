#!/bin/bash -x
ROOTDIR=`pushd $(dirname $0)/.. > /dev/null /dev/null; pwd; popd > /dev/null`
echo $ROOTDIR
pushd $ROOTDIR/openstack_catalog/web > /dev/null
mkdir -p api/v1/
if [ ! -f api/v1/assets ] || [ static/assets.yaml -nt api/v1/assets ];
then
	python $ROOTDIR/tools/yaml2json.py < static/assets.yaml > api/v1/assets
fi
popd > /dev/null
