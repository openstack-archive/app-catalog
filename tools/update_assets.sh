#!/bin/bash
ROOTDIR=`pushd $(dirname $0)/.. > /dev/null /dev/null; pwd; popd > /dev/null`
echo $ROOTDIR
pushd $ROOTDIR/openstack_catalog/web > /dev/null
mkdir -p api/v1/
if [ ! -f static/assets_dead.yaml ];
then
	echo 'assets: {}' > static/assets_dead.yaml
fi
if [ ! -f api/v1/assets ] || [ static/assets.yaml -nt api/v1/assets ] || [ static/assets_dead.yaml -nt api/v1/assets ];
then
	$ROOTDIR/tools/asset_history.sh static/assets.yaml > /tmp/assets_merge.yaml
	python $ROOTDIR/tools/yaml2json.py /tmp/assets_merge.yaml static/assets_dead.yaml < static/assets.yaml > /tmp/assets.$$
	zopfli --i150 -c /tmp/assets.$$ > /tmp/assets.$$.gz || gzip -c /tmp/assets.$$ > /tmp/assets.$$.gz
	mv /tmp/assets.$$.gz api/v1/assets.gz
	mv /tmp/assets.$$ api/v1/assets
fi
popd > /dev/null
